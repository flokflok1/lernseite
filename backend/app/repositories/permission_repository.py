"""
Permission Repository - Database-driven Permission Checking

RBAC 2.0: Uses PostgreSQL functions instead of hardcoded role matrices.
Queries core.role_permissions and core.user_permissions tables.

This replaces the old hardcoded ROLE_PERMISSIONS dictionary in permissions.py.
All permission checks now use database-stored role-permission relationships.
"""

from typing import Optional, Set
from app.repositories.base_repository import BaseRepository
from app.database.connection import fetch_one, fetch_all


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

    @classmethod
    def get_role_permissions(cls, role_id: int) -> Set[str]:
        """
        Get all permissions assigned to a specific role.

        Args:
            role_id: ID of the role

        Returns:
            Set of permission keys assigned to this role

        Example:
            >>> perms = PermissionRepository.get_role_permissions(role_id=9)  # admin
            >>> 'admin:users' in perms
            True
        """
        try:
            results = fetch_all(
                """
                SELECT DISTINCT p.permission_key
                FROM core.role_permissions rp
                JOIN core.permissions p ON rp.permission_id = p.permission_id
                WHERE rp.role_id = %s
                ORDER BY p.permission_key
                """,
                (role_id,)
            )
            return {row.get('permission_key') for row in results if row}
        except Exception as e:
            import logging
            logging.error(f"Error fetching permissions for role {role_id}: {e}")
            return set()

    @classmethod
    def assign_permission_to_role(cls, role_id: int, permission_key: str) -> bool:
        """
        Assign a permission to a role.

        Args:
            role_id: ID of the role
            permission_key: Key of the permission to assign

        Returns:
            True if assigned successfully, False otherwise
        """
        try:
            from app.database.connection import execute_query

            result = execute_query(
                """
                INSERT INTO core.role_permissions (role_id, permission_id)
                SELECT %s, permission_id FROM core.permissions
                WHERE permission_key = %s
                ON CONFLICT DO NOTHING
                """,
                (role_id, permission_key)
            )
            return True
        except Exception as e:
            import logging
            logging.error(
                f"Error assigning permission {permission_key} to role {role_id}: {e}"
            )
            return False

    @classmethod
    def revoke_permission_from_role(cls, role_id: int, permission_key: str) -> bool:
        """
        Revoke a permission from a role.

        Args:
            role_id: ID of the role
            permission_key: Key of the permission to revoke

        Returns:
            True if revoked successfully, False otherwise
        """
        try:
            from app.database.connection import execute_query

            execute_query(
                """
                DELETE FROM core.role_permissions
                WHERE role_id = %s AND permission_id = (
                    SELECT permission_id FROM core.permissions
                    WHERE permission_key = %s
                )
                """,
                (role_id, permission_key)
            )
            return True
        except Exception as e:
            import logging
            logging.error(
                f"Error revoking permission {permission_key} from role {role_id}: {e}"
            )
            return False

