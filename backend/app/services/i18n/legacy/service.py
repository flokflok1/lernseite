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

from app.repositories.i18n_repository import I18nRepository
from app.infrastructure.cache.service import CacheService
from app.database import get_connection

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
