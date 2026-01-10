"""
Users Domain - Profile Routes (User Journey)

User-facing profile management endpoints:
- GET /users/:id  - Get user by ID (self or admin)
- PUT /users/:id  - Update user (self or admin)

Architecture: Journey-Based DDD
Database: PostgreSQL via UserRepository (direct SQL)
ISO 27001:2013 compliant - User profile management
"""

from flask import Blueprint

from ._helpers import (
    request, jsonify, g,
    ValidationError,
    UserUpdate, UserResponse,
    UserRepository, UserService,
    token_required,
    can_manage_user, get_accessible_roles
)


users_profile_bp = Blueprint('users_profile', __name__)


@users_profile_bp.route('/users/<user_id>', methods=['GET'])
@token_required
def get_user(user_id: str):
    """
    Get user by ID

    Path Parameters:
        user_id: User ID (UUID)

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
        is_admin = current_user.get('role') in ['admin', 'superadmin']
        is_org_admin = (
            current_user.get('role') in ['school_admin', 'company_admin'] and
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


@users_profile_bp.route('/users/<user_id>', methods=['PUT'])
@token_required
def update_user(user_id: str):
    """
    Update user

    Path Parameters:
        user_id: User ID (UUID)

    Request Body (all fields optional):
        {
            "firstname": "Jane",
            "lastname": "Doe",
            "email": "jane@example.com",
            "role_id": 2,
            "status": "active"
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
        if update_data.role_id:
            if is_self:
                return jsonify({
                    'success': False,
                    'error': 'Forbidden',
                    'message': 'You cannot change your own role'
                }), 403

            accessible_roles = get_accessible_roles(current_user.get('role'))
            if update_data.role_id not in accessible_roles:
                return jsonify({
                    'success': False,
                    'error': 'Insufficient permissions',
                    'message': f'You cannot assign the role ID "{update_data.role_id}"'
                }), 403

        # If updating status, check permissions
        if update_data.status:
            if is_self:
                return jsonify({
                    'success': False,
                    'error': 'Forbidden',
                    'message': 'You cannot change your own account status'
                }), 403

            if not can_manage:
                return jsonify({
                    'success': False,
                    'error': 'Insufficient permissions',
                    'message': 'You cannot change this user\'s status'
                }), 403

        # Update user via UserService (includes EventBus publish)
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

        updated_user = UserService.update_profile(user_id, **update_dict)

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
