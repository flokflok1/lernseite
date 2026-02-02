"""
i18n Repository - Translations & Bundles Data Access Layer

Implements database operations for:
- Translation storage and retrieval
- Bundle generation for frontend
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import psycopg
from psycopg.rows import dict_row
from app.infrastructure.persistence.repositories.base_repository import BaseRepository


class I18nTranslationsRepository(BaseRepository):
    """
    i18n Translations & Bundles Repository.

    Manages:
    - Translation storage and retrieval
    - Translation approval workflow
    - Bundle generation for frontend
    """

    def __init__(self, connection: psycopg.Connection):
        self.table_name = "translations.i18n_translations"
        self.conn = connection

    # =========================================================================
    # TRANSLATION STORAGE & RETRIEVAL
    # =========================================================================

    def get_translation(
        self,
        namespace_code: str,
        key_path: str,
        language_code: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get single translation.

        Args:
            namespace_code: Namespace code
            key_path: Key path
            language_code: Language code

        Returns:
            Translation data or None if not found
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("""
                SELECT
                    t.translation_id,
                    k.key_path,
                    t.language_code,
                    t.value,
                    t.status,
                    t.is_verified,
                    t.created_by,
                    t.created_at,
                    t.updated_at
                FROM translations.i18n_translations t
                JOIN translations.i18n_keys k ON t.key_id = k.key_id
                JOIN translations.i18n_namespaces n ON k.namespace_id = n.namespace_id
                WHERE n.namespace_code = %s
                  AND k.key_path = %s
                  AND t.language_code = %s
                  AND t.status IN ('active', 'draft')
            """, (namespace_code, key_path, language_code))
            return cursor.fetchone()

    def get_translations_for_language(
        self,
        language_code: str,
        namespace_code: Optional[str] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all translations for a language (optionally filtered by namespace).

        Args:
            language_code: Language code
            namespace_code: Optional namespace filter
            limit: Max results
            offset: Skip N results

        Returns:
            List of translations
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            if namespace_code:
                cursor.execute("""
                    SELECT
                        k.key_path,
                        t.language_code,
                        t.value,
                        t.status,
                        t.updated_at
                    FROM translations.i18n_translations t
                    JOIN translations.i18n_keys k ON t.key_id = k.key_id
                    JOIN translations.i18n_namespaces n ON k.namespace_id = n.namespace_id
                    WHERE t.language_code = %s
                      AND n.namespace_code = %s
                      AND t.status IN ('active', 'draft')
                    ORDER BY k.key_path ASC
                    LIMIT %s OFFSET %s
                """, (language_code, namespace_code, limit, offset))
            else:
                cursor.execute("""
                    SELECT
                        n.namespace_code,
                        k.key_path,
                        t.language_code,
                        t.value,
                        t.status,
                        t.updated_at
                    FROM translations.i18n_translations t
                    JOIN translations.i18n_keys k ON t.key_id = k.key_id
                    JOIN translations.i18n_namespaces n ON k.namespace_id = n.namespace_id
                    WHERE t.language_code = %s
                      AND t.status IN ('active', 'draft')
                    ORDER BY n.namespace_code, k.key_path ASC
                    LIMIT %s OFFSET %s
                """, (language_code, limit, offset))

            return cursor.fetchall()

    def create_translation(
        self,
        namespace_code: str,
        key_path: str,
        language_code: str,
        translation_text: str,
        translated_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create new translation.

        Args:
            namespace_code: Namespace code
            key_path: Key path
            language_code: Language code
            translation_text: Translated text
            translated_by: User who translated (optional)

        Returns:
            Created translation
        """
        # Get or create key
        from app.infrastructure.persistence.repositories.i18n_repository_languages import I18nLanguagesRepository
        lang_repo = I18nLanguagesRepository(self.conn)
        key = lang_repo.get_or_create_key(namespace_code, key_path)
        key_id = key['key_id']

        # Insert translation
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("""
                INSERT INTO translations.i18n_translations
                (key_id, language_code, value, status, source, created_by)
                VALUES (%s, %s, %s, 'active', 'import', %s)
                ON CONFLICT (key_id, language_code) DO UPDATE
                SET value = %s,
                    updated_at = NOW()
                RETURNING translation_id, key_id, language_code, value, status
            """, (key_id, language_code, translation_text, translated_by, translation_text))
            result = cursor.fetchone()
            self.conn.commit()
            return result

    def approve_translation(
        self,
        translation_id: str,
        reviewed_by: str
    ) -> Dict[str, Any]:
        """
        Approve translation (mark as verified and active).

        Args:
            translation_id: Translation ID
            reviewed_by: User who reviewed

        Returns:
            Updated translation
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("""
                UPDATE translations.i18n_translations
                SET
                    status = 'active',
                    is_verified = TRUE,
                    verified_by = %s,
                    verified_at = NOW(),
                    updated_at = NOW()
                WHERE translation_id = %s
                RETURNING translation_id, language_code, value, status, is_verified
            """, (reviewed_by, translation_id))
            result = cursor.fetchone()
            self.conn.commit()
            return result

    # =========================================================================
    # BUNDLE GENERATION (for frontend)
    # =========================================================================

    def get_translation_bundle(
        self,
        language_code: str,
        namespace_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get translation bundle for frontend (nested dictionary format).

        Example output:
        {
            'admin': {
                'users': {'title': 'Users', 'description': 'Manage users'},
                'courses': {'title': 'Courses'}
            },
            'common': {
                'ok': 'OK',
                'cancel': 'Cancel'
            }
        }

        Args:
            language_code: Language code
            namespace_code: Optional namespace filter

        Returns:
            Nested dictionary of translations with fallback support
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            # Call database function for bundle generation
            # Note: PostgreSQL JSONB is automatically converted to dict by psycopg3
            cursor.execute("""
                SELECT get_i18n_bundle(%s, %s) as bundle
            """, (language_code, namespace_code))
            result = cursor.fetchone()

            if result and result['bundle']:
                # Bundle is already a dict (psycopg3 converts JSONB → dict)
                bundle = result['bundle']
                if isinstance(bundle, dict):
                    return bundle
                # Fallback for string responses (shouldn't happen with JSONB)
                import json
                if isinstance(bundle, str):
                    return json.loads(bundle)

            return {}
