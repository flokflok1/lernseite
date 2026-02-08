"""
i18n Keys Module
================
Translation key and namespace management.
"""

from typing import Optional, Dict, Any, List
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query
import json
import logging

logger = logging.getLogger(__name__)


class KeyManager:
    """Manages translation keys and namespaces."""

    @staticmethod
    def get_namespaces() -> List[Dict[str, Any]]:
        """
        Get all i18n namespaces.

        Returns:
            List of namespace definitions
        """
        try:
            query = """
                SELECT
                    n.namespace_code,
                    n.name,
                    n.description,
                    n.icon,
                    n.sort_order,
                    (SELECT COUNT(*) FROM translations.i18n_keys k
                     WHERE k.namespace_code = n.namespace_code AND k.is_active = TRUE) as key_count
                FROM translations.i18n_namespaces n
                WHERE n.is_active = TRUE
                ORDER BY n.sort_order
            """
            return fetch_all(query) or []
        except Exception as e:
            logger.error(f"Error fetching namespaces: {e}")
            return []

    @staticmethod
    def get_keys(
        namespace_code: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        primary_language: str = 'de'
    ) -> Dict[str, Any]:
        """
        Get translation keys with pagination.

        Args:
            namespace_code: Optional namespace filter
            search: Optional search term for key path/context
            limit: Results per page
            offset: Results offset
            primary_language: Primary language code for fallback values

        Returns:
            Dictionary with keys, total count, and pagination info
        """
        try:
            # Build WHERE conditions
            conditions = ["k.is_active = TRUE"]
            params = []

            if namespace_code:
                conditions.append("k.namespace_code = %s")
                params.append(namespace_code)

            if search:
                conditions.append("(k.key_path ILIKE %s OR k.context ILIKE %s)")
                params.extend([f"%{search}%", f"%{search}%"])

            where_clause = " AND ".join(conditions)

            # Count total
            count_query = f"""
                SELECT COUNT(*) as total
                FROM translations.i18n_keys k
                WHERE {where_clause}
            """
            count_result = fetch_one(count_query, tuple(params))
            total = count_result['total'] if count_result else 0

            # Get keys with translation counts
            query = f"""
                SELECT
                    k.key_id,
                    k.namespace_code,
                    k.key_path,
                    k.default_value,
                    k.description,
                    k.context as context_hint,
                    k.is_active,
                    k.created_at,
                    (SELECT translated_value FROM translations.i18n_translations
                     WHERE key_id = k.key_id AND language_code = %s LIMIT 1) as primary_value,
                    (SELECT COUNT(*) FROM translations.i18n_translations
                     WHERE key_id = k.key_id) as translation_count,
                    (SELECT COUNT(*) FROM translations.supported_languages
                     WHERE is_active = TRUE) as total_languages
                FROM translations.i18n_keys k
                WHERE {where_clause}
                ORDER BY k.namespace_code, k.key_path
                LIMIT %s OFFSET %s
            """
            # Insert primary_language at the beginning of params
            params.insert(0, primary_language)
            params.extend([limit, offset])
            keys = fetch_all(query, tuple(params)) or []

            return {
                'keys': keys,
                'total': total,
                'limit': limit,
                'offset': offset
            }
        except Exception as e:
            logger.error(f"Error fetching keys: {e}")
            return {'keys': [], 'total': 0, 'limit': limit, 'offset': offset}

    @staticmethod
    def create_key(
        namespace_code: str,
        key_path: str,
        default_value: str = '',
        description: Optional[str] = None,
        context: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a new translation key.

        Args:
            namespace_code: The namespace code for this key
            key_path: Dot-notation key path (e.g., 'common.save')
            default_value: Default text (usually German)
            description: Optional description for translators
            context: Optional UI context information

        Returns:
            New key ID (UUID) or None on error
        """
        try:
            query = """
                INSERT INTO translations.i18n_keys
                    (namespace_code, key_path, default_value, description, context)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (namespace_code, key_path) DO NOTHING
                RETURNING key_id
            """
            result = fetch_one(query, (
                namespace_code, key_path, default_value, description, context
            ))
            return result['key_id'] if result else None
        except Exception as e:
            logger.error(f"Error creating key: {e}")
            return None
