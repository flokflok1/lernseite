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

from app.core.bootstrap import extensions
from app.infrastructure.cache.service import CacheService
from flask import current_app

logger = logging.getLogger(__name__)

# Import group repository for database-driven group validation
# (prevents circular imports - imported only when needed)
def _get_group_repository():
    from app.infrastructure.persistence.repositories.learning_method.groups import LearningMethodGroupRepository
    return LearningMethodGroupRepository


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
            - groups: Grouped metadata for UI organisation

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
            with extensions.db_pool.connection() as conn:
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

                    # Get groups from database (100% database-driven)
                    GroupRepository = _get_group_repository()
                    all_groups = GroupRepository.find_all()

                    # Convert to list and process schemas
                    methods_list = []
                    groups_dict = {}

                    # Build groups_dict from database (not hardcoded!)
                    for group_data in all_groups:
                        group_code = group_data.get('group_code')
                        groups_dict[group_code] = {
                            'name': f"{group_data.get('name')} ({group_code})",  # e.g., "Erklärend (A)"
                            'count': 0,
                            'description': group_data.get('description', ''),
                            'icon': group_data.get('icon', '📋')
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
    def get_max_active_type(cls) -> int:
        """
        Get the maximum active learning method type from database.

        Dynamic query - allows system to scale beyond hardcoded limits.

        Returns:
            Maximum method_type value for active learning methods

        Example:
            >>> max_type = LearningMethodCatalogRepository.get_max_active_type()
            >>> 11  # Currently 12 methods (0-11)
        """
        try:
            with extensions.db_pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT COALESCE(MAX(method_type), 0)
                        FROM learning_methods.learning_method_types
                        WHERE active = TRUE
                    """)
                    result = cur.fetchone()
                    return result[0] if result else 0
        except Exception as e:
            logger.exception(f"Error getting max active method type: {e}")
            return 11  # Fallback to current max

    @classmethod
    def get_all_active_types(cls) -> List[int]:
        """
        Get list of all active learning method types from database.

        Used for cache invalidation and dynamic system scaling.

        Returns:
            List of active method_type values

        Example:
            >>> types = LearningMethodCatalogRepository.get_all_active_types()
            >>> [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]  # All 12 methods
        """
        try:
            with extensions.db_pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT method_type
                        FROM learning_methods.learning_method_types
                        WHERE active = TRUE
                        ORDER BY method_type
                    """)
                    results = cur.fetchall()
                    return [row[0] for row in results] if results else []
        except Exception as e:
            logger.exception(f"Error getting active method types: {e}")
            return list(range(12))  # Fallback to 0-11

    @classmethod
    def get_by_type(cls, method_type: int, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get single Learning Method by type ID with UI schema.

        Args:
            method_type: Learning method type (must be active in database)
            use_cache: Use cached result (default: True)

        Returns:
            Dictionary with method metadata and ui_schema, or None if not found

        Raises:
            ValueError: If method_type is invalid or inactive

        Example:
            >>> lm00 = LearningMethodCatalogRepository.get_by_type(0)
            >>> lm00['name']
            'Tiefgehende Erklärung'
        """
        # Validate method_type dynamically
        if not isinstance(method_type, int) or method_type < 0:
            raise ValueError(f"Invalid method_type: {method_type}. Must be a non-negative integer")

        max_type = cls.get_max_active_type()
        if method_type > max_type:
            raise ValueError(f"Invalid method_type: {method_type}. Maximum active type is {max_type}")

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
            with extensions.db_pool.connection() as conn:
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
            group_code: Group code (dynamically validated against database, e.g., 'A', 'B', 'C')
            use_cache: Use cached result (default: True)

        Returns:
            List of methods in group, or None if invalid group

        Raises:
            ValueError: If group_code does not exist in learning_method_groups table

        Example:
            >>> group_a = LearningMethodCatalogRepository.get_by_group('A')
            >>> len(group_a)
            5  # 5 methods in Group A
        """
        # Validate group code against database (dynamically, not hardcoded!)
        GroupRepository = _get_group_repository()
        group = GroupRepository.find_by_code(group_code)
        if not group:
            raise ValueError(f"Invalid group_code: {group_code}. Group not found in database")

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
            with extensions.db_pool.connection() as conn:
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
        Invalidate all catalog caches dynamically.

        Call this when a new LM is added or LM configuration changes.
        Dynamically queries database for all active types - no hardcoded limits.

        Example:
            >>> # After updating learning methods
            >>> LearningMethodCatalogRepository.invalidate_cache()
        """
        try:
            # Invalidate full catalog cache
            cache_key = CacheService.make_key('CATALOG', 'learning_methods', 'all')
            CacheService.delete(cache_key)

            # Invalidate group caches - DYNAMIC (query from database, not hardcoded!)
            GroupRepository = _get_group_repository()
            all_groups = GroupRepository.find_all()
            for group_data in all_groups:
                group_code = group_data.get('group_code')
                cache_key = CacheService.make_key('CATALOG', 'learning_methods', f'group_{group_code}')
                CacheService.delete(cache_key)

            # Invalidate individual method caches - DYNAMIC (no hardcoded range!)
            active_types = cls.get_all_active_types()
            for method_type in active_types:
                cache_key = CacheService.make_key('CATALOG', 'learning_methods', f'type_{method_type}')
                CacheService.delete(cache_key)

            logger.info(f"Learning method catalog caches invalidated ({len(active_types)} methods)")

        except Exception as e:
            logger.exception(f"Error invalidating catalog cache: {e}")


__all__ = ['LearningMethodCatalogRepository']
