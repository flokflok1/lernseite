"""
LernsystemX Admin API - User Management (Part 1: CRUD & Group Operations)

Admin endpoints for user listing, creation, details, and group management.

Endpoints:
- GET /api/v1/admin/users - List users with filtering and pagination
- POST /api/v1/admin/users - Create a new user
- GET /api/v1/admin/users/{id} - Get detailed user information
- PATCH /api/v1/admin/users/{id}/role - [DEPRECATED] Change user role
- PATCH /api/v1/admin/users/{id}/groups - Update user group memberships

See users_part2.py for moderation actions (ban, unban, delete, verify).

Phase B24 - Admin User Management Implementation
"""

from flask import jsonify, request, g
from pydantic import BaseModel, EmailStr, Field, ValidationError

from app.api.v1 import api_v1
from app.api.middleware.auth import permission_required
from app.infrastructure.persistence.repositories.user.admin import UserAdminRepository
from app.infrastructure.persistence.repositories.user.auth import UserAuthRepository
from app.application.services.system.audit.service import AuditService


# ==========================================
# PYDANTIC MODELS
# ==========================================

class CreateUserRequest(BaseModel):
    """Request body for creating a new user."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(
        default='free',
        description='Role name: free, premium, creator, teacher, admin, owner'
    )

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


# ==========================================
# CRUD & GROUP ENDPOINTS
# ==========================================

@api_v1.route('/admin/users', methods=['GET'])
@permission_required('admin.users:read')
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
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        status = request.args.get('status', '')
        role = request.args.get('role', '')
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')

        result = UserAdminRepository.admin_list_users(
            page=page,
            per_page=per_page,
            status=status,
            role=role,
            search=search,
            sort=sort_by,
            order=sort_order
        )

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
@permission_required('admin.users:write')
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
@permission_required('admin.users:read')
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
        user_details = UserAdminRepository.admin_get_user_details(user_id)

        if not user_details:
            return jsonify({
                'success': False,
                'error': 'User not found',
                'message': f'No user found with ID: {user_id}'
            }), 404

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
def admin_change_user_role_deprecated(user_id: str):
    """
    @deprecated This endpoint is deprecated. Use PATCH /admin/users/{id}/groups instead.

    This endpoint will be removed on 2027-01-20 (12 months from now).
    The old role-based system has been replaced with Group-Based Architecture (GBA).
    """
    return jsonify({
        'success': False,
        'error': 'DEPRECATED_ENDPOINT',
        'message': 'This endpoint is deprecated. Use PATCH /admin/users/{id}/groups instead (GBA)',
        'migration_guide': {
            'old_endpoint': 'PATCH /admin/users/{id}/role',
            'old_body': '{"new_role": "premium"}',
            'new_endpoint': 'PATCH /admin/users/{id}/groups',
            'new_body': '{"group_ids": [1, 2, 3], "replace": true}',
            'removal_date': '2027-01-20'
        }
    }), 410


@api_v1.route('/admin/users/<string:user_id>/groups', methods=['PATCH'])
@permission_required('admin.users:write')
def admin_update_user_groups(user_id: str):
    """
    Update user's group memberships (GBA - Group-Based Architecture).

    Path Parameters:
        user_id (str): User ID

    Request Body:
        {
            "group_ids": [1, 2, 3],      // List of group IDs to assign
            "replace": true              // If true, replace all groups; if false, add to existing
        }

    Response:
        200: Groups updated successfully
        400: Missing required fields or invalid input
        403: Forbidden (insufficient permissions)
        404: User not found
        500: Server error
    """
    try:
        data = request.get_json()
        group_ids = data.get('group_ids', [])
        replace = data.get('replace', False)

        if not isinstance(group_ids, list) or len(group_ids) == 0:
            return jsonify({
                'success': False,
                'error': 'Invalid request',
                'message': 'group_ids must be a non-empty array'
            }), 400

        success = UserAdminRepository.admin_update_groups(
            user_id=user_id,
            group_slugs=[str(gid) for gid in group_ids],
            changed_by=g.current_user['user_id'],
            replace=replace
        )

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to update groups',
                'message': 'User not found or invalid group IDs'
            }), 404

        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='update_user_groups',
            resource_type='admin_users',
            resource_id=user_id,
            severity='medium',
            details={'group_ids': group_ids, 'replace': replace}
        )

        return jsonify({
            'success': True,
            'message': 'User groups updated successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to update user groups',
            'message': str(e)
        }), 500


__all__ = [
    'CreateUserRequest',
    'admin_list_users',
    'admin_create_user',
    'admin_get_user_details',
    'admin_change_user_role_deprecated',
    'admin_update_user_groups',
]
