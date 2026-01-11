"""
i18n Keys Module
================
Translation key and namespace management.
"""

from typing import Optional, Dict, Any, List
from src.database.connection import fetch_one, fetch_all, execute_query
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
                    n.namespace_id,
                    n.namespace_code,
                    n.name,
                    n.description,
                    n.icon,
                    n.sort_order,
                    0 as key_count
                FROM i18n_namespaces n
                WHERE n.is_active = TRUE
                ORDER BY n.sort_order
            """
            return fetch_all(query) or []
        except Exception as e:
            logger.error(f"Error fetching namespaces: {e}")
            return []

    @staticmethod
    def get_keys(
        namespace_id: Optional[int] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        primary_language: str = 'de'
    ) -> Dict[str, Any]:
        """
        Get translation keys with pagination.

        Args:
            namespace_id: Optional namespace filter
            search: Optional search term for key path/context
            limit: Results per page
            offset: Results offset
            primary_language: Primary language code for fallback values

        Returns:
            Dictionary with keys, total count, and pagination info
        """
        try:
            # Build WHERE conditions
            conditions = ["1=1"]  # Always true base condition
            params = []

            if namespace_id:
                conditions.append("k.namespace_id = %s")
                params.append(namespace_id)

            if search:
                conditions.append("(k.key_path ILIKE %s OR k.context ILIKE %s)")
                params.extend([f"%{search}%", f"%{search}%"])

            where_clause = " AND ".join(conditions)

            # Count total
            count_query = f"""
                SELECT COUNT(*) as total
                FROM i18n_keys k
                WHERE {where_clause}
            """
            count_result = fetch_one(count_query, tuple(params))
            total = count_result['total'] if count_result else 0

            # Get keys with translation counts
            query = f"""
                SELECT
                    k.key_id,
                    k.namespace_id,
                    n.namespace_code,
                    k.key_path,
                    k.context as description,
                    k.context as context_hint,
                    k.max_length,
                    k.placeholders,
                    TRUE as is_active,
                    k.created_at,
                    (SELECT value FROM i18n_translations WHERE key_id = k.key_id AND language_code = %s LIMIT 1) as primary_value,
                    (SELECT COUNT(*) FROM i18n_translations WHERE key_id = k.key_id) as translation_count,
                    (SELECT COUNT(*) FROM supported_languages WHERE active = TRUE) as total_languages
                FROM i18n_keys k
                LEFT JOIN i18n_namespaces n ON k.namespace_id = n.namespace_id
                WHERE {where_clause}
                ORDER BY n.sort_order, k.key_path
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
        namespace_id: int,
        key_path: str,
        description: Optional[str] = None,
        context_hint: Optional[str] = None,
        max_length: Optional[int] = None,
        placeholders: Optional[List[str]] = None
    ) -> Optional[int]:
        """
        Create a new translation key.

        Args:
            namespace_id: The namespace for this key
            key_path: Dot-notation key path (e.g., 'common.save')
            description: Optional description for translators
            context_hint: Optional UI context information
            max_length: Optional max length for translations
            placeholders: Optional list of placeholder names

        Returns:
            New key ID or None on error
        """
        try:
            query = """
                INSERT INTO i18n_keys (namespace_id, key_path, description, context_hint, max_length, placeholders)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING key_id
            """
            result = fetch_one(query, (
                namespace_id, key_path, description, context_hint, max_length,
                json.dumps(placeholders) if placeholders else None
            ))
            return result['key_id'] if result else None
        except Exception as e:
            logger.error(f"Error creating key: {e}")
            return None
