"""
LernsystemX User Preferences Repository

Repository for user-specific preferences including:
- Window sizes (admin desktop)
- UI settings (taskbar, sidebars, etc.)
- General preferences

Phase: Admin Desktop OS - User Preferences Persistence
"""

from typing import Optional, Dict, Any
import json

from app.repositories.base_repository import BaseRepository
from app.database.connection import fetch_one, execute_query


class UserPreferencesRepository(BaseRepository):
    """Repository for user preferences management"""

    table_name = 'user_preferences'
    pk_column = 'preference_id'

    @classmethod
    def get_by_user_id(cls, user_id: str) -> Optional[Dict]:
        """
        Get preferences for a user.
        Returns None if no preferences exist yet.

        Args:
            user_id: UUID of the user

        Returns:
            Preferences dict or None
        """
        query = """
            SELECT
                preference_id,
                user_id,
                window_sizes,
                ui_settings,
                general_settings,
                created_at,
                updated_at
            FROM user_preferences
            WHERE user_id = %s
        """
        return fetch_one(query, (user_id,))

    @classmethod
    def get_or_create(cls, user_id: str) -> Dict:
        """
        Get preferences for a user, creating an empty record if none exists.

        Args:
            user_id: UUID of the user

        Returns:
            Preferences dict (always returns a valid dict)
        """
        existing = cls.get_by_user_id(user_id)
        if existing:
            return existing

        # Create new preferences for user
        return cls.create({
            'user_id': user_id,
            'window_sizes': {},
            'ui_settings': {},
            'general_settings': {}
        })

    @classmethod
    def get_window_sizes(cls, user_id: str) -> Dict[str, Dict[str, int]]:
        """
        Get window sizes for a user.

        Args:
            user_id: UUID of the user

        Returns:
            Dict mapping window_type to {width, height}
            e.g. {"admin-model-selector": {"width": 800, "height": 600}}
        """
        prefs = cls.get_by_user_id(user_id)
        if prefs and prefs.get('window_sizes'):
            return prefs['window_sizes']
        return {}

    @classmethod
    def update_window_size(
        cls,
        user_id: str,
        window_type: str,
        width: int,
        height: int
    ) -> Dict:
        """
        Update a single window size for a user.
        Uses JSONB merge to only update the specified window type.

        Args:
            user_id: UUID of the user
            window_type: Type of window (e.g. 'admin-model-selector')
            width: Window width in pixels
            height: Window height in pixels

        Returns:
            Updated preferences dict
        """
        # Use UPSERT with JSONB concatenation
        query = """
            INSERT INTO user_preferences (user_id, window_sizes, ui_settings, general_settings)
            VALUES (%s, %s::jsonb, '{}'::jsonb, '{}'::jsonb)
            ON CONFLICT (user_id)
            DO UPDATE SET
                window_sizes = user_preferences.window_sizes || %s::jsonb,
                updated_at = NOW()
            RETURNING *
        """

        # Create the window size object
        window_size_json = json.dumps({window_type: {'width': width, 'height': height}})

        result = fetch_one(query, (user_id, window_size_json, window_size_json))
        return result

    @classmethod
    def update_window_sizes(cls, user_id: str, window_sizes: Dict[str, Dict[str, int]]) -> Dict:
        """
        Update all window sizes for a user (replaces entire window_sizes object).

        Args:
            user_id: UUID of the user
            window_sizes: Dict of window_type -> {width, height}

        Returns:
            Updated preferences dict
        """
        query = """
            INSERT INTO user_preferences (user_id, window_sizes, ui_settings, general_settings)
            VALUES (%s, %s::jsonb, '{}'::jsonb, '{}'::jsonb)
            ON CONFLICT (user_id)
            DO UPDATE SET
                window_sizes = %s::jsonb,
                updated_at = NOW()
            RETURNING *
        """

        window_sizes_json = json.dumps(window_sizes)
        result = fetch_one(query, (user_id, window_sizes_json, window_sizes_json))
        return result

    @classmethod
    def update_ui_settings(cls, user_id: str, ui_settings: Dict[str, Any]) -> Dict:
        """
        Update UI settings for a user (merges with existing settings).

        Args:
            user_id: UUID of the user
            ui_settings: UI settings to merge

        Returns:
            Updated preferences dict
        """
        query = """
            INSERT INTO user_preferences (user_id, window_sizes, ui_settings, general_settings)
            VALUES (%s, '{}'::jsonb, %s::jsonb, '{}'::jsonb)
            ON CONFLICT (user_id)
            DO UPDATE SET
                ui_settings = user_preferences.ui_settings || %s::jsonb,
                updated_at = NOW()
            RETURNING *
        """

        ui_settings_json = json.dumps(ui_settings)
        result = fetch_one(query, (user_id, ui_settings_json, ui_settings_json))
        return result

    @classmethod
    def update_general_settings(cls, user_id: str, general_settings: Dict[str, Any]) -> Dict:
        """
        Update general settings for a user (merges with existing settings).

        Args:
            user_id: UUID of the user
            general_settings: General settings to merge

        Returns:
            Updated preferences dict
        """
        query = """
            INSERT INTO user_preferences (user_id, window_sizes, ui_settings, general_settings)
            VALUES (%s, '{}'::jsonb, '{}'::jsonb, %s::jsonb)
            ON CONFLICT (user_id)
            DO UPDATE SET
                general_settings = user_preferences.general_settings || %s::jsonb,
                updated_at = NOW()
            RETURNING *
        """

        general_settings_json = json.dumps(general_settings)
        result = fetch_one(query, (user_id, general_settings_json, general_settings_json))
        return result

    @classmethod
    def delete_window_size(cls, user_id: str, window_type: str) -> Optional[Dict]:
        """
        Remove a specific window size from user preferences.

        Args:
            user_id: UUID of the user
            window_type: Type of window to remove

        Returns:
            Updated preferences dict or None if not found
        """
        query = """
            UPDATE user_preferences
            SET
                window_sizes = window_sizes - %s,
                updated_at = NOW()
            WHERE user_id = %s
            RETURNING *
        """

        return fetch_one(query, (window_type, user_id))

    @classmethod
    def reset_preferences(cls, user_id: str) -> Optional[Dict]:
        """
        Reset all preferences for a user to defaults.

        Args:
            user_id: UUID of the user

        Returns:
            Reset preferences dict or None if not found
        """
        query = """
            UPDATE user_preferences
            SET
                window_sizes = '{}'::jsonb,
                ui_settings = '{}'::jsonb,
                general_settings = '{}'::jsonb,
                updated_at = NOW()
            WHERE user_id = %s
            RETURNING *
        """

        return fetch_one(query, (user_id,))
