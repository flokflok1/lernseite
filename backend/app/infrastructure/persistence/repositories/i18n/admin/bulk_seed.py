"""
i18n Bulk Seed Repository

Handles the high-performance bulk seeding of i18n keys and translations
from frontend locale files into the database.

Uses PostgreSQL COPY protocol for fast bulk loading and manages
trigger disabling/re-enabling for performance during large imports.
"""

from typing import Dict, Any
import logging
import time

from app.infrastructure.persistence.database.connection import get_connection
from psycopg.rows import dict_row

logger = logging.getLogger(__name__)


class I18nBulkSeedRepository:
    """Repository for bulk i18n seed operations using COPY protocol."""

    @classmethod
    def seed_all_locales(
        cls,
        locales: Dict[str, Dict[str, str]],
        primary_lang: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Bulk-seed all i18n keys and translations from locale data.

        Uses temp tables + COPY protocol for performance.
        Disables per-row triggers during bulk load and updates
        language progress stats once at the end.

        Args:
            locales: {lang_code: {key_path: value}} for all languages
            primary_lang: Primary language code (keys derived from this)
            user_id: ID of the user performing the seed

        Returns:
            Dict with keys_created, keys_updated, translations_set counts
        """
        results = {'keys_created': 0, 'keys_updated': 0, 'translations_set': 0}
        primary_messages = locales.get(primary_lang, {})

        if not primary_messages:
            return results

        t0 = time.monotonic()

        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # 1. Get existing namespaces
                cur.execute("SELECT namespace_code FROM translations.i18n_namespaces")
                existing_ns = {r['namespace_code'] for r in cur.fetchall()}

                # 2. Collect and batch-create missing namespaces
                key_ns_map = cls._build_namespace_map(primary_messages)
                needed_ns = set(key_ns_map.values()) - existing_ns

                if needed_ns:
                    cls._create_namespaces(cur, needed_ns)

                # 3. Bulk-upsert keys via temp table + COPY
                key_id_map = cls._upsert_keys(cur, primary_messages, key_ns_map, results)

                t1 = time.monotonic()
                logger.info(f"Keys upserted in {t1-t0:.1f}s: {len(key_id_map)} keys")

                # 4. Disable triggers, bulk-upsert translations, re-enable
                cls._upsert_translations(cur, locales, key_id_map, user_id, results)

                # 5. Update language progress stats once
                cls._update_language_progress(cur)

                t2 = time.monotonic()
                logger.info(f"Translations upserted in {t2-t1:.1f}s, total: {t2-t0:.1f}s")

        return results

    @staticmethod
    def _build_namespace_map(messages: Dict[str, str]) -> Dict[str, str]:
        """Build key_path -> namespace_code mapping."""
        key_ns_map = {}
        for key_path in messages:
            parts = key_path.split('.')
            key_ns_map[key_path] = parts[0] if len(parts) > 1 else 'common'
        return key_ns_map

    @staticmethod
    def _create_namespaces(cur, needed_ns: set) -> None:
        """Batch-create missing namespaces."""
        ns_values = []
        ns_params = []
        for ns_code in needed_ns:
            ns_values.append("(%s, %s)")
            ns_params.extend([ns_code, ns_code.replace('.', ' > ').title()])
        cur.execute(
            "INSERT INTO translations.i18n_namespaces (namespace_code, name) "
            "VALUES " + ", ".join(ns_values) + " ON CONFLICT DO NOTHING",
            ns_params
        )

    @staticmethod
    def _upsert_keys(cur, primary_messages, key_ns_map, results) -> Dict[str, str]:
        """Bulk-upsert keys via COPY into temp table, return key_id map."""
        cur.execute(
            "CREATE TEMP TABLE _tmp_keys ("
            "namespace_code VARCHAR, key_path VARCHAR, default_value TEXT"
            ") ON COMMIT DROP"
        )

        with cur.copy("COPY _tmp_keys (namespace_code, key_path, default_value) FROM STDIN") as copy:
            for key_path, value in primary_messages.items():
                copy.write_row((key_ns_map[key_path], key_path, str(value) if value else ''))

        cur.execute(
            "INSERT INTO translations.i18n_keys (namespace_code, key_path, default_value) "
            "SELECT namespace_code, key_path, default_value FROM _tmp_keys "
            "ON CONFLICT (namespace_code, key_path) DO UPDATE SET "
            "default_value = EXCLUDED.default_value, updated_at = NOW() "
            "RETURNING key_id, key_path, (xmax = 0) AS is_new"
        )
        key_rows = cur.fetchall()

        key_id_map = {}
        for row in key_rows:
            key_id_map[row['key_path']] = row['key_id']
            if row.get('is_new'):
                results['keys_created'] += 1
            else:
                results['keys_updated'] += 1

        return key_id_map

    @classmethod
    def _upsert_translations(cls, cur, locales, key_id_map, user_id, results) -> None:
        """Bulk-upsert translations with triggers disabled for performance."""
        # Disable per-row triggers (they update language_progress on EVERY row)
        cur.execute(
            "ALTER TABLE translations.i18n_translations "
            "DISABLE TRIGGER trg_update_language_progress_insert"
        )
        cur.execute(
            "ALTER TABLE translations.i18n_translations "
            "DISABLE TRIGGER trg_update_language_progress_update"
        )

        try:
            for lang_code, messages in locales.items():
                cls._upsert_language_translations(
                    cur, lang_code, messages, key_id_map, user_id, results
                )
        finally:
            # Re-enable triggers even if an error occurs
            cur.execute(
                "ALTER TABLE translations.i18n_translations "
                "ENABLE TRIGGER trg_update_language_progress_insert"
            )
            cur.execute(
                "ALTER TABLE translations.i18n_translations "
                "ENABLE TRIGGER trg_update_language_progress_update"
            )

    @staticmethod
    def _upsert_language_translations(cur, lang_code, messages, key_id_map, user_id, results):
        """Upsert translations for a single language via COPY + temp table."""
        cur.execute(
            "CREATE TEMP TABLE _tmp_trans ("
            "key_id UUID, language_code VARCHAR(10), "
            "translated_value TEXT, translator_user_id VARCHAR"
            ") ON COMMIT DROP"
        )

        row_count = 0
        with cur.copy("COPY _tmp_trans FROM STDIN") as copy:
            for key_path, value in messages.items():
                key_id = key_id_map.get(key_path)
                if key_id and value:
                    copy.write_row((str(key_id), lang_code, str(value), str(user_id)))
                    row_count += 1

        if row_count > 0:
            cur.execute(
                "INSERT INTO translations.i18n_translations "
                "(key_id, language_code, translated_value, translator_user_id, translation_source) "
                "SELECT key_id, language_code, translated_value, "
                "translator_user_id::uuid, 'imported' FROM _tmp_trans "
                "ON CONFLICT (key_id, language_code) DO UPDATE SET "
                "translated_value = EXCLUDED.translated_value, updated_at = NOW()"
            )
            results['translations_set'] += row_count

        cur.execute("DROP TABLE IF EXISTS _tmp_trans")

    @staticmethod
    def sync_entity_display_name(namespace: str, key_path: str, display_name: dict):
        """Sync a single entity's display_name dict into i18n keys + translations.

        Used when creating/updating entities with multilingual display names
        (e.g., exam_type_registry, exam_regions).
        """
        from app.infrastructure.persistence.database.connection import (
            fetch_one, execute_query,
        )

        # Upsert key
        execute_query(
            "INSERT INTO translations.i18n_keys (namespace_code, key_path, default_value) "
            "VALUES (%s, %s, %s) "
            "ON CONFLICT (namespace_code, key_path) "
            "  DO UPDATE SET default_value = EXCLUDED.default_value, updated_at = NOW()",
            (namespace, key_path, display_name.get('de', '')),
        )

        row = fetch_one(
            "SELECT key_id FROM translations.i18n_keys "
            "WHERE namespace_code = %s AND key_path = %s",
            (namespace, key_path),
        )
        if not row:
            return

        key_id = row['key_id']
        for lang, value in display_name.items():
            if not value:
                continue
            execute_query(
                "INSERT INTO translations.i18n_translations "
                "  (key_id, language_code, translated_value, translation_source) "
                "VALUES (%s, %s, %s, 'imported') "
                "ON CONFLICT (key_id, language_code) "
                "  DO UPDATE SET translated_value = EXCLUDED.translated_value, "
                "    updated_at = NOW()",
                (key_id, lang, value),
            )

    @staticmethod
    def _update_language_progress(cur) -> None:
        """Update language progress stats once (replaces per-row trigger calls)."""
        cur.execute("""
            UPDATE translations.supported_languages sl SET
                total_keys = sub.total_keys,
                translated_keys = sub.translated_keys,
                completion_percent = CASE
                    WHEN sub.total_keys > 0
                    THEN (sub.translated_keys::DECIMAL / sub.total_keys::DECIMAL) * 100
                    ELSE 0
                END,
                updated_at = CURRENT_TIMESTAMP
            FROM (
                SELECT
                    sl2.language_code,
                    (SELECT COUNT(DISTINCT key_id) FROM translations.i18n_translations) AS total_keys,
                    COUNT(DISTINCT t.key_id) AS translated_keys
                FROM translations.supported_languages sl2
                LEFT JOIN translations.i18n_translations t
                    ON t.language_code = sl2.language_code
                GROUP BY sl2.language_code
            ) sub
            WHERE sl.language_code = sub.language_code
        """)
