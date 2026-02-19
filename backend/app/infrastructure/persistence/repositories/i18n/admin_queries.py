"""
i18n Admin Query Repository - SQL for admin translation endpoints.

Provides static methods for translation management:
- Language verification
- Key upsert
- Translation counting for bulk operations
- Batch fetching for bulk translation
- Target language name lookup
- Review listing (paginated with source comparison)
- Translation editing and verification
- Namespace listing
- Key upsert for seed operations
- Namespace creation
"""

from typing import Optional, Dict, List, Tuple

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query
)


class I18nAdminQueryRepository:
    """SQL queries for admin translation management endpoints."""

    @staticmethod
    def language_exists(language_code: str) -> Optional[Dict]:
        """Check if a language exists in supported_languages."""
        return fetch_one(
            "SELECT language_code FROM translations.supported_languages WHERE language_code = %s",
            (language_code,)
        )

    @staticmethod
    def upsert_key(namespace_code: str, key_path: str, default_value: str) -> Optional[Dict]:
        """Upsert an i18n key, returning key_id and whether it was inserted."""
        return fetch_one(
            """
            INSERT INTO translations.i18n_keys (namespace_code, key_path, default_value)
            VALUES (%s, %s, %s)
            ON CONFLICT (namespace_code, key_path) DO UPDATE SET updated_at = NOW()
            RETURNING key_id, (xmax = 0) AS was_inserted
            """,
            (namespace_code, key_path, default_value)
        )

    @staticmethod
    def count_keys_needing_translation(
        source_language: str,
        target_language: str,
        namespace_code: Optional[str] = None
    ) -> int:
        """Count keys that have source translation but not target."""
        query = """
            SELECT COUNT(*) AS total
            FROM translations.i18n_keys k
            WHERE k.is_active = TRUE
            AND EXISTS (
                SELECT 1 FROM translations.i18n_translations t
                WHERE t.key_id = k.key_id AND t.language_code = %s
            )
            AND NOT EXISTS (
                SELECT 1 FROM translations.i18n_translations t
                WHERE t.key_id = k.key_id AND t.language_code = %s
            )
        """
        params = [source_language, target_language]
        if namespace_code:
            query += " AND k.namespace_code = %s"
            params.append(namespace_code)

        result = fetch_one(query, tuple(params))
        return result['total'] if result else 0

    @staticmethod
    def fetch_keys_needing_translation(
        source_language: str,
        target_language: str,
        namespace_code: Optional[str] = None,
        batch_size: int = 50
    ) -> List[Dict]:
        """Fetch a batch of keys needing translation."""
        query = """
            SELECT k.key_id, k.key_path, k.namespace_code,
                   t.translated_value AS source_value
            FROM translations.i18n_keys k
            JOIN translations.i18n_translations t
                ON t.key_id = k.key_id AND t.language_code = %s
            WHERE k.is_active = TRUE
            AND NOT EXISTS (
                SELECT 1 FROM translations.i18n_translations t2
                WHERE t2.key_id = k.key_id AND t2.language_code = %s
            )
        """
        params = [source_language, target_language]
        if namespace_code:
            query += " AND k.namespace_code = %s"
            params.append(namespace_code)
        query += " ORDER BY k.namespace_code, k.key_path LIMIT %s"
        params.append(batch_size)

        return fetch_all(query, tuple(params)) or []

    @staticmethod
    def get_language_name(language_code: str) -> Optional[str]:
        """Get the display name of a language."""
        result = fetch_one(
            "SELECT language_name FROM translations.supported_languages WHERE language_code = %s",
            (language_code,)
        )
        return result['language_name'] if result else None

    @staticmethod
    def count_review_translations(
        language: str, where_sql: str, params: list
    ) -> int:
        """Count translations matching review filters."""
        query = f"""
            SELECT COUNT(*) AS total
            FROM translations.i18n_keys k
            JOIN translations.i18n_translations t
                ON t.key_id = k.key_id AND t.language_code = %s
            WHERE {where_sql}
        """
        result = fetch_one(query, tuple([language] + params))
        return result['total'] if result else 0

    @staticmethod
    def fetch_review_translations(
        language: str,
        source_language: str,
        where_sql: str,
        params: list,
        per_page: int,
        offset: int
    ) -> List[Dict]:
        """Fetch translations for review with source comparison."""
        query = f"""
            SELECT
                t.translation_id,
                k.key_id,
                k.key_path,
                k.namespace_code,
                src.translated_value  AS source_value,
                t.translated_value,
                t.translation_source,
                t.is_verified,
                t.quality_score,
                t.updated_at
            FROM translations.i18n_keys k
            JOIN translations.i18n_translations t
                ON t.key_id = k.key_id AND t.language_code = %s
            LEFT JOIN translations.i18n_translations src
                ON src.key_id = k.key_id AND src.language_code = %s
            WHERE {where_sql}
            ORDER BY k.namespace_code, k.key_path
            LIMIT %s OFFSET %s
        """
        main_params = [language, source_language] + params + [per_page, offset]
        return fetch_all(query, tuple(main_params)) or []

    @staticmethod
    def edit_translation(translation_id: str, new_value: str, user_id) -> Optional:
        """Update a translation value, marking it as manual and verified."""
        return execute_query(
            """
            UPDATE translations.i18n_translations
            SET translated_value  = %s,
                translation_source = 'manual',
                is_verified        = TRUE,
                translator_user_id = %s,
                updated_at         = NOW()
            WHERE translation_id = %s
            RETURNING translation_id
            """,
            (new_value, user_id, translation_id)
        )

    @staticmethod
    def verify_translation(translation_id: str) -> Optional:
        """Mark a single translation as verified."""
        return execute_query(
            """
            UPDATE translations.i18n_translations
            SET is_verified = TRUE, updated_at = NOW()
            WHERE translation_id = %s
            RETURNING translation_id
            """,
            (translation_id,)
        )

    @staticmethod
    def bulk_verify_translations(translation_ids: list) -> None:
        """Verify multiple translations at once."""
        execute_query(
            """
            UPDATE translations.i18n_translations
            SET is_verified = TRUE, updated_at = NOW()
            WHERE translation_id = ANY(%s)
            """,
            (translation_ids,)
        )

    @staticmethod
    def get_all_namespaces() -> List[Dict]:
        """Get all namespace codes."""
        return fetch_all(
            "SELECT namespace_code FROM translations.i18n_namespaces"
        ) or []

    @staticmethod
    def create_namespace(namespace_code: str, name: str) -> None:
        """Create a namespace if it doesn't exist."""
        execute_query(
            "INSERT INTO translations.i18n_namespaces (namespace_code, name) "
            "VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (namespace_code, name)
        )

    @staticmethod
    def upsert_key_with_default(
        namespace_code: str, key_path: str, default_value: str
    ) -> Optional[Dict]:
        """Upsert a key with default value update on conflict."""
        return fetch_one(
            "INSERT INTO translations.i18n_keys (namespace_code, key_path, default_value) "
            "VALUES (%s, %s, %s) "
            "ON CONFLICT (namespace_code, key_path) DO UPDATE SET "
            "default_value = EXCLUDED.default_value, updated_at = NOW() "
            "RETURNING key_id, (xmax = 0) AS is_new",
            (namespace_code, key_path, default_value)
        )

    @staticmethod
    def upsert_translation(key_id, language_code: str, value: str, user_id) -> None:
        """Upsert a translation value for a key and language."""
        execute_query(
            "INSERT INTO translations.i18n_translations "
            "(key_id, language_code, translated_value, translator_user_id, translation_source) "
            "VALUES (%s, %s, %s, %s, 'imported') "
            "ON CONFLICT (key_id, language_code) DO UPDATE SET "
            "translated_value = EXCLUDED.translated_value, updated_at = NOW()",
            (key_id, language_code, value, user_id)
        )
