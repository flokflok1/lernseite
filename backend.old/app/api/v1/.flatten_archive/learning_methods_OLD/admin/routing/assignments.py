"""
Routing Assignment Endpoints (DDD)

CRUD operations for individual LM model assignments.
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

from app.api.system_features.learning_methods.core.routing import (
    LMIDRange,
    ModelAssignmentFactory,
    ModelAssignedEvent,
    ModelUnassignedEvent
)

from . import lm_routing_assignments_bp

logger = logging.getLogger(__name__)


def _validate_lm_id(lm_id: int) -> Tuple[Dict, int] | None:
    """
    Validate learning method ID.

    Returns:
        None if valid, or (error_response, status_code) if invalid
    """
    if not LMIDRange.validate(lm_id):
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_LM_ID',
                'message': f'Learning method ID must be between {LMIDRange.MIN} and {LMIDRange.MAX}'
            }
        }), 400
    return None


@lm_routing_assignments_bp.route('/<int:lm_id>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
@limiter.limit("60 per minute")
def get_lm_assignment(lm_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Get model assignment for a specific learning method.

    Args:
        lm_id: Learning method ID (0-11)

    Returns:
        JSON response with assignment details

    DDD: Uses LMIDRange for validation
    """
    try:
        # Validate LM ID
        validation_error = _validate_lm_id(lm_id)
        if validation_error:
            return validation_error

        lm_def = get_method_by_id(lm_id)
        assignment = LMModelAssignmentRepository.get_assignment_for_lm(lm_id, scope='system')
        requirement = LMModelRequirementsRepository.get_requirement(lm_id)

        return jsonify({
            'success': True,
            'data': {
                'learning_method_id': lm_id,
                'lm_code': LMIDRange.format_code(lm_id),
                'lm_name': lm_def.name if lm_def else f'LM{lm_id}',
                'lm_group': lm_def.group.value if lm_def else None,
                'lm_type': lm_def.method_type.value if lm_def else None,
                'ki_usage': lm_def.ki_usage.value if lm_def else None,
                'requirement': {
                    'required': requirement.get('required', True) if requirement else True,
                    'recommended_categories': requirement.get('recommended_categories', ['chat']) if requirement else ['chat'],
                    'requires_vision': requirement.get('requires_vision', False) if requirement else False
                },
                'assignment': {
                    'assignment_id': assignment.get('assignment_id'),
                    'model_id': assignment.get('model_id'),
                    'model_name': assignment.get('model_name'),
                    'model_display_name': assignment.get('model_display_name'),
                    'model_category': assignment.get('model_category'),
                    'provider_name': assignment.get('provider_name'),
                    'provider_display_name': assignment.get('provider_display_name')
                } if assignment else None,
                'is_configured': assignment is not None
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting LM assignment: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_ASSIGNMENT_ERROR',
                'message': str(e)
            }
        }), 500


@lm_routing_assignments_bp.route('/<int:lm_id>', methods=['PUT'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
@limiter.limit("30 per minute")
def set_lm_assignment(lm_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Set system-level model assignment for a learning method.

    Args:
        lm_id: Learning method ID (0-11)

    Request Body:
        { "model_id": 5 }

    Returns:
        JSON response with created assignment

    DDD: Uses ModelAssignmentFactory, emits ModelAssignedEvent
    """
    try:
        # Validate LM ID
        validation_error = _validate_lm_id(lm_id)
        if validation_error:
            return validation_error

        data = request.get_json()
        if not data or 'model_id' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'model_id is required'
                }
            }), 400

        model_id = data['model_id']
        user_id = g.current_user.get('user_id')

        # DDD: Use Factory to create assignment (validates business rules)
        assignment_data = ModelAssignmentFactory.create_assignment(
            learning_method_id=lm_id,
            model_id=model_id,
            scope='system',
            created_by=user_id
        )

        # Save to repository
        assignment = LMModelAssignmentRepository.set_system_assignment(
            learning_method_id=lm_id,
            model_id=model_id,
            created_by=user_id
        )

        if not assignment:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CREATE_FAILED',
                    'message': 'Failed to create assignment'
                }
            }), 500

        # Get LM name for message
        lm_def = get_method_by_id(lm_id)
        lm_name = lm_def.name if lm_def else f'LM{lm_id}'

        # DDD: Create and log domain event
        event = ModelAssignedEvent.create(
            learning_method_id=lm_id,
            model_id=model_id,
            scope='system',
            assigned_by=user_id
        )

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='set_lm_model_assignment',
            resource_type='lm_routing',
            resource_id=str(lm_id),
            details=event.to_dict()
        )

        return jsonify({
            'success': True,
            'data': assignment,
            'message': f'Model assigned to {LMIDRange.format_code(lm_id)} ({lm_name})'
        }), 200

    except ValueError as e:
        # Factory validation error
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        logger.error(f"Error setting LM assignment: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'SET_ASSIGNMENT_ERROR',
                'message': str(e)
            }
        }), 500


@lm_routing_assignments_bp.route('/<int:lm_id>', methods=['DELETE'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
@limiter.limit("30 per minute")
def remove_lm_assignment(lm_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Remove system-level model assignment for a learning method.

    Args:
        lm_id: Learning method ID (0-11)

    Returns:
        JSON response with success message

    DDD: Emits ModelUnassignedEvent
    """
    try:
        # Validate LM ID
        validation_error = _validate_lm_id(lm_id)
        if validation_error:
            return validation_error

        # Get current assignment
        assignment = LMModelAssignmentRepository.get_assignment_for_lm(lm_id, scope='system')

        if not assignment:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': f'No assignment found for {LMIDRange.format_code(lm_id)}'
                }
            }), 404

        # Remove assignment
        assignment_id = assignment['assignment_id']
        LMModelAssignmentRepository.remove_assignment(assignment_id)

        # DDD: Create and log domain event
        event = ModelUnassignedEvent.create(
            learning_method_id=lm_id,
            assignment_id=assignment_id,
            unassigned_by=g.current_user.get('user_id')
        )

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='remove_lm_model_assignment',
            resource_type='lm_routing',
            resource_id=str(lm_id),
            details=event.to_dict()
        )

        return jsonify({
            'success': True,
            'message': f'Assignment removed for {LMIDRange.format_code(lm_id)}'
        }), 200

    except Exception as e:
        logger.error(f"Error removing LM assignment: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'REMOVE_ASSIGNMENT_ERROR',
                'message': str(e)
            }
        }), 500
