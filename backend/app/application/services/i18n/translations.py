"""
i18n Translations Module
========================
Core translation CRUD operations, bundle retrieval, and caching.
"""

from typing import Optional, Dict, Any, List
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query
from app.infrastructure.cache.service import CacheService
import logging

logger = logging.getLogger(__name__)


class TranslationManager:
    """Manages translation operations and caching."""

    # Cache TTL for bundles (1 hour)
    BUNDLE_CACHE_TTL = 3600

    @staticmethod
    def get_bundle(language_code: str, namespace: Optional[str] = None) -> Dict[str, str]:
        """
        Get translation bundle for a language.
        Uses database function with fallback support.

        Args:
            language_code: ISO language code
            namespace: Optional namespace filter

        Returns:
            Dictionary of translation keys and values
        """
        cache_key = f"i18n:bundle:{language_code}:{namespace or 'all'}"

        # Try cache first
        cached = CacheService.cache_get(cache_key)
        if cached:
            return cached

        try:
            # Cast parameters to varchar for PostgreSQL function call
            query = "SELECT get_i18n_bundle(%s::varchar, %s::varchar) AS bundle"
            result = fetch_one(query, (language_code, namespace))

            if result and result.get('bundle'):
                bundle = result['bundle']
                CacheService.cache_set(cache_key, bundle, TranslationManager.BUNDLE_CACHE_TTL)
                return bundle

            return {}
        except Exception as e:
            logger.error(f"Error fetching i18n bundle: {e}")
            return {}

    @staticmethod
    def get_translation(
        namespace: str,
        key_path: str,
        language_code: str,
        fallback: bool = True
    ) -> Optional[str]:
        """
        Get single translation with optional fallback chain support.

        Args:
            namespace: Translation namespace (e.g., 'common', 'admin')
            key_path: Key path with dot notation (e.g., 'actions.delete')
            language_code: ISO language code (de, en, pl)
            fallback: Enable fallback chain to other languages

        Returns:
            Translation text or None if not found
        """
        try:
            # Get bundle for requested language
            bundle = TranslationManager.get_bundle(language_code, namespace)

            if bundle and key_path in bundle:
                return bundle[key_path]

            # If fallback enabled and not found, try fallback chain
            if fallback:
                # Fallback chain: de -> pl -> en
                fallback_chain = []
                if language_code == 'de':
                    fallback_chain = ['pl', 'en']
                elif language_code == 'pl':
                    fallback_chain = ['de', 'en']
                elif language_code == 'en':
                    fallback_chain = ['de', 'pl']

                for fallback_lang in fallback_chain:
                    fallback_bundle = TranslationManager.get_bundle(fallback_lang, namespace)
                    if fallback_bundle and key_path in fallback_bundle:
                        return fallback_bundle[key_path]

            return None
        except Exception as e:
            logger.error(f"Error fetching translation {namespace}/{key_path}/{language_code}: {e}")
            return None

    @staticmethod
    def get_key_translations(key_id: str) -> List[Dict[str, Any]]:
        """
        Get all translations for a key across all languages.

        Args:
            key_id: The key identifier

        Returns:
            List of translation records with language metadata
        """
        try:
            query = """
                SELECT
                    t.translation_id,
                    t.key_id,
                    t.language_code,
                    sl.language_name,
                    sl.native_name,
                    sl.flag_emoji,
                    t.value,
                    t.is_verified,
                    t.is_machine_translated,
                    t.translator_id,
                    u.username as translator_name,
                    t.created_at,
                    t.updated_at
                FROM i18n_translations t
                JOIN supported_languages sl ON t.language_code = sl.language_code
                LEFT JOIN users u ON t.translator_id = u.user_id
                WHERE t.key_id = %s
                ORDER BY sl.priority, sl.language_code
            """
            return fetch_all(query, (key_id,)) or []
        except Exception as e:
            logger.error(f"Error fetching key translations: {e}")
            return []

    @staticmethod
    def set_translation(
        key_id: str,
        language_code: str,
        value: str,
        translator_id: Optional[str] = None,
        is_machine_translated: bool = False
    ) -> bool:
        """
        Set or update a translation.

        Args:
            key_id: The key identifier
            language_code: Target language code
            value: Translation value
            translator_id: Optional translator user ID
            is_machine_translated: Whether AI-generated

        Returns:
            True if successful
        """
        try:
            source = 'ai' if is_machine_translated else 'manual'
            query = """
                INSERT INTO i18n_translations (key_id, language_code, value, created_by, source)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (key_id, language_code)
                DO UPDATE SET
                    value = EXCLUDED.value,
                    created_by = COALESCE(EXCLUDED.created_by, i18n_translations.created_by),
                    source = EXCLUDED.source,
                    updated_at = NOW()
            """
            execute_query(query, (key_id, language_code, value, translator_id, source))
            TranslationManager.invalidate_cache(language_code)
            return True
        except Exception as e:
            logger.error(f"Error setting translation: {e}")
            return False

    @staticmethod
    def invalidate_cache(language_code: Optional[str] = None):
        """
        Invalidate translation cache.

        Args:
            language_code: Optional specific language to invalidate
        """
        try:
            if language_code:
                CacheService.cache_delete(f"i18n:bundle:{language_code}:all")
            else:
                CacheService.cache_delete("i18n:*")
            CacheService.cache_delete("i18n:languages")
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
