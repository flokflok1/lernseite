"""
Group Repository Module

Provides repositories for group-based authorization (RBAC 3.0).

Classes:
    - GroupRepository: Core group operations (CRUD, membership)
    - GroupManagementRepository: Admin operations (batch, permissions, analytics)
    - GroupServiceQueryRepository: Helper queries for GroupManagementService
"""

from app.infrastructure.persistence.repositories.group.core import GroupRepository
from app.infrastructure.persistence.repositories.group.management import GroupManagementRepository
from app.infrastructure.persistence.repositories.group.service_queries import GroupServiceQueryRepository
from app.infrastructure.persistence.repositories.group.admin_queries import GroupAdminQueryRepository

__all__ = [
    'GroupRepository',
    'GroupManagementRepository',
    'GroupServiceQueryRepository',
    'GroupAdminQueryRepository',
]
