"""
Routing Recommendations Endpoints (DDD)

Model recommendations and auto-setup for learning methods.
"""

from flask import request, jsonify, g, current_app
from typing import Dict, Any, Tuple, List
import logging

from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.extensions import limiter
from app.repositories.lm_model_routing import (
    LMModelAssignmentRepository,
    LMModelRequirementsRepository
)
from app.database.connection import fetch_all
from app.services.audit_service import AuditService
from app.ki.learning_method_mapping import get_method_by_id

from app.api.system_features.learning_methods.core.routing import (
    LMIDRange,
    CostPreset,
    RoutingRecommendationService,
    ModelAssignmentFactory
)

from . import lm_routing_recommendations_bp, lm_routing_auto_setup_bp

logger = logging.getLogger(__name__)


def _get_active_models_with_api_key() -> List[Dict[str, Any]]:
    """Get all active models with configured API keys."""
    query = """
        SELECT
            m.model_id,
            m.model_name,
            m.display_name,
            m.category,
            m.context_window,
            m.supports_vision,
            m.supports_functions,
            m.cost_level,
            p.name as provider_name,
            p.display_name as provider_display_name,
            CASE WHEN p.encrypted_api_key IS NOT NULL THEN TRUE ELSE FALSE END as has_api_key
        FROM ai_models m
        LEFT JOIN ai_providers p ON m.provider_id = p.provider_id
        WHERE m.active = TRUE
        ORDER BY m.input_price_per_1k ASC NULLS LAST
    """
    return fetch_all(query)


@lm_routing_recommendations_bp.route('/recommend/<int:lm_id>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
@limiter.limit("30 per minute")
def recommend_models_for_lm(lm_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Get recommended models for a specific learning method.

    Args:
        lm_id: Learning method ID (0-11)

    Query Parameters:
        preset: Cost preset (cheap, medium, expensive) - default: medium
        limit: Max recommendations - default: 3

    Returns:
        JSON response with recommended models

    DDD: Uses RoutingRecommendationService for scoring
    """
    try:
        # Validate LM ID
        if not LMIDRange.validate(lm_id):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_LM_ID',
                    'message': f'Invalid LM ID: {lm_id}'
                }
            }), 400

        # Get cost preset from query params
        preset_str = request.args.get('preset', 'medium')
        try:
            cost_preset = CostPreset(preset_str)
        except ValueError:
            cost_preset = CostPreset.MEDIUM

        limit = int(request.args.get('limit', 3))

        # Get LM requirement
        requirement = LMModelRequirementsRepository.get_requirement(lm_id)
        if not requirement:
            requirement = {
                'required': True,
                'recommended_categories': ['chat'],
                'requires_vision': False
            }

        # Get available models
        models = _get_active_models_with_api_key()

        # DDD: Use Service to recommend models
        recommendations = RoutingRecommendationService.recommend_models(
            models=models,
            requirement=requirement,
            cost_preset=cost_preset,
            limit=limit
        )

        # Get LM info
        lm_def = get_method_by_id(lm_id)

        return jsonify({
            'success': True,
            'data': {
                'learning_method_id': lm_id,
                'lm_code': LMIDRange.format_code(lm_id),
                'lm_name': lm_def.name if lm_def else f'LM{lm_id}',
                'requirement': requirement,
                'recommendations': recommendations,
                'preset': preset_str
            }
        }), 200

    except Exception as e:
        logger.error(f"Error recommending models: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'RECOMMEND_ERROR',
                'message': str(e)
            }
        }), 500


@lm_routing_auto_setup_bp.route('/auto-setup', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
@limiter.limit("5 per minute")
def auto_setup_all_lms() -> Tuple[Dict[str, Any], int]:
    """
    Automatically assign recommended models to all unconfigured LMs.

    Request Body:
        {
            "preset": "cheap" | "medium" | "expensive",
            "override_existing": false
        }

    Returns:
        JSON response with assignment results

    DDD: Uses RoutingRecommendationService for model selection
    """
    try:
        data = request.get_json() or {}
        preset_str = data.get('preset', 'medium')
        override_existing = data.get('override_existing', False)

        # Validate preset
        try:
            cost_preset = CostPreset(preset_str)
        except ValueError:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_PRESET',
                    'message': f'Invalid preset: {preset_str}'
                }
            }), 400

        user_id = g.current_user.get('user_id')

        # Get available models
        models = _get_active_models_with_api_key()

        configured = 0
        skipped = 0
        failed = 0
        assignments = []

        # Process each LM (0-11)
        for lm_id in range(LMIDRange.MAX + 1):
            # Check if already configured
            if not override_existing:
                existing = LMModelAssignmentRepository.get_assignment_for_lm(lm_id, scope='system')
                if existing:
                    skipped += 1
                    continue

            # Get requirement
            requirement = LMModelRequirementsRepository.get_requirement(lm_id)
            if not requirement:
                requirement = {
                    'required': True,
                    'recommended_categories': ['chat'],
                    'requires_vision': False
                }

            # Skip if not required
            if not requirement.get('required', True):
                skipped += 1
                continue

            # DDD: Get recommendations using Service
            recommendations = RoutingRecommendationService.recommend_models(
                models=models,
                requirement=requirement,
                cost_preset=cost_preset,
                limit=1
            )

            if not recommendations:
                failed += 1
                continue

            # Assign best model
            best_model = recommendations[0]
            try:
                # DDD: Use Factory to validate
                ModelAssignmentFactory.create_assignment(
                    learning_method_id=lm_id,
                    model_id=best_model['model_id'],
                    scope='system',
                    created_by=user_id
                )

                # Save to repository
                LMModelAssignmentRepository.set_system_assignment(
                    learning_method_id=lm_id,
                    model_id=best_model['model_id'],
                    created_by=user_id
                )

                configured += 1
                assignments.append({
                    'lm_id': lm_id,
                    'lm_code': LMIDRange.format_code(lm_id),
                    'model_id': best_model['model_id'],
                    'model_name': best_model.get('model_name'),
                    'score': best_model.get('recommendation_score')
                })

            except Exception as e:
                logger.error(f"Failed to assign LM{lm_id}: {e}")
                failed += 1

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='auto_setup_lm_routing',
            resource_type='lm_routing',
            resource_id='auto_setup',
            details={
                'preset': preset_str,
                'configured': configured,
                'skipped': skipped,
                'failed': failed
            }
        )

        return jsonify({
            'success': True,
            'data': {
                'preset': preset_str,
                'preset_label': cost_preset.display_name,
                'configured': configured,
                'skipped': skipped,
                'failed': failed,
                'assignments': assignments
            },
            'message': f'{configured} LMs auto-configured with {cost_preset.display_name} preset'
        }), 200

    except Exception as e:
        logger.error(f"Error in auto-setup: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'AUTO_SETUP_ERROR',
                'message': str(e)
            }
        }), 500
