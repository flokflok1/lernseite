"""
Security Decorators for Owner-Admin System

This module provides decorators for protecting endpoints with Owner-Admin checks.

RBAC 2.0: Uses PermissionService for dynamic permission threshold checks.
"""

from functools import wraps
from flask import jsonify
from app.middleware.auth import get_current_user
from app.services.permission_service import PermissionService


def require_owner():
    """
    Decorator to require Owner-Admin access.

    RBAC 2.0: Uses PermissionService to check 'owner.access' permission (threshold: 10).
    This ensures dynamic, database-driven permission checks instead of hardcoded roles.

    Usage:
        @admin_bp.route('/owner/system-settings')
        @require_owner()
        def owner_settings():
            return jsonify({'status': 'ok'})

    Returns:
        403 Forbidden if user doesn't have owner-level access
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get current user from JWT token
            user = get_current_user()

            if not user:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'UNAUTHORIZED',
                        'message': 'Authentication required'
                    }
                }), 401

            # RBAC 2.0: Check 'owner.access' permission via PermissionService
            # This checks if hierarchy_level >= threshold for 'owner.access' (default: 10)
            if not PermissionService.check_threshold(user, 'owner.access'):
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'FORBIDDEN',
                        'message': 'Owner-Admin access required'
                    }
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_owner_or_permission(permission_code: str):
    """
    Decorator that allows Owner-Admin OR specific permission.

    RBAC 2.0: Uses PermissionService for both owner check and permission check.
    Owner-level access (hierarchy_level >= 10) bypasses specific permission checks.

    Args:
        permission_code: Permission required (e.g. 'courses.manage')

    Usage:
        @admin_bp.route('/courses', methods=['POST'])
        @require_owner_or_permission('courses.manage')
        def create_course():
            return jsonify({'status': 'ok'})
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()

            if not user:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'UNAUTHORIZED',
                        'message': 'Authentication required'
                    }
                }), 401

            # RBAC 2.0: Check owner access OR specific permission
            # Owner-level users (hierarchy_level >= 10) bypass specific permission checks
            if PermissionService.check_threshold(user, 'owner.access'):
                return f(*args, **kwargs)

            # Check specific permission for non-owner users
            if PermissionService.check_threshold(user, permission_code):
                return f(*args, **kwargs)

            # Neither owner nor required permission
            return jsonify({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': f'Permission {permission_code} required or Owner-Admin access'
                }
            }), 403

        return decorated_function
    return decorator
