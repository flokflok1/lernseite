"""
LernsystemX - Permission System (GBA - Group-Based Architecture)

MIGRATED from RBAC 2.0 to GBA. This module now re-exports the compatibility wrapper
to maintain backward compatibility during the transition.

All permission checking now uses:
- app.application.services.system.auth.permission.PermissionService (NEW)
- core.groups, core.users_groups, core.group_permissions tables (NEW)

Legacy code should migrate to:
  from app.api.middleware.auth import permission_required
  @permission_required('admin.users:read')

ISO 27001:2013 compliant - Access Control (group-based, database-driven audit trail)
"""

# Re-export from compatibility wrapper to maintain backward compatibility during migration
from app.infrastructure.security.permissions_compat import (
    Permissions,
    require_permission,
    require_system_admin,
    require_org_admin,
    require_org_member,
    user_has_permission,
    get_user_permissions,
)

__all__ = [
    'Permissions',
    'require_permission',
    'require_system_admin',
    'require_org_admin',
    'require_org_member',
    'user_has_permission',
    'get_user_permissions',
]
