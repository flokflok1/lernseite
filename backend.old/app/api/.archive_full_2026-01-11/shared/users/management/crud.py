"""
LernsystemX Users API - CRUD Operations

Admin-focused user management endpoints:
- GET    /api/v1/users           - List users (paginated, filtered)
- POST   /api/v1/users           - Create user (admin only)
- DELETE /api/v1/users/:id       - Delete user (soft delete)

ISO 27001:2013 compliant - User management and access control
"""

from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError

from app.models.user import (
    UserCreate,
    UserResponse,
    UserListResponse
)
from app.repositories.user import UserRepository
from app.middleware.auth import (
    admin_required,
    role_required,
    can_manage_user,
    get_accessible_roles
)

users_crud_bp = Blueprint('users_crud', __name__)


@users_crud_bp.route('/users', methods=['GET'])
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
            # Convert to pagination format
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
            # Paginate users
            result = UserRepository.paginate(
                page=page,
                per_page=per_page,
                order_by='created_at DESC',
                **conditions
            )

        # Convert to Pydantic models
        user_responses = [UserResponse(**user) for user in result['items']]

        # Create paginated response
        user_list = UserListResponse(
            items=user_responses,
            total=result['total'],
            page=result['page'],
            per_page=result['per_page'],
            total_pages=result['total_pages'],
            has_prev=result['has_prev'],
            has_next=result['has_next']
        )

        return jsonify({
            'success': True,
            **user_list.model_dump()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to list users',
            'details': str(e)
        }), 500


@users_crud_bp.route('/users', methods=['POST'])
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

        # Get request data
        data = request.get_json()

        # Validate with Pydantic
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

        # Create user
        user = UserRepository.create_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role,
            organization_id=user_data.organization_id
        )

        # Convert to response model
        user_response = UserResponse(**user)

        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'user': user_response.model_dump()
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'User creation failed',
            'details': str(e)
        }), 500


@users_crud_bp.route('/users/<int:user_id>', methods=['DELETE'])
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

        # Fetch target user
        target_user = UserRepository.find_by_id(user_id)

        if not target_user:
            return jsonify({
                'success': False,
                'error': 'User not found',
                'message': f'User with ID {user_id} does not exist'
            }), 404

        # Check permissions
        if not can_manage_user(current_user, target_user):
            return jsonify({
                'success': False,
                'error': 'Insufficient permissions',
                'message': 'You do not have permission to delete this user'
            }), 403

        # Soft delete (deactivate)
        UserRepository.deactivate_user(user_id)

        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'User deletion failed',
            'details': str(e)
        }), 500
