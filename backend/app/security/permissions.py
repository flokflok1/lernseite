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
    Decorator to require system admin role (admin, superadmin, or owner).

    RBAC 2.0: Also accepts users with hierarchy_level >= 9.

    Usage:
        @app.route('/admin/system')
        @require_system_admin
        def system_settings():
            ...
    """
    @wraps(fn)
    @token_required
    def wrapper(*args, **kwargs):
        current_user = g.current_user
        role = current_user.get('role')
        hierarchy_level = current_user.get('hierarchy_level', 0)

        # RBAC 2.0: Allow by hierarchy_level OR role
        if role in ['admin', 'superadmin', 'owner'] or hierarchy_level >= 9:
            return fn(*args, **kwargs)

        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'System administrator access required'
        }), 403

    return wrapper


def require_org_admin(fn):
    """
    Decorator to require organisation admin role (school_admin, company_admin, or higher).

    RBAC 2.0: Also accepts users with hierarchy_level >= 5.

    Usage:
        @app.route('/organisations/<org_id>/settings')
        @require_org_admin
        def org_settings(org_id):
            ...
    """
    @wraps(fn)
    @token_required
    def wrapper(*args, **kwargs):
        current_user = g.current_user
        role = current_user.get('role')
        hierarchy_level = current_user.get('hierarchy_level', 0)

        # Org admins + system admins
        allowed_roles = ['school_admin', 'company_admin', 'admin', 'superadmin', 'owner']

        # RBAC 2.0: Allow by hierarchy_level OR role
        if role in allowed_roles or hierarchy_level >= 5:
            return fn(*args, **kwargs)

        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'Organisation administrator access required'
        }), 403

    return wrapper


def require_org_member(fn):
    """
    Decorator to check if user is member of an organisation.

    Checks if user has organization_id set and matches the org_id parameter.

    Usage:
        @app.route('/organisations/<org_id>/courses')
        @require_org_member
        def org_courses(org_id):
            ...
    """
    @wraps(fn)
    @token_required
    def wrapper(*args, **kwargs):
        current_user = g.current_user
        user_org_id = current_user.get('organization_id')

        # System admins can access any org
        if current_user.get('role') in ['admin', 'superadmin', 'owner']:
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
