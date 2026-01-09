"""
Admin User Actions API

Endpoints for user moderation and token management:
- POST /admin/users/<user_id>/ban - Ban user
- POST /admin/users/<user_id>/unban - Unban user
- DELETE /admin/users/<user_id> - Delete user (soft)
- POST /admin/users/<user_id>/tokens/grant - Grant tokens

Moved from admin/users/actions.py to users/admin/actions.py
DDD Refactoring - 2026-01-08
"""

from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError
from datetime import datetime, timedelta
from typing import Dict, Any

from app.models.admin import BanUserRequest, GrantTokensRequest
from app.repositories.user import UserRepository
from app.repositories.token import TokenRepository
from app.services.audit_service import AuditService
from app.middleware.auth import token_required, get_current_user
from app.security.permissions import require_permission, Permissions

admin_users_actions_bp = Blueprint(
    'admin_users_actions',
    __name__,
    url_prefix='/admin/users'
)


@admin_users_actions_bp.route('/<user_id>/ban', methods=['POST'])
@require_permission(Permissions.ADMIN_USER_WRITE)
def admin_ban_user(user_id: str) -> tuple[Dict[str, Any], int]:
    """
    Ban a user.

    Path Parameters:
        user_id: User UUID

    Request Body:
        {
            "reason": "Violation of community guidelines",
            "duration_days": 30,
            "permanent": false,
            "notify_user": true
        }

    Response:
        200: User banned
        404: User not found
        403: Cannot ban yourself or other admins
    """
    try:
        current_user = get_current_user()

        # Prevent banning yourself
        if user_id == current_user['user_id']:
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'You cannot ban yourself'
            }), 403

        data = request.get_json()
        ban_request = BanUserRequest(**data)

        # Check if target user is admin (prevent banning admins)
        target_user = UserRepository.find_by_id(user_id)
        if not target_user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        if target_user.get('role') == 'admin':
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'Cannot ban admin users'
            }), 403

        # Calculate ban expiry
        banned_until = None
        if not ban_request.permanent and ban_request.duration_days:
            banned_until = datetime.utcnow() + timedelta(days=ban_request.duration_days)

        # Ban user
        success = UserRepository.admin_ban_user(
            user_id=user_id,
            reason=ban_request.reason,
            banned_until=banned_until,
            banned_by=current_user['user_id']
        )

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to ban user'
            }), 500

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.users.ban',
            resource_type='user',
            resource_id=user_id,
            details={
                'reason': ban_request.reason,
                'duration_days': ban_request.duration_days,
                'permanent': ban_request.permanent,
                'banned_until': banned_until.isoformat() if banned_until else None
            },
            severity='critical'
        )

        # TODO: Notify user via email if notify_user is True

        return jsonify({
            'success': True,
            'message': 'User banned successfully',
            'banned_until': banned_until.isoformat() if banned_until else None
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
            'error': 'Failed to ban user',
            'details': str(e)
        }), 500


@admin_users_actions_bp.route('/<user_id>/unban', methods=['POST'])
@require_permission(Permissions.ADMIN_USER_WRITE)
def admin_unban_user(user_id: str) -> tuple[Dict[str, Any], int]:
    """
    Unban a user.

    Path Parameters:
        user_id: User UUID

    Request Body:
        {
            "reason": "Appeal approved"
        }

    Response:
        200: User unbanned
        404: User not found
    """
    try:
        current_user = get_current_user()
        data = request.get_json()
        reason = data.get('reason', 'Unbanned by admin')

        # Unban user
        success = UserRepository.admin_unban_user(
            user_id=user_id,
            unbanned_by=current_user['user_id']
        )

        if not success:
            return jsonify({
                'success': False,
                'error': 'User not found or unban failed'
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.users.unban',
            resource_type='user',
            resource_id=user_id,
            details={'reason': reason},
            severity='high'
        )

        return jsonify({
            'success': True,
            'message': 'User unbanned successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to unban user',
            'details': str(e)
        }), 500


@admin_users_actions_bp.route('/<user_id>', methods=['DELETE'])
@require_permission(Permissions.ADMIN_USER_DELETE)
def admin_delete_user(user_id: str) -> tuple[Dict[str, Any], int]:
    """
    Soft delete a user (deactivate account).

    Path Parameters:
        user_id: User UUID

    Request Body:
        {
            "reason": "GDPR deletion request",
            "hard_delete": false
        }

    Response:
        200: User deleted
        403: Cannot delete yourself or other admins
        404: User not found
    """
    try:
        current_user = get_current_user()

        # Prevent deleting yourself
        if user_id == current_user['user_id']:
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'You cannot delete yourself'
            }), 403

        data = request.get_json() or {}
        reason = data.get('reason', 'Deleted by admin')
        hard_delete = data.get('hard_delete', False)

        # Check if target user is admin
        target_user = UserRepository.find_by_id(user_id)
        if not target_user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        if target_user.get('role') == 'admin' and not hard_delete:
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'Cannot delete admin users'
            }), 403

        # Delete user (soft delete by default)
        success = UserRepository.admin_delete_user(
            user_id=user_id,
            reason=reason,
            deleted_by=current_user['user_id'],
            hard_delete=hard_delete
        )

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to delete user'
            }), 500

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.users.delete',
            resource_type='user',
            resource_id=user_id,
            details={
                'reason': reason,
                'hard_delete': hard_delete
            },
            severity='critical'
        )

        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to delete user',
            'details': str(e)
        }), 500


@admin_users_actions_bp.route('/<user_id>/tokens/grant', methods=['POST'])
@require_permission(Permissions.ADMIN_USER_WRITE)
def admin_grant_tokens(user_id: str) -> tuple[Dict[str, Any], int]:
    """
    Grant tokens to a user.

    Path Parameters:
        user_id: User UUID

    Request Body:
        {
            "amount": 5000,
            "reason": "Goodwill gesture for reported bug"
        }

    Response:
        200: Tokens granted
        404: User not found
    """
    try:
        current_user = get_current_user()
        data = request.get_json()

        grant_request = GrantTokensRequest(**data)

        # Grant tokens
        new_balance = TokenRepository.admin_grant_tokens(
            user_id=user_id,
            amount=grant_request.amount,
            reason=grant_request.reason,
            granted_by=current_user['user_id']
        )

        if new_balance is None:
            return jsonify({
                'success': False,
                'error': 'User not found or token grant failed'
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=current_user['user_id'],
            action='admin.users.grant_tokens',
            resource_type='user',
            resource_id=user_id,
            details={
                'amount': grant_request.amount,
                'reason': grant_request.reason,
                'new_balance': new_balance
            },
            severity='medium'
        )

        return jsonify({
            'success': True,
            'message': f'{grant_request.amount} tokens granted',
            'new_balance': new_balance
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
            'error': 'Failed to grant tokens',
            'details': str(e)
        }), 500
