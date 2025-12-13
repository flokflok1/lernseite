"""
LernsystemX Admin User Management API

Comprehensive user administration endpoints:
- GET    /api/v1/admin/users - List all users with filters
- GET    /api/v1/admin/users/{user_id} - Get user details
- PUT    /api/v1/admin/users/{user_id}/role - Change user role
- POST   /api/v1/admin/users/{user_id}/ban - Ban user
- POST   /api/v1/admin/users/{user_id}/unban - Unban user
- POST   /api/v1/admin/users/{user_id}/tokens/grant - Grant tokens
- DELETE /api/v1/admin/users/{user_id} - Delete user (soft)
- POST   /api/v1/admin/users/{user_id}/verify-creator - Verify creator

Phase B24 - Admin System - ISO 27001:2013 compliant
Based on Dok 24 (Admin-System.md)
"""

from flask import request, jsonify, g
from pydantic import ValidationError
from datetime import datetime, timedelta
from typing import Optional

from app.api import api_v1
from app.models.admin import (
    UserListResponse,
    UserDetailResponse,
    RoleChangeRequest,
    BanUserRequest,
    GrantTokensRequest,
    AdminActionResponse
)
from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository
from app.services.audit_service import AuditService
from app.middleware.auth import token_required, get_current_user
from app.security.permissions import require_permission, Permissions


@api_v1.route('/admin/users', methods=['GET'])
@require_permission(Permissions.ADMIN_USER_READ)
def admin_list_users():
    """
    List all users with advanced filtering.

    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 50, max: 100)
        role: Filter by role (free, premium, creator, teacher, school, company, admin)
        search: Search by email or name
        status: Filter by status (active, suspended, banned)
        sort: Sort field (created_at, last_login, email)
        order: Sort order (asc, desc)

    Response:
        200: User list
        {
            "success": true,
            "users": [
                {
                    "user_id": "uuid",
                    "email": "user@example.com",
                    "firstname": "John",
                    "lastname": "Doe",
                    "role": "premium",
                    "status": "active",
                    "created_at": "2025-01-15T10:00:00Z",
                    "last_login": "2025-11-19T10:00:00Z",
                    "email_verified": true
                }
            ],
            "pagination": {
                "total": 1234,
                "page": 1,
                "per_page": 50,
                "total_pages": 25
            }
        }

        401: Unauthorized
        403: Forbidden (requires ADMIN_USER_READ)
    """
    try:
        # Parse query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        role = request.args.get('role')
        search = request.args.get('search')
        status = request.args.get('status', 'active')
        sort = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc')

        # Get users from repository
        result = UserRepository.admin_list_users(
            page=page,
            per_page=per_page,
            role=role,
            search=search,
            status=status,
            sort=sort,
            order=order
        )

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='admin.users.list',
            resource_type='user',
            details={'filters': {'role': role, 'search': search, 'status': status}}
        )

        return jsonify({
            'success': True,
            'users': result['users'],
            'pagination': result['pagination']
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid parameter',
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to list users',
            'details': str(e)
        }), 500


@api_v1.route('/admin/users/<user_id>', methods=['GET'])
@require_permission(Permissions.ADMIN_USER_READ)
def admin_get_user_details(user_id: str):
    """
    Get detailed information about a specific user.

    Path Parameters:
        user_id: User UUID

    Response:
        200: User details
        {
            "success": true,
            "user": {
                "user_id": "uuid",
                "email": "user@example.com",
                "firstname": "John",
                "lastname": "Doe",
                "role": "premium",
                "status": "active",
                "created_at": "2025-01-15T10:00:00Z",
                "last_login": "2025-11-19T10:00:00Z",
                "email_verified": true,
                "two_factor_enabled": false,
                "organisation_id": null,
                "subscription": {
                    "plan": "premium",
                    "status": "active",
                    "expires_at": "2025-12-19T10:00:00Z"
                },
                "tokens": {
                    "balance": 5000,
                    "total_used": 2500
                },
                "courses_created": 12,
                "courses_enrolled": 45,
                "login_history": [...],
                "ban_history": [...]
            }
        }

        404: User not found
        401: Unauthorized
        403: Forbidden
    """
    try:
        # Get comprehensive user details
        user_details = UserRepository.admin_get_user_details(user_id)

        if not user_details:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='admin.users.view',
            resource_type='user',
            resource_id=user_id
        )

        return jsonify({
            'success': True,
            'user': user_details
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()  # Print full traceback to console
        return jsonify({
            'success': False,
            'error': 'Failed to get user details',
            'details': str(e)
        }), 500


@api_v1.route('/admin/users/<user_id>/role', methods=['PUT'])
@require_permission(Permissions.ADMIN_USER_WRITE)
def admin_change_user_role(user_id: str):
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


@api_v1.route('/admin/users/<user_id>/ban', methods=['POST'])
@require_permission(Permissions.ADMIN_USER_WRITE)
def admin_ban_user(user_id: str):
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


@api_v1.route('/admin/users/<user_id>/unban', methods=['POST'])
@require_permission(Permissions.ADMIN_USER_WRITE)
def admin_unban_user(user_id: str):
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


@api_v1.route('/admin/users/<user_id>/tokens/grant', methods=['POST'])
@require_permission(Permissions.ADMIN_USER_WRITE)
def admin_grant_tokens(user_id: str):
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


@api_v1.route('/admin/users/<user_id>', methods=['DELETE'])
@require_permission(Permissions.ADMIN_USER_DELETE)
def admin_delete_user(user_id: str):
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


@api_v1.route('/admin/users/<user_id>/verify-creator', methods=['POST'])
@require_permission(Permissions.ADMIN_USER_WRITE)
def admin_verify_creator(user_id: str):
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
