"""
i18n Suggestions Module
=======================
Translation suggestions and community voting system.
"""

from typing import Optional, Dict, Any, List
from app.database.connection import fetch_one, fetch_all, execute_query
import logging

logger = logging.getLogger(__name__)


class SuggestionManager:
    """Manages translation suggestions and voting."""

    @staticmethod
    def submit_suggestion(
        user_id: str,
        language_code: str,
        suggested_value: str,
        translation_id: Optional[str] = None,
        key_id: Optional[str] = None,
        reason: Optional[str] = None,
        invalidate_cache=None
    ) -> Optional[str]:
        """
        Submit a translation suggestion.

        Args:
            user_id: Submitter user ID
            language_code: Target language code
            suggested_value: Suggested translation value
            translation_id: Optional existing translation ID
            key_id: Optional key ID
            reason: Optional reason for suggestion
            invalidate_cache: Optional callback to invalidate cache

        Returns:
            Suggestion ID or None on error
        """
        try:
            query = """
                INSERT INTO i18n_suggestions
                    (translation_id, key_id, language_code, suggested_value, reason, suggested_by)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING suggestion_id
            """
            result = fetch_one(query, (
                translation_id, key_id, language_code, suggested_value, reason, user_id
            ))

            if result:
                if invalidate_cache:
                    invalidate_cache(language_code)
                return str(result['suggestion_id'])

            return None
        except Exception as e:
            logger.error(f"Error submitting suggestion: {e}")
            return None

    @staticmethod
    def vote_suggestion(user_id: str, suggestion_id: str, vote_type: str) -> bool:
        """
        Vote for a translation suggestion.

        Args:
            user_id: Voting user ID
            suggestion_id: Target suggestion ID
            vote_type: Vote type ('up' or 'down')

        Returns:
            True if successful
        """
        try:
            query = """
                INSERT INTO i18n_suggestion_votes (suggestion_id, user_id, vote_type)
                VALUES (%s, %s, %s)
                ON CONFLICT (suggestion_id, user_id)
                DO UPDATE SET vote_type = EXCLUDED.vote_type
            """
            execute_query(query, (suggestion_id, user_id, vote_type))
            return True
        except Exception as e:
            logger.error(f"Error voting suggestion: {e}")
            return False

    @staticmethod
    def get_suggestions(
        language_code: Optional[str] = None,
        status: str = 'pending',
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get translation suggestions.

        Args:
            language_code: Optional language filter
            status: Suggestion status ('pending', 'approved', 'rejected')
            limit: Max results

        Returns:
            List of suggestion records
        """
        try:
            query = """
                SELECT
                    s.suggestion_id,
                    s.translation_id,
                    s.key_id,
                    s.language_code,
                    s.suggested_value,
                    s.reason,
                    s.suggested_by,
                    u.username as suggested_by_username,
                    s.suggested_at,
                    s.votes_up,
                    s.votes_down,
                    s.vote_score,
                    s.status,
                    t.value as current_value,
                    COALESCE(k.key_path, '') as key_path
                FROM i18n_suggestions s
                LEFT JOIN users u ON s.suggested_by = u.user_id
                LEFT JOIN i18n_translations t ON s.translation_id = t.translation_id
                LEFT JOIN i18n_keys k ON COALESCE(s.key_id, t.key_id) = k.key_id
                WHERE s.status = %s
                AND (%s IS NULL OR s.language_code = %s)
                ORDER BY s.vote_score DESC, s.suggested_at DESC
                LIMIT %s
            """
            return fetch_all(query, (status, language_code, language_code, limit)) or []
        except Exception as e:
            logger.error(f"Error fetching suggestions: {e}")
            return []

    @staticmethod
    def request_translation(
        user_id: str,
        target_language: str,
        scope: str = 'full',
        namespace_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Request translation for a language (on-demand).

        Args:
            user_id: Requesting user ID
            target_language: Target language code
            scope: Translation scope ('full' or 'namespace')
            namespace_id: Optional namespace for scoped requests

        Returns:
            Request info with ID and count or None on error
        """
        try:
            check_query = """
                SELECT request_id, request_count
                FROM i18n_translation_requests
                WHERE target_language = %s AND scope = %s
                AND status IN ('pending', 'processing')
            """
            existing = fetch_one(check_query, (target_language, scope))

            if existing:
                update_query = """
                    UPDATE i18n_translation_requests
                    SET request_count = request_count + 1, priority = priority + 1
                    WHERE request_id = %s
                    RETURNING request_id, request_count
                """
                result = fetch_one(update_query, (existing['request_id'],))
            else:
                insert_query = """
                    INSERT INTO i18n_translation_requests
                        (target_language, scope, namespace_id, requested_by)
                    VALUES (%s, %s, %s, %s)
                    RETURNING request_id, request_count
                """
                result = fetch_one(insert_query, (
                    target_language, scope, namespace_id, user_id
                ))

            return result
        except Exception as e:
            logger.error(f"Error requesting translation: {e}")
            return None
