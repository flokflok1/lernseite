"""
i18n Suggestions Module
=======================
Translation suggestions and community voting system.
"""

from typing import Optional, Dict, Any, List
from app.infrastructure.persistence.repositories.i18n.translations.service_queries import I18nSuggestionQueriesRepository
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
            result = I18nSuggestionQueriesRepository.submit_suggestion(
                translation_id=translation_id,
                key_id=key_id,
                language_code=language_code,
                suggested_value=suggested_value,
                user_id=user_id,
                reason=reason
            )

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
            I18nSuggestionQueriesRepository.vote_suggestion(suggestion_id, user_id, vote_type)
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
            return I18nSuggestionQueriesRepository.get_suggestions(
                status=status,
                language_code=language_code,
                limit=limit
            )
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
            existing = I18nSuggestionQueriesRepository.get_pending_request(target_language, scope)

            if existing:
                result = I18nSuggestionQueriesRepository.increment_request_count(existing['request_id'])
            else:
                result = I18nSuggestionQueriesRepository.create_translation_request(
                    target_language, scope, namespace_id, user_id
                )

            return result
        except Exception as e:
            logger.error(f"Error requesting translation: {e}")
            return None
