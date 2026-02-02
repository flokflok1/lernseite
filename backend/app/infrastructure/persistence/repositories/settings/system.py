"""
LernsystemX System Settings Repository

Database operations for system_settings table.
Pure psycopg3 - No ORM.

Table: system_settings
PK: setting_id (SERIAL)
Unique: key
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from app.infrastructure.persistence.repositories.base_repository import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query, update_returning, insert_returning


class SystemSettingsRepository(BaseRepository):
    """
    System Settings Repository

    Manages system-wide configuration stored in database.
    """

    table_name = 'system_settings'
    pk_column = 'setting_id'

    @classmethod
    def get_setting(cls, key: str) -> Optional[str]:
        """
        Get setting value by key

        Args:
            key: Setting key (e.g. 'system.maintenance_mode')

        Returns:
            Setting value as string or None if not found
        """
        try:
            query = """
                SELECT value
                FROM system_settings
                WHERE key = %s
            """

            result = fetch_one(query, (key,))
            return result['value'] if result else None

        except Exception as e:
            # Table doesn't exist yet (during setup) or other DB error
            # Return None to allow system to continue
            import logging
            logging.debug(f"Could not get setting '{key}': {e}")
            return None

    @classmethod
    def get_setting_obj(cls, key: str) -> Optional[Dict]:
        """
        Get full setting object by key

        Args:
            key: Setting key

        Returns:
            Full setting dict with all columns or None
        """
        try:
            query = """
                SELECT *
                FROM system_settings
                WHERE key = %s
            """

            result = fetch_one(query, (key,))

            if result and result.get('value_type') == 'json':
                # Parse JSON value
                try:
                    result['value'] = json.loads(result['value'])
                except (json.JSONDecodeError, TypeError):
                    pass

            return result

        except Exception as e:
            # Table doesn't exist yet (during setup) or other DB error
            import logging
            logging.debug(f"Could not get setting object '{key}': {e}")
            return None

    @classmethod
    def update_setting(cls, key: str, value: Any, value_type: str = 'string') -> bool:
        """
        Update setting value

        Args:
            key: Setting key
            value: New value
            value_type: Type of value (string, number, boolean, json)

        Returns:
            True if updated, False if not found
        """
        # Convert value to string for storage
        if value_type == 'json':
            value_str = json.dumps(value)
        elif value_type == 'boolean':
            value_str = 'true' if value else 'false'
        else:
            value_str = str(value)

        query = """
            UPDATE system_settings
            SET value = %s,
                value_type = %s,
                updated_at = %s
            WHERE key = %s
        """

        rows_affected = execute_query(query, (value_str, value_type, datetime.utcnow(), key))
        return rows_affected > 0

    @classmethod
    def get_all_settings(cls, category: Optional[str] = None) -> List[Dict]:
        """
        Get all settings, optionally filtered by category

        Args:
            category: Optional category filter (e.g. 'system', 'ai', 'billing')

        Returns:
            List of setting dicts
        """
        if category:
            query = """
                SELECT *
                FROM system_settings
                WHERE category = %s
                ORDER BY category, key
            """
            results = fetch_all(query, (category,))
        else:
            query = """
                SELECT *
                FROM system_settings
                ORDER BY category, key
            """
            results = fetch_all(query)

        # Parse JSON values
        for result in results:
            if result.get('value_type') == 'json':
                try:
                    result['value'] = json.loads(result['value'])
                except (json.JSONDecodeError, TypeError):
                    pass

        return results

    @classmethod
    def create_setting(
        cls,
        key: str,
        value: Any,
        category: str = 'general',
        description: str = None,
        editable: bool = True,
        value_type: str = 'string',
        encrypted: bool = False
    ) -> Dict:
        """
        Create new setting

        Args:
            key: Unique setting key
            value: Setting value
            category: Setting category
            description: Optional description
            editable: Whether setting is editable via UI
            value_type: Type of value
            encrypted: Whether value should be encrypted

        Returns:
            Created setting dict
        """
        # Convert value to string for storage
        if value_type == 'json':
            value_str = json.dumps(value)
        elif value_type == 'boolean':
            value_str = 'true' if value else 'false'
        else:
            value_str = str(value)

        query = """
            INSERT INTO system_settings (
                key,
                value,
                value_type,
                encrypted,
                category,
                description,
                editable,
                created_at,
                updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """

        now = datetime.utcnow()
        result = insert_returning(
            query,
            (
                key,
                value_str,
                value_type,
                encrypted,
                category,
                description,
                editable,
                now,
                now
            )
        )

        if result and result.get('value_type') == 'json':
            try:
                result['value'] = json.loads(result['value'])
            except (json.JSONDecodeError, TypeError):
                pass

        return result

    @classmethod
    def setting_exists(cls, key: str) -> bool:
        """
        Check if setting exists

        Args:
            key: Setting key

        Returns:
            True if setting exists
        """
        query = """
            SELECT EXISTS (
                SELECT 1
                FROM system_settings
                WHERE key = %s
            )
        """

        result = fetch_one(query, (key,))
        return result['exists'] if result else False

    @classmethod
    def get_by_category(cls, category: str) -> List[Dict]:
        """
        Get all settings in a category

        Args:
            category: Category name

        Returns:
            List of setting dicts
        """
        return cls.get_all_settings(category=category)

    @classmethod
    def delete_setting(cls, key: str) -> bool:
        """
        Delete setting by key

        Args:
            key: Setting key

        Returns:
            True if deleted
        """
        query = """
            DELETE FROM system_settings
            WHERE key = %s
        """

        rows_affected = execute_query(query, (key,))
        return rows_affected > 0

    @classmethod
    def get_editable_settings(cls) -> List[Dict]:
        """
        Get all editable settings (for admin UI)

        Returns:
            List of editable setting dicts
        """
        query = """
            SELECT *
            FROM system_settings
            WHERE editable = TRUE
            ORDER BY category, key
        """

        results = fetch_all(query)

        # Parse JSON values
        for result in results:
            if result.get('value_type') == 'json':
                try:
                    result['value'] = json.loads(result['value'])
                except (json.JSONDecodeError, TypeError):
                    pass

        return results
