"""
LernsystemX Users Domain - Core Package

Domain-Driven Design (DDD) core for User domain.

Structure:
    - value_objects.py: UserRole, AccountStatus, UserType, PermissionScope
    - factory.py: UserFactory for aggregate creation
    - services.py: UserService for domain logic

This package contains the core domain logic following DDD principles:
- Value Objects: Immutable types representing domain concepts
- Factories: Complex object creation with business rules
- Domain Services: Stateless domain operations

ISO 27001:2013 A.9 - Access control domain implementation
Refactored: 2026-01-08 per Developer-Guide-KI Section 1 (DDD Factory Pattern)
"""

from .value_objects import (
    UserRole,
    AccountStatus,
    UserType,
    PermissionScope,
    UserId,
    Email,
    OrganisationId,
)
from .factory import UserFactory
from .services import UserService

__all__ = [
    # Value Objects
    'UserRole',
    'AccountStatus',
    'UserType',
    'PermissionScope',
    'UserId',
    'Email',
    'OrganisationId',
    # Factory
    'UserFactory',
    # Services
    'UserService',
]
