"""
LernsystemX Users API

User management endpoints:
- GET    /api/v1/users - List users (paginated, filtered)
- GET    /api/v1/users/:id - Get user by ID
- POST   /api/v1/users - Create user (admin only)
- PUT    /api/v1/users/:id - Update user
- DELETE /api/v1/users/:id - Delete user (soft delete)
- POST   /api/v1/users/:id/activate - Activate user
- POST   /api/v1/users/:id/deactivate - Deactivate user
- GET    /api/v1/users/search - Search users

ISO 27001:2013 compliant - User management and access control
"""

from flask import request, jsonify, g
from pydantic import ValidationError

from app.api import api_v1
from app.models.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse
)
from app.repositories.user_repository import UserRepository
from app.middleware.auth import (
    token_required,
    admin_required,
    role_required,
    get_current_user,
    can_manage_user,
    get_accessible_roles
)


@api_v1.route('/users', methods=['GET'])
@role_required('admin', 'superadmin', 'school_admin', 'company_admin')
def list_users():
    """
    List users with pagination and filtering

    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)
        role: Filter by role
        organisation_id: Filter by organisation
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
        org_id = request.args.get('organisation_id')
        is_active = request.args.get('is_active')
        search_query = request.args.get('search')

        # Build filter conditions
        conditions = {}

        # Organisation admins can only see users in their organisation
        if current_user['role'] in ['school_admin', 'company_admin']:
            conditions['organisation_id'] = current_user['organisation_id']
        elif org_id:
            conditions['organisation_id'] = int(org_id)

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


@api_v1.route('/users/<int:user_id>', methods=['GET'])
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

        # Fetch user
        user = UserRepository.find_by_id(user_id)

        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found',
                'message': f'User with ID {user_id} does not exist'
            }), 404

        # Check permissions
        # Users can view themselves
        # Admins can view anyone
        # Org admins can view users in their org
        is_self = current_user['user_id'] == user_id
        is_admin = current_user['role'] in ['admin', 'superadmin']
        is_org_admin = (
            current_user['role'] in ['school_admin', 'company_admin'] and
            current_user.get('organisation_id') == user.get('organisation_id')
        )

        if not (is_self or is_admin or is_org_admin):
            return jsonify({
                'success': False,
                'error': 'Insufficient permissions',
                'message': 'You do not have permission to view this user'
            }), 403

        # Convert to Pydantic model
        user_response = UserResponse(**user)

        return jsonify({
            'success': True,
            'user': user_response.model_dump()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get user',
            'details': str(e)
        }), 500


@api_v1.route('/users', methods=['POST'])
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
            "organisation_id": 1
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
            if user_data.organisation_id != current_user.get('organisation_id'):
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
            organisation_id=user_data.organisation_id
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


@api_v1.route('/users/<int:user_id>', methods=['PUT'])
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

        # Fetch target user
        target_user = UserRepository.find_by_id(user_id)

        if not target_user:
            return jsonify({
                'success': False,
                'error': 'User not found',
                'message': f'User with ID {user_id} does not exist'
            }), 404

        # Check permissions
        is_self = current_user['user_id'] == user_id
        can_manage = can_manage_user(current_user, target_user)

        if not (is_self or can_manage):
            return jsonify({
                'success': False,
                'error': 'Insufficient permissions',
                'message': 'You do not have permission to update this user'
            }), 403

        # Get request data
        data = request.get_json()

        # Validate with Pydantic
        update_data = UserUpdate(**data)

        # If updating role, check permissions
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

        # If updating is_active, check permissions
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

        # Update user (only include non-None fields)
        update_dict = {
            k: v for k, v in update_data.model_dump().items()
            if v is not None
        }

        if not update_dict:
            return jsonify({
                'success': False,
                'error': 'No fields to update',
                'message': 'Please provide at least one field to update'
            }), 400

        updated_user = UserRepository.update(user_id, update_dict)

        # Convert to response model
        user_response = UserResponse(**updated_user)

        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'user': user_response.model_dump()
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
            'error': 'User update failed',
            'details': str(e)
        }), 500


@api_v1.route('/users/<int:user_id>', methods=['DELETE'])
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


@api_v1.route('/users/<int:user_id>/activate', methods=['POST'])
@admin_required
def activate_user(user_id: int):
    """
    Activate user account

    Path Parameters:
        user_id: User ID

    Response:
        200: User activated successfully
        403: Insufficient permissions
        404: User not found
    """
    try:
        current_user = g.current_user

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
                'message': 'You do not have permission to activate this user'
            }), 403

        # Activate user
        UserRepository.activate_user(user_id)

        return jsonify({
            'success': True,
            'message': 'User activated successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'User activation failed',
            'details': str(e)
        }), 500


@api_v1.route('/users/<int:user_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_user(user_id: int):
    """
    Deactivate user account

    Path Parameters:
        user_id: User ID

    Response:
        200: User deactivated successfully
        403: Insufficient permissions or self-deactivation attempt
        404: User not found
    """
    try:
        current_user = g.current_user

        # Prevent self-deactivation
        if current_user['user_id'] == user_id:
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'You cannot deactivate your own account'
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
                'message': 'You do not have permission to deactivate this user'
            }), 403

        # Deactivate user
        UserRepository.deactivate_user(user_id)

        return jsonify({
            'success': True,
            'message': 'User deactivated successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'User deactivation failed',
            'details': str(e)
        }), 500


@api_v1.route('/users/search', methods=['GET'])
@role_required('admin', 'superadmin', 'school_admin', 'company_admin', 'teacher')
def search_users():
    """
    Search users by email, name

    Query Parameters:
        q: Search query
        limit: Max results (default: 10, max: 50)
        role: Filter by role

    Response:
        200: List of matching users
    """
    try:
        current_user = g.current_user

        # Get query parameters
        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 10)), 50)
        role_filter = request.args.get('role')

        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query required',
                'message': 'Please provide a search query'
            }), 400

        # Search users
        users = UserRepository.search_users(
            query=query,
            limit=limit,
            role=role_filter
        )

        # Filter by organisation for org admins
        if current_user['role'] in ['school_admin', 'company_admin', 'teacher']:
            org_id = current_user.get('organisation_id')
            users = [
                u for u in users
                if u.get('organisation_id') == org_id
            ]

        # Convert to Pydantic models
        user_responses = [UserResponse(**user) for user in users]

        return jsonify({
            'success': True,
            'users': [u.model_dump() for u in user_responses],
            'total': len(user_responses)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Search failed',
            'details': str(e)
        }), 500


@api_v1.route('/users/stats', methods=['GET'])
@admin_required
def get_user_stats():
    """
    Get user statistics

    Response:
        200: User statistics
        - total: Total number of users
        - active: Active users
        - by_role: Count by role
    """
    try:
        stats = UserRepository.get_user_stats()

        return jsonify({
            'success': True,
            'stats': stats
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get stats',
            'details': str(e)
        }), 500
