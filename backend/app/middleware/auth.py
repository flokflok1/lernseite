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

from app.repositories.user import UserRepository


# Role hierarchy for RBAC
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
    'superadmin': 9
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
                return jsonify({
                    'success': False,
                    'error': 'Invalid token',
                    'message': 'User ID not found in token'
                }), 401

            # Fetch user from database
            user = UserRepository.find_by_id(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found',
                    'message': 'User associated with token does not exist'
                }), 401

            # Check if user is active
            if not user.get('is_active', True):
                return jsonify({
                    'success': False,
                    'error': 'Account deactivated',
                    'message': 'Your account has been deactivated'
                }), 403

            # Store user in request context
            g.current_user = user

            return fn(*args, **kwargs)

        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Authentication failed',
                'message': str(e)
            }), 401

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
                return jsonify({
                    'success': False,
                    'error': 'Insufficient permissions',
                    'message': f'This endpoint requires one of these roles: {", ".join(allowed_roles)}',
                    'required_roles': list(allowed_roles),
                    'user_role': user_role
                }), 403

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

        # Check if user is admin or superadmin
        if user_role not in ['admin', 'superadmin']:
            return jsonify({
                'success': False,
                'error': 'Admin access required',
                'message': 'This endpoint requires admin or superadmin privileges',
                'user_role': user_role
            }), 403

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

            # Admin/Superadmin has all permissions
            if user_role in ('admin', 'superadmin'):
                return fn(*args, **kwargs)

            # Check permissions against database
            from app.repositories.base_repository import BaseRepository

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
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'FORBIDDEN',
                        'message': 'Insufficient permissions',
                        'required_permissions': list(permissions),
                        'user_role': user_role
                    }
                }), 403

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
            return jsonify({
                'success': False,
                'error': 'Organisation membership required',
                'message': 'This endpoint requires you to be part of an organisation'
            }), 403

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
    current_role = current_user.get('role', 'user')
    target_role = target_user.get('role', 'user')

    # Superadmin can manage anyone
    if current_role == 'superadmin':
        return True

    # Admin can manage non-admins and non-superadmins
    if current_role == 'admin':
        return target_role not in ['admin', 'superadmin']

    # Organisation admins can manage users in their organisation
    if current_role in ['school_admin', 'company_admin']:
        same_org = (
            current_user.get('organization_id') ==
            target_user.get('organization_id')
        )
        can_manage_role = target_role in [
            'user', 'premium', 'teacher', 'creator'
        ]
        return same_org and can_manage_role

    # Teachers can manage students in their organisation
    if current_role == 'teacher':
        same_org = (
            current_user.get('organization_id') ==
            target_user.get('organization_id')
        )
        can_manage_role = target_role in ['user', 'premium']
        return same_org and can_manage_role

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
