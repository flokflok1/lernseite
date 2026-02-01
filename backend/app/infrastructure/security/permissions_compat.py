"""
Compatibility Wrapper for RBAC 2.0 → GBA Migration

This file provides backward compatibility for code still using old @require_permission()
decorators while the system is migrated from RBAC 2.0 to GBA (Group-Based Architecture).

Maps old permission checking to new PermissionService.check_permission() system.

IMPORTANT: This is a TEMPORARY bridge. All code should migrate to use the new
@permission_required() decorator from app.api.middleware.auth.

Migration Path:
  OLD: from app.infrastructure.security.permissions import require_permission, Permissions
       @require_permission(Permissions.ADMIN_USER_READ)

  NEW: from app.api.middleware.auth import permission_required
       @permission_required('admin.user:read')

This wrapper automatically translates old permission codes to new GBA format.
"""

from functools import wraps
from typing import Set
from flask import jsonify, g
from app.api.middleware.auth import token_required

# ============================================================================
# PERMISSION CONSTANTS (OLD RBAC 2.0 - For backward compatibility)
# ============================================================================
# These constants are mapped to new GBA permission codes in _map_permission_code()

class Permissions:
    """
    OLD RBAC 2.0 permission constants.

    These are automatically mapped to new GBA permission codes.
    DO NOT add new constants here - instead add them to GBA system.
    """

    # User Management
    MANAGE_USERS = 'admin:users'
    VIEW_USERS = 'view:users'
    MODIFY_USER_ROLES = 'admin:users:roles'

    # Organisation Management
    MANAGE_ORGANISATIONS = 'admin:organisations'
    VIEW_ORGANISATIONS = 'view:organisations'
    MANAGE_ORG_MEMBERS = 'manage:org:members'
    MANAGE_ORG_SETTINGS = 'manage:org:settings'

    # Course Management
    CREATE_COURSES = 'create:courses'
    MANAGE_COURSES = 'manage:courses'
    PUBLISH_COURSES = 'publish:courses'
    MODERATE_COURSES = 'moderate:courses'

    # Analytics
    VIEW_SYSTEM_ANALYTICS = 'view:analytics:system'
    VIEW_ORG_ANALYTICS = 'view:analytics:org'
    VIEW_OWN_ANALYTICS = 'view:analytics:own'

    # Billing & Tokens
    MANAGE_BILLING = 'manage:billing'
    VIEW_BILLING = 'view:billing'
    MANAGE_TOKEN_POOL = 'manage:tokens'
    VIEW_TOKEN_POOL = 'view:tokens'

    # AI Features
    USE_AI_BASIC = 'use:ai:basic'
    USE_AI_PREMIUM = 'use:ai:premium'
    USE_AI_PRO = 'use:ai:pro'
    CREATE_AI_CONTENT = 'create:ai'

    # Content Moderation
    MODERATE_CONTENT = 'moderate:content'
    MODERATE_USERS = 'moderate:users'

    # System Administration
    MANAGE_SYSTEM = 'admin:system'
    ADMIN_SYSTEM_READ = 'admin:system:read'
    ADMIN_SYSTEM_WRITE = 'admin:system:write'
    VIEW_SYSTEM_LOGS = 'view:logs:system'
    MANAGE_FEATURE_FLAGS = 'manage:features'

    # Admin User Management
    ADMIN_USER_READ = 'admin:user:read'
    ADMIN_USER_WRITE = 'admin:user:write'
    ADMIN_USER_DELETE = 'admin:user:delete'

    # Admin Course Management
    ADMIN_COURSE_READ = 'admin:course:read'
    ADMIN_COURSE_WRITE = 'admin:course:write'
    ADMIN_COURSE_DELETE = 'admin:course:delete'

    # Admin Lesson Management
    ADMIN_LESSON_READ = 'admin:lesson:read'
    ADMIN_LESSON_WRITE = 'admin:lesson:write'
    ADMIN_LESSON_DELETE = 'admin:lesson:delete'

    # Admin AI Job Management
    ADMIN_AI_JOBS_READ = 'admin:ai:jobs:read'
    ADMIN_AI_JOBS_WRITE = 'admin:ai:jobs:write'
    ADMIN_AI_JOBS_EXECUTE = 'admin:ai:jobs:execute'

    # LiveRoom
    CREATE_LIVEROOM_BASIC = 'create:liveroom:basic'
    CREATE_LIVEROOM_PRO = 'create:liveroom:pro'


# ============================================================================
# PERMISSION CODE MAPPING (OLD RBAC 2.0 → NEW GBA)
# ============================================================================

def _map_permission_code(old_permission: str) -> str:
    """
    Map old RBAC 2.0 permission codes to new GBA permission codes.

    GBA permission codes use format: 'domain.resource:action'
    Examples:
      - 'admin.users:manage'
      - 'admin.courses:write'
      - 'analytics.system:view'

    Args:
        old_permission: Old RBAC 2.0 permission code (e.g., 'admin:users')

    Returns:
        New GBA permission code
    """
    # Mapping of old → new permission codes
    permission_map = {
        # User Management
        'admin:users': 'admin.users:manage',
        'view:users': 'admin.users:read',
        'admin:users:roles': 'admin.users:manage',

        # Organisation Management
        'admin:organisations': 'admin.organisations:manage',
        'view:organisations': 'admin.organisations:read',
        'manage:org:members': 'admin.organisations:manage',
        'manage:org:settings': 'admin.organisations:manage',

        # Course Management
        'create:courses': 'content.courses:create',
        'manage:courses': 'content.courses:manage',
        'publish:courses': 'content.courses:publish',
        'moderate:courses': 'content.moderation:moderate',

        # Analytics
        'view:analytics:system': 'analytics.system:view',
        'view:analytics:org': 'analytics.organisations:view',
        'view:analytics:own': 'analytics.personal:view',

        # Billing & Tokens
        'manage:billing': 'admin.billing:manage',
        'view:billing': 'admin.billing:read',
        'manage:tokens': 'admin.tokens:manage',
        'view:tokens': 'admin.tokens:read',

        # AI Features
        'use:ai:basic': 'ai.features:use_basic',
        'use:ai:premium': 'ai.features:use_premium',
        'use:ai:pro': 'ai.features:use_pro',
        'create:ai': 'ai.content:create',

        # Content Moderation
        'moderate:content': 'content.moderation:moderate',
        'moderate:users': 'admin.moderation:moderate',

        # System Administration
        'admin:system': 'admin.system:manage',
        'admin:system:read': 'admin.system:read',
        'admin:system:write': 'admin.system:write',
        'view:logs:system': 'admin.logs:read',
        'manage:features': 'admin.features:manage',

        # Admin User Management
        'admin:user:read': 'admin.users:read',
        'admin:user:write': 'admin.users:write',
        'admin:user:delete': 'admin.users:delete',

        # Admin Course Management
        'admin:course:read': 'admin.courses:read',
        'admin:course:write': 'admin.courses:write',
        'admin:course:delete': 'admin.courses:delete',

        # Admin Lesson Management
        'admin:lesson:read': 'admin.lessons:read',
        'admin:lesson:write': 'admin.lessons:write',
        'admin:lesson:delete': 'admin.lessons:delete',

        # Admin AI Job Management
        'admin:ai:jobs:read': 'admin.ai.jobs:read',
        'admin:ai:jobs:write': 'admin.ai.jobs:write',
        'admin:ai:jobs:execute': 'admin.ai.jobs:execute',

        # LiveRoom
        'create:liveroom:basic': 'liveroom.basic:create',
        'create:liveroom:pro': 'liveroom.pro:create',
    }

    return permission_map.get(old_permission, old_permission)


# ============================================================================
# DECORATORS (OLD RBAC 2.0 - Compatibility Wrapper)
# ============================================================================
# All decorators now use the NEW PermissionService.check_permission() internally

def require_permission(permission: str):
    """
    Decorator to require a specific permission (GBA - via compatibility wrapper).

    DEPRECATED: Use @permission_required() from app.api.middleware.auth instead.

    This is a compatibility wrapper that maps old permission codes to new GBA system.

    Usage (OLD - still works):
        @require_permission(Permissions.ADMIN_USER_READ)
        def list_users():
            ...

    Usage (NEW - preferred):
        @permission_required('admin.users:read')
        def list_users():
            ...

    Args:
        permission: Old RBAC 2.0 permission code (e.g., 'admin:user:read')

    Returns:
        403 Forbidden if user doesn't have permission
    """
    # Map old permission code to new GBA code
    gba_permission = _map_permission_code(permission)

    def decorator(fn):
        @wraps(fn)
        @token_required
        def wrapper(*args, **kwargs):
            from app.application.services.system.auth.permission import PermissionService

            current_user = g.current_user

            # Check permission using NEW PermissionService (GBA)
            if not PermissionService.check_permission(current_user, gba_permission):
                return jsonify({
                    'success': False,
                    'error': 'Forbidden',
                    'message': f'Missing required permission: {gba_permission}'
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_system_admin(fn):
    """
    Decorator to require system admin privileges (GBA - via compatibility wrapper).

    DEPRECATED: Use @admin_required from app.api.middleware.auth instead.

    This is a compatibility wrapper that uses the new PermissionService.

    Checks for 'view_any_resource' permission (system admin capability).

    Args:
        fn: Flask view function to wrap

    Returns:
        403 Forbidden if not system admin
    """
    @wraps(fn)
    @token_required
    def wrapper(*args, **kwargs):
        from app.application.services.system.auth.permission import PermissionService

        current_user = g.current_user

        # System admins have 'view_any_resource' permission (GBA)
        if not PermissionService.check_permission(current_user, 'view_any_resource'):
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'System administrator access required'
            }), 403

        return fn(*args, **kwargs)

    return wrapper


def require_org_admin(fn):
    """
    Decorator to require organisation admin privileges (GBA - via compatibility wrapper).

    DEPRECATED: Use @permission_required('admin.organisations:manage') instead.

    This is a compatibility wrapper that uses the new PermissionService.

    Checks for 'users.manage' permission (org admin capability).

    Args:
        fn: Flask view function to wrap

    Returns:
        403 Forbidden if not org admin
    """
    @wraps(fn)
    @token_required
    def wrapper(*args, **kwargs):
        from app.application.services.system.auth.permission import PermissionService

        current_user = g.current_user

        # Org admins have 'users.manage' permission (GBA)
        # OR system admins have 'view_any_resource'
        has_permission = (
            PermissionService.check_permission(current_user, 'users.manage') or
            PermissionService.check_permission(current_user, 'view_any_resource')
        )

        if not has_permission:
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'Organisation administrator access required'
            }), 403

        return fn(*args, **kwargs)

    return wrapper


def require_org_member(fn):
    """
    Decorator to check if user is member of a specific organisation (resource-based access).

    This decorator verifies resource ownership, NOT capabilities.
    Uses organisation_id from JWT token for fast check.

    Args:
        fn: Flask view function to wrap

    Returns:
        403 Forbidden if not member of organisation
    """
    @wraps(fn)
    @token_required
    def wrapper(*args, **kwargs):
        current_user = g.current_user
        user_org_id = current_user.get('organisation_id')

        # System admins (view_any_resource) can access any org
        from app.application.services.system.auth.permission import PermissionService
        if PermissionService.check_permission(current_user, 'view_any_resource'):
            return fn(*args, **kwargs)

        # Get org_id from URL parameters
        org_id = kwargs.get('org_id') or kwargs.get('organisation_id')

        if not org_id:
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': 'Organisation ID not provided'
            }), 400

        # Check if user belongs to the organisation
        if str(user_org_id) != str(org_id):
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'Access denied: Not a member of this organisation'
            }), 403

        return fn(*args, **kwargs)

    return wrapper


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
#    from app.infrastructure.security.permissions import require_permission, Permissions
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
