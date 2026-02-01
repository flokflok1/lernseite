"""
i18n Config Module
==================
AI moderation configuration and moderation dashboard.
"""

from typing import Dict, Any, Optional, List
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages i18n AI configuration and moderation settings."""

    @staticmethod
    def get_ai_config() -> Dict[str, Any]:
        """
        Get AI moderation configuration.

        Returns:
            Dictionary of configuration key-value pairs
        """
        try:
            query = "SELECT config_key, config_value FROM i18n_ai_config"
            rows = fetch_all(query) or []
            return {row['config_key']: row['config_value'] for row in rows}
        except Exception as e:
            logger.error(f"Error fetching AI config: {e}")
            return {}

    @staticmethod
    def update_ai_config(config_key: str, config_value: Any, user_id: str) -> bool:
        """
        Update a single AI config value.

        Args:
            config_key: The config key to update (e.g., 'moderation_model')
            config_value: The new value (will be stored as JSONB)
            user_id: The user making the change

        Returns:
            True if successful
        """
        try:
            import json
            # Convert value to JSON string for JSONB storage
            json_value = json.dumps(config_value)

            query = """
                INSERT INTO i18n_ai_config (config_key, config_value, updated_by, updated_at)
                VALUES (%s, %s::jsonb, %s, NOW())
                ON CONFLICT (config_key) DO UPDATE SET
                    config_value = EXCLUDED.config_value,
                    updated_by = EXCLUDED.updated_by,
                    updated_at = NOW()
            """
            execute_query(query, (config_key, json_value, user_id))
            logger.info(f"Updated i18n config '{config_key}' by user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating AI config '{config_key}': {e}")
            return False

    @staticmethod
    def get_moderation_dashboard() -> List[Dict[str, Any]]:
        """
        Get moderation dashboard data.

        Returns:
            List of moderation dashboard entries by language
        """
        try:
            query = """
                SELECT
                    sl.language_code,
                    sl.language_name,
                    sl.flag as flag_emoji,
                    0 AS pending_count,
                    0 AS ai_reviewing_count,
                    0 AS awaiting_human_count,
                    0 AS pending_suggestions,
                    0 AS ai_reviews_24h,
                    NULL AS avg_quality_7d
                FROM translations.supported_languages sl
                WHERE sl.is_active = TRUE
                ORDER BY sl.priority
            """
            return fetch_all(query) or []
        except Exception as e:
            logger.error(f"Error fetching moderation dashboard: {e}")
            return []

    @staticmethod
    def get_moderation_queue(
        status: Optional[str] = None,
        language_code: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get moderation queue items.

        Args:
            status: Optional status filter
            language_code: Optional language filter
            limit: Max results

        Returns:
            List of queue items (currently empty stub)
        """
        return []

    @staticmethod
    def review_queue_item(
        queue_id: str,
        user_id: str,
        decision: str,
        comment: Optional[str] = None
    ) -> bool:
        """
        Human review of a queue item.

        Args:
            queue_id: Queue item ID
            user_id: Reviewing user ID
            decision: Review decision
            comment: Optional comment

        Returns:
            True if successful (currently stub)
        """
        return True
