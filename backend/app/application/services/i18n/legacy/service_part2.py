"""
i18n Service - Secondary Operations (Part 2)

Implements:
- API backward-compatibility aliases
- Language progress statistics
- Community translation suggestions (voting, creating)

Split from service.py to comply with Quality Gate G01 (max 500 lines per file).
"""

from typing import Optional, Dict, Any, List
import logging

from app.infrastructure.persistence.database import get_connection

logger = logging.getLogger(__name__)


class I18nServicePart2:
    """
    i18n Service Part 2 - Secondary operations.

    Contains:
    - API aliases for backward compatibility
    - Language progress reporting
    - Community translation suggestions
    """

    # =========================================================================
    # API ALIASES (for backward compatibility with different API versions)
    # =========================================================================

    @classmethod
    def get_bundle(
        cls,
        language_code: str,
        namespace_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Alias for get_translation_bundle() for backward compatibility."""
        return cls.get_translation_bundle(language_code, namespace_code)

    @classmethod
    def get_languages(cls) -> List[Dict[str, Any]]:
        """Alias for get_supported_languages() for backward compatibility."""
        return cls.get_supported_languages()

    # =========================================================================
    # LANGUAGE PROGRESS
    # =========================================================================

    @classmethod
    def get_language_progress(cls, language_code: str) -> Optional[Dict[str, Any]]:
        """
        Get translation progress for a language.

        Returns stats about how many translations are complete vs pending.

        Args:
            language_code: Language code

        Returns:
            Dict with progress statistics or None if language not found
        """
        try:
            from app.infrastructure.persistence.repositories.i18n.repository import (
                I18nRepository,
            )

            with get_connection() as conn:
                repo = I18nRepository(conn)
                languages = repo.get_supported_languages()

                # Find the language
                language = next(
                    (l for l in languages if l.get('language_code') == language_code),
                    None
                )

                if not language:
                    return None

                # Get translation stats
                all_translations = repo.get_translations_for_language(
                    language_code, limit=10000
                )
                pending = len(
                    [t for t in all_translations if t.get('status') == 'pending']
                )
                approved = len(
                    [t for t in all_translations if t.get('status') == 'approved']
                )

                total = len(all_translations)
                percentage = round(
                    (approved / total * 100) if total else 0, 2
                )

                return {
                    'language_code': language_code,
                    'language_name': language.get('name'),
                    'total': total,
                    'approved': approved,
                    'pending': pending,
                    'percentage': percentage,
                }

        except Exception as e:
            logger.error(
                f"Error getting language progress for {language_code}: {e}"
            )
            return None

    # =========================================================================
    # TRANSLATION SUGGESTIONS (Community contributions)
    # =========================================================================

    @classmethod
    def get_pending_suggestions(
        cls,
        language_code: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get pending community translation suggestions.

        Args:
            language_code: Optional language filter
            limit: Max results (default 100, max 500)

        Returns:
            List of pending suggestions with voting data
        """
        try:
            from app.infrastructure.persistence.repositories.i18n.repository import (
                I18nRepository,
            )

            with get_connection() as conn:
                repo = I18nRepository(conn)
                suggestions = repo.get_pending_suggestions(
                    language_code, min(limit, 500)
                )

            return suggestions

        except Exception as e:
            logger.error(f"Error getting pending suggestions: {e}")
            return []

    @classmethod
    def suggest_translation(
        cls,
        namespace_code: str,
        key_path: str,
        language_code: str,
        suggested_text: str,
        user_id: str,
        reason: str = ""
    ) -> Dict[str, Any]:
        """
        Create a new translation suggestion from community member.

        Args:
            namespace_code: Namespace code
            key_path: Key path
            language_code: Target language
            suggested_text: Suggested translation
            user_id: User creating suggestion
            reason: Optional reason for suggestion

        Returns:
            Created suggestion data

        Raises:
            ValueError: If parameters invalid
        """
        if not suggested_text or not suggested_text.strip():
            raise ValueError("Suggestion text cannot be empty")

        try:
            from app.infrastructure.persistence.repositories.i18n.repository import (
                I18nRepository,
            )

            with get_connection() as conn:
                repo = I18nRepository(conn)

                suggestion = repo.create_suggestion(
                    namespace_code=namespace_code,
                    key_path=key_path,
                    language_code=language_code,
                    suggested_text=suggested_text,
                    suggested_by=user_id,
                    reason=reason
                )

                return suggestion

        except Exception as e:
            logger.error(f"Error creating suggestion: {e}")
            raise

    @classmethod
    def vote_on_suggestion(
        cls,
        suggestion_id: str,
        user_id: str,
        vote_value: int
    ) -> Dict[str, Any]:
        """
        Vote on a translation suggestion (+1 upvote, -1 downvote).

        Args:
            suggestion_id: Suggestion ID
            user_id: User voting
            vote_value: 1 for upvote, -1 for downvote

        Returns:
            Updated suggestion with vote count

        Raises:
            ValueError: If vote_value invalid
        """
        if vote_value not in [-1, 1]:
            raise ValueError("Vote must be 1 (upvote) or -1 (downvote)")

        try:
            from app.infrastructure.persistence.repositories.i18n.repository import (
                I18nRepository,
            )

            with get_connection() as conn:
                repo = I18nRepository(conn)

                suggestion = repo.vote_on_suggestion(
                    suggestion_id=suggestion_id,
                    user_id=user_id,
                    vote_value=vote_value
                )

                return suggestion

        except Exception as e:
            logger.error(f"Error voting on suggestion: {e}")
            raise
