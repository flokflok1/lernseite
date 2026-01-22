"""
Authentication & Authorization Services

Permission and role management:
- Permission checking and enforcement
- Role definition and hierarchy
- Role Studio (advanced role management)
"""

from .permission import PermissionService
from .studio import RoleStudioService

# PHASE B: RolesService removed (replaced with Groups system)

__all__ = [
    'PermissionService',
    'RoleStudioService',
]
