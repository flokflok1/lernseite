"""
Authorization Service

Provides authorization and hierarchy level calculations for users.
Database-driven, no hardcoded logic.

ISO 27001:2013 compliant - Access Control
"""

from typing import List, Dict, Any, Optional
from app.infrastructure.persistence.database.connection import execute_query


class AuthorizationService:
    """
    Authorization service for hierarchy-based access control.

    Hierarchy Levels (0-1000):
    - User's level is determined by highest level among all assigned groups
    - Uses database values only - NO hardcoded role logic in code
    """

    @staticmethod
    def get_user_hierarchy_level(user_id: str) -> int:
        """
        Get user's maximum hierarchy level from all assigned groups.

        Args:
            user_id: User UUID

        Returns:
            Integer between 0-1000
            - 0: Guest/No group
            - 1000: Highest authority (Owner)

        Note:
            Uses user-specific override if set in users_groups.hierarchy_level,
            otherwise uses group default from groups.hierarchy_level
        """
        try:
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

            if result and len(result) > 0:
                level = result[0].get('max_level', 0)
                return max(0, min(1000, level))  # Clamp to 0-1000
            return 0

        except Exception as e:
            # Log error and return guest level
            print(f"Error getting hierarchy level for user {user_id}: {e}")
            return 0

    @staticmethod
    def has_hierarchy_level(user_id: str, required_level: int) -> bool:
        """
        Check if user has at least the required hierarchy level.

        Args:
            user_id: User UUID
            required_level: Minimum level required (0-1000)

        Returns:
            True if user's level >= required_level

        Example:
            - User has level 500
            - has_hierarchy_level(user_id, 500) → True
            - has_hierarchy_level(user_id, 501) → False
            - has_hierarchy_level(user_id, 250) → True
        """
        user_level = AuthorizationService.get_user_hierarchy_level(user_id)
        return user_level >= required_level

    @staticmethod
    def get_user_groups_with_levels(user_id: str) -> List[Dict[str, Any]]:
        """
        Get all user's groups with their effective hierarchy levels.

        Args:
            user_id: User UUID

        Returns:
            List of groups with id, name, slug, type, hierarchy_level
            Sorted by hierarchy_level DESC
        """
        try:
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

        except Exception as e:
            print(f"Error getting user groups for {user_id}: {e}")
            return []

    @staticmethod
    def format_groups_response(groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format groups list for API response.

        Args:
            groups: Raw groups from database

        Returns:
            Formatted list with string IDs
        """
        return [
            {
                'id': str(g['id']),
                'name': g['name'],
                'slug': g['slug'],
                'type': g['group_type'],
                'hierarchy_level': g['hierarchy_level'],
                'access_level': g.get('access_level')
            } for g in groups
        ]
