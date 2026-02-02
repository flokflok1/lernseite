"""
System Services Layer

Core system infrastructure services:
- Authentication & Authorization (auth/)
- Audit logging and compliance (audit/)
- File management and context (files/)
- Group Management (group_management/) - RBAC 3.0 group-based authorization
"""

from app.application.services.system.auth import (
    PermissionService,
)
from app.application.services.system.audit import AuditService
from app.application.services.system.group_management import GroupManagementService

# PHASE B: RolesService removed (replaced with Groups system)

__all__ = [
    'PermissionService',
    'AuditService',
    'GroupManagementService',
]
