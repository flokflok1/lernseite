"""
Auth Repository Module

Provides repositories for authorization and permission queries.

Classes:
    - AuthorizationRepository: Hierarchy level and group queries
    - PermissionQueryRepository: Permission lookup queries (group-based)
"""

from app.infrastructure.persistence.repositories.auth.authorization import AuthorizationRepository
from app.infrastructure.persistence.repositories.auth.permission_queries import PermissionQueryRepository

__all__ = [
    'AuthorizationRepository',
    'PermissionQueryRepository',
]
