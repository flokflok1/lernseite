"""
Routing Bulk Operations (DDD)

Bulk assignment operations for multiple learning methods.
"""

from flask import request, jsonify, g
from typing import Dict, Any, Tuple
import logging

from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.extensions import limiter
from app.repositories.lm_model_routing import LMModelAssignmentRepository
from app.services.audit_service import AuditService

from app.api.system_features.learning_methods.core.routing import (
    LMIDRange,
    ModelAssignmentFactory
)

from . import lm_routing_bulk_bp

logger = logging.getLogger(__name__)


@lm_routing_bulk_bp.route('/bulk', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
@limiter.limit("10 per minute")
def bulk_set_lm_assignments() -> Tuple[Dict[str, Any], int]:
    """
    Bulk set multiple system-level model assignments.

    Request Body:
        {
            "assignments": [
                { "learning_method_id": 0, "model_id": 5 },
                { "learning_method_id": 1, "model_id": 5 },
                ...
            ]
        }

    Returns:
        JSON response with results

    DDD: Validates all assignments using Factory before persisting
    """
    try:
        data = request.get_json()
        if not data or 'assignments' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'assignments array is required'
                }
            }), 400

        assignments = data['assignments']
        user_id = g.current_user.get('user_id')

        # DDD: Validate all assignments using Factory first
        validated_assignments = []
        for assignment in assignments:
            lm_id = assignment.get('learning_method_id')
            model_id = assignment.get('model_id')

            # Validate
            if lm_id is None:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'MISSING_LM_ID',
                        'message': 'learning_method_id is required'
                    }
                }), 400

            if not LMIDRange.validate(lm_id):
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_LM_ID',
                        'message': f'Invalid learning_method_id: {lm_id}'
                    }
                }), 400

            if model_id is None:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'MISSING_MODEL_ID',
                        'message': f'model_id missing for LM{lm_id}'
                    }
                }), 400

            # Use Factory to create assignment data
            try:
                assignment_data = ModelAssignmentFactory.create_assignment(
                    learning_method_id=lm_id,
                    model_id=model_id,
                    scope='system',
                    created_by=user_id
                )
                validated_assignments.append({
                    'learning_method_id': lm_id,
                    'model_id': model_id
                })
            except ValueError as e:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': str(e)
                    }
                }), 400

        # Bulk create in repository
        result = LMModelAssignmentRepository.bulk_set_system_assignments(
            assignments=validated_assignments,
            created_by=user_id
        )

        # Audit log
        AuditService.log_action(
            user_id=user_id,
            action='bulk_set_lm_model_assignments',
            resource_type='lm_routing',
            resource_id='bulk',
            details={
                'count': result['created'],
                'errors': len(result['errors'])
            }
        )

        return jsonify({
            'success': True,
            'data': result,
            'message': f'{result["created"]} assignments created'
        }), 200

    except Exception as e:
        logger.error(f"Error in bulk assignment: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'BULK_SET_ERROR',
                'message': str(e)
            }
        }), 500
