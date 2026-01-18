"""
LernsystemX Widget Repository (Doku-konform)

Handles widgets table operations:
- Get all widget definitions
- Get widgets for specific role
- Check widget availability
- Admin: Create/update widget types

Pure psycopg3 - No ORM

Tabelle: widgets (NOT widget_types!)
PK: widget_id (UUID, NOT SERIAL!)
"""

from typing import Optional, List, Dict
from datetime import datetime

from app.infrastructure.persistence.repositories.base_repository import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query, insert_returning


class WidgetRepository(BaseRepository):
    """
    Widget repository (Doku-konform)

    Manages widget type registry (Tabelle: widgets)
    """

    table_name = 'widgets'
    pk_column = 'widget_id'

    @classmethod
    def get_all_widgets(cls, active_only: bool = True) -> List[Dict]:
        """
        Get all widget types

        Args:
            active_only: Only return active widgets

        Returns:
            List of widget dicts
        """
        query = """
            SELECT
                widget_id,
                widget_type,
                name,
                description,
                component_path,
                default_settings,
                min_role_required,
                is_active,
                version,
                created_at
            FROM widgets
            WHERE is_active = TRUE OR %s = FALSE
            ORDER BY name
        """

        return fetch_all(query, (active_only,))

    @classmethod
    def get_widget_by_type(cls, widget_type: str) -> Optional[Dict]:
        """
        Get widget by type

        Args:
            widget_type: Widget type (e.g. 'progress', 'ki_recommendations')

        Returns:
            Widget dict or None
        """
        query = """
            SELECT *
            FROM widgets
            WHERE widget_type = %s
        """

        return fetch_one(query, (widget_type,))

    @classmethod
    def get_widget_by_id(cls, widget_id: str) -> Optional[Dict]:
        """
        Get widget by ID

        Args:
            widget_id: Widget UUID

        Returns:
            Widget dict or None
        """
        query = """
            SELECT *
            FROM widgets
            WHERE widget_id = %s
        """

        return fetch_one(query, (widget_id,))

    @classmethod
    def get_widgets_for_role(cls, role: str) -> List[Dict]:
        """
        Get all widgets available for a specific role

        Uses PostgreSQL function get_widgets_for_role()

        Args:
            role: User role

        Returns:
            List of available widget dicts
        """
        query = """
            SELECT *
            FROM get_widgets_for_role(%s)
        """

        return fetch_all(query, (role,))

    @classmethod
    def is_widget_available(cls, widget_type: str, role: str) -> bool:
        """
        Check if widget is available for role

        Args:
            widget_type: Widget type
            role: User role

        Returns:
            bool: True if available
        """
        # Use helper function to check role hierarchy
        available_widgets = cls.get_widgets_for_role(role)
        return any(w['widget_type'] == widget_type for w in available_widgets)

    @classmethod
    def count_widgets(cls) -> int:
        """
        Count total active widgets

        Returns:
            int: Widget count
        """
        query = "SELECT COUNT(*) as count FROM widgets WHERE is_active = TRUE"
        result = fetch_one(query)
        return result['count'] if result else 0

    @classmethod
    def create_widget_type(
        cls,
        widget_type: str,
        name: str,
        component_path: str,
        description: Optional[str] = None,
        min_role_required: str = 'free',
        default_settings: Optional[Dict] = None,
        version: str = '1.0.0'
    ) -> Dict:
        """
        Create new widget type (Admin only)

        Args:
            widget_type: Unique widget type identifier
            name: Display name
            component_path: Vue component path
            description: Optional description
            min_role_required: Minimum role required
            default_settings: Default JSONB settings
            version: Widget version

        Returns:
            Created widget dict
        """
        query = """
            INSERT INTO widgets (
                widget_type,
                name,
                description,
                component_path,
                default_settings,
                min_role_required,
                is_active,
                version,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, TRUE, %s, %s)
            RETURNING *
        """

        now = datetime.utcnow()
        return insert_returning(
            query,
            (
                widget_type,
                name,
                description,
                component_path,
                default_settings or {},
                min_role_required,
                version,
                now
            )
        )

    @classmethod
    def update_widget_type(
        cls,
        widget_id: str,
        updates: Dict
    ) -> Optional[Dict]:
        """
        Update widget type (Admin only)

        Args:
            widget_id: Widget UUID
            updates: Dict with update fields

        Returns:
            Updated widget dict or None
        """
        allowed_fields = [
            'name', 'description', 'component_path',
            'default_settings', 'min_role_required',
            'is_active', 'version'
        ]

        set_clauses = []
        params = []

        for field, value in updates.items():
            if field in allowed_fields:
                set_clauses.append(f"{field} = %s")
                params.append(value)

        if not set_clauses:
            return cls.get_widget_by_id(widget_id)

        params.append(widget_id)

        query = f"""
            UPDATE widgets
            SET {', '.join(set_clauses)}
            WHERE widget_id = %s
            RETURNING *
        """

        result = fetch_one(query, tuple(params))
        return result

    @classmethod
    def delete_widget_type(cls, widget_id: str) -> bool:
        """
        Delete widget type (Soft delete - set is_active = false)

        Args:
            widget_id: Widget UUID

        Returns:
            bool: Success
        """
        query = """
            UPDATE widgets
            SET is_active = FALSE
            WHERE widget_id = %s
        """

        execute_query(query, (widget_id,))
        return True

    @classmethod
    def get_widget_stats(cls) -> Dict:
        """
        Get widget statistics

        Returns:
            Dict with stats
        """
        query = """
            SELECT
                COUNT(*) as total_widgets,
                COUNT(*) FILTER (WHERE is_active = TRUE) as active_widgets,
                COUNT(*) FILTER (WHERE min_role_required = 'free') as free_widgets,
                COUNT(*) FILTER (WHERE min_role_required IN ('premium', 'creator')) as premium_widgets
            FROM widgets
        """

        result = fetch_one(query)
        return result or {}
