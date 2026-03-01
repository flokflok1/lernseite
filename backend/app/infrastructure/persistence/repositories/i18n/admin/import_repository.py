"""
i18n Import Repository

Database operations for i18n import process.
- Get namespace IDs from codes
- Create i18n_keys entries (unique per namespace + key_path)
- Create i18n_translations entries (per key + language)
- Handle conflicts (idempotent operations)
- Track import statistics

Uses BaseRepository pattern - direct SQL with psycopg3, no ORM.

Example:
    # Get namespace
    namespace_id = I18nImportRepository.get_namespace_id('admin')

    # Create key
    key_id = await I18nImportRepository.create_key(namespace_id, 'admin.roles.loadFailed')

    # Create translation
    translation_id = await I18nImportRepository.create_translation(
        key_id,
        'de',
        'Rollen konnten nicht geladen werden'
    )

ISO/IEC/IEEE 26515:2018 compliant
"""

from typing import Optional, Dict, List, Any
from uuid import UUID
import logging

from app.infrastructure.persistence.repositories.core.base import BaseRepository

logger = logging.getLogger(__name__)


class I18nImportRepository(BaseRepository):
    """Repository for i18n import database operations"""

    @staticmethod
    def get_namespace_id(namespace_code: str) -> Optional[int]:
        """
        Get namespace ID by code

        Args:
            namespace_code: e.g. 'admin', 'common', 'windows'

        Returns:
            namespace_id (int) or None if not found
        """
        query = """
            SELECT namespace_id
            FROM translations.i18n_namespaces
            WHERE namespace_code = %s
        """
        result = I18nImportRepository.fetch_one(query, (namespace_code,))
        return result['namespace_id'] if result else None

    @staticmethod
    def get_all_namespaces() -> Dict[str, int]:
        """
        Get all namespaces as mapping code → id

        Returns:
            {
              'admin': 1,
              'common': 2,
              'windows': 3,
              ...
            }
        """
        query = """
            SELECT namespace_code, namespace_id
            FROM translations.i18n_namespaces
            WHERE is_active = true
            ORDER BY namespace_code
        """
        results = I18nImportRepository.fetch_all(query)
        return {row['namespace_code']: row['namespace_id'] for row in results}

    @staticmethod
    def create_key(namespace_id: int, key_path: str, context: Optional[str] = None) -> Optional[str]:
        """
        Create i18n_key entry (idempotent)

        If key already exists for namespace, returns existing key_id.

        Args:
            namespace_id: Namespace ID
            key_path: e.g. 'admin.roles.loadFailed'
            context: Optional context for translation (e.g. plural forms info)

        Returns:
            key_id (UUID string) or None on failure
        """
        query = """
            INSERT INTO translations.i18n_keys (namespace_id, key_path, context)
            VALUES (%s, %s, %s)
            ON CONFLICT (namespace_id, key_path) DO NOTHING
            RETURNING key_id
        """
        try:
            result = I18nImportRepository.fetch_one(
                query,
                (namespace_id, key_path, context)
            )
            if result:
                return str(result['key_id'])

            # If insert returned nothing, key already exists - fetch it
            query_existing = """
                SELECT key_id FROM translations.i18n_keys
                WHERE namespace_id = %s AND key_path = %s
            """
            existing = I18nImportRepository.fetch_one(
                query_existing,
                (namespace_id, key_path)
            )
            return str(existing['key_id']) if existing else None

        except Exception as e:
            logger.error(f"Failed to create i18n key {key_path}: {str(e)}")
            return None

    @staticmethod
    def create_translation(
        key_id: str,
        language_code: str,
        value: str,
        source: str = 'import',
        status: str = 'active'
    ) -> Optional[str]:
        """
        Create i18n_translation entry (idempotent)

        If translation already exists for key + language, updates it.

        Args:
            key_id: UUID of i18n_key
            language_code: e.g. 'de', 'en', 'pl'
            value: The translated text
            source: 'manual' | 'deepl' | 'google' | 'community' | 'ai' | 'import'
            status: 'draft' | 'active' | 'needs_review' | 'outdated'

        Returns:
            translation_id (UUID string) or None on failure
        """
        query = """
            INSERT INTO translations.i18n_translations
            (key_id, language_code, value, source, status)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (key_id, language_code) DO UPDATE SET
                value = EXCLUDED.value,
                source = EXCLUDED.source,
                status = EXCLUDED.status,
                updated_at = NOW()
            RETURNING translation_id
        """
        try:
            result = I18nImportRepository.fetch_one(
                query,
                (key_id, language_code, value, source, status)
            )
            return str(result['translation_id']) if result else None

        except Exception as e:
            logger.error(
                f"Failed to create translation for key {key_id} [{language_code}]: {str(e)}"
            )
            return None

    @staticmethod
    def get_import_statistics() -> Dict[str, Any]:
        """
        Get current i18n import statistics

        Returns:
            {
              'total_keys': 345,
              'total_translations': 1035,
              'languages_count': 3,
              'namespaces_count': 8,
              'keys_by_namespace': {
                'admin': 50,
                'common': 15,
                'windows': 48,
                ...
              },
              'translations_by_language': {
                'de': 345,
                'en': 345,
                'pl': 345
              }
            }
        """
        # Total keys
        keys_query = "SELECT COUNT(*) as count FROM translations.i18n_keys"
        keys_result = I18nImportRepository.fetch_one(keys_query)
        total_keys = keys_result['count'] if keys_result else 0

        # Total translations
        trans_query = "SELECT COUNT(*) as count FROM translations.i18n_translations"
        trans_result = I18nImportRepository.fetch_one(trans_query)
        total_translations = trans_result['count'] if trans_result else 0

        # Languages count
        langs_query = """
            SELECT COUNT(DISTINCT language_code) as count
            FROM translations.i18n_translations
        """
        langs_result = I18nImportRepository.fetch_one(langs_query)
        languages_count = langs_result['count'] if langs_result else 0

        # Namespaces count
        ns_query = "SELECT COUNT(*) as count FROM translations.i18n_namespaces WHERE is_active = true"
        ns_result = I18nImportRepository.fetch_one(ns_query)
        namespaces_count = ns_result['count'] if ns_result else 0

        # Keys by namespace
        keys_by_ns_query = """
            SELECT n.namespace_code, COUNT(k.key_id) as count
            FROM translations.i18n_namespaces n
            LEFT JOIN translations.i18n_keys k ON n.namespace_id = k.namespace_id
            WHERE n.is_active = true
            GROUP BY n.namespace_code
            ORDER BY count DESC
        """
        keys_by_ns = {}
        for row in I18nImportRepository.fetch_all(keys_by_ns_query):
            keys_by_ns[row['namespace_code']] = row['count']

        # Translations by language
        trans_by_lang_query = """
            SELECT language_code, COUNT(translation_id) as count
            FROM translations.i18n_translations
            GROUP BY language_code
            ORDER BY language_code
        """
        trans_by_lang = {}
        for row in I18nImportRepository.fetch_all(trans_by_lang_query):
            trans_by_lang[row['language_code']] = row['count']

        return {
            'total_keys': total_keys,
            'total_translations': total_translations,
            'languages_count': languages_count,
            'namespaces_count': namespaces_count,
            'keys_by_namespace': keys_by_ns,
            'translations_by_language': trans_by_lang
        }

    @staticmethod
    def delete_all_imports() -> bool:
        """
        Delete all imported translations (for cleanup/reimport)

        WARNING: This deletes all i18n_translations and i18n_keys!
        Use only for testing or controlled reimport.

        Returns:
            True if successful
        """
        try:
            # Delete translations first (foreign key constraint)
            I18nImportRepository.execute(
                "DELETE FROM translations.i18n_translations"
            )
            # Delete keys
            I18nImportRepository.execute(
                "DELETE FROM translations.i18n_keys"
            )
            logger.warning("Deleted all i18n_translations and i18n_keys")
            return True
        except Exception as e:
            logger.error(f"Failed to delete imports: {str(e)}")
            return False

    @staticmethod
    def validate_import_complete() -> Dict[str, Any]:
        """
        Validate that import is complete for all primary languages

        Checks:
        - All primary languages (de, en, pl) have same number of keys
        - No null values in translations
        - All keys have translations for all languages

        Returns:
            {
              'is_complete': True | False,
              'issues': ['issue 1', 'issue 2', ...],
              'summary': {...}
            }
        """
        issues = []
        primary_langs = ['de', 'en', 'pl']

        # Check translation counts per language
        counts_query = """
            SELECT language_code, COUNT(translation_id) as count
            FROM translations.i18n_translations
            WHERE language_code = ANY(%s)
            GROUP BY language_code
            ORDER BY language_code
        """
        results = I18nImportRepository.fetch_all(counts_query, (primary_langs,))
        counts = {row['language_code']: row['count'] for row in results}

        # All languages should have same count
        unique_counts = set(counts.values())
        if len(unique_counts) > 1:
            issues.append(f"Languages have different translation counts: {counts}")

        # Check for null values
        null_query = """
            SELECT COUNT(*) as count FROM translations.i18n_translations
            WHERE value IS NULL OR value = ''
        """
        null_result = I18nImportRepository.fetch_one(null_query)
        if null_result and null_result['count'] > 0:
            issues.append(f"Found {null_result['count']} empty/null translations")

        # Check for keys missing translations
        missing_query = """
            SELECT k.key_id, k.key_path, COUNT(t.translation_id) as trans_count
            FROM translations.i18n_keys k
            LEFT JOIN translations.i18n_translations t ON k.key_id = t.key_id
            WHERE t.language_code = ANY(%s)
            GROUP BY k.key_id, k.key_path
            HAVING COUNT(t.translation_id) < %s
            LIMIT 10
        """
        missing = I18nImportRepository.fetch_all(missing_query, (primary_langs, len(primary_langs)))
        if missing:
            issues.append(f"Found {len(missing)} keys missing translations for some languages")

        return {
            'is_complete': len(issues) == 0,
            'issues': issues,
            'summary': {
                'translations_per_language': counts,
                'total_keys': I18nImportRepository.fetch_one(
                    "SELECT COUNT(*) as count FROM translations.i18n_keys"
                )['count']
            }
        }


# Export for use in Setup Wizard
__all__ = ['I18nImportRepository']
