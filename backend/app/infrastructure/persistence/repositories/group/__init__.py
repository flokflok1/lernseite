"""
Group Repository Module

Provides repositories for group-based authorization (RBAC 3.0).

Classes:
    - GroupRepository: Core group operations (CRUD, membership)
    - GroupManagementRepository: Admin operations (batch, permissions, analytics)
"""

from app.infrastructure.persistence.repositories.group.core import GroupRepository
from app.infrastructure.persistence.repositories.group.management import GroupManagementRepository

__all__ = [
    'GroupRepository',
    'GroupManagementRepository',
]
