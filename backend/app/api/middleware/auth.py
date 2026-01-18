"""
LernsystemX Authentication Middleware

JWT-based authentication and role-based access control (RBAC):
- Token verification
- User authentication
- Role-based authorization
- Permission checking

ISO 27001:2013 compliant - Access control and authentication
"""

from functools import wraps
from typing import Optional, Callable, List
from flask import request, jsonify, g
from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt_identity,
    get_jwt
)

from app.infrastructure.persistence.repositories.user import UserRepository
from app.infrastructure.i18n.error_codes import ErrorCode, error_response


# Role hierarchy for RBAC (RBAC 2.0 - Owner at level 10)
ROLE_HIERARCHY = {
    'user': 1,
    'premium': 2,
    'creator': 3,
    'teacher': 4,
    'school_admin': 5,
    'company_admin': 5,
    'moderator': 6,
    'support': 7,
    'admin': 8,
    'superadmin': 9,
    'owner': 10  # RBAC 2.0: Owner-Administrator (highest level)
}


def get_current_user_id() -> Optional[int]:
    """
    Get current user ID from JWT token

    Returns:
        User ID or None if not authenticated

    Example:
        >>> user_id = get_current_user_id()
        >>> if user_id:
        ...     print(f"User ID: {user_id}")
    """
    try:
        verify_jwt_in_request(optional=True)
        return get_jwt_identity()
    except Exception:
        return None


def get_current_user() -> Optional[dict]:
    """
    Get current user data from JWT token

    Returns:
        User dict or None if not authenticated

    Example:
        >>> user = get_current_user()
        >>> if user:
        ...     print(f"User: {user['email']}")
    """
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            # Check if user is already in request context
            if hasattr(g, 'current_user'):
                return g.current_user

            # Fetch user from database
            user = UserRepository.find_by_id(user_id)
            if user and user.get('is_active', True):
                g.current_user = user
                return user

        return None
    except Exception:
        return None


def token_required(fn: Callable) -> Callable:
    """
    Decorator to require valid JWT token

    Usage:
        @app.route('/protected')
        @token_required
        def protected_route():
            user = get_current_user()
            return jsonify({'message': f'Hello {user["email"]}'})

    Returns:
        401 if token is missing or invalid
        403 if user is inactive
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # Verify JWT token
            verify_jwt_in_request()

            # Get user ID from token
            user_id = get_jwt_identity()
            if not user_id:
                return error_response(ErrorCode.AUTH_TOKEN_INVALID, status=401)

            # Fetch user from database
            user = UserRepository.find_by_id(user_id)
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, status=401)

            # Check if user is active
            if not user.get('is_active', True):
                return error_response(ErrorCode.AUTH_ACCOUNT_DISABLED, status=403)

            # Store user in request context
            g.current_user = user

            return fn(*args, **kwargs)

        except Exception as e:
            return error_response(ErrorCode.AUTH_TOKEN_INVALID, status=401)

    return wrapper


def role_required(*allowed_roles: str) -> Callable:
    """
    Decorator to require specific roles

    Args:
        *allowed_roles: One or more allowed roles

    Usage:
        @app.route('/admin')
        @role_required('admin', 'superadmin')
        def admin_route():
            return jsonify({'message': 'Admin area'})

    Returns:
        401 if not authenticated
        403 if user doesn't have required role
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        @token_required
        def wrapper(*args, **kwargs):
            user = g.current_user
            user_role = user.get('role', 'user')

            # Check if user has one of the allowed roles
            if user_role not in allowed_roles:
                return error_response(
                    ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
                    status=403,
                    details={
                        'required_roles': list(allowed_roles),
                        'user_role': user_role
                    }
                )

            return fn(*args, **kwargs)

        return wrapper
    return decorator


def admin_required(fn: Callable) -> Callable:
    """
    Decorator to require admin or superadmin role

    Usage:
        @app.route('/admin/users')
        @admin_required
        def admin_users():
            return jsonify({'users': [...]})

    Returns:
        401 if not authenticated
        403 if user is not admin/superadmin
    """
    @wraps(fn)
    @token_required
    def wrapper(*args, **kwargs):
        user = g.current_user
        user_role = user.get('role', 'user')

        # Check if user is admin or above (RBAC 2.0: dynamic from DB)
        from app.application.services.permission_service import PermissionService
        if not PermissionService.check_threshold(user, 'view_any_resource'):
            return error_response(
                ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
                status=403,
                details={'user_role': user_role}
            )

        return fn(*args, **kwargs)

    return wrapper


def permission_required(*permissions: str) -> Callable:
    """
    Decorator to require specific permissions (checks against database)

    Args:
        *permissions: One or more required permissions (ANY match = access granted)

    Usage:
        @app.route('/courses/publish')
        @permission_required('courses.publish')
        def publish_course():
            return jsonify({'message': 'Course published'})

        # Multiple permissions (user needs ANY of these)
        @app.route('/i18n/moderate')
        @permission_required('i18n.moderate', 'i18n.edit')
        def moderate_translations():
            return jsonify({'message': 'Moderating...'})

    Note:
        Permissions are checked against:
        1. User-specific overrides (user_permissions table)
        2. Role-based permissions (role_permissions table)
        3. Admin role has all permissions

    Returns:
        401 if not authenticated
        403 if user doesn't have required permissions
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        @token_required
        def wrapper(*args, **kwargs):
            user = g.current_user
            user_id = user.get('user_id')
            user_role = user.get('role', 'user')

            # Admin and above has all permissions (RBAC 2.0: dynamic from DB)
            from app.application.services.permission_service import PermissionService
            if PermissionService.check_threshold(user, 'view_any_resource'):
                return fn(*args, **kwargs)

            # Check permissions against database
            from app.infrastructure.persistence.repositories.base_repository import BaseRepository

            has_any_permission = False
            for perm in permissions:
                try:
                    result = BaseRepository.fetch_one(
                        "SELECT user_has_permission(%s, %s) as has_perm",
                        (user_id, perm)
                    )
                    if result and result.get('has_perm'):
                        has_any_permission = True
                        break
                except Exception:
                    # If DB function doesn't exist, fall back to role hierarchy
                    role_level = ROLE_HIERARCHY.get(user_role, 0)
                    has_any_permission = role_level >= 5
                    break

            if not has_any_permission:
                return error_response(
                    ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
                    status=403,
                    details={
                        'required_permissions': list(permissions),
                        'user_role': user_role
                    }
                )

            return fn(*args, **kwargs)

        return wrapper
    return decorator


def organisation_member_required(fn: Callable) -> Callable:
    """
    Decorator to require user to be member of an organisation

    Usage:
        @app.route('/org/courses')
        @organisation_member_required
        def org_courses():
            user = get_current_user()
            org_id = user['organization_id']
            return jsonify({'org_id': org_id})

    Returns:
        401 if not authenticated
        403 if user is not part of any organisation
    """
    @wraps(fn)
    @token_required
    def wrapper(*args, **kwargs):
        user = g.current_user

        if not user.get('organization_id'):
            return error_response(
                ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
                status=403,
                details={'reason': 'organisation_membership_required'}
            )

        return fn(*args, **kwargs)

    return wrapper


def rate_limit_check(max_requests: int = 100, window_seconds: int = 60) -> Callable:
    """
    Decorator for custom rate limiting

    Args:
        max_requests: Maximum requests allowed
        window_seconds: Time window in seconds

    Usage:
        @app.route('/api/expensive')
        @rate_limit_check(max_requests=10, window_seconds=60)
        def expensive_endpoint():
            return jsonify({'data': '...'})

    Note:
        This is a placeholder. Actual implementation should use
        Redis or Flask-Limiter for distributed rate limiting.

    Returns:
        429 if rate limit exceeded
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # TODO: Implement actual rate limiting with Redis
            # For now, just pass through
            return fn(*args, **kwargs)

        return wrapper
    return decorator


def check_role_hierarchy(user_role: str, target_role: str) -> bool:
    """
    Check if user role is higher or equal to target role

    Args:
        user_role: Current user's role
        target_role: Target role to check against

    Returns:
        True if user_role >= target_role in hierarchy

    Example:
        >>> is_allowed = check_role_hierarchy('admin', 'teacher')
        >>> print(is_allowed)  # True

        >>> is_allowed = check_role_hierarchy('teacher', 'admin')
        >>> print(is_allowed)  # False
    """
    user_level = ROLE_HIERARCHY.get(user_role, 0)
    target_level = ROLE_HIERARCHY.get(target_role, 0)
    return user_level >= target_level


def can_manage_user(current_user: dict, target_user: dict) -> bool:
    """
    Check if current user can manage target user

    Rules:
    - Superadmin can manage anyone
    - Admin can manage non-admins
    - Organisation admins can manage users in their org
    - Teachers can manage students in their org
    - Users cannot manage others

    Args:
        current_user: Current user dict
        target_user: Target user dict

    Returns:
        True if current user can manage target user

    Example:
        >>> can_manage = can_manage_user(admin_user, student_user)
        >>> print(can_manage)  # True
    """
    # Use hierarchy_level for dynamic permission checking (RBAC 2.0)
    current_hierarchy = current_user.get('hierarchy_level', 1)
    target_hierarchy = target_user.get('hierarchy_level', 1)
    current_role = current_user.get('role', 'user')
    target_role = target_user.get('role', 'user')

    # Users can only manage users with LOWER hierarchy
    # (Admin hierarchy 8 can manage up to 7, Owner hierarchy 10 can manage all)
    if current_hierarchy > target_hierarchy:
        return True

    # Organisation admins can manage users in their organisation (RBAC 2.0)
    # hierarchy_level 5 = school_admin, company_admin
    if current_hierarchy == 5:
        same_org = (
            current_user.get('organization_id') ==
            target_user.get('organization_id')
        )
        # Can manage users with hierarchy <= 4 (user, premium, creator, teacher)
        can_manage_hierarchy = target_hierarchy <= 4
        return same_org and can_manage_hierarchy

    # Teachers can manage students in their organisation (RBAC 2.0)
    # hierarchy_level 4 = teacher
    if current_hierarchy == 4:
        same_org = (
            current_user.get('organization_id') ==
            target_user.get('organization_id')
        )
        # Can manage users with hierarchy <= 2 (user, premium)
        can_manage_hierarchy = target_hierarchy <= 2
        return same_org and can_manage_hierarchy

    # Regular users cannot manage others
    return False


def get_accessible_roles(user_role: str) -> List[str]:
    """
    Get list of roles that a user can assign to others

    Args:
        user_role: Current user's role

    Returns:
        List of roles that can be assigned

    Example:
        >>> roles = get_accessible_roles('admin')
        >>> print(roles)  # ['user', 'premium', 'creator', 'teacher', ...]
    """
    role_permissions = {
        'superadmin': [
            'user', 'premium', 'creator', 'teacher',
            'school_admin', 'company_admin', 'moderator',
            'support', 'admin', 'superadmin'
        ],
        'admin': [
            'user', 'premium', 'creator', 'teacher',
            'school_admin', 'company_admin', 'moderator', 'support'
        ],
        'school_admin': ['user', 'premium', 'teacher'],
        'company_admin': ['user', 'premium', 'teacher', 'creator'],
        'teacher': ['user', 'premium'],
    }

    return role_permissions.get(user_role, [])
