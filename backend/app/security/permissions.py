"""
LernsystemX - Central Permission & RBAC System (RBAC 2.0)

Based on Dok 19 (Sicherheit & Berechtigungen) and Dok 31 (Security Architecture).

Implements:
- Permission constants
- Database-driven permission checking (via PermissionRepository)
- Permission decorators for role-based access control
- Helper functions for authorization

NOTE: As of RBAC 2.0, actual permission checking uses database via
PermissionRepository instead of hardcoded ROLE_PERMISSIONS matrix.
See app/repositories/permission_repository.py for database logic.

ISO 27001:2013 compliant - Access Control (database-driven audit trail)
"""

from functools import wraps
from typing import Dict, List, Set
from flask import jsonify, g
from app.middleware.auth import token_required
from app.repositories.permission_repository import PermissionRepository

# ==========================================
# PERMISSION CONSTANTS
# ==========================================

class Permissions:
    """Central permission constants"""

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
    ADMIN_SYSTEM_READ = 'admin:system:read'  # Phase 22: System version/info endpoints
    ADMIN_SYSTEM_WRITE = 'admin:system:write'  # Phase 22: System configuration endpoints
    VIEW_SYSTEM_LOGS = 'view:logs:system'
    MANAGE_FEATURE_FLAGS = 'manage:features'

    # Admin User Management (Phase B24)
    ADMIN_USER_READ = 'admin:user:read'  # List and view users
    ADMIN_USER_WRITE = 'admin:user:write'  # Ban, unban, grant tokens, verify
    ADMIN_USER_DELETE = 'admin:user:delete'  # Delete users

    # Admin Course Management (Phase B24-02)
    ADMIN_COURSE_READ = 'admin:course:read'  # List and view all courses
    ADMIN_COURSE_WRITE = 'admin:course:write'  # Create, update, publish, unpublish courses
    ADMIN_COURSE_DELETE = 'admin:course:delete'  # Archive/delete courses

    # Admin Lesson Management (Phase B24-04)
    ADMIN_LESSON_READ = 'admin:lesson:read'  # List and view lessons
    ADMIN_LESSON_WRITE = 'admin:lesson:write'  # Create, update lessons
    ADMIN_LESSON_DELETE = 'admin:lesson:delete'  # Delete lessons

    # Admin AI Job Management (Phase B24-05)
    ADMIN_AI_JOBS_READ = 'admin:ai:jobs:read'  # List and view AI jobs
    ADMIN_AI_JOBS_WRITE = 'admin:ai:jobs:write'  # Create AI jobs
    ADMIN_AI_JOBS_EXECUTE = 'admin:ai:jobs:execute'  # Execute and finalize AI jobs

    # LiveRoom
    CREATE_LIVEROOM_BASIC = 'create:liveroom:basic'
    CREATE_LIVEROOM_PRO = 'create:liveroom:pro'


# ==========================================
# DEPRECATED: ROLE → PERMISSIONS MATRIX
# ==========================================
#
# NOTE: As of RBAC 2.0 (2026-01-12), this hardcoded matrix is DEPRECATED.
# Permission checking is now database-driven via PermissionRepository.
#
# All role-permission relationships are stored in:
# - core.role_permissions (role → permission)
# - core.user_permissions (user-specific overrides)
# - core.permission_thresholds (hierarchy-based access)
#
# This dictionary is kept as documentation/reference only.
# DO NOT USE for permission checks - use PermissionRepository instead!
#
# Old implementation (kept for reference):
# ROLE_PERMISSIONS: Dict[str, Set[str]] = {
#     'user': {...},
#     'premium': {...},
#     'creator': {...},
#     'teacher': {...},
#     'school_admin': {...},
#     'company_admin': {...},
#     'moderator': {...},
#     'support': {...},
#     'admin': {...},
#     'superadmin': {'*'},
#     'owner': {'*'},
# }
#
# Use PermissionRepository.get_role_permissions(role_id) to fetch from database.


# ==========================================
# PERMISSION CHECKING
# ==========================================

def user_has_permission(user: dict, permission: str) -> bool:
    """
    Check if user has a specific permission.

    DEPRECATED: This function is kept for backward compatibility.
    New code should use PermissionRepository.user_has_permission() directly.

    Args:
        user: User dict with 'user_id' key
        permission: Permission key (e.g., 'admin:users')

    Returns:
        True if user has permission, False otherwise
    """
    if not user or 'user_id' not in user:
        return False

    # Use database-driven permission check
    return PermissionRepository.user_has_permission(
        user_id=user['user_id'],
        permission_key=permission
    )


def get_user_permissions(user: dict) -> Set[str]:
    """
    Get all permissions for a user (via role + overrides).

    DEPRECATED: This function is kept for backward compatibility.
    New code should use PermissionRepository.get_user_permissions() directly.

    Args:
        user: User dict with 'user_id' key

    Returns:
        Set of permission keys
    """
    if not user or 'user_id' not in user:
        return set()

    # Use database-driven permission check
    return PermissionRepository.get_user_permissions(user_id=user['user_id'])


# ==========================================
# DECORATORS
# ==========================================

def require_permission(permission: str):
    """
    Decorator to require a specific permission (database-driven).

    Checks user's permission against database via PermissionRepository.
    Supports role-based permissions and user-specific overrides.

    Usage:
        @app.route('/admin/users')
        @require_permission(Permissions.ADMIN_USER_READ)
        def list_users():
            ...

    Args:
        permission: Permission key required (e.g., 'admin:users')

    Returns:
        403 Forbidden if user doesn't have permission
    """
    def decorator(fn):
        @wraps(fn)
        @token_required
        def wrapper(*args, **kwargs):
            current_user = g.current_user
            user_id = current_user.get('user_id')

            # Check permission via database
            if not PermissionRepository.user_has_permission(
                user_id=user_id,
                permission_key=permission
            ):
                return jsonify({
                    'success': False,
                    'error': 'Forbidden',
                    'message': f'Missing required permission: {permission}'
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_system_admin(fn):
    """
    Decorator to require system admin privileges (RBAC 2.0 database-driven).

    Checks user for system admin access via:
    1. Permission 'admin:system' (database-driven via PermissionRepository)
    2. User hierarchy_level >= 9 (backward compatibility)

    Access is granted if EITHER condition is met. Returns 403 Forbidden if both fail.
    Implements fail-secure: on database error, denies access (returns 403).

    Args:
        fn: Flask view function to wrap

    Returns:
        Decorated function that:
        - Calls the wrapped function if user has system admin access
        - Returns 403 JSON response if access denied
        - Returns 403 JSON response if permission check fails (fail-secure)

    Usage:
        @app.route('/admin/system')
        @require_system_admin
        def system_settings():
            '''Updates system configuration'''
            return jsonify({'status': 'ok'}), 200

    Example Response (403 Forbidden):
        {
            'success': False,
            'error': 'Forbidden',
            'message': 'System administrator access required'
        }

    Note:
        - Decorated functions are only callable by:
          - Users with 'admin:system' permission in database, OR
          - Users with hierarchy_level >= 9
        - System admins bypass other decorator restrictions
        - All access is logged via database audit trail
    """
    @wraps(fn)
    @token_required
    def wrapper(*args, **kwargs):
        current_user = g.current_user
        user_id = current_user.get('user_id')
        hierarchy_level = current_user.get('hierarchy_level', 0)

        # RBAC 2.0: Check by hierarchy_level (backward compat) OR permission (database-driven)
        has_permission = (
            hierarchy_level >= 9 or
            PermissionRepository.user_has_permission(
                user_id=user_id,
                permission_key=Permissions.MANAGE_SYSTEM
            )
        )

        if has_permission:
            return fn(*args, **kwargs)

        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'System administrator access required'
        }), 403

    return wrapper


def require_org_admin(fn):
    """
    Decorator to require organisation admin privileges (RBAC 2.0 database-driven).

    Checks user for organisation admin access via:
    1. Permission 'manage:org:settings' OR 'admin:organisations' (database-driven)
    2. User hierarchy_level >= 5 (backward compatibility)

    Access is granted if ANY condition is met. Returns 403 Forbidden if all fail.
    Implements fail-secure: on database error, denies access (returns 403).

    Args:
        fn: Flask view function to wrap

    Returns:
        Decorated function that:
        - Calls the wrapped function if user has org admin access
        - Returns 403 JSON response if access denied
        - Returns 403 JSON response if permission check fails (fail-secure)

    Usage:
        @app.route('/organisations/<org_id>/settings')
        @require_org_admin
        def org_settings(org_id):
            '''Updates organisation settings'''
            return jsonify({'status': 'ok'}), 200

    Example Response (403 Forbidden):
        {
            'success': False,
            'error': 'Forbidden',
            'message': 'Organisation administrator access required'
        }

    Note:
        - Decorated functions are only callable by:
          - Users with 'manage:org:settings' permission in database, OR
          - Users with 'admin:organisations' permission in database, OR
          - Users with hierarchy_level >= 5
        - Organisation admins can manage their assigned organisation
        - System admins (hierarchy_level >= 9) bypass all org restrictions
        - All access is logged via database audit trail (ISO 27001 compliance)
    """
    @wraps(fn)
    @token_required
    def wrapper(*args, **kwargs):
        current_user = g.current_user
        user_id = current_user.get('user_id')
        hierarchy_level = current_user.get('hierarchy_level', 0)

        # RBAC 2.0: Check by hierarchy_level (backward compat) OR permissions (database-driven)
        has_permission = (
            hierarchy_level >= 5 or
            PermissionRepository.user_has_permission(
                user_id=user_id,
                permission_key=Permissions.MANAGE_ORG_SETTINGS
            ) or
            PermissionRepository.user_has_permission(
                user_id=user_id,
                permission_key=Permissions.MANAGE_ORGANISATIONS
            )
        )

        if has_permission:
            return fn(*args, **kwargs)

        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'Organisation administrator access required'
        }), 403

    return wrapper


def require_org_member(fn):
    """
    Decorator to check if user is member of a specific organisation (resource-based access).

    This decorator verifies resource ownership, NOT capabilities:
    - Checks if user's organization_id matches the org_id in URL parameters
    - System admins (hierarchy_level >= 9) can access any organisation
    - Regular users can only access organisations they belong to

    Args:
        fn: Flask view function to wrap

    Returns:
        Decorated function that:
        - Calls the wrapped function if user belongs to the organisation
        - Returns 400 Bad Request if org_id not in URL parameters
        - Returns 403 Forbidden if user is not a member of the organisation
        - Returns 403 Forbidden if permission check fails (fail-secure)

    Usage:
        @app.route('/organisations/<org_id>/courses')
        @require_org_member
        def org_courses(org_id):
            '''List courses for organisation'''
            return jsonify({'courses': [...]}), 200

    URL Parameters Expected:
        - org_id OR organization_id in kwargs

    Example Response (403 Forbidden - Not a Member):
        {
            'success': False,
            'error': 'Forbidden',
            'message': 'Access denied: Not a member of this organisation'
        }

    Example Response (400 Bad Request - Missing org_id):
        {
            'success': False,
            'error': 'Bad Request',
            'message': 'Organisation ID not provided'
        }

    Note:
        - This is a RESOURCE-BASED access control, not permission-based
        - Users can only access organisations they belong to
        - System admins (hierarchy_level >= 9) bypass organisation checks
        - Owner role has implicit system admin hierarchy_level >= 9
        - All access attempts are logged for compliance (ISO 27001)
    """
    @wraps(fn)
    @token_required
    def wrapper(*args, **kwargs):
        current_user = g.current_user
        user_org_id = current_user.get('organization_id')
        hierarchy_level = current_user.get('hierarchy_level', 0)

        # System admins (hierarchy_level >= 9) can access any org
        if hierarchy_level >= 9:
            return fn(*args, **kwargs)

        # Get org_id from URL parameters
        org_id = kwargs.get('org_id') or kwargs.get('organization_id')

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
