"""
Routing AI-Powered Auto-Setup (DDD)

AI-powered automatic model assignment with intelligent matching.
"""

from flask import request, jsonify, g
from typing import Dict, Any, Tuple
import logging

from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.extensions import limiter
from app.repositories.lm_model_routing import (
    LMModelAssignmentRepository,
    LMModelRequirementsRepository
)
from app.services.audit_service import AuditService
from app.ki.learning_method_mapping import get_method_by_id

from app.api.v1.learning_methods.core.routing import (
    LMIDRange,
    CostPreset,
    RoutingRecommendationService,
    ModelAssignmentFactory
)

from .blueprints import lm_routing_ai_setup_bp

logger = logging.getLogger(__name__)


@lm_routing_ai_setup_bp.route('/ai-auto-setup', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
@limiter.limit("3 per hour")
def ai_auto_setup() -> Tuple[Dict[str, Any], int]:
    """
    AI-powered auto-setup with intelligent model matching.

    Uses AI to analyze LM requirements and recommend optimal models
    based on capabilities, cost, and performance characteristics.

    Request Body:
        {
            "cost_preference": "cheap" | "medium" | "expensive",
            "analyze_requirements": true,
            "override_existing": false
        }

    Returns:
        JSON response with setup results

    DDD: Uses RoutingRecommendationService with advanced scoring

    Note: This is a placeholder for future AI-powered recommendation.
    Currently delegates to the standard auto-setup with recommendations.
    """
    try:
        data = request.get_json() or {}
        cost_preference = data.get('cost_preference', 'medium')
        override_existing = data.get('override_existing', False)

        # Validate cost preference
        try:
            cost_preset = CostPreset(cost_preference)
        except ValueError:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_COST_PREFERENCE',
                    'message': f'Invalid cost_preference: {cost_preference}'
                }
            }), 400

        user_id = g.current_user.get('user_id')

        # TODO: Future AI-powered analysis
        # For now, use the same logic as auto-setup but with detailed logging

        # Get available models
        from .recommendations import _get_active_models_with_api_key
        models = _get_active_models_with_api_key()

        configured = 0
        skipped = 0
        failed = 0
        assignments = []

        # Process each LM
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
                logger.warning(f"No compatible models found for LM{lm_id}")
                continue

            # Assign best model
            best_model = recommendations[0]
            try:
                # DDD: Validate with Factory
                ModelAssignmentFactory.create_assignment(
                    learning_method_id=lm_id,
                    model_id=best_model['model_id'],
                    scope='system',
                    created_by=user_id
                )

                # Save
                LMModelAssignmentRepository.set_system_assignment(
                    learning_method_id=lm_id,
                    model_id=best_model['model_id'],
                    created_by=user_id
                )

                configured += 1
                lm_def = get_method_by_id(lm_id)
                assignments.append({
                    'lm_id': lm_id,
                    'lm_code': LMIDRange.format_code(lm_id),
                    'lm_name': lm_def.name if lm_def else f'LM{lm_id}',
                    'model_id': best_model['model_id'],
                    'model_name': best_model.get('model_name'),
                    'model_display_name': best_model.get('display_name'),
                    'score': best_model.get('recommendation_score'),
                    'cost_level': best_model.get('cost_level')
                })

            except Exception as e:
                logger.error(f"Failed to assign LM{lm_id}: {e}")
                failed += 1

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='ai_auto_setup_lm_routing',
            resource_type='lm_routing',
            resource_id='ai_auto_setup',
            details={
                'cost_preference': cost_preference,
                'configured': configured,
                'skipped': skipped,
                'failed': failed,
                'ai_powered': False  # Will be True when AI analysis implemented
            }
        )

        return jsonify({
            'success': True,
            'data': {
                'cost_preference': cost_preference,
                'configured': configured,
                'skipped': skipped,
                'failed': failed,
                'assignments': assignments,
                'ai_analysis_used': False  # Future feature
            },
            'message': f'AI auto-setup complete: {configured} LMs configured'
        }), 200

    except Exception as e:
        logger.error(f"Error in AI auto-setup: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'AI_AUTO_SETUP_ERROR',
                'message': str(e)
            }
        }), 500
