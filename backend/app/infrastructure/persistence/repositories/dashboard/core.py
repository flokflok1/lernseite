"""
LernsystemX Dashboard Repository

Handles all dashboard layout database operations:
- Get user dashboard layout
- Save user dashboard layout
- Delete user layout (reset to default)
- Get layout by user and role

Pure psycopg3 - No ORM
ISO 9001:2015 compliant - Repository pattern
"""

from typing import Optional, Dict
from datetime import datetime
import json

from app.infrastructure.persistence.repositories.base_repository import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query, insert_returning, update_returning


class DashboardRepository(BaseRepository):
    """
    Dashboard layout repository

    Manages user-specific dashboard layouts with pure psycopg3
    """

    table_name = 'dashboard_layouts'
    pk_column = 'layout_id'

    @classmethod
    def get_user_layout(cls, user_id: int) -> Optional[Dict]:
        """
        Get user's dashboard layout

        Args:
            user_id: User ID

        Returns:
            Dict with layout data or None if not found

        Example:
            >>> layout = DashboardRepository.get_user_layout(123)
            >>> if layout:
            ...     print(layout['layout_json'])
        """
        query = """
            SELECT
                layout_id,
                user_id,
                organisation_id,
                role,
                layout_json,
                source,
                is_default,
                created_at,
                updated_at
            FROM dashboard_layouts
            WHERE user_id = %s
            ORDER BY updated_at DESC
            LIMIT 1
        """

        result = fetch_one(query, (user_id,))

        if result:
            # Parse JSONB layout_json field
            if isinstance(result['layout_json'], str):
                result['layout_json'] = json.loads(result['layout_json'])

        return result

    @classmethod
    def save_user_layout(
        cls,
        user_id: int,
        role: str,
        layout_json: Dict,
        organisation_id: Optional[int] = None,
        source: str = 'user'
    ) -> Dict:
        """
        Save or update user's dashboard layout

        Args:
            user_id: User ID
            role: User role
            layout_json: Layout configuration as dict
            organisation_id: Organisation ID (optional)
            source: Layout source ('user', 'role', 'organisation', 'system')

        Returns:
            Dict with saved layout data

        Example:
            >>> layout_data = {
            ...     'widgets': [{'widgetId': 'welcome', 'order': 0}],
            ...     'version': 1
            ... }
            >>> saved = DashboardRepository.save_user_layout(
            ...     user_id=123,
            ...     role='premium',
            ...     layout_json=layout_data
            ... )
        """
        # Check if layout already exists
        existing = cls.get_user_layout(user_id)

        if existing:
            # Update existing layout
            update_query = """
                UPDATE dashboard_layouts
                SET
                    role = %s,
                    layout_json = %s,
                    organisation_id = %s,
                    source = %s,
                    updated_at = %s
                WHERE user_id = %s
                RETURNING *
            """

            result = update_returning(
                update_query,
                (
                    role,
                    json.dumps(layout_json),
                    organisation_id,
                    source,
                    datetime.utcnow(),
                    user_id
                )
            )
        else:
            # Insert new layout
            insert_query = """
                INSERT INTO dashboard_layouts (
                    user_id,
                    organisation_id,
                    role,
                    layout_json,
                    source,
                    is_default,
                    created_at,
                    updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """

            result = insert_returning(
                insert_query,
                (
                    user_id,
                    organisation_id,
                    role,
                    json.dumps(layout_json),
                    source,
                    False,
                    datetime.utcnow(),
                    datetime.utcnow()
                )
            )

        # Parse JSONB field
        if result and isinstance(result['layout_json'], str):
            result['layout_json'] = json.loads(result['layout_json'])

        return result

    @classmethod
    def delete_user_layout(cls, user_id: int) -> bool:
        """
        Delete user's custom layout (reset to default)

        Args:
            user_id: User ID

        Returns:
            bool: True if layout was deleted, False otherwise

        Example:
            >>> success = DashboardRepository.delete_user_layout(123)
            >>> if success:
            ...     print("Layout reset to default")
        """
        query = """
            DELETE FROM dashboard_layouts
            WHERE user_id = %s
        """

        rows_affected = execute_query(query, (user_id,))
        return rows_affected > 0

    @classmethod
    def layout_exists(cls, user_id: int) -> bool:
        """
        Check if user has a custom layout

        Args:
            user_id: User ID

        Returns:
            bool: True if user has custom layout

        Example:
            >>> has_custom = DashboardRepository.layout_exists(123)
        """
        query = """
            SELECT COUNT(*) as count
            FROM dashboard_layouts
            WHERE user_id = %s
        """

        result = fetch_one(query, (user_id,))
        return result and result['count'] > 0

    @classmethod
    def get_layouts_by_role(cls, role: str, limit: int = 10) -> list:
        """
        Get all layouts for a specific role (for analytics/defaults)

        Args:
            role: User role
            limit: Maximum number of layouts to return

        Returns:
            List of layout dicts

        Example:
            >>> layouts = DashboardRepository.get_layouts_by_role('premium', limit=5)
        """
        query = """
            SELECT
                layout_id,
                user_id,
                role,
                layout_json,
                source,
                created_at,
                updated_at
            FROM dashboard_layouts
            WHERE role = %s
            ORDER BY updated_at DESC
            LIMIT %s
        """

        results = fetch_all(query, (role, limit))

        # Parse JSONB fields
        for result in results:
            if isinstance(result['layout_json'], str):
                result['layout_json'] = json.loads(result['layout_json'])

        return results

    @classmethod
    def count_custom_layouts(cls) -> int:
        """
        Count total number of custom layouts

        Returns:
            int: Number of custom layouts in database

        Example:
            >>> total = DashboardRepository.count_custom_layouts()
        """
        query = "SELECT COUNT(*) as count FROM dashboard_layouts WHERE source = 'user'"
        result = fetch_one(query)
        return result['count'] if result else 0

    @classmethod
    def get_layouts_by_organisation(cls, organisation_id: int) -> list:
        """
        Get all layouts for an organisation

        Args:
            organisation_id: Organisation ID

        Returns:
            List of layout dicts

        Example:
            >>> org_layouts = DashboardRepository.get_layouts_by_organisation(5)
        """
        query = """
            SELECT
                layout_id,
                user_id,
                role,
                layout_json,
                source,
                created_at,
                updated_at
            FROM dashboard_layouts
            WHERE organisation_id = %s
            ORDER BY updated_at DESC
        """

        results = fetch_all(query, (organisation_id,))

        # Parse JSONB fields
        for result in results:
            if isinstance(result['layout_json'], str):
                result['layout_json'] = json.loads(result['layout_json'])

        return results
