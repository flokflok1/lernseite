"""
Group Service Query Repository - Helper queries for GroupManagementService.

Provides entity-existence checks and permission assignment queries
used by the group management service layer.

These queries were extracted from app/application/services/system/group_management/
to enforce DDD repository boundaries (no SQL in services).
"""

from typing import Optional, Dict

from app.infrastructure.persistence.database.connection import fetch_one, execute_query


class GroupServiceQueryRepository:
    """Helper queries used by GroupManagementService."""

    @staticmethod
    def count_group_members(group_id: str) -> Optional[Dict]:
        """
        Count members in a group.

        Args:
            group_id: Group ID

        Returns:
            Dict with 'count' key, or None
        """
        return fetch_one(
            "SELECT COUNT(*) as count FROM core.users_groups WHERE group_id = %s",
            (group_id,)
        )

    @staticmethod
    def user_exists(user_id: str) -> Optional[Dict]:
        """
        Check if a user exists by user_id.

        Args:
            user_id: User ID (UUID)

        Returns:
            Dict with 'user_id' key if found, None otherwise
        """
        return fetch_one(
            "SELECT user_id FROM core.users WHERE user_id = %s",
            (user_id,)
        )

    @staticmethod
    def user_exists_by_id(user_id: str) -> Optional[Dict]:
        """
        Check if a user exists by id column.

        Args:
            user_id: User ID

        Returns:
            Dict with 'id' key if found, None otherwise
        """
        return fetch_one(
            "SELECT id FROM core.users WHERE id = %s",
            (user_id,)
        )

    @staticmethod
    def organisation_exists(organisation_id: str) -> Optional[Dict]:
        """
        Check if an organisation exists.

        Args:
            organisation_id: Organisation ID (UUID)

        Returns:
            Dict with 'id' key if found, None otherwise
        """
        return fetch_one(
            "SELECT id FROM organisations.organisations WHERE organisation_id = %s",
            (organisation_id,)
        )

    @staticmethod
    def admin_permissions_exist() -> Optional[Dict]:
        """
        Check if admin-level permissions exist (hierarchy_level >= 3).

        Returns:
            Dict with 'id' of first matching permission, or None
        """
        return fetch_one(
            """
            SELECT id FROM core.permissions
            WHERE required_hierarchy_level >= 3
            ORDER BY code
            """
        )

    @staticmethod
    def assign_admin_permissions_to_group(
        group_id: str,
        assigned_by: Optional[str]
    ) -> None:
        """
        Assign all admin-level permissions to a group.

        Inserts permissions where required_hierarchy_level >= 3.
        Uses ON CONFLICT to skip already-assigned permissions.

        Args:
            group_id: Group ID to assign permissions to
            assigned_by: User ID who is granting the permissions
        """
        execute_query(
            """
            INSERT INTO core.group_permissions (group_id, permission_id, granted_by)
            SELECT %s, id, %s FROM core.permissions
            WHERE required_hierarchy_level >= 3
            ON CONFLICT (group_id, permission_id) DO NOTHING
            """,
            (group_id, assigned_by)
        )
