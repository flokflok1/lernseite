"""
Authorization Repository - Hierarchy level and group queries.

Provides database access for:
- User hierarchy level calculation
- User group membership with levels
- User effective permissions (via SQL function)
- User active groups for token refresh
- Two-factor authentication updates
"""

from typing import List, Dict, Any, Optional

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query


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
        return fetch_all(
            """
            SELECT COALESCE(MAX(COALESCE(ug.hierarchy_level, g.hierarchy_level)), 0) as max_level
            FROM core.users_groups ug
            JOIN core.groups g ON ug.group_id = g.id
            WHERE ug.user_id = %s
                AND ug.is_active = TRUE
                AND ug.left_at IS NULL
            """,
            (user_id,)
        ) or []

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
        return fetch_all(
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
            (user_id,)
        ) or []

    @staticmethod
    def get_user_effective_permissions(user_id: str) -> List[Dict[str, Any]]:
        """
        Get user's effective permissions using SQL function.

        Args:
            user_id: User UUID

        Returns:
            List of dicts with 'permission_code' key
        """
        return fetch_all(
            "SELECT * FROM get_user_effective_permissions(%s)",
            (user_id,)
        ) or []

    @staticmethod
    def get_user_active_groups(user_id: str) -> List[Dict[str, Any]]:
        """
        Get user's active groups for token refresh.

        Args:
            user_id: User UUID

        Returns:
            List of groups with id, name, slug, group_type, frontend_role,
            access_level, joined_at. Sorted by joined_at ASC.
        """
        return fetch_all(
            """
            SELECT
                g.id,
                g.name,
                g.slug,
                g.group_type,
                g.frontend_role,
                ug.access_level,
                ug.joined_at
            FROM core.users_groups ug
            JOIN core.groups g ON ug.group_id = g.id
            WHERE ug.user_id = %s
                AND ug.is_active = TRUE
                AND ug.left_at IS NULL
            ORDER BY ug.joined_at ASC
            """,
            (user_id,)
        ) or []

    @staticmethod
    def set_two_factor_secret(user_id: str, totp_secret: str) -> None:
        """
        Store TOTP secret for 2FA setup.

        Args:
            user_id: User UUID
            totp_secret: TOTP secret string
        """
        execute_query(
            "UPDATE users SET two_factor_secret = %s WHERE user_id = %s",
            (totp_secret, user_id)
        )

    @staticmethod
    def enable_two_factor(user_id: str) -> None:
        """
        Enable two-factor authentication for user.

        Args:
            user_id: User UUID
        """
        execute_query(
            "UPDATE users SET two_factor_enabled = true WHERE user_id = %s",
            (user_id,)
        )

    @staticmethod
    def disable_two_factor(user_id: str) -> None:
        """
        Disable two-factor authentication and clear secret.

        Args:
            user_id: User UUID
        """
        execute_query(
            "UPDATE users SET two_factor_enabled = false, two_factor_secret = NULL WHERE user_id = %s",
            (user_id,)
        )
