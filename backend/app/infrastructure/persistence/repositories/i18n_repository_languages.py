"""
i18n Repository - Languages & Keys Data Access Layer

Implements database operations for:
- Language management
- Namespace management
- i18n keys
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import psycopg
from psycopg.rows import dict_row
from app.infrastructure.persistence.repositories.base_repository import BaseRepository


class I18nLanguagesRepository(BaseRepository):
    """
    i18n Languages & Keys Repository.

    Manages:
    - i18n languages and configurations
    - i18n namespaces
    - i18n keys
    """

    def __init__(self, connection: psycopg.Connection):
        self.table_name = "translations.supported_languages"
        self.conn = connection

    # =========================================================================
    # LANGUAGE MANAGEMENT
    # =========================================================================

    def get_supported_languages(self) -> List[Dict[str, Any]]:
        """
        Get all supported languages.

        Returns:
            List of language configurations (code, name, priority, is_primary, flag_emoji, completion_percent)
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("""
                SELECT
                    language_code,
                    language_name,
                    native_name,
                    flag_emoji,
                    priority,
                    is_primary,
                    fallback_language,
                    active,
                    completion_percent,
                    total_keys,
                    translated_keys,
                    created_at
                FROM translations.supported_languages
                ORDER BY priority ASC, language_code ASC
            """)
            return cursor.fetchall()

    def get_language(self, language_code: str) -> Optional[Dict[str, Any]]:
        """
        Get language configuration.

        Args:
            language_code: Language code (e.g., 'de', 'en', 'pl')

        Returns:
            Language configuration or None if not found
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("""
                SELECT
                    language_code,
                    language_name,
                    native_name,
                    flag_emoji,
                    priority,
                    is_primary,
                    fallback_language,
                    active,
                    completion_percent,
                    total_keys,
                    translated_keys,
                    created_at
                FROM translations.supported_languages
                WHERE language_code = %s
            """, (language_code,))
            return cursor.fetchone()

    def get_primary_languages(self) -> List[Dict[str, Any]]:
        """
        Get primary languages (translation sources).

        Returns:
            List of primary languages ordered by priority
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("""
                SELECT
                    language_code,
                    language_name,
                    native_name,
                    flag_emoji,
                    priority,
                    is_primary,
                    fallback_language,
                    active,
                    completion_percent,
                    total_keys,
                    translated_keys,
                    created_at
                FROM translations.supported_languages
                WHERE is_primary = TRUE AND active = TRUE
                ORDER BY priority ASC
            """)
            return cursor.fetchall()

    # =========================================================================
    # NAMESPACE & KEY MANAGEMENT
    # =========================================================================

    def get_namespaces(self) -> List[Dict[str, Any]]:
        """
        Get all i18n namespaces (admin, common, courses, etc.).

        Returns:
            List of namespace configurations
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("""
                SELECT
                    namespace_id,
                    namespace_code,
                    name,
                    description,
                    sort_order,
                    created_at
                FROM translations.i18n_namespaces
                WHERE is_active = TRUE
                ORDER BY sort_order ASC, namespace_code ASC
            """)
            return cursor.fetchall()

    def get_or_create_namespace(
        self,
        namespace_code: str,
        namespace_name: str
    ) -> Dict[str, Any]:
        """
        Get or create namespace.

        Args:
            namespace_code: Code (e.g., 'admin', 'common')
            namespace_name: Display name

        Returns:
            Namespace configuration
        """
        # Try to get existing
        namespace = self.get_namespace(namespace_code)
        if namespace:
            return namespace

        # Create new
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("""
                INSERT INTO translations.i18n_namespaces
                (namespace_code, name, description, sort_order, is_active)
                VALUES (%s, %s, %s, %s, TRUE)
                RETURNING namespace_id, namespace_code, name, description, sort_order
            """, (namespace_code, namespace_name, "", 0))
            result = cursor.fetchone()
            self.conn.commit()
            return result

    def get_namespace(self, namespace_code: str) -> Optional[Dict[str, Any]]:
        """
        Get namespace by code.

        Args:
            namespace_code: Namespace code

        Returns:
            Namespace configuration or None
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("""
                SELECT
                    namespace_id,
                    namespace_code,
                    name,
                    description,
                    sort_order,
                    is_active,
                    created_at
                FROM translations.i18n_namespaces
                WHERE namespace_code = %s
            """, (namespace_code,))
            return cursor.fetchone()

    def get_or_create_key(
        self,
        namespace_code: str,
        key_path: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Get or create i18n key.

        Args:
            namespace_code: Namespace code
            key_path: Key path (e.g., 'admin.users.title')
            context: Additional context for translators

        Returns:
            Key configuration
        """
        # Try to get existing
        key = self.get_key(namespace_code, key_path)
        if key:
            return key

        # Get namespace ID (required for foreign key)
        namespace = self.get_namespace(namespace_code)
        if not namespace:
            raise ValueError(f"Namespace {namespace_code} not found")

        namespace_id = namespace.get('namespace_id')
        if not namespace_id:
            # If namespace_id is not in result, query it directly
            with self.conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute("""
                    SELECT namespace_id FROM translations.i18n_namespaces
                    WHERE namespace_code = %s
                """, (namespace_code,))
                result = cursor.fetchone()
                if result:
                    namespace_id = result['namespace_id']
                else:
                    raise ValueError(f"Namespace ID not found for {namespace_code}")

        # Create new
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("""
                INSERT INTO translations.i18n_keys
                (namespace_id, key_path, context)
                VALUES (%s, %s, %s)
                ON CONFLICT (namespace_id, key_path) DO NOTHING
                RETURNING key_id, namespace_id, key_path, context
            """, (namespace_id, key_path, context))
            result = cursor.fetchone()
            self.conn.commit()

            if not result:
                # If conflict, fetch the existing key
                cursor.execute("""
                    SELECT key_id, namespace_id, key_path, context
                    FROM translations.i18n_keys
                    WHERE namespace_id = %s AND key_path = %s
                """, (namespace_id, key_path))
                result = cursor.fetchone()

            return result

    def get_key(
        self,
        namespace_code: str,
        key_path: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get i18n key.

        Args:
            namespace_code: Namespace code
            key_path: Key path

        Returns:
            Key configuration or None
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            # Use JOIN to find key by namespace_code + key_path
            cursor.execute("""
                SELECT
                    k.key_id,
                    k.namespace_id,
                    k.key_path,
                    k.context
                FROM translations.i18n_keys k
                JOIN translations.i18n_namespaces n ON k.namespace_id = n.namespace_id
                WHERE n.namespace_code = %s AND k.key_path = %s
            """, (namespace_code, key_path))
            return cursor.fetchone()
