"""
LernsystemX Users API - Part 2

User status management and search endpoints.

Endpoints in this file:
- POST /api/v1/users/:id/activate   - Activate user account
- POST /api/v1/users/:id/deactivate - Deactivate user account
- GET  /api/v1/users/search         - Search users
- GET  /api/v1/users/stats          - Get user statistics

Core endpoints in users.py:
- GET, POST, DELETE /api/v1/users
- GET, PUT /api/v1/users/:id

ISO 27001:2013 compliant - User management and access control
Refactored: 2026-01-12 - Consolidated from users/ folder into flat file
"""

from flask import Blueprint, request, jsonify, g

from app.domain.models.user import UserResponse
from app.infrastructure.persistence.repositories.user import UserRepository
from app.api.middleware.auth import admin_required, permission_required, can_manage_user


# Create users_part2 blueprint (extends users blueprint)
users_part2_bp = Blueprint('users_part2', __name__, url_prefix='/users')


# =============================================================================
# STATUS MANAGEMENT
# =============================================================================

@users_part2_bp.route('/<int:user_id>/activate', methods=['POST'])
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
                'message': 'You do not have permission to activate this user'
            }), 403

        UserRepository.activate_user(user_id)

        return jsonify({'success': True, 'message': 'User activated successfully'}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': 'User activation failed', 'details': str(e)}), 500


@users_part2_bp.route('/<int:user_id>/deactivate', methods=['POST'])
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
                'message': 'You do not have permission to deactivate this user'
            }), 403

        UserRepository.deactivate_user(user_id)

        return jsonify({'success': True, 'message': 'User deactivated successfully'}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': 'User deactivation failed', 'details': str(e)}), 500


# =============================================================================
# SEARCH AND STATISTICS
# =============================================================================

@users_part2_bp.route('/search', methods=['GET'])
@permission_required('admin.users:read')
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

        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 10)), 50)
        role_filter = request.args.get('role')

        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query required',
                'message': 'Please provide a search query'
            }), 400

        users = UserRepository.search_users(query=query, limit=limit, role=role_filter)

        # Filter by organisation for org admins
        if current_user['role'] in ['school_admin', 'company_admin', 'teacher']:
            org_id = current_user.get('organization_id')
            users = [u for u in users if u.get('organization_id') == org_id]

        user_responses = [UserResponse(**user) for user in users]

        return jsonify({
            'success': True,
            'users': [u.model_dump() for u in user_responses],
            'total': len(user_responses)
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': 'Search failed', 'details': str(e)}), 500


@users_part2_bp.route('/stats', methods=['GET'])
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

        return jsonify({'success': True, 'stats': stats}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': 'Failed to get stats', 'details': str(e)}), 500


# Export blueprint
__all__ = ['users_part2_bp']
