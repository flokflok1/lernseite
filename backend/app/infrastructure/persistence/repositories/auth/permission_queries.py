"""
Permission Query Repository - Group-based permission lookups.

Provides database access for:
- User group lookups for permission resolution
- User permission aggregation across groups
- Group-to-permission mapping
- Group permission listing
"""

from typing import List, Dict, Any

from app.infrastructure.persistence.database.connection import fetch_all


class PermissionQueryRepository:
    """Repository for group-based permission queries."""

    @staticmethod
    def get_user_groups(user_id: str) -> List[Dict[str, Any]]:
        """
        Get user's groups (slug and id) for permission resolution.

        Args:
            user_id: User ID

        Returns:
            List of dicts with 'slug' and 'id' keys
        """
        return fetch_all(
            """
            SELECT g.slug, g.id
            FROM core.users_groups ug
            JOIN core.groups g ON ug.group_id = g.id
            WHERE ug.user_id = %s AND ug.deleted_at IS NULL
            """,
            (user_id,)
        ) or []

    @staticmethod
    def get_permissions_for_groups(group_ids: list) -> List[Dict[str, Any]]:
        """
        Get all distinct permission codes for a list of group IDs.

        Args:
            group_ids: List of group IDs

        Returns:
            List of dicts with 'code' key
        """
        return fetch_all(
            """
            SELECT DISTINCT p.code
            FROM core.group_permissions gp
            JOIN core.permissions p ON gp.permission_id = p.id
            WHERE gp.group_id = ANY(%s)
            """,
            (group_ids,)
        ) or []

    @staticmethod
    def get_groups_with_permission(permission_code: str) -> List[Dict[str, Any]]:
        """
        Get all groups that have a specific permission.

        Args:
            permission_code: Permission code (e.g., 'courses.edit')

        Returns:
            List of group dicts with 'id', 'slug', 'name'
        """
        return fetch_all(
            """
            SELECT DISTINCT g.id, g.slug, g.name
            FROM core.group_permissions gp
            JOIN core.permissions p ON gp.permission_id = p.id
            JOIN core.groups g ON gp.group_id = g.id
            WHERE p.code = %s AND g.deleted_at IS NULL
            ORDER BY g.name
            """,
            (permission_code,)
        ) or []

    @staticmethod
    def get_group_permission_codes(group_id: str) -> List[Dict[str, Any]]:
        """
        Get all permission codes for a specific group.

        Args:
            group_id: Group ID

        Returns:
            List of dicts with 'code' key
        """
        return fetch_all(
            """
            SELECT DISTINCT p.code
            FROM core.group_permissions gp
            JOIN core.permissions p ON gp.permission_id = p.id
            WHERE gp.group_id = %s
            """,
            (group_id,)
        ) or []
