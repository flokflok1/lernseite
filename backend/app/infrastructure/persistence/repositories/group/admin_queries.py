"""
Group Admin Query Repository - SQL for admin group routes.

Provides static methods for admin group management endpoints:
- Get group by ID (admin schema)
- Update group
- Delete group
- Get group members (paginated)
- Remove member
- Get group permissions (paginated)
- Revoke permission
- List all permissions from registry
- Get distinct permission categories
"""

from typing import Optional, Dict, List, Tuple

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query
)


class GroupAdminQueryRepository:
    """SQL queries for admin group management routes."""

    @staticmethod
    def get_group_by_id(group_id: str) -> Optional[Dict]:
        """Get a single group by ID (admin schema with hierarchy_level)."""
        return fetch_one(
            """
            SELECT id, name, slug, description, hierarchy_level, group_type,
                   organisation_id, is_system_group, is_protected, created_at, updated_at
            FROM core.groups
            WHERE id = %s
            """,
            (group_id,)
        )

    @staticmethod
    def update_group(group_id: str, updates: List[str], params: list) -> Optional[Dict]:
        """
        Update a group with dynamic fields.

        Args:
            group_id: Group ID
            updates: List of SQL SET clauses (e.g. ['name = %s', 'description = %s'])
            params: List of parameter values matching the SET clauses
        """
        params.append(group_id)
        return execute_query(
            f"""
            UPDATE core.groups
            SET {', '.join(updates)}, updated_at = NOW()
            WHERE id = %s AND is_protected = FALSE
            RETURNING id, name, slug, description, hierarchy_level, group_type,
                      is_system_group, is_protected, created_at, updated_at
            """,
            tuple(params),
            fetch_one=True
        )

    @staticmethod
    def delete_group(group_id: str) -> Optional[Dict]:
        """Delete a group (only if not protected). Returns deleted row or None."""
        return execute_query(
            """
            DELETE FROM core.groups
            WHERE id = %s AND is_protected = FALSE
            RETURNING id
            """,
            (group_id,),
            fetch_one=True
        )

    @staticmethod
    def get_group_members(
        group_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict]:
        """Get members of a group with pagination."""
        return fetch_all(
            """
            SELECT ug.user_id, ug.access_level, ug.joined_at, ug.is_active,
                   u.email, u.full_name, u.username
            FROM core.users_groups ug
            JOIN core.users u ON ug.user_id = u.user_id
            WHERE ug.group_id = %s AND ug.is_active = TRUE
            ORDER BY ug.joined_at DESC
            LIMIT %s OFFSET %s
            """,
            (group_id, limit, offset)
        ) or []

    @staticmethod
    def count_group_members(group_id: str) -> int:
        """Count active members in a group."""
        result = fetch_one(
            """
            SELECT COUNT(*) as total
            FROM core.users_groups
            WHERE group_id = %s AND is_active = TRUE
            """,
            (group_id,)
        )
        return result['total'] if result else 0

    @staticmethod
    def remove_member(group_id: str, user_id: str) -> bool:
        """Remove a member from a group (soft delete)."""
        result = execute_query(
            """
            UPDATE core.users_groups
            SET is_active = FALSE, left_at = NOW()
            WHERE group_id = %s AND user_id = %s
            RETURNING user_id
            """,
            (group_id, user_id),
            fetch_one=True
        )
        return result is not None

    @staticmethod
    def get_group_permissions_paginated(
        group_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict]:
        """Get permissions of a group with pagination."""
        return fetch_all(
            """
            SELECT p.id, p.code, p.display_name, p.category, p.description, gp.created_at
            FROM core.group_permissions gp
            JOIN core.permissions p ON gp.permission_id = p.id
            WHERE gp.group_id = %s
            ORDER BY p.code ASC
            LIMIT %s OFFSET %s
            """,
            (group_id, limit, offset)
        ) or []

    @staticmethod
    def count_group_permissions(group_id: str) -> int:
        """Count permissions assigned to a group."""
        result = fetch_one(
            """
            SELECT COUNT(*) as total
            FROM core.group_permissions
            WHERE group_id = %s
            """,
            (group_id,)
        )
        return result['total'] if result else 0

    @staticmethod
    def revoke_permission(group_id: str, permission_id: str) -> bool:
        """Revoke a permission from a group."""
        result = execute_query(
            """
            DELETE FROM core.group_permissions
            WHERE group_id = %s AND permission_id = %s
            RETURNING permission_id
            """,
            (group_id, permission_id),
            fetch_one=True
        )
        return result is not None

    @staticmethod
    def get_all_permissions(category: Optional[str] = None) -> List[Dict]:
        """Get all permissions from registry, optionally filtered by category."""
        if category:
            return fetch_all(
                """
                SELECT id, code, display_name, category, description
                FROM core.permissions
                WHERE category = %s
                ORDER BY category, code ASC
                """,
                (category,)
            ) or []
        else:
            return fetch_all(
                """
                SELECT id, code, display_name, category, description
                FROM core.permissions
                ORDER BY category, code ASC
                """
            ) or []

    @staticmethod
    def get_permission_categories() -> List[str]:
        """Get distinct permission categories."""
        result = fetch_all(
            """
            SELECT DISTINCT category
            FROM core.permissions
            ORDER BY category ASC
            """
        )
        return [c['category'] for c in result] if result else []
