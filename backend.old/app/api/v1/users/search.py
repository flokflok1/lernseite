"""
LernsystemX Users API - Search and Statistics

Endpoints:
- GET /api/v1/users/search - Search users by email, name
- GET /api/v1/users/stats  - Get user statistics (admin only)

ISO 27001:2013 compliant - User management
"""

from flask import Blueprint, request, jsonify, g

from app.models.user import UserResponse
from app.repositories.user import UserRepository
from app.middleware.auth import admin_required, role_required

users_search_bp = Blueprint('users_search', __name__)


@users_search_bp.route('/users/search', methods=['GET'])
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
            org_id = current_user.get('organization_id')
            users = [
                u for u in users
                if u.get('organization_id') == org_id
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


@users_search_bp.route('/users/stats', methods=['GET'])
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
