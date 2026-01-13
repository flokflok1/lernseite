"""
Admin User CRUD API

Endpoints for user listing and details:
- GET /admin/users - List all users with filters
- GET /admin/users/<user_id> - Get user details

Moved from admin/users/crud.py to users/admin/crud.py
DDD Refactoring - 2026-01-08
"""

from flask import Blueprint, request, jsonify, g
from typing import Dict, Any

from app.repositories.user import UserRepository
from app.services.audit_service import AuditService
from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions

admin_users_crud_bp = Blueprint(
    'admin_users_crud',
    __name__,
    url_prefix='/admin/users'
)


@admin_users_crud_bp.route('', methods=['GET'])
@require_permission(Permissions.ADMIN_USER_READ)
def admin_list_users() -> tuple[Dict[str, Any], int]:
    """
    List all users with advanced filtering.

    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 50, max: 100)
        role: Filter by role (free, premium, creator, teacher, school, company, admin)
        search: Search by email or name
        status: Filter by status (active, suspended, banned)
        sort: Sort field (created_at, last_login, email)
        order: Sort order (asc, desc)

    Response:
        200: User list
        {
            "success": true,
            "users": [
                {
                    "user_id": "uuid",
                    "email": "user@example.com",
                    "firstname": "John",
                    "lastname": "Doe",
                    "role": "premium",
                    "status": "active",
                    "created_at": "2025-01-15T10:00:00Z",
                    "last_login": "2025-11-19T10:00:00Z",
                    "email_verified": true
                }
            ],
            "pagination": {
                "total": 1234,
                "page": 1,
                "per_page": 50,
                "total_pages": 25
            }
        }

        401: Unauthorized
        403: Forbidden (requires ADMIN_USER_READ)
    """
    try:
        # Parse query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        role = request.args.get('role')
        search = request.args.get('search')
        status = request.args.get('status', 'active')
        sort = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc')

        # Get users from repository
        result = UserRepository.admin_list_users(
            page=page,
            per_page=per_page,
            role=role,
            search=search,
            status=status,
            sort=sort,
            order=order
        )

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='admin.users.list',
            resource_type='user',
            details={'filters': {'role': role, 'search': search, 'status': status}}
        )

        return jsonify({
            'success': True,
            'users': result['users'],
            'pagination': result['pagination']
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid parameter',
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to list users',
            'details': str(e)
        }), 500


@admin_users_crud_bp.route('/<user_id>', methods=['GET'])
@require_permission(Permissions.ADMIN_USER_READ)
def admin_get_user_details(user_id: str) -> tuple[Dict[str, Any], int]:
    """
    Get detailed information about a specific user.

    Path Parameters:
        user_id: User UUID

    Response:
        200: User details
        {
            "success": true,
            "user": {
                "user_id": "uuid",
                "email": "user@example.com",
                "firstname": "John",
                "lastname": "Doe",
                "role": "premium",
                "status": "active",
                "created_at": "2025-01-15T10:00:00Z",
                "last_login": "2025-11-19T10:00:00Z",
                "email_verified": true,
                "two_factor_enabled": false,
                "organization_id": null,
                "subscription": {
                    "plan": "premium",
                    "status": "active",
                    "expires_at": "2025-12-19T10:00:00Z"
                },
                "tokens": {
                    "balance": 5000,
                    "total_used": 2500
                },
                "courses_created": 12,
                "courses_enrolled": 45,
                "login_history": [...],
                "ban_history": [...]
            }
        }

        404: User not found
        401: Unauthorized
        403: Forbidden
    """
    try:
        # Get comprehensive user details
        user_details = UserRepository.admin_get_user_details(user_id)

        if not user_details:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        # Audit log
        AuditService.log_action(
            user_id=g.current_user['user_id'],
            action='admin.users.view',
            resource_type='user',
            resource_id=user_id
        )

        return jsonify({
            'success': True,
            'user': user_details
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to get user details',
            'details': str(e)
        }), 500
