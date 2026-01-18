"""
LernsystemX Widget Instance Repository (Doku-konform)

Handles user_widgets table operations:
- Get user's widget instances
- Add/remove widgets
- Update widget positions (Drag & Drop)
- Update widget settings

Pure psycopg3 - No ORM

Tabelle: user_widgets (NOT user_dashboard_widgets!)
PK: user_widget_id (UUID)
"""

from typing import Optional, List, Dict
from datetime import datetime
import json

from app.infrastructure.persistence.repositories.base_repository import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query, insert_returning, update_returning


class WidgetInstanceRepository(BaseRepository):
    """
    User Widgets repository (Doku-konform)

    Manages user-specific widget instances (Tabelle: user_widgets)
    """

    table_name = 'user_widgets'
    pk_column = 'user_widget_id'

    @classmethod
    def get_user_widgets(cls, user_id: str, layout_id: Optional[str] = None) -> List[Dict]:
        """
        Get all widget instances for user

        Args:
            user_id: User UUID
            layout_id: Optional layout UUID

        Returns:
            List of widget instance dicts with widget metadata
        """
        if layout_id:
            query = """
                SELECT
                    uw.*,
                    w.widget_type,
                    w.name as widget_name,
                    w.component_path,
                    w.default_settings
                FROM user_widgets uw
                JOIN widgets w ON uw.widget_id = w.widget_id
                WHERE uw.user_id = %s
                  AND uw.layout_id = %s
                ORDER BY uw.display_order, uw.position_y, uw.position_x
            """
            params = (user_id, layout_id)
        else:
            query = """
                SELECT
                    uw.*,
                    w.widget_type,
                    w.name as widget_name,
                    w.component_path,
                    w.default_settings
                FROM user_widgets uw
                JOIN widgets w ON uw.widget_id = w.widget_id
                WHERE uw.user_id = %s
                ORDER BY uw.display_order, uw.position_y, uw.position_x
            """
            params = (user_id,)

        results = fetch_all(query, params)

        # Parse JSONB custom_settings and default_settings
        for result in results:
            if isinstance(result.get('custom_settings'), str):
                result['custom_settings'] = json.loads(result['custom_settings'])
            if isinstance(result.get('default_settings'), str):
                result['default_settings'] = json.loads(result['default_settings'])

        return results

    @classmethod
    def get_widget_instance(cls, widget_instance_id: str) -> Optional[Dict]:
        """
        Get single widget instance

        Args:
            widget_instance_id: Widget instance UUID (user_widget_id)

        Returns:
            Widget instance dict or None
        """
        query = """
            SELECT
                uw.*,
                w.widget_type,
                w.name as widget_name,
                w.component_path,
                w.default_settings
            FROM user_widgets uw
            JOIN widgets w ON uw.widget_id = w.widget_id
            WHERE uw.user_widget_id = %s
        """

        result = fetch_one(query, (widget_instance_id,))

        if result:
            if isinstance(result.get('custom_settings'), str):
                result['custom_settings'] = json.loads(result['custom_settings'])
            if isinstance(result.get('default_settings'), str):
                result['default_settings'] = json.loads(result['default_settings'])

        return result

    @classmethod
    def add_widget(
        cls,
        user_id: str,
        widget_id: str,  # UUID now, not integer!
        layout_id: Optional[str] = None,
        position_x: int = 0,
        position_y: int = 0,
        width: int = 2,
        height: int = 1,
        display_order: int = 0,
        custom_settings: Optional[Dict] = None
    ) -> Dict:
        """
        Add widget to user's dashboard

        Args:
            user_id: User UUID
            widget_id: Widget UUID (from widgets table)
            layout_id: Layout UUID
            position_x: Grid X position
            position_y: Grid Y position
            width: Grid width
            height: Grid height
            display_order: Display order
            custom_settings: Custom settings dict

        Returns:
            Created widget instance dict
        """
        query = """
            INSERT INTO user_widgets (
                user_id,
                widget_id,
                layout_id,
                position_x,
                position_y,
                width,
                height,
                display_order,
                custom_settings,
                is_visible,
                is_collapsed,
                created_at,
                updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, FALSE, %s, %s)
            RETURNING *
        """

        now = datetime.utcnow()
        result = insert_returning(
            query,
            (
                user_id,
                widget_id,
                layout_id,
                position_x,
                position_y,
                width,
                height,
                display_order,
                json.dumps(custom_settings or {}),
                now,
                now
            )
        )

        if result and isinstance(result.get('custom_settings'), str):
            result['custom_settings'] = json.loads(result['custom_settings'])

        return result

    @classmethod
    def update_widget_position(
        cls,
        widget_instance_id: str,
        position_x: int,
        position_y: int,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Update widget position (Drag & Drop)

        Args:
            widget_instance_id: Widget instance UUID (user_widget_id)
            position_x: New X position
            position_y: New Y position
            width: Optional new width
            height: Optional new height

        Returns:
            Updated widget instance dict
        """
        if width is not None and height is not None:
            query = """
                UPDATE user_widgets
                SET position_x = %s,
                    position_y = %s,
                    width = %s,
                    height = %s,
                    updated_at = %s
                WHERE user_widget_id = %s
                RETURNING *
            """
            params = (position_x, position_y, width, height, datetime.utcnow(), widget_instance_id)
        else:
            query = """
                UPDATE user_widgets
                SET position_x = %s,
                    position_y = %s,
                    updated_at = %s
                WHERE user_widget_id = %s
                RETURNING *
            """
            params = (position_x, position_y, datetime.utcnow(), widget_instance_id)

        result = update_returning(query, params)

        if result and isinstance(result.get('custom_settings'), str):
            result['custom_settings'] = json.loads(result['custom_settings'])

        return result

    @classmethod
    def update_widget_settings(
        cls,
        widget_instance_id: str,
        custom_settings: Dict
    ) -> Optional[Dict]:
        """
        Update widget settings

        Args:
            widget_instance_id: Widget instance UUID (user_widget_id)
            custom_settings: New settings dict

        Returns:
            Updated widget instance dict
        """
        query = """
            UPDATE user_widgets
            SET custom_settings = %s,
                updated_at = %s
            WHERE user_widget_id = %s
            RETURNING *
        """

        result = update_returning(
            query,
            (json.dumps(custom_settings), datetime.utcnow(), widget_instance_id)
        )

        if result and isinstance(result.get('custom_settings'), str):
            result['custom_settings'] = json.loads(result['custom_settings'])

        return result

    @classmethod
    def toggle_widget_visibility(cls, widget_instance_id: str) -> bool:
        """
        Toggle widget visibility

        Args:
            widget_instance_id: Widget instance UUID (user_widget_id)

        Returns:
            bool: New visibility state
        """
        query = """
            UPDATE user_widgets
            SET is_visible = NOT is_visible,
                updated_at = %s
            WHERE user_widget_id = %s
            RETURNING is_visible
        """

        result = update_returning(query, (datetime.utcnow(), widget_instance_id))
        return result['is_visible'] if result else False

    @classmethod
    def remove_widget(cls, widget_instance_id: str) -> bool:
        """
        Remove widget from dashboard

        Args:
            widget_instance_id: Widget instance UUID (user_widget_id)

        Returns:
            bool: True if deleted
        """
        query = """
            DELETE FROM user_widgets
            WHERE user_widget_id = %s
        """

        rows_affected = execute_query(query, (widget_instance_id,))
        return rows_affected > 0

    @classmethod
    def count_user_widgets(cls, user_id: str) -> int:
        """
        Count widgets for user

        Args:
            user_id: User UUID

        Returns:
            int: Widget count
        """
        query = """
            SELECT COUNT(*) as count
            FROM user_widgets
            WHERE user_id = %s
        """

        result = fetch_one(query, (user_id,))
        return result['count'] if result else 0

    @classmethod
    def get_widget_by_user_and_type(
        cls,
        user_id: str,
        widget_type: str,
        layout_id: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Check if user already has a widget of this type

        Args:
            user_id: User UUID
            widget_type: Widget type
            layout_id: Optional layout UUID

        Returns:
            Widget instance or None
        """
        if layout_id:
            query = """
                SELECT uw.*
                FROM user_widgets uw
                JOIN widgets w ON uw.widget_id = w.widget_id
                WHERE uw.user_id = %s
                  AND w.widget_type = %s
                  AND uw.layout_id = %s
            """
            params = (user_id, widget_type, layout_id)
        else:
            query = """
                SELECT uw.*
                FROM user_widgets uw
                JOIN widgets w ON uw.widget_id = w.widget_id
                WHERE uw.user_id = %s
                  AND w.widget_type = %s
            """
            params = (user_id, widget_type)

        return fetch_one(query, params)
