"""
i18n Languages Module
=====================
Language metadata, progress tracking, and primary language management.
"""

from typing import Optional, Dict, Any, List
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all
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
            query = "SELECT language_code FROM supported_languages WHERE is_primary = TRUE LIMIT 1"
            result = fetch_one(query)
            if result:
                LanguageManager._primary_language = result['language_code']
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

        primary_lang = LanguageManager.get_primary_language()

        try:
            # Get total keys count
            key_count_query = "SELECT COUNT(*) as cnt FROM i18n_keys WHERE TRUE"
            key_count_result = fetch_one(key_count_query)
            total_keys = key_count_result['cnt'] if key_count_result else 0

            query = """
                SELECT
                    sl.language_code,
                    sl.language_name,
                    sl.native_name,
                    sl.flag_emoji,
                    COALESCE(sl.is_primary, FALSE) as is_primary,
                    COALESCE(sl.priority, 100) as priority,
                    sl.fallback_language,
                    COALESCE(sl.rtl, FALSE) as rtl,
                    sl.active,
                    %s as total_keys,
                    COALESCE(trans_count.cnt, 0) as translated_keys,
                    CASE WHEN %s > 0 THEN ROUND(COALESCE(trans_count.cnt, 0) * 100.0 / %s) ELSE 0 END as completion_percent,
                    0 as verified_keys,
                    0 as pending_suggestions
                FROM supported_languages sl
                LEFT JOIN (
                    SELECT language_code, COUNT(*) as cnt
                    FROM i18n_translations
                    GROUP BY language_code
                ) trans_count ON sl.language_code = trans_count.language_code
                WHERE sl.active = TRUE
                ORDER BY sl.priority, sl.language_name
            """
            result = fetch_all(query, (total_keys, total_keys, total_keys))
            languages = result if result else []

            CacheService.cache_set(cache_key, languages, 300)
            return languages
        except Exception as e:
            logger.error(f"Error fetching languages: {e}")
            return []

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
            # Get total keys count
            key_count_query = "SELECT COUNT(*) as cnt FROM i18n_keys WHERE TRUE"
            key_count_result = fetch_one(key_count_query)
            total_keys = key_count_result['cnt'] if key_count_result else 0

            query = """
                SELECT
                    sl.language_code,
                    sl.language_name,
                    sl.native_name,
                    sl.flag_emoji,
                    COALESCE(sl.is_primary, FALSE) as is_primary,
                    COALESCE(sl.priority, 100) as priority,
                    sl.fallback_language,
                    sl.active,
                    %s as total_keys,
                    COALESCE(trans_count.cnt, 0) as translated_keys,
                    CASE WHEN %s > 0 THEN ROUND(COALESCE(trans_count.cnt, 0) * 100.0 / %s) ELSE 0 END as completion_percent
                FROM supported_languages sl
                LEFT JOIN (
                    SELECT language_code, COUNT(*) as cnt
                    FROM i18n_translations
                    WHERE language_code = %s
                    GROUP BY language_code
                ) trans_count ON sl.language_code = trans_count.language_code
                WHERE sl.language_code = %s
            """
            progress = fetch_one(query, (total_keys, total_keys, total_keys, language_code, language_code))

            if not progress:
                return None

            return {
                'progress': progress,
                'missing_sample': []
            }
        except Exception as e:
            logger.error(f"Error fetching language progress: {e}")
            return None
