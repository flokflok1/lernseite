"""
LernsystemX Authentication Middleware

JWT-based authentication and group-based access control (GBA):
- Token verification
- User authentication
- Group-based authorization
- Permission checking

ISO 27001:2013 compliant - Access control and authentication

RBAC 3.0 - Group-Based Architecture (GBA):
Users belong to Groups, Groups have Permissions.
No more hierarchy_level or role-based checks.
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
from app.infrastructure.persistence.repositories.auth.permission_queries import PermissionQueryRepository


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
        # Skip authentication for CORS preflight requests
        # OPTIONS requests don't include Authorization headers
        if request.method == 'OPTIONS':
            return fn(*args, **kwargs)

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

            # Merge JWT claims (permissions, groups) into user dict for fast permission checks
            # The JWT contains pre-computed permissions from login, avoiding DB lookups
            jwt_claims = get_jwt()
            if 'permissions' in jwt_claims:
                user['permissions'] = jwt_claims['permissions']
            if 'groups' in jwt_claims:
                user['groups'] = jwt_claims['groups']

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
    Decorator to require admin or superadmin group membership

    Usage:
        @app.route('/admin/users')
        @admin_required
        def admin_users():
            return jsonify({'users': [...]})

    Returns:
        401 if not authenticated
        403 if user is not in admin group
    """
    @wraps(fn)
    @token_required
    def wrapper(*args, **kwargs):
        user = g.current_user
        user_id = user.get('user_id')

        # Check if user has admin permission via group membership (GBA)
        from app.application.services.system.auth.permission import PermissionService

        # Ensure user has groups populated for permission check
        # If 'groups' not in user dict, use 'role' as single group (from find_by_id)
        if 'groups' not in user and 'role' in user:
            user['groups'] = [user['role']]

        # Check if user has admin system access permission (GBA)
        # Uses admin.system:read as the baseline admin permission
        has_permission = PermissionService.check_permission(user, 'admin.system:read')

        # Fallback: If no permission via groups, check by user_id directly
        if not has_permission and user_id:
            user_perms = PermissionService.get_user_permissions(user_id)
            has_permission = 'admin.system:read' in user_perms

        if not has_permission:
            user_groups = user.get('groups', [])
            group_names = user_groups if isinstance(user_groups, list) else []

            return error_response(
                ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
                status=403,
                details={'user_groups': group_names}
            )

        return fn(*args, **kwargs)

    return wrapper


def permission_required(*permissions: str) -> Callable:
    """
    Decorator to require specific permissions via group membership (GBA)

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
        Permissions are checked via group membership (GBA):
        1. User's groups from JWT token
        2. Group permissions from core.group_permissions table
        3. Admin groups have all permissions

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

            # Admin group has all permissions (GBA)
            from app.application.services.system.auth.permission import PermissionService

            # Check if user has admin system access (bypasses specific permission checks)
            if PermissionService.check_permission(user, 'admin.system:read'):
                return fn(*args, **kwargs)

            # Check if user has ANY of the required permissions (GBA)
            has_any_permission = False
            for perm in permissions:
                if PermissionService.check_permission(user, perm):
                    has_any_permission = True
                    break

            if not has_any_permission:
                user_groups = user.get('groups', [])
                group_names = [g.get('name', 'unknown') for g in user_groups] if isinstance(user_groups, list) else []

                return error_response(
                    ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
                    status=403,
                    details={
                        'required_permissions': list(permissions),
                        'user_groups': group_names
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
            org_id = user['organisation_id']
            return jsonify({'org_id': org_id})

    Returns:
        401 if not authenticated
        403 if user is not part of any organisation
    """
    @wraps(fn)
    @token_required
    def wrapper(*args, **kwargs):
        user = g.current_user

        if not user.get('organisation_id'):
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




def can_manage_user(current_user: dict, target_user: dict) -> bool:
    """
    Check if current user can manage target user (GBA)

    Rules (Group-Based Architecture):
    - System admins can manage anyone
    - Organisation admins can manage users in their org (non-admin)
    - Teachers can manage students in their org
    - Regular users cannot manage others

    Args:
        current_user: Current user dict (with groups array from JWT)
        target_user: Target user dict (with groups array from JWT)

    Returns:
        True if current user can manage target user

    Example:
        >>> admin_groups = [{'slug': 'system-admin', ...}]
        >>> current_user = {'user_id': '1', 'groups': admin_groups, ...}
        >>> target_user = {'user_id': '2', 'groups': [{'slug': 'user', ...}], ...}
        >>> can_manage = can_manage_user(current_user, target_user)
        >>> print(can_manage)  # True
    """
    from app.application.services.system.auth.permission import PermissionService

    # Check if current user is system admin (has admin.system:read permission)
    if PermissionService.check_permission(current_user, 'admin.system:read'):
        # System admins can manage anyone except other system admins
        if PermissionService.check_permission(target_user, 'admin.system:read'):
            return False  # Admin can't manage other admins
        return True

    # Check if current user is organisation admin
    # (can manage users in their org with manage_users permission)
    if PermissionService.check_permission(current_user, 'users.manage'):
        same_org = (
            current_user.get('organisation_id') ==
            target_user.get('organisation_id')
        )
        # Can manage users who don't have system admin permission
        can_manage_target = not PermissionService.check_permission(
            target_user,
            'admin.system:read'
        )
        return same_org and can_manage_target

    # Check if current user is teacher
    # (can manage students in their org with students.manage permission)
    if PermissionService.check_permission(current_user, 'students.manage'):
        same_org = (
            current_user.get('organisation_id') ==
            target_user.get('organisation_id')
        )
        # Can manage users who don't have admin permissions
        is_admin = PermissionService.check_permission(
            target_user,
            'users.manage'
        ) or PermissionService.check_permission(target_user, 'admin.system:read')
        return same_org and not is_admin

    # Regular users cannot manage others
    return False


def get_accessible_groups(current_user: dict) -> List[dict]:
    """
    Get list of groups that a user can assign to others (GBA)

    Groups are fetched from database based on user's permissions.
    Hierarchy:
    - System admins can assign any group
    - Organisation admins can assign non-admin groups in their org
    - Teachers cannot assign groups

    Args:
        current_user: Current user dict (with groups and permissions from JWT)

    Returns:
        List of group dicts that can be assigned

    Example:
        >>> groups = get_accessible_groups(admin_user)
        >>> print(groups)  # [{'id': '...', 'name': 'user', ...}, ...]
    """
    from app.application.services.system.auth.permission import PermissionService

    # System admins can assign any group
    if PermissionService.check_permission(current_user, 'groups.manage'):
        try:
            return PermissionQueryRepository.get_all_groups()
        except Exception:
            return []

    # Organisation admins can assign non-admin groups in their org
    if PermissionService.check_permission(current_user, 'users.manage'):
        org_id = current_user.get('organisation_id')
        if org_id:
            try:
                return PermissionQueryRepository.get_org_non_role_groups(org_id)
            except Exception:
                return []

    # Regular users cannot assign groups
    return []
