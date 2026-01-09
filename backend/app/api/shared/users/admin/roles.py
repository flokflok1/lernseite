"""
Admin User Roles API

Endpoints for user role management:
- PUT /admin/users/<user_id>/role - Change user role
- POST /admin/users/<user_id>/verify-creator - Verify creator status

Moved from admin/users/roles.py to users/admin/roles.py
DDD Refactoring - 2026-01-08
"""

from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError
from typing import Dict, Any

from app.models.admin import RoleChangeRequest
from app.repositories.user import UserRepository
from app.services.audit_service import AuditService
from app.middleware.auth import token_required, get_current_user
from app.security.permissions import require_permission, Permissions

admin_users_roles_bp = Blueprint(
    'admin_users_roles',
    __name__,
    url_prefix='/admin/users'
)


@admin_users_roles_bp.route('/<user_id>/role', methods=['PUT'])
@require_permission(Permissions.ADMIN_USER_WRITE)
def admin_change_user_role(user_id: str) -> tuple[Dict[str, Any], int]:
    """
    Change user's role.

    Path Parameters:
        user_id: User UUID

    Request Body:
        {
            "role": "premium",
            "reason": "Upgrade requested by support"
        }

    Response:
        200: Role changed successfully
        400: Invalid role
        404: User not found
        403: Cannot change own role
    """
    try:
        current_user = get_current_user()

        # Prevent changing own role
        if user_id == current_user['user_id']:
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'You cannot change your own role'
            }), 403

        data = request.get_json()

        # Validate request
        role_change = RoleChangeRequest(**data)

        # Change role
        success = UserRepository.admin_change_role(
            user_id=user_id,
            new_role=role_change.role,
            changed_by=current_user['user_id']
        )

        if not success:
            return jsonify({
                'success': False,
                'error': 'User not found or role change failed'
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.users.change_role',
            resource_type='user',
            resource_id=user_id,
            details={
                'new_role': role_change.role,
                'reason': role_change.reason
            },
            severity='high'
        )

        return jsonify({
            'success': True,
            'message': f'User role changed to {role_change.role}'
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to change role',
            'details': str(e)
        }), 500


@admin_users_roles_bp.route('/<user_id>/verify-creator', methods=['POST'])
@require_permission(Permissions.ADMIN_USER_WRITE)
def admin_verify_creator(user_id: str) -> tuple[Dict[str, Any], int]:
    """
    Verify a creator (mark as trusted/verified).

    Path Parameters:
        user_id: User UUID

    Request Body:
        {
            "verified": true,
            "reason": "Quality content creator"
        }

    Response:
        200: Creator verified
        404: User not found
        400: User is not a creator
    """
    try:
        current_user = get_current_user()
        data = request.get_json()

        verified = data.get('verified', True)
        reason = data.get('reason', '')

        # Get user
        target_user = UserRepository.find_by_id(user_id)
        if not target_user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        if target_user.get('role') != 'creator':
            return jsonify({
                'success': False,
                'error': 'User is not a creator'
            }), 400

        # Verify creator
        success = UserRepository.admin_verify_creator(
            user_id=user_id,
            verified=verified,
            verified_by=current_user['user_id']
        )

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to verify creator'
            }), 500

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.users.verify_creator',
            resource_type='user',
            resource_id=user_id,
            details={
                'verified': verified,
                'reason': reason
            },
            severity='medium'
        )

        return jsonify({
            'success': True,
            'message': f'Creator {"verified" if verified else "unverified"} successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to verify creator',
            'details': str(e)
        }), 500
