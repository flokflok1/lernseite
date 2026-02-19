"""
i18n Keys Module
================
Translation key and namespace management.
"""

from typing import Optional, Dict, Any, List
from app.infrastructure.persistence.repositories.i18n.service_queries import I18nKeyQueriesRepository
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
            return I18nKeyQueriesRepository.get_namespaces_with_key_count()
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
            keys, total = I18nKeyQueriesRepository.get_keys_paginated(
                primary_language=primary_language,
                namespace_code=namespace_code,
                search=search,
                limit=limit,
                offset=offset
            )

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
            result = I18nKeyQueriesRepository.create_key(
                namespace_code, key_path, default_value, description, context
            )
            return result['key_id'] if result else None
        except Exception as e:
            logger.error(f"Error creating key: {e}")
            return None
