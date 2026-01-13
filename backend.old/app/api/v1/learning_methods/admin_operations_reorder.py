"""
Learning Method Reorder Endpoint (DDD)

Reorder learning methods within a chapter.
Uses MethodValidationService for validation.
"""

from flask import request, jsonify, g
from typing import Dict, Any, Tuple
import logging

from app.extensions import limiter
from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.repositories.learning_method.instances import LearningMethodInstanceRepository
from app.services.audit_service import AuditService

from app.api.v1.learning_methods.services import MethodValidationService

from .blueprints import lm_operations_bp

logger = logging.getLogger(__name__)


@lm_operations_bp.route('/chapters/<chapter_id>/learning-methods/reorder', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("30 per minute")
def reorder_learning_methods(chapter_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Reorder learning methods within a chapter.

    Args:
        chapter_id: Chapter UUID

    Request Body:
        {
            "method_ids": ["uuid1", "uuid2", "uuid3"]
        }

    Returns:
        JSON response with success status

    DDD: Uses MethodValidationService to validate reorder list

    Business Rules:
    - method_ids must contain exactly the same IDs as existing methods
    - No duplicates
    - No missing or extra IDs
    """
    try:
        data = request.get_json()
        if not data or 'method_ids' not in data:
            return jsonify({
                'success': False,
                'error': 'method_ids required'
            }), 400

        method_ids = data['method_ids']

        if not isinstance(method_ids, list):
            return jsonify({
                'success': False,
                'error': 'method_ids must be a list'
            }), 400

        # Get existing methods in chapter
        existing_methods = LearningMethodInstanceRepository.find_by_chapter(
            chapter_id,
            published_only=False
        )
        existing_ids = [m['method_id'] for m in existing_methods]

        # DDD: Validate reorder list using Service
        MethodValidationService.validate_reorder_list(method_ids, existing_ids)

        # Perform reorder
        success = LearningMethodInstanceRepository.reorder(chapter_id, method_ids)

        if success:
            # Audit log
            user_id = g.current_user['user_id']
            AuditService.log_action(
                user_id=user_id,
                action='learning_method.reorder',
                resource_type='chapter',
                resource_id=chapter_id,
                details={
                    'new_order': method_ids,
                    'count': len(method_ids)
                }
            )

            return jsonify({
                'success': True,
                'message': 'Learning methods reordered',
                'count': len(method_ids)
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to reorder learning methods'
            }), 500

    except ValueError as ve:
        logger.warning(f"Validation error reordering learning methods: {ve}")
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'message': str(ve)
        }), 400

    except Exception as e:
        logger.error(f"Error reordering learning methods: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to reorder learning methods',
            'message': str(e)
        }), 500
