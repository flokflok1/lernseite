"""
i18n Languages Module
=====================
Language metadata, progress tracking, and primary language management.
"""

from typing import Optional, Dict, Any, List
from app.infrastructure.persistence.repositories.i18n.translations.service_queries import I18nLanguageStatsRepository
from app.infrastructure.cache.service import CacheService
import logging

logger = logging.getLogger(__name__)


class LanguageManager:
    """Manages language metadata and translation progress."""

    # Cached primary language code
    _primary_language: Optional[str] = None

    @staticmethod
    def get_primary_language() -> str:
        """
        Get the primary language code from database (cached).

        Returns:
            Language code (defaults to 'de' if not found)
        """
        if LanguageManager._primary_language:
            return LanguageManager._primary_language

        try:
            code = I18nLanguageStatsRepository.get_primary_language_code()
            if code:
                LanguageManager._primary_language = code
                return LanguageManager._primary_language
        except Exception as e:
            logger.warning(f"Could not fetch primary language: {e}")

        # Fallback to German
        return 'de'

    @staticmethod
    def invalidate_primary_language_cache():
        """Clear cached primary language."""
        LanguageManager._primary_language = None

    @staticmethod
    def get_languages() -> List[Dict[str, Any]]:
        """
        Get all available languages with progress statistics.

        Returns:
            List of language records with translation progress
        """
        cache_key = "i18n:languages"

        cached = CacheService.cache_get(cache_key)
        if cached:
            return cached

        try:
            languages = I18nLanguageStatsRepository.get_languages_with_progress(active_only=True)
            CacheService.cache_set(cache_key, languages, 300)
            return languages
        except Exception as e:
            logger.error(f"Error fetching languages: {e}")
            return []

    @staticmethod
    def get_all_languages() -> List[Dict[str, Any]]:
        """
        Get ALL languages (including inactive) for admin management.

        Returns:
            List of all language records with progress statistics
        """
        cache_key = "i18n:languages:all"

        cached = CacheService.cache_get(cache_key)
        if cached:
            return cached

        try:
            languages = I18nLanguageStatsRepository.get_languages_with_progress(active_only=False)
            CacheService.cache_set(cache_key, languages, 300)
            return languages
        except Exception as e:
            logger.error(f"Error fetching all languages: {e}")
            return []

    @staticmethod
    def set_primary_language(language_code: str) -> bool:
        """
        Set a language as the primary (default) language.

        Args:
            language_code: The language code to set as primary

        Returns:
            True if successful, False otherwise
        """
        try:
            I18nLanguageStatsRepository.set_primary_language(language_code)
            LanguageManager.invalidate_primary_language_cache()
            CacheService.cache_delete("i18n:languages")
            CacheService.cache_delete("i18n:languages:all")
            return True
        except Exception as e:
            logger.error(f"Error setting primary language to {language_code}: {e}")
            return False

    @staticmethod
    def get_language_progress(language_code: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed progress for a specific language.

        Args:
            language_code: The target language code

        Returns:
            Progress information with translation statistics
        """
        try:
            progress = I18nLanguageStatsRepository.get_language_progress(language_code)

            if not progress:
                return None

            return {
                'progress': progress,
                'missing_sample': []
            }
        except Exception as e:
            logger.error(f"Error fetching language progress: {e}")
            return None
