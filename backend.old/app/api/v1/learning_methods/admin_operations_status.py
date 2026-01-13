"""
Learning Method Status Operations (DDD)

Publish and unpublish learning method instances.
Uses MethodValidationService and LearningMethodInstanceFactory.
"""

from flask import jsonify, g
from typing import Dict, Any, Tuple
import logging

from app.extensions import limiter
from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.repositories.learning_method.instances import LearningMethodInstanceRepository
from app.services.audit_service import AuditService

from app.api.v1.learning_methods.factory import LearningMethodInstanceFactory
from app.api.v1.learning_methods.services import MethodValidationService
from app.api.v1.learning_methods.value_objects import MethodStatus

from .blueprints import lm_operations_bp

logger = logging.getLogger(__name__)


@lm_operations_bp.route('/learning-methods/<method_id>/publish', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("30 per minute")
def publish_learning_method(method_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Publish a learning method instance.

    Args:
        method_id: Method UUID

    Returns:
        JSON response with updated instance

    DDD: Uses MethodValidationService and MethodStatus

    Business Rules:
    - Can only publish DRAFT instances
    - Status transition: DRAFT → PUBLISHED
    """
    try:
        # Fetch existing instance
        existing = LearningMethodInstanceRepository.find_by_id(method_id)
        if not existing:
            return jsonify({
                'success': False,
                'error': 'Learning method not found'
            }), 404

        # Get current status
        current_status = MethodStatus(existing['status'])

        # DDD: Validate status transition
        MethodValidationService.validate_status_transition(
            current_status,
            MethodStatus.PUBLISHED
        )

        user_id = g.current_user['user_id']

        # DDD: Use Factory to create update data
        update_data = LearningMethodInstanceFactory.create_update_data(
            status=MethodStatus.PUBLISHED,
            updated_by=user_id
        )

        # Update in repository
        updated = LearningMethodInstanceRepository.update(method_id, update_data)

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='learning_method.publish',
            resource_type='learning_method',
            resource_id=method_id,
            details={
                'previous_status': current_status.value,
                'new_status': MethodStatus.PUBLISHED.value
            }
        )

        return jsonify({
            'success': True,
            'learning_method': updated,
            'message': 'Learning method published'
        }), 200

    except ValueError as ve:
        logger.warning(f"Validation error publishing learning method: {ve}")
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'message': str(ve)
        }), 400

    except Exception as e:
        logger.error(f"Error publishing learning method {method_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to publish learning method',
            'message': str(e)
        }), 500


@lm_operations_bp.route('/learning-methods/<method_id>/unpublish', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("30 per minute")
def unpublish_learning_method(method_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Unpublish a learning method instance.

    Args:
        method_id: Method UUID

    Returns:
        JSON response with updated instance

    DDD: Uses MethodValidationService and MethodStatus

    Business Rules:
    - Can only unpublish PUBLISHED instances
    - Status transition: PUBLISHED → DRAFT
    """
    try:
        # Fetch existing instance
        existing = LearningMethodInstanceRepository.find_by_id(method_id)
        if not existing:
            return jsonify({
                'success': False,
                'error': 'Learning method not found'
            }), 404

        # Get current status
        current_status = MethodStatus(existing['status'])

        # DDD: Validate status transition
        MethodValidationService.validate_status_transition(
            current_status,
            MethodStatus.DRAFT
        )

        user_id = g.current_user['user_id']

        # DDD: Use Factory to create update data
        update_data = LearningMethodInstanceFactory.create_update_data(
            status=MethodStatus.DRAFT,
            updated_by=user_id
        )

        # Update in repository
        updated = LearningMethodInstanceRepository.update(method_id, update_data)

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='learning_method.unpublish',
            resource_type='learning_method',
            resource_id=method_id,
            details={
                'previous_status': current_status.value,
                'new_status': MethodStatus.DRAFT.value
            }
        )

        return jsonify({
            'success': True,
            'learning_method': updated,
            'message': 'Learning method unpublished'
        }), 200

    except ValueError as ve:
        logger.warning(f"Validation error unpublishing learning method: {ve}")
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'message': str(ve)
        }), 400

    except Exception as e:
        logger.error(f"Error unpublishing learning method {method_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to unpublish learning method',
            'message': str(e)
        }), 500
