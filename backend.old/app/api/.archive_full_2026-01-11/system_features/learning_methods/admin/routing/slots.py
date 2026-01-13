"""
Routing Capability Slots Endpoints (DDD)

Capability slot management and cost preset application.
Multi-model support where different capabilities use different AI models.
"""

from flask import request, jsonify, g, current_app
from typing import Dict, Any, Tuple
import logging

from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.extensions import limiter
from app.repositories.lm_slot import CapabilitySlotRepository
from app.services.lm_slot_resolver import get_resolver, get_manager
from app.services.audit_service import AuditService

from app.api.system_features.learning_methods.core.routing import (
    LMIDRange,
    CostPreset,
    SlotPresetAppliedEvent
)

from . import lm_routing_slots_bp

logger = logging.getLogger(__name__)


@lm_routing_slots_bp.route('/slots', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
@limiter.limit("60 per minute")
def get_all_capability_slots() -> Tuple[Dict[str, Any], int]:
    """
    Get all available capability slots.

    Returns:
        JSON response with slots list

    DDD: Exposes capability slot domain concept
    """
    try:
        slots = CapabilitySlotRepository.find_all_sorted()
        return jsonify({
            'success': True,
            'data': {
                'slots': slots
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting capability slots: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_SLOTS_ERROR',
                'message': str(e)
            }
        }), 500


@lm_routing_slots_bp.route('/slots/<slot_code>/models', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
@limiter.limit("60 per minute")
def get_compatible_models_for_slot(slot_code: str) -> Tuple[Dict[str, Any], int]:
    """
    Get all models compatible with a specific slot.

    Args:
        slot_code: Capability slot code (e.g., 'chat', 'vision', 'code')

    Returns:
        JSON response with compatible models

    DDD: Uses slot manager to determine compatibility
    """
    try:
        # Get slot details
        slot = CapabilitySlotRepository.find_by_code(slot_code)
        if not slot:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SLOT_NOT_FOUND',
                    'message': f'Unknown slot: {slot_code}'
                }
            }), 404

        # Get compatible models from manager
        manager = get_manager()
        models = manager.get_compatible_models(slot_code)

        return jsonify({
            'success': True,
            'data': {
                'slot_code': slot_code,
                'slot_display_name': slot.get('display_name'),
                'required_category': slot.get('required_category'),
                'compatible_models': models
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting compatible models: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_MODELS_ERROR',
                'message': str(e)
            }
        }), 500


@lm_routing_slots_bp.route('/slots/apply-preset', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
@limiter.limit("3 per hour")
def apply_slot_preset() -> Tuple[Dict[str, Any], int]:
    """
    Apply a cost preset to all LM slots.

    Automatically configures all slots for all LMs with models
    matching the cost preset.

    Request Body:
        {
            "preset": "cheap" | "medium" | "expensive"
        }

    Returns:
        JSON response with assignment results

    DDD: Uses CostPreset value object and emits SlotPresetAppliedEvent

    Presets:
        - cheap: Prefer free/low cost models
        - medium: Prefer medium cost models
        - expensive: Prefer high/very_high cost (premium) models

    Domain Rule: Chat slot ALWAYS uses best model regardless of preset
    """
    try:
        data = request.get_json() or {}
        preset_str = data.get('preset', 'medium')

        # DDD: Validate using CostPreset enum
        try:
            cost_preset = CostPreset(preset_str)
        except ValueError:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_PRESET',
                    'message': 'Preset must be cheap, medium, or expensive'
                }
            }), 400

        user_id = g.current_user.get('user_id')
        manager = get_manager()
        resolver = get_resolver()

        # Get cost priorities from CostPreset value object
        cost_preferences = cost_preset.cost_priority
        chat_cost_preference = CostPreset.chat_priority()

        configured = 0
        skipped = 0
        failed = 0
        assignments = []

        # Process each LM (0-11 for 12 Content-LMs)
        for lm_id in range(LMIDRange.MAX + 1):
            lm_overview = resolver.get_lm_overview(lm_id)
            if not lm_overview:
                continue

            for slot_info in lm_overview.get('slots', []):
                slot_code = slot_info['slot_code']

                try:
                    compatible_models = manager.get_compatible_models(slot_code)
                    if not compatible_models:
                        skipped += 1
                        continue

                    # DDD: Chat slot uses best model (domain rule)
                    active_preference = chat_cost_preference if slot_code == 'chat' else cost_preferences

                    # Sort models by cost preference
                    def get_sort_key(model):
                        cost = model.get('cost_level', 'medium')
                        try:
                            cost_priority = active_preference.index(cost)
                        except ValueError:
                            cost_priority = 999
                        return (cost_priority, model.get('model_name', ''))

                    sorted_models = sorted(compatible_models, key=get_sort_key)

                    if sorted_models:
                        best_model = sorted_models[0]
                        manager.assign_model(
                            learning_method_id=lm_id,
                            slot_code=slot_code,
                            model_id=best_model['model_id'],
                            scope='system',
                            created_by=user_id
                        )

                        configured += 1
                        assignments.append({
                            'lm_id': lm_id,
                            'lm_code': LMIDRange.format_code(lm_id),
                            'slot_code': slot_code,
                            'model_name': best_model.get('model_name'),
                            'cost_level': best_model.get('cost_level', 'medium')
                        })
                    else:
                        skipped += 1

                except Exception as slot_err:
                    logger.error(f'Failed to assign LM{lm_id}/{slot_code}: {slot_err}')
                    failed += 1

        # DDD: Create and log domain event
        event = SlotPresetAppliedEvent.create(
            preset=preset_str,
            configured_count=configured,
            skipped_count=skipped,
            failed_count=failed,
            applied_by=user_id
        )

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='apply_slot_preset',
            resource_type='lm_slot_routing',
            resource_id=preset_str,
            details=event.to_dict()
        )

        return jsonify({
            'success': True,
            'data': {
                'preset': preset_str,
                'preset_label': cost_preset.display_name,
                'configured': configured,
                'skipped': skipped,
                'failed': failed,
                'assignments': assignments[:20]  # Limit response size
            },
            'message': f'Preset "{cost_preset.display_name}" angewendet: {configured} Slots konfiguriert'
        }), 200

    except Exception as e:
        logger.error(f'Error applying preset: {e}')
        return jsonify({
            'success': False,
            'error': {
                'code': 'APPLY_PRESET_ERROR',
                'message': str(e)
            }
        }), 500
