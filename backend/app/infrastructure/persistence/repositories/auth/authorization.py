"""
Authorization Repository - Hierarchy level and group queries.

Provides database access for:
- User hierarchy level calculation
- User group membership with levels
"""

from typing import List, Dict, Any

from app.infrastructure.persistence.database.connection import execute_query


class AuthorizationRepository:
    """Repository for authorization hierarchy queries."""

    @staticmethod
    def get_user_max_hierarchy_level(user_id: str) -> List[Dict[str, Any]]:
        """
        Get user's maximum hierarchy level from all assigned groups.

        Args:
            user_id: User UUID

        Returns:
            List with single dict containing 'max_level', or empty list
        """
        result = execute_query(
            """
            SELECT COALESCE(MAX(COALESCE(ug.hierarchy_level, g.hierarchy_level)), 0) as max_level
            FROM core.users_groups ug
            JOIN core.groups g ON ug.group_id = g.id
            WHERE ug.user_id = %s
                AND ug.is_active = TRUE
                AND ug.left_at IS NULL
            """,
            (user_id,),
            fetch=True
        )
        return result if result else []

    @staticmethod
    def get_user_groups_with_levels(user_id: str) -> List[Dict[str, Any]]:
        """
        Get all user's groups with their effective hierarchy levels.

        Args:
            user_id: User UUID

        Returns:
            List of groups with id, name, slug, group_type, frontend_role,
            hierarchy_level, access_level, joined_at.
            Sorted by hierarchy_level DESC.
        """
        result = execute_query(
            """
            SELECT
                g.id,
                g.name,
                g.slug,
                g.group_type,
                g.frontend_role,
                g.hierarchy_level,
                ug.access_level,
                ug.joined_at
            FROM core.users_groups ug
            JOIN core.groups g ON ug.group_id = g.id
            WHERE ug.user_id = %s
                AND ug.is_active = TRUE
                AND ug.left_at IS NULL
            ORDER BY g.hierarchy_level DESC
            """,
            (user_id,),
            fetch=True
        )
        return result if result else []
