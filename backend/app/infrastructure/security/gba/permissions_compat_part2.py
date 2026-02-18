"""
Compatibility Wrapper for RBAC 2.0 -> GBA Migration (Part 2)

This file contains utility functions and advanced decorators from the
permissions compatibility layer.

Split from permissions_compat.py to comply with Quality Gate G01 (max 500 lines per file).

Contents:
  - user_has_permission() - Check if user has a specific permission
  - get_user_permissions() - Get all permissions for a user
  - require_owner() - Decorator for Owner-Admin access
  - require_owner_or_permission() - Decorator for Owner OR specific permission

All functions are DEPRECATED - migrate to new GBA system:
  from app.api.middleware.auth import permission_required, admin_required
"""

from functools import wraps
from typing import Set

from flask import jsonify

from app.infrastructure.security.gba.permissions_compat import _map_permission_code


# ============================================================================
# UTILITY FUNCTIONS (OLD - Deprecated but kept for compatibility)
# ============================================================================

def user_has_permission(user: dict, permission: str) -> bool:
    """
    Check if user has a specific permission (compatibility wrapper).

    DEPRECATED: Use PermissionService.check_permission() directly instead.

    Args:
        user: User dict with 'user_id' key
        permission: Old RBAC 2.0 permission code

    Returns:
        True if user has permission, False otherwise
    """
    from app.application.services.system.auth.permission import PermissionService

    if not user:
        return False

    # Map old permission code to new GBA code
    gba_permission = _map_permission_code(permission)

    # Check using new PermissionService
    return PermissionService.check_permission(user, gba_permission)


def get_user_permissions(user: dict) -> Set[str]:
    """
    Get all permissions for a user (compatibility wrapper).

    DEPRECATED: Use PermissionService.get_user_permissions() directly instead.

    Args:
        user: User dict

    Returns:
        Set of permission codes (OLD RBAC 2.0 format)
    """
    from app.application.services.system.auth.permission import PermissionService

    if not user or 'user_id' not in user:
        return set()

    # Get new GBA permissions
    gba_permissions = PermissionService.get_user_permissions(user.get('user_id'))

    # Map back to old format (reverse mapping)
    # This is lossy but allows backward compatibility
    reverse_map = {
        'admin.users:manage': 'admin:users',
        'admin.users:read': 'view:users',
        'content.courses:manage': 'manage:courses',
        'admin.system:manage': 'admin:system',
        'view_any_resource': 'admin:system',  # System admin
        'users.manage': 'admin:organisations',  # Org admin
    }

    old_permissions = set()
    for gba_perm in gba_permissions:
        old_perm = reverse_map.get(gba_perm, gba_perm)
        old_permissions.add(old_perm)

    return old_permissions


# ============================================================================
# ADVANCED DECORATORS (OLD - Deprecated but kept for compatibility)
# ============================================================================

def require_owner():
    """
    Decorator to require Owner-Admin access (GBA - via compatibility wrapper).

    DEPRECATED: Use @admin_required from app.api.middleware.auth instead.

    Owner-level users have 'view_any_resource' permission (highest GBA privilege).

    Usage (OLD - still works):
        @require_owner()
        def owner_settings():
            ...

    Returns:
        403 Forbidden if user doesn't have owner-level access
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.api.middleware.auth import get_current_user
            from app.application.services.system.auth.permission import PermissionService

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

            # GBA: Owner-level access requires 'view_any_resource' permission
            if not PermissionService.check_permission(user, 'view_any_resource'):
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
    Decorator that allows Owner-Admin OR specific permission (GBA - via compatibility wrapper).

    DEPRECATED: Consider using @permission_required from app.api.middleware.auth instead.

    Owner-level users (with 'view_any_resource') bypass specific permission checks.

    Args:
        permission_code: Old RBAC 2.0 permission code (e.g. 'admin:courses')

    Usage (OLD - still works):
        @require_owner_or_permission('admin:courses')
        def create_course():
            ...

    Returns:
        403 Forbidden if user doesn't have owner access or required permission
    """
    # Map old permission code to new GBA code
    gba_permission = _map_permission_code(permission_code)

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.api.middleware.auth import get_current_user
            from app.application.services.system.auth.permission import PermissionService

            user = get_current_user()

            if not user:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'UNAUTHORIZED',
                        'message': 'Authentication required'
                    }
                }), 401

            # GBA: Check owner access (view_any_resource) OR specific permission
            if (PermissionService.check_permission(user, 'view_any_resource') or
                    PermissionService.check_permission(user, gba_permission)):
                return f(*args, **kwargs)

            # Neither owner nor required permission
            return jsonify({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': f'Permission {gba_permission} required or Owner-Admin access'
                }
            }), 403

        return decorated_function
    return decorator


# ============================================================================
# MIGRATION NOTES
# ============================================================================
#
# This compatibility wrapper allows the codebase to function while migrating
# from RBAC 2.0 (role-based) to GBA (group-based).
#
# Migration Steps:
#
# 1. OLD CODE (Still works, via this wrapper):
#    from app.infrastructure.security.gba.permissions import require_permission, Permissions
#    @require_permission(Permissions.ADMIN_USER_READ)
#    def list_users():
#        return jsonify([...])
#
# 2. NEW CODE (Preferred):
#    from app.api.middleware.auth import permission_required
#    @permission_required('admin.users:read')
#    def list_users():
#        return jsonify([...])
#
# The wrapper automatically translates old permission codes to new GBA codes
# via _map_permission_code() function.
#
# Once all files have been migrated to new syntax, this wrapper can be deleted.
