"""
Role-Based Access Control (RBAC) Module

MIGRATED from RBAC 2.0 to GBA. This module now re-exports decorators from
the compatibility wrapper to maintain backward compatibility.

All code should migrate to use:
  from app.api.middleware.auth import admin_required, permission_required
"""

# Re-export from compatibility wrapper to maintain backward compatibility
from app.infrastructure.security.permissions_compat import (
    require_owner,
    require_owner_or_permission
)

__all__ = [
    'require_owner',
    'require_owner_or_permission'
]
