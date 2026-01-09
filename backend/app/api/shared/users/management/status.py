"""
LernsystemX Users API - Status Management

Endpoints:
- POST /api/v1/users/:id/activate   - Activate user account
- POST /api/v1/users/:id/deactivate - Deactivate user account

ISO 27001:2013 compliant - User access control
"""

from flask import Blueprint, jsonify, g

from app.repositories.user import UserRepository
from app.middleware.auth import admin_required, can_manage_user

users_status_bp = Blueprint('users_status', __name__)


@users_status_bp.route('/users/<int:user_id>/activate', methods=['POST'])
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


@users_status_bp.route('/users/<int:user_id>/deactivate', methods=['POST'])
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
