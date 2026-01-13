"""
Routing Resolution Endpoint (DDD)

Runtime model resolution for testing routing logic.
"""

from flask import request, jsonify
from typing import Dict, Any, Tuple
import logging

from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.extensions import limiter
from app.repositories.lm_model_routing import (
    LMModelAssignmentRepository,
    LMModelRequirementsRepository
)

from app.api.v1.learning_methods.core.routing import (
    RoutingResolutionService
)

from .blueprints import lm_routing_resolution_bp

logger = logging.getLogger(__name__)


@lm_routing_resolution_bp.route('/resolve', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
@limiter.limit("60 per minute")
def resolve_lm_model() -> Tuple[Dict[str, Any], int]:
    """
    Resolve which model to use for a learning method with context.

    Used for testing the resolution logic.

    Request Body:
        {
            "learning_method_id": 0,
            "chapter_id": "optional-chapter-uuid",
            "course_id": "optional-course-uuid"
        }

    Returns:
        JSON response with resolved model

    DDD: Uses RoutingResolutionService for hierarchical scope resolution
    """
    try:
        data = request.get_json()
        if not data or 'learning_method_id' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'learning_method_id is required'
                }
            }), 400

        lm_id = data['learning_method_id']
        chapter_id = data.get('chapter_id')
        course_id = data.get('course_id')

        # Get resolved model from repository
        result = LMModelAssignmentRepository.resolve_model_for_lm(
            learning_method_id=lm_id,
            chapter_id=chapter_id,
            course_id=course_id
        )

        # Check if model is required
        is_required = LMModelRequirementsRepository.is_model_required(lm_id)

        # DDD: Use Service to determine if can generate
        can_generate = RoutingResolutionService.can_generate(
            resolved_assignment=result if result['is_configured'] else None,
            is_required=is_required
        )

        return jsonify({
            'success': True,
            'data': {
                **result,
                'model_required': is_required,
                'can_generate': can_generate
            }
        }), 200

    except Exception as e:
        logger.error(f"Error resolving model: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'RESOLVE_ERROR',
                'message': str(e)
            }
        }), 500
