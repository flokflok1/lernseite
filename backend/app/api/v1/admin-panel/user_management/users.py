"""
LernsystemX Admin API - User Management

Admin endpoints for user CRUD operations, role management, and moderation actions.

Endpoints:
- GET /api/v1/admin/users - List users with filtering and pagination
- GET /api/v1/admin/users/{id} - Get detailed user information
- PATCH /api/v1/admin/users/{id}/role - Change user role
- POST /api/v1/admin/users/{id}/ban - Ban user
- POST /api/v1/admin/users/{id}/unban - Unban user
- DELETE /api/v1/admin/users/{id} - Delete user (soft or hard)
- POST /api/v1/admin/users/{id}/verify - Verify creator status

Phase B24 - Admin User Management Implementation
"""

from flask import jsonify, request, g
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ValidationError

from app.api.v1 import api_v1
from app.infrastructure.security.permissions import require_permission, Permissions
from app.infrastructure.persistence.repositories.user.admin import UserAdminRepository
from app.infrastructure.persistence.repositories.user.auth import UserAuthRepository
from app.services.audit_service import AuditService, Severity
from app.api.middleware.auth import get_current_user


# ==========================================
# PYDANTIC MODELS
# ==========================================

class CreateUserRequest(BaseModel):
    """Request body for creating a new user"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(default='free', description='Role name: free, premium, creator, teacher, admin, owner')

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "first_name": "John",
                "last_name": "Doe",
                "role": "admin"
            }
        }


@api_v1.route('/admin/users', methods=['GET'])
@require_permission(Permissions.ADMIN_USER_READ)
def admin_list_users():
    """
    List all users with filtering, pagination, and sorting.

    Query Parameters:
        - page (int): Page number (default: 1)
        - per_page (int): Items per page (default: 20, max: 100)
        - status (str): Filter by status (active/inactive/banned)
        - role (str): Filter by role
        - search (str): Search in name or email
        - sort_by (str): Sort field (created_at/last_login/email)
        - sort_order (str): Sort direction (asc/desc, default: desc)

    Response:
        200: User list with pagination metadata
        403: Forbidden (insufficient permissions)
        500: Server error
    """
    try:
        # Parse query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        status = request.args.get('status', '')
        role = request.args.get('role', '')
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')

        # Get users from repository
        result = UserAdminRepository.admin_list_users(
            page=page,
            per_page=per_page,
            status=status,
            role=role,
            search=search,
            sort=sort_by,      # Repository expects 'sort', not 'sort_by'
            order=sort_order   # Repository expects 'order', not 'sort_order'
        )

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='list_users',
            resource_type='admin_users',
            severity='info',
            details={
                'page': page,
                'per_page': per_page,
                'filters': {'status': status, 'role': role, 'search': search}
            }
        )

        return jsonify({
            'success': True,
            'users': result.get('users', []),
            'total': result.get('pagination', {}).get('total', 0),
            'page': result.get('pagination', {}).get('page', page),
            'limit': result.get('pagination', {}).get('per_page', per_page),
            'total_pages': result.get('pagination', {}).get('total_pages', 1)
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid parameters',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to list users',
            'message': str(e)
        }), 500


@api_v1.route('/admin/users', methods=['POST'])
@require_permission(Permissions.ADMIN_USER_WRITE)
def admin_create_user():
    """
    Create a new user (Admin only).

    Request Body:
        {
            "email": "user@example.com",
            "password": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe",
            "role": "admin"  // Optional, default: "free"
        }

    Response:
        201: User created successfully
        400: Validation error or user already exists
        403: Forbidden (insufficient permissions)
        500: Server error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Invalid request',
                'message': 'Request body is empty'
            }), 400

        user_data = CreateUserRequest(**data)

        # Create user via repository
        user = UserAuthRepository.create_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role
        )

        if not user:
            return jsonify({
                'success': False,
                'error': 'Failed to create user',
                'message': 'User creation failed'
            }), 500

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='create_user',
            resource_type='admin_users',
            resource_id=user.get('user_id'),
            severity='medium',
            details={'email': user_data.email, 'role': user_data.role}
        )

        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'data': user
        }), 201

    except ValidationError as e:
        # Pydantic validation error - extract field errors
        error_details = []
        for error in e.errors():
            field = error['loc'][0]
            msg = error['msg']
            error_details.append(f"{field}: {msg}")

        return jsonify({
            'success': False,
            'error': 'Validation error',
            'message': '; '.join(error_details)
        }), 400
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to create user',
            'message': str(e)
        }), 500


@api_v1.route('/admin/users/<string:user_id>', methods=['GET'])
@require_permission(Permissions.ADMIN_USER_READ)
def admin_get_user_details(user_id: str):
    """
    Get detailed user information including subscription, courses, and login history.

    Path Parameters:
        user_id (str): User ID

    Response:
        200: Detailed user information
        403: Forbidden (insufficient permissions)
        404: User not found
        500: Server error
    """
    try:
        # Get user details from repository
        user_details = UserAdminRepository.admin_get_user_details(user_id)

        if not user_details:
            return jsonify({
                'success': False,
                'error': 'User not found',
                'message': f'No user found with ID: {user_id}'
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='view_user_details',
            resource_type='admin_users',
            resource_id=user_id,
            severity='info'
        )

        return jsonify({
            'success': True,
            'data': user_details
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get user details',
            'message': str(e)
        }), 500


@api_v1.route('/admin/users/<string:user_id>/role', methods=['PATCH'])
@require_permission(Permissions.ADMIN_USER_WRITE)
def admin_change_user_role(user_id: str):
    """
    Change user role.

    Path Parameters:
        user_id (str): User ID

    Request Body:
        {
            "new_role": "premium"  // One of: user, premium, creator, teacher, etc.
        }

    Response:
        200: Role changed successfully
        400: Invalid role
        403: Forbidden (insufficient permissions)
        404: User not found
        500: Server error
    """
    try:
        data = request.get_json()
        new_role = data.get('new_role')

        if not new_role:
            return jsonify({
                'success': False,
                'error': 'Missing required field',
                'message': 'new_role is required'
            }), 400

        # Change role via repository
        success = UserAdminRepository.admin_change_role(
            user_id=user_id,
            new_role=new_role,
            changed_by_user_id=g.current_user['user_id']
        )

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to change role',
                'message': 'User not found or invalid role'
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='change_user_role',
            resource_type='admin_users',
            resource_id=user_id,
            severity='medium',
            details={'new_role': new_role}
        )

        return jsonify({
            'success': True,
            'message': f'User role changed to {new_role}'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to change user role',
            'message': str(e)
        }), 500


@api_v1.route('/admin/users/<string:user_id>/ban', methods=['POST'])
@require_permission(Permissions.ADMIN_USER_WRITE)
def admin_ban_user(user_id: str):
    """
    Ban user with reason and optional duration.

    Path Parameters:
        user_id (str): User ID

    Request Body:
        {
            "reason": "Violation of terms",  // Required
            "duration_days": 7               // Optional (null = permanent)
        }

    Response:
        200: User banned successfully
        400: Missing reason
        403: Forbidden (insufficient permissions)
        404: User not found
        500: Server error
    """
    try:
        data = request.get_json()
        reason = data.get('reason')
        duration_days = data.get('duration_days')

        if not reason:
            return jsonify({
                'success': False,
                'error': 'Missing required field',
                'message': 'reason is required'
            }), 400

        # Ban user via repository
        success = UserAdminRepository.admin_ban_user(
            user_id=user_id,
            reason=reason,
            banned_by_user_id=g.current_user['user_id'],
            duration_days=duration_days
        )

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to ban user',
                'message': 'User not found or already banned'
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='ban_user',
            resource_type='admin_users',
            resource_id=user_id,
            severity='high',
            details={'reason': reason, 'duration_days': duration_days}
        )

        return jsonify({
            'success': True,
            'message': 'User banned successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to ban user',
            'message': str(e)
        }), 500


@api_v1.route('/admin/users/<string:user_id>/unban', methods=['POST'])
@require_permission(Permissions.ADMIN_USER_WRITE)
def admin_unban_user(user_id: str):
    """
    Unban user.

    Path Parameters:
        user_id (str): User ID

    Response:
        200: User unbanned successfully
        403: Forbidden (insufficient permissions)
        404: User not found or not banned
        500: Server error
    """
    try:
        # Unban user via repository
        success = UserAdminRepository.admin_unban_user(
            user_id=user_id,
            unbanned_by_user_id=g.current_user['user_id']
        )

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to unban user',
                'message': 'User not found or not currently banned'
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='unban_user',
            resource_type='admin_users',
            resource_id=user_id,
            severity='medium'
        )

        return jsonify({
            'success': True,
            'message': 'User unbanned successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to unban user',
            'message': str(e)
        }), 500


@api_v1.route('/admin/users/<string:user_id>', methods=['DELETE'])
@require_permission(Permissions.ADMIN_USER_DELETE)
def admin_delete_user(user_id: str):
    """
    Delete user (soft or hard delete).

    Path Parameters:
        user_id (str): User ID

    Query Parameters:
        hard (bool): If true, permanently delete (default: false = soft delete)

    Response:
        200: User deleted successfully
        403: Forbidden (insufficient permissions)
        404: User not found
        500: Server error
    """
    try:
        hard_delete = request.args.get('hard', 'false').lower() == 'true'

        # Delete user via repository
        success = UserAdminRepository.admin_delete_user(
            user_id=user_id,
            deleted_by_user_id=g.current_user['user_id'],
            hard_delete=hard_delete
        )

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to delete user',
                'message': 'User not found'
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='delete_user',
            resource_type='admin_users',
            resource_id=user_id,
            severity='critical',
            details={'hard_delete': hard_delete}
        )

        return jsonify({
            'success': True,
            'message': f'User {"permanently deleted" if hard_delete else "soft deleted"} successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to delete user',
            'message': str(e)
        }), 500


@api_v1.route('/admin/users/<string:user_id>/verify', methods=['POST'])
@require_permission(Permissions.ADMIN_USER_WRITE)
def admin_verify_creator(user_id: str):
    """
    Verify creator status for user.

    Path Parameters:
        user_id (str): User ID

    Response:
        200: Creator verified successfully
        403: Forbidden (insufficient permissions)
        404: User not found or not a creator
        500: Server error
    """
    try:
        # Verify creator via repository
        success = UserAdminRepository.admin_verify_creator(
            user_id=user_id,
            verified_by_user_id=g.current_user['user_id']
        )

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to verify creator',
                'message': 'User not found or not a creator'
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='verify_creator',
            resource_type='admin_users',
            resource_id=user_id,
            severity='medium'
        )

        return jsonify({
            'success': True,
            'message': 'Creator verified successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to verify creator',
            'message': str(e)
        }), 500


__all__ = [
    'admin_list_users',
    'admin_create_user',
    'admin_get_user_details',
    'admin_change_user_role',
    'admin_ban_user',
    'admin_unban_user',
    'admin_delete_user',
    'admin_verify_creator',
]
