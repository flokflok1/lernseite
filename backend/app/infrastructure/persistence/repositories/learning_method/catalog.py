"""
Learning Method Catalog Repository - Schema-Based Dynamic System

Data access layer for learning method type catalog (lm00-lm11) with ui_schemas.

This repository fetches from learning_methods.learning_method_types table
and includes the ui_schema JSONB column for dynamic form rendering.

Features:
- Get all 12 LM types with full metadata and schemas
- Get single LM by type with schema
- Support for i18n-aware schemas (keys + fallbacks)
- Caching for performance
- Support for language-specific metadata

Uses psycopg3 connection pool - NO ORM!
"""

from typing import Dict, Any, Optional, List
import psycopg
from psycopg.rows import dict_row
import json
import logging

from app.core.bootstrap.extensions import db_pool
from app.infrastructure.cache.service import CacheService
from flask import current_app

logger = logging.getLogger(__name__)


class LearningMethodCatalogRepository:
    """
    Repository for learning method type catalog with UI schemas.

    All 12 Content-LM types (lm00-lm11) are accessed here.
    Each method includes full ui_schema for dynamic form rendering.
    """

    @classmethod
    def get_full_catalog(cls, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get complete catalog of all 12 Learning Methods with UI schemas.

        Args:
            use_cache: Use cached result (default: True)

        Returns:
            Dictionary with:
            - learning_methods: List of all 12 LMs with full metadata and schemas
            - total: Count (always 12)
            - groups: Grouped metadata for UI organization

        Example:
            >>> catalog = LearningMethodCatalogRepository.get_full_catalog()
            >>> len(catalog['learning_methods'])
            12
            >>> catalog['learning_methods'][0]['method_type']
            0
        """
        if use_cache:
            cache_key = CacheService.make_key('CATALOG', 'learning_methods', 'all')
            ttl = current_app.config.get('CACHE_CATALOG_TTL', 3600)

            def load_catalog():
                return cls._fetch_full_catalog()

            return CacheService.cache_get_or_set(cache_key, ttl, load_catalog)

        return cls._fetch_full_catalog()

    @classmethod
    def _fetch_full_catalog(cls) -> Optional[Dict[str, Any]]:
        """
        Internal method to fetch full catalog from database.

        Returns:
            Catalog dictionary or None if query fails
        """
        try:
            with db_pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    # Fetch all 12 LM types with schemas
                    cur.execute("""
                        SELECT
                            type_id,
                            method_type,
                            name,
                            description,
                            group_code,
                            tier,
                            ki_usage,
                            active,
                            config,
                            ui_schema,
                            icon,
                            created_at,
                            updated_at
                        FROM learning_methods.learning_method_types
                        WHERE active = TRUE
                        ORDER BY group_code, method_type
                    """)

                    methods = cur.fetchall()

                    if not methods:
                        logger.warning("No active learning methods found in catalog")
                        return None

                    # Convert to list and process schemas
                    methods_list = []
                    groups_dict = {
                        'A': {'name': 'Erklärend (Explanation)', 'count': 0, 'description': 'Explanatory methods for building understanding'},
                        'B': {'name': 'Praxis (Practice)', 'count': 0, 'description': 'Practical methods for exercise and application'},
                        'C': {'name': 'Prüfung (Assessment)', 'count': 0, 'description': 'Assessment methods for evaluating competency'}
                    }

                    for method in methods:
                        # Process ui_schema if it's a string (PostgreSQL returns as string sometimes)
                        if isinstance(method.get('ui_schema'), str):
                            try:
                                method['ui_schema'] = json.loads(method['ui_schema'])
                            except (json.JSONDecodeError, TypeError):
                                logger.warning(f"Failed to parse ui_schema for method_type {method['method_type']}")
                                method['ui_schema'] = {}

                        # Process config similarly
                        if isinstance(method.get('config'), str):
                            try:
                                method['config'] = json.loads(method['config'])
                            except (json.JSONDecodeError, TypeError):
                                method['config'] = {}

                        # Convert timestamps to ISO format strings
                        if hasattr(method.get('created_at'), 'isoformat'):
                            method['created_at'] = method['created_at'].isoformat()
                        if hasattr(method.get('updated_at'), 'isoformat'):
                            method['updated_at'] = method['updated_at'].isoformat()

                        methods_list.append(method)

                        # Count by group
                        group_code = method.get('group_code')
                        if group_code in groups_dict:
                            groups_dict[group_code]['count'] += 1

                    # Build result
                    return {
                        'learning_methods': methods_list,
                        'total': len(methods_list),
                        'groups': groups_dict
                    }

        except Exception as e:
            logger.exception(f"Error fetching learning method catalog: {e}")
            return None

    @classmethod
    def get_by_type(cls, method_type: int, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get single Learning Method by type ID with UI schema.

        Args:
            method_type: Learning method type (0-11 for lm00-lm11)
            use_cache: Use cached result (default: True)

        Returns:
            Dictionary with method metadata and ui_schema, or None if not found

        Raises:
            ValueError: If method_type is not 0-11

        Example:
            >>> lm00 = LearningMethodCatalogRepository.get_by_type(0)
            >>> lm00['name']
            'Tiefgehende Erklärung'
        """
        if not isinstance(method_type, int) or method_type < 0 or method_type > 11:
            raise ValueError(f"Invalid method_type: {method_type}. Must be 0-11 (lm00-lm11)")

        if use_cache:
            cache_key = CacheService.make_key('CATALOG', 'learning_methods', f'type_{method_type}')
            ttl = current_app.config.get('CACHE_CATALOG_TTL', 3600)

            def load_method():
                return cls._fetch_by_type(method_type)

            return CacheService.cache_get_or_set(cache_key, ttl, load_method)

        return cls._fetch_by_type(method_type)

    @classmethod
    def _fetch_by_type(cls, method_type: int) -> Optional[Dict[str, Any]]:
        """
        Internal method to fetch single LM type from database.

        Args:
            method_type: Learning method type (0-11)

        Returns:
            Method dictionary or None if not found
        """
        try:
            with db_pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute("""
                        SELECT
                            type_id,
                            method_type,
                            name,
                            description,
                            group_code,
                            tier,
                            ki_usage,
                            active,
                            config,
                            ui_schema,
                            icon,
                            created_at,
                            updated_at
                        FROM learning_methods.learning_method_types
                        WHERE method_type = %s AND active = TRUE
                    """, (method_type,))

                    method = cur.fetchone()

                    if not method:
                        logger.warning(f"Learning method type {method_type} not found or inactive")
                        return None

                    # Process ui_schema if it's a string
                    if isinstance(method.get('ui_schema'), str):
                        try:
                            method['ui_schema'] = json.loads(method['ui_schema'])
                        except (json.JSONDecodeError, TypeError):
                            logger.warning(f"Failed to parse ui_schema for method_type {method_type}")
                            method['ui_schema'] = {}

                    # Process config similarly
                    if isinstance(method.get('config'), str):
                        try:
                            method['config'] = json.loads(method['config'])
                        except (json.JSONDecodeError, TypeError):
                            method['config'] = {}

                    # Convert timestamps to ISO format strings
                    if hasattr(method.get('created_at'), 'isoformat'):
                        method['created_at'] = method['created_at'].isoformat()
                    if hasattr(method.get('updated_at'), 'isoformat'):
                        method['updated_at'] = method['updated_at'].isoformat()

                    return method

        except Exception as e:
            logger.exception(f"Error fetching learning method type {method_type}: {e}")
            return None

    @classmethod
    def get_by_group(cls, group_code: str, use_cache: bool = True) -> Optional[List[Dict[str, Any]]]:
        """
        Get all Learning Methods in a specific group with UI schemas.

        Args:
            group_code: Group code ('A', 'B', or 'C')
            use_cache: Use cached result (default: True)

        Returns:
            List of methods in group, or None if invalid group

        Raises:
            ValueError: If group_code is not A, B, or C

        Example:
            >>> group_a = LearningMethodCatalogRepository.get_by_group('A')
            >>> len(group_a)
            5  # 5 methods in Group A
        """
        if group_code not in ('A', 'B', 'C'):
            raise ValueError(f"Invalid group_code: {group_code}. Must be A, B, or C")

        if use_cache:
            cache_key = CacheService.make_key('CATALOG', 'learning_methods', f'group_{group_code}')
            ttl = current_app.config.get('CACHE_CATALOG_TTL', 3600)

            def load_group():
                return cls._fetch_by_group(group_code)

            return CacheService.cache_get_or_set(cache_key, ttl, load_group)

        return cls._fetch_by_group(group_code)

    @classmethod
    def _fetch_by_group(cls, group_code: str) -> Optional[List[Dict[str, Any]]]:
        """
        Internal method to fetch LM group from database.

        Args:
            group_code: Group code ('A', 'B', or 'C')

        Returns:
            List of methods in group or None if query fails
        """
        try:
            with db_pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute("""
                        SELECT
                            type_id,
                            method_type,
                            name,
                            description,
                            group_code,
                            tier,
                            ki_usage,
                            active,
                            config,
                            ui_schema,
                            icon,
                            created_at,
                            updated_at
                        FROM learning_methods.learning_method_types
                        WHERE group_code = %s AND active = TRUE
                        ORDER BY method_type
                    """, (group_code,))

                    methods = cur.fetchall()

                    if not methods:
                        logger.warning(f"No learning methods found in group {group_code}")
                        return []

                    # Process each method
                    for method in methods:
                        # Process ui_schema if it's a string
                        if isinstance(method.get('ui_schema'), str):
                            try:
                                method['ui_schema'] = json.loads(method['ui_schema'])
                            except (json.JSONDecodeError, TypeError):
                                method['ui_schema'] = {}

                        # Process config similarly
                        if isinstance(method.get('config'), str):
                            try:
                                method['config'] = json.loads(method['config'])
                            except (json.JSONDecodeError, TypeError):
                                method['config'] = {}

                        # Convert timestamps to ISO format strings
                        if hasattr(method.get('created_at'), 'isoformat'):
                            method['created_at'] = method['created_at'].isoformat()
                        if hasattr(method.get('updated_at'), 'isoformat'):
                            method['updated_at'] = method['updated_at'].isoformat()

                    return methods

        except Exception as e:
            logger.exception(f"Error fetching learning methods group {group_code}: {e}")
            return None

    @classmethod
    def invalidate_cache(cls) -> None:
        """
        Invalidate all catalog caches.

        Call this when a new LM is added or LM configuration changes.

        Example:
            >>> # After updating learning methods
            >>> LearningMethodCatalogRepository.invalidate_cache()
        """
        try:
            # Invalidate full catalog cache
            cache_key = CacheService.make_key('CATALOG', 'learning_methods', 'all')
            CacheService.delete(cache_key)

            # Invalidate group caches
            for group in ['A', 'B', 'C']:
                cache_key = CacheService.make_key('CATALOG', 'learning_methods', f'group_{group}')
                CacheService.delete(cache_key)

            # Invalidate individual method caches
            for method_type in range(12):
                cache_key = CacheService.make_key('CATALOG', 'learning_methods', f'type_{method_type}')
                CacheService.delete(cache_key)

            logger.info("Learning method catalog caches invalidated")

        except Exception as e:
            logger.exception(f"Error invalidating catalog cache: {e}")


__all__ = ['LearningMethodCatalogRepository']
