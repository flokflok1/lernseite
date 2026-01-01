"""
LernsystemX Security Module

Centralized security, permissions, and RBAC management.
"""

from .permissions import (
    Permissions,
    ROLE_PERMISSIONS,
    user_has_permission,
    get_user_permissions,
    require_permission,
    require_system_admin,
    require_org_admin,
    require_org_member,
)

from .rate_limit import (
    login_rate_limit,
    twofa_rate_limit,
    sensitive_endpoint_limit,
    api_rate_limit,
    BruteForceProtection,
    init_rate_limiter,
    handle_rate_limit_exceeded,
)

__all__ = [
    # Permissions
    'Permissions',
    'ROLE_PERMISSIONS',
    'user_has_permission',
    'get_user_permissions',
    'require_permission',
    'require_system_admin',
    'require_org_admin',
    'require_org_member',

    # Rate Limiting
    'login_rate_limit',
    'twofa_rate_limit',
    'sensitive_endpoint_limit',
    'api_rate_limit',
    'BruteForceProtection',
    'init_rate_limiter',
    'handle_rate_limit_exceeded',
]
