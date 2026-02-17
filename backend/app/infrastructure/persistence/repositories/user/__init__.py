"""
User Repository Package

Modular user repository with separate concerns:
- crud.py: Create, read, search operations
- auth.py: Authentication and password management
- roles.py: Role and lifecycle management
- admin.py: Admin core operations (listing, details, groups)
- admin_part2.py: Admin moderation operations (ban, unban, delete, verify)
- profile.py: User profile preferences

Main exports for backward compatibility use UserRepository class.
For granular access, import specific modules directly.

Example (backward compatible):
    >>> from app.infrastructure.persistence.repositories.user import UserRepository
    >>> user = UserRepository.find_by_id('uuid')

Example (direct imports):
    >>> from app.infrastructure.persistence.repositories.user.crud import UserCrudRepository
    >>> from app.infrastructure.persistence.repositories.user.auth import UserAuthRepository
"""

from app.infrastructure.persistence.repositories.user.crud import UserCrudRepository
from app.infrastructure.persistence.repositories.user.auth import UserAuthRepository
from app.infrastructure.persistence.repositories.user.roles import UserRoleRepository
from app.infrastructure.persistence.repositories.user.admin import UserAdminRepository
from app.infrastructure.persistence.repositories.user.admin_part2 import UserAdminModerationRepository
from app.infrastructure.persistence.repositories.user.profile import UserProfileRepository


class UserRepository(
    UserCrudRepository,
    UserAuthRepository,
    UserRoleRepository,
    UserAdminRepository,
    UserAdminModerationRepository,
    UserProfileRepository
):
    """
    Unified UserRepository combining all functionality

    This class uses multiple inheritance to aggregate methods from specialized
    module classes. All methods are organized by domain.
    """
    pass


__all__ = [
    'UserRepository',
    'UserCrudRepository',
    'UserAuthRepository',
    'UserRoleRepository',
    'UserAdminRepository',
    'UserAdminModerationRepository',
    'UserProfileRepository',
]
