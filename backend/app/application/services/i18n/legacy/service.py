"""
i18n Service - Core Translation Operations

Implements:
- Translation bundle generation (for frontend)
- Language fallback chains
- Caching strategy (Redis)
- Translation CRUD operations
"""

from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

from app.infrastructure.persistence.repositories.i18n_repository import I18nRepository
from app.infrastructure.cache.service import CacheService
from app.infrastructure.persistence.database import get_connection

logger = logging.getLogger(__name__)


class I18nService:
    """
    i18n Service - Core translation operations.

    Manages:
    - Translation bundle generation for frontend
    - Language fallback chains
    - Caching with Redis
    - Translation CRUD operations
    """

    # Cache configuration
    CACHE_TTL = 300  # 5 minutes for translation bundles
    CACHE_PREFIX_BUNDLE = "CACHE:I18N:BUNDLE"
    CACHE_PREFIX_LANGUAGES = "CACHE:I18N:LANGUAGES"
    CACHE_PREFIX_NAMESPACES = "CACHE:I18N:NAMESPACES"

    @classmethod
    def get_translation_bundle(
        cls,
        language_code: str,
        namespace_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get translation bundle for frontend.

        Returns nested dictionary structure for all translations in a language.
        Includes fallback chain support (if translation missing, uses fallback language).

        Args:
            language_code: Language code (e.g., 'de', 'en', 'pl')
            namespace_code: Optional namespace filter (e.g., 'admin', 'common')

        Returns:
            Nested dictionary of translations

        Example:
            >>> bundle = I18nService.get_translation_bundle('de')
            >>> bundle['admin']['users']['title']
            'Benutzer'
        """
        # Generate cache key
        cache_key = f"{cls.CACHE_PREFIX_BUNDLE}:{language_code}:{namespace_code or 'all'}"

        # Try cache first
        cached = CacheService.cache_get(cache_key)
        if cached is not None:
            return cached

        try:
            with get_connection() as conn:
                repo = I18nRepository(conn)

                # Get bundle from database
                bundle = repo.get_translation_bundle(language_code, namespace_code)

            # Cache the result
            CacheService.cache_set(cache_key, bundle, ttl=cls.CACHE_TTL)

            return bundle

        except Exception as e:
            logger.error(f"Error getting translation bundle for {language_code}: {e}")
            return {}

    @classmethod
    def get_supported_languages(cls) -> List[Dict[str, Any]]:
        """
        Get all supported languages (cached).

        Returns:
            List of language configurations with codes, names, priorities

        Example:
            >>> languages = I18nService.get_supported_languages()
            >>> [l['language_code'] for l in languages]
            ['de', 'pl', 'en', ...]
        """
        # Check cache
        cache_key = f"{cls.CACHE_PREFIX_LANGUAGES}:all"
        cached = CacheService.cache_get(cache_key)
        if cached is not None:
            return cached

        try:
            with get_connection() as conn:
                repo = I18nRepository(conn)
                languages = repo.get_supported_languages()

            # Convert datetime fields to ISO strings for JSON serialization
            for lang in languages:
                if 'created_at' in lang and isinstance(lang['created_at'], datetime):
                    lang['created_at'] = lang['created_at'].isoformat()

            # Cache for 1 day (languages don't change often)
            CacheService.cache_set(cache_key, languages, ttl=86400)

            return languages

        except Exception as e:
            logger.error(f"Error getting supported languages: {e}")
            return []

    @classmethod
    def get_primary_languages(cls) -> List[Dict[str, Any]]:
        """
        Get primary languages (translation sources).

        Primary languages are those that translations are created in before
        being translated to other languages.

        Returns:
            List of primary language configurations
        """
        languages = cls.get_supported_languages()
        return [l for l in languages if l.get('is_primary')]

    @classmethod
    def get_language_fallback_chain(cls, language_code: str) -> List[str]:
        """
        Get fallback chain for a language.

        Example: de_DE → de → en (fallback to English if translation missing)

        Args:
            language_code: Language code

        Returns:
            List of language codes in fallback order
        """
        fallback_chain = [language_code]

        try:
            with get_connection() as conn:
                repo = I18nRepository(conn)
                current_lang = language_code

                # Follow fallback chain
                while current_lang:
                    lang_config = repo.get_language(current_lang)
                    if not lang_config:
                        break

                    fallback = lang_config.get('fallback_language_code')
                    if fallback and fallback not in fallback_chain:
                        fallback_chain.append(fallback)
                        current_lang = fallback
                    else:
                        break

        except Exception as e:
            logger.error(f"Error getting fallback chain for {language_code}: {e}")

        return fallback_chain

    @classmethod
    def get_translation(
        cls,
        namespace_code: str,
        key_path: str,
        language_code: str,
        fallback: bool = True
    ) -> Optional[str]:
        """
        Get single translation with optional fallback.

        Args:
            namespace_code: Namespace code
            key_path: Key path (e.g., 'admin.users.title')
            language_code: Language code
            fallback: Use fallback chain if translation missing

        Returns:
            Translated text or None if not found

        Example:
            >>> text = I18nService.get_translation('admin', 'users.title', 'de')
            >>> text
            'Benutzer'
        """
        with get_connection() as conn:
            repo = I18nRepository(conn)

            # Try requested language
            translation = repo.get_translation(namespace_code, key_path, language_code)
            if translation:
                return translation['value']

            # Try fallback chain if enabled
            if fallback:
                fallback_chain = cls.get_language_fallback_chain(language_code)

                for fallback_lang in fallback_chain[1:]:  # Skip first (already tried)
                    translation = repo.get_translation(
                        namespace_code,
                        key_path,
                        fallback_lang
                    )
                    if translation:
                        return translation['value']

            return None

    @classmethod
    def create_translation(
        cls,
        namespace_code: str,
        key_path: str,
        language_code: str,
        translation_text: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create new translation.

        Args:
            namespace_code: Namespace code
            key_path: Key path
            language_code: Language code
            translation_text: Translated text
            user_id: User creating translation (optional)

        Returns:
            Created translation data

        Raises:
            ValueError: If parameters invalid
        """
        if not translation_text or not translation_text.strip():
            raise ValueError("Translation text cannot be empty")

        try:
            with get_connection() as conn:
                repo = I18nRepository(conn)

                # Create translation
                translation = repo.create_translation(
                    namespace_code,
                    key_path,
                    language_code,
                    translation_text,
                    translated_by=user_id
                )

                # Invalidate cache
                cls.invalidate_bundle_cache(language_code)

                return translation

        except Exception as e:
            logger.error(
                f"Error creating translation ({namespace_code}/{key_path}/{language_code}): {e}"
            )
            raise

    # =========================================================================
    # CACHE MANAGEMENT
    # =========================================================================

    @classmethod
    def invalidate_bundle_cache(cls, language_code: str) -> None:
        """
        Invalidate translation bundle cache for a language.

        Call this when translations change to ensure frontend gets latest data.

        Args:
            language_code: Language code to invalidate
        """
        try:
            with get_connection() as conn:
                repo = I18nRepository(conn)
                repo.invalidate_language_cache(language_code)

            # Also invalidate Redis cache
            CacheService.cache_delete_pattern(f"{cls.CACHE_PREFIX_BUNDLE}:{language_code}:*")

            logger.info(f"Translation cache invalidated for language: {language_code}")

        except Exception as e:
            logger.error(f"Error invalidating cache for {language_code}: {e}")

    @classmethod
    def invalidate_all_caches(cls) -> None:
        """Invalidate all translation caches (use sparingly)."""
        try:
            with get_connection() as conn:
                repo = I18nRepository(conn)
                repo.invalidate_all_caches()

            # Also invalidate Redis
            CacheService.cache_delete_pattern(f"{cls.CACHE_PREFIX_BUNDLE}:*")

            logger.info("All translation caches invalidated")

        except Exception as e:
            logger.error(f"Error invalidating all caches: {e}")

    # =========================================================================
    # API ALIASES (for backward compatibility with different API versions)
    # =========================================================================

    @classmethod
    def get_bundle(cls, language_code: str, namespace_code: Optional[str] = None) -> Dict[str, Any]:
        """Alias for get_translation_bundle() for backward compatibility."""
        return cls.get_translation_bundle(language_code, namespace_code)

    @classmethod
    def get_languages(cls) -> List[Dict[str, Any]]:
        """Alias for get_supported_languages() for backward compatibility."""
        return cls.get_supported_languages()

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
                all_translations = repo.get_translations_for_language(language_code, limit=10000)
                pending = len([t for t in all_translations if t.get('status') == 'pending'])
                approved = len([t for t in all_translations if t.get('status') == 'approved'])

                return {
                    'language_code': language_code,
                    'language_name': language.get('name'),
                    'total': len(all_translations),
                    'approved': approved,
                    'pending': pending,
                    'percentage': round((approved / len(all_translations) * 100) if all_translations else 0, 2)
                }

        except Exception as e:
            logger.error(f"Error getting language progress for {language_code}: {e}")
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
            from app.infrastructure.persistence.repositories.i18n_repository import I18nRepository

            with get_connection() as conn:
                repo = I18nRepository(conn)
                suggestions = repo.get_pending_suggestions(language_code, min(limit, 500))

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
            from app.infrastructure.persistence.repositories.i18n_repository import I18nRepository

            with get_connection() as conn:
                repo = I18nRepository(conn)

                # Create suggestion
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
            from app.infrastructure.persistence.repositories.i18n_repository import I18nRepository

            with get_connection() as conn:
                repo = I18nRepository(conn)

                # Record vote
                suggestion = repo.vote_on_suggestion(
                    suggestion_id=suggestion_id,
                    user_id=user_id,
                    vote_value=vote_value
                )

                return suggestion

        except Exception as e:
            logger.error(f"Error voting on suggestion: {e}")
            raise
