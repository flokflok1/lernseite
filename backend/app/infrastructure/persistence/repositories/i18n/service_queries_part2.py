"""
i18n Service Queries Repository - Part 2
==========================================
AI translation, config, and translation CRUD queries.

Extracted from:
- application/services/i18n/ai_generation.py
- application/services/i18n/config.py
- application/services/i18n/translations.py
"""

from typing import Optional, Dict, Any, List
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query


class I18nAIQueriesRepository:
    """AI translation generation data queries."""

    @staticmethod
    def get_key_with_source(key_id: str, primary_language: str) -> Optional[Dict[str, Any]]:
        """Get key info with source translation and language name."""
        return fetch_one(
            """
            SELECT
                k.key_path,
                k.description,
                k.context as context_hint,
                k.namespace_code,
                t.translated_value as source_value,
                sl.language_name as source_language_name
            FROM translations.i18n_keys k
            LEFT JOIN translations.i18n_translations t
                ON k.key_id = t.key_id AND t.language_code = %s
            LEFT JOIN translations.supported_languages sl
                ON sl.language_code = %s
            WHERE k.key_id = %s
            """,
            (primary_language, primary_language, key_id)
        )

    @staticmethod
    def get_language_info(language_code: str) -> Optional[Dict[str, Any]]:
        """Get language name and native name."""
        return fetch_one(
            "SELECT language_name, native_name FROM translations.supported_languages WHERE language_code = %s",
            (language_code,)
        )

    @staticmethod
    def get_untranslated_keys(
        target_language: str,
        primary_language: str,
        namespace_code: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get keys missing translations for target but having source."""
        query = """
            SELECT k.key_id, k.key_path
            FROM translations.i18n_keys k
            WHERE k.is_active = TRUE
            AND NOT EXISTS (
                SELECT 1 FROM translations.i18n_translations t
                WHERE t.key_id = k.key_id AND t.language_code = %s
            )
            AND EXISTS (
                SELECT 1 FROM translations.i18n_translations t
                WHERE t.key_id = k.key_id AND t.language_code = %s
            )
        """
        params: list = [target_language, primary_language]

        if namespace_code:
            query += " AND k.namespace_code = %s"
            params.append(namespace_code)

        query += " LIMIT %s"
        params.append(limit)

        return fetch_all(query, tuple(params)) or []


class I18nConfigQueriesRepository:
    """AI config and moderation dashboard queries."""

    @staticmethod
    def get_ai_config() -> List[Dict[str, Any]]:
        """Get all AI config key-value pairs."""
        return fetch_all(
            "SELECT config_key, config_value FROM translations.i18n_ai_config"
        ) or []

    @staticmethod
    def update_ai_config(config_key: str, json_value: str, user_id: str) -> None:
        """Upsert an AI config value (expects pre-serialized JSON string)."""
        execute_query(
            """
            INSERT INTO translations.i18n_ai_config (config_key, config_value, updated_by, updated_at)
            VALUES (%s, %s::jsonb, %s, NOW())
            ON CONFLICT (config_key) DO UPDATE SET
                config_value = EXCLUDED.config_value,
                updated_by = EXCLUDED.updated_by,
                updated_at = NOW()
            """,
            (config_key, json_value, user_id)
        )

    @staticmethod
    def get_moderation_dashboard() -> List[Dict[str, Any]]:
        """Get moderation dashboard data by language."""
        return fetch_all(
            """
            SELECT
                sl.language_code,
                sl.language_name,
                sl.flag AS flag_svg_code,
                0 AS pending_count,
                0 AS ai_reviewing_count,
                0 AS awaiting_human_count,
                0 AS pending_suggestions,
                0 AS ai_reviews_24h,
                NULL AS avg_quality_7d
            FROM translations.supported_languages sl
            WHERE sl.is_active = TRUE
            ORDER BY sl.priority
            """
        ) or []


class I18nTranslationQueriesRepository:
    """Translation bundle and CRUD queries."""

    @staticmethod
    def get_bundle(language_code: str, namespace: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get translation bundle via DB function."""
        return fetch_one(
            "SELECT get_i18n_bundle(%s::varchar, %s::varchar) AS bundle",
            (language_code, namespace)
        )

    @staticmethod
    def get_key_translations_detail(key_id: str) -> List[Dict[str, Any]]:
        """Get all translations for a key with language metadata and translator info."""
        return fetch_all(
            """
            SELECT
                t.translation_id,
                t.key_id,
                t.language_code,
                sl.language_name,
                sl.native_name,
                sl.flag AS flag_svg_code,
                t.translated_value,
                t.is_verified,
                t.translation_source,
                t.translator_user_id,
                u.full_name as translator_name,
                t.created_at,
                t.updated_at
            FROM translations.i18n_translations t
            JOIN translations.supported_languages sl ON t.language_code = sl.language_code
            LEFT JOIN core.users u ON t.translator_user_id = u.user_id
            WHERE t.key_id = %s
            ORDER BY sl.priority, sl.language_code
            """,
            (key_id,)
        ) or []

    @staticmethod
    def set_translation(
        key_id: str,
        language_code: str,
        translated_value: str,
        translator_user_id: Optional[str] = None,
        translation_source: str = 'manual'
    ) -> None:
        """Upsert a translation value."""
        execute_query(
            """
            INSERT INTO translations.i18n_translations
                (key_id, language_code, translated_value, translator_user_id, translation_source)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (key_id, language_code)
            DO UPDATE SET
                translated_value = EXCLUDED.translated_value,
                translator_user_id = COALESCE(EXCLUDED.translator_user_id, translations.i18n_translations.translator_user_id),
                translation_source = EXCLUDED.translation_source,
                updated_at = NOW()
            """,
            (key_id, language_code, translated_value, translator_user_id, translation_source)
        )
