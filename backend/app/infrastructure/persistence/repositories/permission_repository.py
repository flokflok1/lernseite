"""
Permission Repository - Database-driven Permission Checking

Uses PostgreSQL functions for permission checking.
All permission checks use database-stored permission relationships via PostgreSQL functions.

PHASE B: Removed role-based methods (get_role_permissions, assign_permission_to_role,
revoke_permission_from_role) that queried deleted core.role_permissions table.
Now uses group-based authorization model.
"""

from typing import Optional, Set
from app.infrastructure.persistence.repositories.base_repository import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all


class PermissionRepository(BaseRepository):
    """
    Repository for permission checking using database functions.

    Implements database-driven RBAC without hardcoded role matrices.
    """

    @classmethod
    def user_has_permission(cls, user_id: str, permission_key: str) -> bool:
        """
        Check if user has a specific permission.

        Uses PostgreSQL function `user_has_permission()` which checks:
        1. User-specific overrides (grants/denials)
        2. Role-based permissions from role_permissions table
        3. Owner and Admin roles get all permissions

        Args:
            user_id: UUID of the user to check
            permission_key: Permission key (e.g., 'admin:users', 'courses.edit')

        Returns:
            True if user has permission, False otherwise

        Example:
            >>> PermissionRepository.user_has_permission(
            ...     user_id='550e8400-e29b-41d4-a716-446655440000',
            ...     permission_key='admin:users'
            ... )
            True
        """
        try:
            result = fetch_one(
                "SELECT user_has_permission(%s, %s) as has_permission",
                (user_id, permission_key)
            )
            return result.get('has_permission', False) if result else False
        except Exception as e:
            # Log error but fail-secure: deny access on error
            import logging
            logging.error(
                f"Error checking permission {permission_key} for user {user_id}: {e}"
            )
            return False

    @classmethod
    def get_user_permissions(cls, user_id: str) -> Set[str]:
        """
        Get all permissions a user has (via role + overrides).

        Uses PostgreSQL function `get_user_permissions()` which returns:
        - All permissions from user's role
        - Plus any user-specific permission overrides
        - Owner and Admin get all available permissions

        Args:
            user_id: UUID of the user

        Returns:
            Set of permission keys (e.g., {'admin:users', 'courses.edit', ...})

        Example:
            >>> perms = PermissionRepository.get_user_permissions(
            ...     user_id='550e8400-e29b-41d4-a716-446655440000'
            ... )
            >>> 'admin:users' in perms
            True
        """
        try:
            results = fetch_all(
                "SELECT permission_key FROM get_user_permissions(%s)",
                (user_id,)
            )
            return {row.get('permission_key') for row in results if row}
        except Exception as e:
            # Log error but fail-secure: return empty set on error
            import logging
            logging.error(f"Error fetching permissions for user {user_id}: {e}")
            return set()

    # PHASE B: Removed role-based methods (get_role_permissions, assign_permission_to_role,
    # revoke_permission_from_role) that queried deleted core.role_permissions table.
    # These are no longer needed in group-based authorization model.

