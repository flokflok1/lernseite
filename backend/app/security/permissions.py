"""
LernsystemX - Central Permission & RBAC System

Based on Dok 19 (Sicherheit & Berechtigungen) and Dok 31 (Security Architecture).

Implements:
- Permission constants
- Role-Permission mapping (RBAC Matrix)
- Permission checking decorators
- Helper functions for authorization

ISO 27001:2013 compliant - Access Control
"""

from functools import wraps
from typing import Dict, List, Set
from flask import jsonify, g
from app.middleware.auth import token_required

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
# RBAC MATRIX: ROLE → PERMISSIONS
# ==========================================

ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    # 1. Free User (Basis-Nutzer)
    'user': {
        Permissions.VIEW_OWN_ANALYTICS,
        # Kann nur eigene Daten lesen, keine besonderen Permissions
    },

    # 2. Premium User
    'premium': {
        Permissions.VIEW_OWN_ANALYTICS,
        Permissions.USE_AI_BASIC,
        Permissions.USE_AI_PREMIUM,
        Permissions.CREATE_COURSES,  # Private Kurse
        Permissions.CREATE_LIVEROOM_BASIC,
        Permissions.VIEW_TOKEN_POOL,
    },

    # 3. Creator
    'creator': {
        Permissions.VIEW_OWN_ANALYTICS,
        Permissions.USE_AI_BASIC,
        Permissions.USE_AI_PREMIUM,
        Permissions.USE_AI_PRO,
        Permissions.CREATE_COURSES,
        Permissions.MANAGE_COURSES,  # Eigene Kurse
        Permissions.PUBLISH_COURSES,  # Global Publishing
        Permissions.CREATE_AI_CONTENT,
        Permissions.CREATE_LIVEROOM_BASIC,
        Permissions.VIEW_TOKEN_POOL,
        Permissions.VIEW_BILLING,
    },

    # 4. Teacher (Lehrer/Dozent)
    'teacher': {
        Permissions.VIEW_OWN_ANALYTICS,
        Permissions.VIEW_ORG_ANALYTICS,  # Nur eigene Org
        Permissions.USE_AI_BASIC,
        Permissions.USE_AI_PREMIUM,
        Permissions.USE_AI_PRO,
        Permissions.CREATE_COURSES,
        Permissions.MANAGE_COURSES,
        Permissions.CREATE_AI_CONTENT,
        Permissions.CREATE_LIVEROOM_BASIC,
        Permissions.CREATE_LIVEROOM_PRO,
        Permissions.VIEW_TOKEN_POOL,
    },

    # 5. School Admin / Company Admin
    'school_admin': {
        Permissions.VIEW_ORG_ANALYTICS,
        Permissions.MANAGE_ORG_MEMBERS,
        Permissions.MANAGE_ORG_SETTINGS,
        Permissions.USE_AI_BASIC,
        Permissions.USE_AI_PREMIUM,
        Permissions.USE_AI_PRO,
        Permissions.CREATE_COURSES,
        Permissions.MANAGE_COURSES,
        Permissions.PUBLISH_COURSES,  # 20 Sprachen
        Permissions.CREATE_AI_CONTENT,
        Permissions.CREATE_LIVEROOM_PRO,
        Permissions.MANAGE_TOKEN_POOL,
        Permissions.MANAGE_BILLING,
    },

    'company_admin': {
        # Same as school_admin
        Permissions.VIEW_ORG_ANALYTICS,
        Permissions.MANAGE_ORG_MEMBERS,
        Permissions.MANAGE_ORG_SETTINGS,
        Permissions.USE_AI_BASIC,
        Permissions.USE_AI_PREMIUM,
        Permissions.USE_AI_PRO,
        Permissions.CREATE_COURSES,
        Permissions.MANAGE_COURSES,
        Permissions.PUBLISH_COURSES,
        Permissions.CREATE_AI_CONTENT,
        Permissions.CREATE_LIVEROOM_PRO,
        Permissions.MANAGE_TOKEN_POOL,
        Permissions.MANAGE_BILLING,
    },

    # 6. Moderator
    'moderator': {
        Permissions.VIEW_USERS,
        Permissions.VIEW_ORGANISATIONS,
        Permissions.MODERATE_CONTENT,
        Permissions.MODERATE_USERS,
        Permissions.VIEW_SYSTEM_ANALYTICS,
    },

    # 7. Support
    'support': {
        Permissions.VIEW_USERS,
        Permissions.VIEW_ORGANISATIONS,
        Permissions.VIEW_SYSTEM_ANALYTICS,
        Permissions.VIEW_SYSTEM_LOGS,
    },

    # 8. Admin
    'admin': {
        Permissions.MANAGE_USERS,
        Permissions.MODIFY_USER_ROLES,
        Permissions.MANAGE_ORGANISATIONS,
        Permissions.VIEW_ORGANISATIONS,
        Permissions.MANAGE_COURSES,
        Permissions.MODERATE_COURSES,
        Permissions.MODERATE_CONTENT,
        Permissions.MODERATE_USERS,
        Permissions.VIEW_SYSTEM_ANALYTICS,
        Permissions.VIEW_ORG_ANALYTICS,
        Permissions.MANAGE_BILLING,
        Permissions.MANAGE_TOKEN_POOL,
        Permissions.VIEW_SYSTEM_LOGS,
        Permissions.MANAGE_FEATURE_FLAGS,
        Permissions.ADMIN_SYSTEM_READ,  # Phase 22: System version/info
        Permissions.ADMIN_SYSTEM_WRITE,  # Phase 22: System configuration
        Permissions.ADMIN_USER_READ,  # Phase B24: Admin user management
        Permissions.ADMIN_USER_WRITE,  # Phase B24: Admin user management
        Permissions.ADMIN_USER_DELETE,  # Phase B24: Admin user management
        Permissions.ADMIN_COURSE_READ,  # Phase B24-02: Admin course management
        Permissions.ADMIN_COURSE_WRITE,  # Phase B24-02: Admin course management
        Permissions.ADMIN_COURSE_DELETE,  # Phase B24-02: Admin course management
        Permissions.ADMIN_LESSON_READ,  # Phase B24-04: Admin lesson management
        Permissions.ADMIN_LESSON_WRITE,  # Phase B24-04: Admin lesson management
        Permissions.ADMIN_LESSON_DELETE,  # Phase B24-04: Admin lesson management
        Permissions.ADMIN_AI_JOBS_READ,  # Phase B24-05: AI job management
        Permissions.ADMIN_AI_JOBS_WRITE,  # Phase B24-05: AI job management
        Permissions.ADMIN_AI_JOBS_EXECUTE,  # Phase B24-05: AI job management
        # Admin has most permissions except full system control
    },

    # 9. Superadmin
    'superadmin': {
        '*'  # All permissions
    }
}


# ==========================================
# PERMISSION CHECKING
# ==========================================

def user_has_permission(user: dict, permission: str) -> bool:
    """
    Check if user has a specific permission based on their role.

    Args:
        user: User dict with 'role' key
        permission: Permission string (e.g., 'admin:users')

    Returns:
        True if user has permission, False otherwise

    Example:
        >>> user = {'user_id': 123, 'role': 'admin'}
        >>> user_has_permission(user, Permissions.MANAGE_USERS)
        True
    """
    if not user or 'role' not in user:
        return False

    role = user['role']
    role_perms = ROLE_PERMISSIONS.get(role, set())

    # Superadmin has all permissions
    if '*' in role_perms:
        return True

    return permission in role_perms


def get_user_permissions(user: dict) -> Set[str]:
    """
    Get all permissions for a user based on their role.

    Args:
        user: User dict with 'role' key

    Returns:
        Set of permission strings
    """
    if not user or 'role' not in user:
        return set()

    role = user['role']
    return ROLE_PERMISSIONS.get(role, set())


# ==========================================
# DECORATORS
# ==========================================

def require_permission(permission: str):
    """
    Decorator to require a specific permission.

    Usage:
        @app.route('/admin/users')
        @require_permission(Permissions.MANAGE_USERS)
        def manage_users():
            ...

    Args:
        permission: Permission string required

    Returns:
        403 Forbidden if user doesn't have permission
    """
    def decorator(fn):
        @wraps(fn)
        @token_required
        def wrapper(*args, **kwargs):
            current_user = g.current_user

            if not user_has_permission(current_user, permission):
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
    Decorator to require system admin role (admin or superadmin).

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

        if role not in ['admin', 'superadmin']:
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'System administrator access required'
            }), 403

        return fn(*args, **kwargs)
    return wrapper


def require_org_admin(fn):
    """
    Decorator to require organisation admin role (school_admin, company_admin, or higher).

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

        # Org admins + system admins
        allowed_roles = ['school_admin', 'company_admin', 'admin', 'superadmin']

        if role not in allowed_roles:
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'Organisation administrator access required'
            }), 403

        return fn(*args, **kwargs)
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
        if current_user.get('role') in ['admin', 'superadmin']:
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
