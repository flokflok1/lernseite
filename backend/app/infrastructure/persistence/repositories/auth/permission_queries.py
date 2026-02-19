"""
Permission Query Repository - Group-based permission lookups.

Provides database access for:
- User group lookups for permission resolution
- User permission aggregation across groups
- Group-to-permission mapping
- Group permission listing
"""

from typing import Optional, List, Dict, Any

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query


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

    # =====================================================
    # Permission Threshold Queries
    # =====================================================

    @staticmethod
    def get_threshold_by_key(permission_key: str) -> Optional[Dict]:
        """Get a specific permission threshold by key."""
        return fetch_one(
            """
            SELECT
                threshold_id,
                permission_key,
                min_hierarchy_level,
                description,
                is_active,
                created_at,
                updated_at
            FROM core.permission_thresholds
            WHERE permission_key = %s
            """,
            (permission_key,)
        )

    @staticmethod
    def get_threshold_status(permission_key: str) -> Optional[Dict]:
        """Get threshold_id and is_active status for a permission key."""
        return fetch_one(
            "SELECT threshold_id, is_active FROM core.permission_thresholds WHERE permission_key = %s",
            (permission_key,)
        )

    @staticmethod
    def get_threshold_level(permission_key: str) -> Optional[Dict]:
        """Get threshold_id and min_hierarchy_level for a permission key."""
        return fetch_one(
            "SELECT threshold_id, min_hierarchy_level FROM core.permission_thresholds WHERE permission_key = %s",
            (permission_key,)
        )

    @staticmethod
    def toggle_threshold_active(permission_key: str, new_status: bool) -> None:
        """Toggle the is_active status of a permission threshold."""
        execute_query(
            """
            UPDATE core.permission_thresholds
            SET is_active = %s, updated_at = NOW()
            WHERE permission_key = %s
            """,
            (new_status, permission_key)
        )

    @staticmethod
    def get_threshold_audit_log(
        permission_key: Optional[str] = None, limit: int = 50
    ) -> List[Dict]:
        """Get permission threshold audit log entries."""
        query = """
            SELECT
                a.audit_id,
                a.threshold_id,
                a.permission_key,
                a.old_min_level,
                a.new_min_level,
                a.action,
                a.changed_at,
                u.email as changed_by
            FROM core.permission_threshold_audit a
            LEFT JOIN core.users u ON a.changed_by_user_id = u.user_id
        """
        params = []

        if permission_key:
            query += " WHERE a.permission_key = %s"
            params.append(permission_key)

        query += " ORDER BY a.changed_at DESC LIMIT %s"
        params.append(limit)

        return fetch_all(query, tuple(params)) or []

    # =====================================================
    # Group Listing Queries (for auth middleware)
    # =====================================================

    @staticmethod
    def get_all_groups() -> List[Dict]:
        """Get all non-deleted groups (for admin group assignment)."""
        return fetch_all(
            """
            SELECT id, name, slug, group_type, frontend_role
            FROM core.groups
            WHERE deleted_at IS NULL
            ORDER BY name ASC
            """
        ) or []

    @staticmethod
    def get_org_non_role_groups(org_id) -> List[Dict]:
        """Get non-role groups for a specific organisation."""
        return fetch_all(
            """
            SELECT id, name, slug, group_type, frontend_role
            FROM core.groups
            WHERE organisation_id = %s
                AND group_type != 'role'
                AND deleted_at IS NULL
            ORDER BY name ASC
            """,
            (org_id,)
        ) or []
