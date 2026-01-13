"""
LernsystemX Users API - Profile Operations

User-focused profile management endpoints:
- GET /api/v1/users/:id  - Get user by ID (self or admin)
- PUT /api/v1/users/:id  - Update user (self or admin)

ISO 27001:2013 compliant - User profile management
Moved from management/profile.py to user/profile.py - DDD Refactoring 2026-01-08
"""

from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError

from app.models.user import (
    UserUpdate,
    UserResponse
)
from app.repositories.user import UserRepository
from app.middleware.auth import (
    token_required,
    can_manage_user,
    get_accessible_roles
)

users_profile_bp = Blueprint('users_profile', __name__)


@users_profile_bp.route('/users/<int:user_id>', methods=['GET'])
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
            current_user.get('organization_id') == user.get('organization_id')
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


@users_profile_bp.route('/users/<int:user_id>', methods=['PUT'])
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
