"""
LernsystemX Users API - Part 1

User management endpoints including CRUD and profile operations.

Endpoints:
- GET    /api/v1/users           - List users (paginated, filtered)
- POST   /api/v1/users           - Create user (admin only)
- DELETE /api/v1/users/:id       - Delete user (soft delete)
- GET    /api/v1/users/:id       - Get user by ID
- PUT    /api/v1/users/:id       - Update user

Additional endpoints in users_part2.py:
- POST /api/v1/users/:id/activate   - Activate user
- POST /api/v1/users/:id/deactivate - Deactivate user
- GET  /api/v1/users/search         - Search users
- GET  /api/v1/users/stats          - Get user statistics

ISO 27001:2013 compliant - User management and access control
Refactored: 2026-01-12 - Consolidated from users/ folder into flat file
"""

from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError

from app.domain.models.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse
)
from app.infrastructure.persistence.repositories.user import UserRepository
from app.api.middleware.auth import (
    admin_required,
    role_required,
    token_required,
    can_manage_user,
    get_accessible_roles
)


# Create users blueprint
users_bp = Blueprint('users', __name__, url_prefix='/users')


# =============================================================================
# CRUD OPERATIONS
# =============================================================================

@users_bp.route('', methods=['GET'])
@role_required('admin', 'superadmin', 'school_admin', 'company_admin')
def list_users():
    """
    List users with pagination and filtering

    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)
        role: Filter by role
        organization_id: Filter by organisation
        is_active: Filter by active status (true/false)
        search: Search by email, first_name, last_name

    Response:
        200: Paginated list of users
        403: Insufficient permissions
    """
    try:
        current_user = g.current_user

        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        role_filter = request.args.get('role')
        org_id = request.args.get('organization_id')
        is_active = request.args.get('is_active')
        search_query = request.args.get('search')

        # Build filter conditions
        conditions = {}

        # Organisation admins can only see users in their organisation
        if current_user['role'] in ['school_admin', 'company_admin']:
            conditions['organization_id'] = current_user['organization_id']
        elif org_id:
            conditions['organization_id'] = int(org_id)

        if role_filter:
            conditions['role'] = role_filter

        if is_active is not None:
            conditions['is_active'] = is_active.lower() == 'true'

        # Search users
        if search_query:
            users_result = UserRepository.search_users(
                query=search_query,
                limit=per_page,
                role=role_filter
            )
            result = {
                'items': users_result,
                'total': len(users_result),
                'page': 1,
                'per_page': per_page,
                'total_pages': 1,
                'has_prev': False,
                'has_next': False
            }
        else:
            result = UserRepository.paginate(
                page=page,
                per_page=per_page,
                order_by='created_at DESC',
                **conditions
            )

        user_responses = [UserResponse(**user) for user in result['items']]
        user_list = UserListResponse(
            items=user_responses,
            total=result['total'],
            page=result['page'],
            per_page=result['per_page'],
            total_pages=result['total_pages'],
            has_prev=result['has_prev'],
            has_next=result['has_next']
        )

        return jsonify({'success': True, **user_list.model_dump()}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': 'Failed to list users', 'details': str(e)}), 500


@users_bp.route('', methods=['POST'])
@admin_required
def create_user():
    """
    Create new user (admin only)

    Request Body:
        {
            "email": "user@example.com",
            "password": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe",
            "role": "user",
            "organization_id": 1
        }

    Response:
        201: User created successfully
        400: Validation error
        403: Insufficient permissions
    """
    try:
        current_user = g.current_user
        data = request.get_json()
        user_data = UserCreate(**data)

        # Check if admin can assign this role
        accessible_roles = get_accessible_roles(current_user['role'])
        if user_data.role not in accessible_roles:
            return jsonify({
                'success': False,
                'error': 'Insufficient permissions',
                'message': f'You cannot assign the role "{user_data.role}"',
                'accessible_roles': accessible_roles
            }), 403

        # Organisation admins can only create users in their organisation
        if current_user['role'] in ['school_admin', 'company_admin']:
            if user_data.organization_id != current_user.get('organization_id'):
                return jsonify({
                    'success': False,
                    'error': 'Insufficient permissions',
                    'message': 'You can only create users in your own organisation'
                }), 403

        user = UserRepository.create_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role,
            organization_id=user_data.organization_id
        )

        user_response = UserResponse(**user)

        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'user': user_response.model_dump()
        }), 201

    except ValidationError as e:
        return jsonify({'success': False, 'error': 'Validation error', 'details': e.errors()}), 400
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'User creation failed', 'details': str(e)}), 500


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id: int):
    """
    Delete user (soft delete - deactivate)

    Path Parameters:
        user_id: User ID

    Response:
        200: User deleted successfully
        403: Insufficient permissions
        404: User not found
    """
    try:
        current_user = g.current_user

        # Prevent self-deletion
        if current_user['user_id'] == user_id:
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'You cannot delete your own account'
            }), 403

        target_user = UserRepository.find_by_id(user_id)
        if not target_user:
            return jsonify({
                'success': False,
                'error': 'User not found',
                'message': f'User with ID {user_id} does not exist'
            }), 404

        if not can_manage_user(current_user, target_user):
            return jsonify({
                'success': False,
                'error': 'Insufficient permissions',
                'message': 'You do not have permission to delete this user'
            }), 403

        UserRepository.deactivate_user(user_id)

        return jsonify({'success': True, 'message': 'User deleted successfully'}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': 'User deletion failed', 'details': str(e)}), 500


# =============================================================================
# PROFILE OPERATIONS
# =============================================================================

@users_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id: int):
    """
    Get user by ID

    Path Parameters:
        user_id: User ID

    Response:
        200: User data
        403: Insufficient permissions
        404: User not found
    """
    try:
        current_user = g.current_user

        user = UserRepository.find_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found',
                'message': f'User with ID {user_id} does not exist'
            }), 404

        # Check permissions: Users can view themselves, admins can view anyone, org admins can view users in their org
        # RBAC 2.0: Use dynamic permission checking
        from app.application.services.permission_service import PermissionService
        is_self = current_user['user_id'] == user_id
        is_admin = PermissionService.check_threshold(current_user, 'users.view_all')
        # hierarchy_level 5 = school_admin, company_admin
        is_org_admin = (
            current_user.get('hierarchy_level', 0) == 5 and
            current_user.get('organization_id') == user.get('organization_id')
        )

        if not (is_self or is_admin or is_org_admin):
            return jsonify({
                'success': False,
                'error': 'Insufficient permissions',
                'message': 'You do not have permission to view this user'
            }), 403

        user_response = UserResponse(**user)

        return jsonify({'success': True, 'user': user_response.model_dump()}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': 'Failed to get user', 'details': str(e)}), 500


@users_bp.route('/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id: int):
    """
    Update user

    Path Parameters:
        user_id: User ID

    Request Body (all fields optional):
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "role": "premium",
            "is_active": true
        }

    Response:
        200: User updated successfully
        400: Validation error
        403: Insufficient permissions
        404: User not found
    """
    try:
        current_user = g.current_user

        target_user = UserRepository.find_by_id(user_id)
        if not target_user:
            return jsonify({
                'success': False,
                'error': 'User not found',
                'message': f'User with ID {user_id} does not exist'
            }), 404

        is_self = current_user['user_id'] == user_id
        can_manage = can_manage_user(current_user, target_user)

        if not (is_self or can_manage):
            return jsonify({
                'success': False,
                'error': 'Insufficient permissions',
                'message': 'You do not have permission to update this user'
            }), 403

        data = request.get_json()
        update_data = UserUpdate(**data)

        # Check role update permissions
        if update_data.role:
            if is_self:
                return jsonify({
                    'success': False,
                    'error': 'Forbidden',
                    'message': 'You cannot change your own role'
                }), 403

            accessible_roles = get_accessible_roles(current_user['role'])
            if update_data.role not in accessible_roles:
                return jsonify({
                    'success': False,
                    'error': 'Insufficient permissions',
                    'message': f'You cannot assign the role "{update_data.role}"'
                }), 403

        # Check is_active update permissions
        if update_data.is_active is not None:
            if is_self:
                return jsonify({
                    'success': False,
                    'error': 'Forbidden',
                    'message': 'You cannot deactivate your own account'
                }), 403

            if not can_manage:
                return jsonify({
                    'success': False,
                    'error': 'Insufficient permissions',
                    'message': 'You cannot activate/deactivate this user'
                }), 403

        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}

        if not update_dict:
            return jsonify({
                'success': False,
                'error': 'No fields to update',
                'message': 'Please provide at least one field to update'
            }), 400

        updated_user = UserRepository.update(user_id, update_dict)
        user_response = UserResponse(**updated_user)

        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'user': user_response.model_dump()
        }), 200

    except ValidationError as e:
        return jsonify({'success': False, 'error': 'Validation error', 'details': e.errors()}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'User update failed', 'details': str(e)}), 500


# Export blueprint
__all__ = ['users_bp']
