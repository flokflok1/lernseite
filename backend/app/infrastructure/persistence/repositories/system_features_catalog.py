"""
System Features Catalog Repository - Schema-Based Dynamic System

Data access layer for system features catalog with ui_schemas.

This repository fetches from support_systems.system_features table
and includes the ui_schema JSONB column for dynamic configuration rendering.

Features:
- Get all 25 System Features with full metadata and schemas
- Get single feature by code with schema
- Get features by category with schema
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


class SystemFeaturesCatalogRepository:
    """
    Repository for system features catalog with UI schemas.

    All 25 System-Features are accessed here.
    Each feature includes full ui_schema for dynamic configuration rendering.
    """

    @classmethod
    def get_full_catalog(cls, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get complete catalog of all System Features with UI schemas.

        Args:
            use_cache: Use cached result (default: True)

        Returns:
            Dictionary with:
            - features: List of all system features with full metadata and schemas
            - total: Count (always 25 or less depending on seeded data)
            - categories: Grouped metadata for UI organization

        Example:
            >>> catalog = SystemFeaturesCatalogRepository.get_full_catalog()
            >>> len(catalog['features'])
            25
            >>> catalog['features'][0]['feature_code']
            'whiteboard_engine'
        """
        if use_cache:
            cache_key = CacheService.make_key('CATALOG', 'system_features', 'all')
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
                    # Fetch all system features with schemas
                    cur.execute("""
                        SELECT
                            feature_id,
                            feature_code,
                            feature_name,
                            description,
                            category,
                            requires_infrastructure,
                            requires_external_service,
                            active,
                            config,
                            ui_schema,
                            icon,
                            created_at,
                            updated_at
                        FROM support_systems.system_features
                        WHERE active = TRUE
                        ORDER BY category, feature_code
                    """)

                    features = cur.fetchall()

                    if not features:
                        logger.warning("No active system features found in catalog")
                        return None

                    # Convert to list and process schemas
                    features_list = []
                    categories_dict = {
                        'audio': {'name': 'Audio', 'count': 0, 'description': 'Audio processing and synthesis'},
                        'collaboration': {'name': 'Collaboration', 'count': 0, 'description': 'Team and group features'},
                        'exam_systems': {'name': 'Exam Systems', 'count': 0, 'description': 'Assessment and examination tools'},
                        'gamification': {'name': 'Gamification', 'count': 0, 'description': 'Engagement and reward systems'},
                        'interactive_tools': {'name': 'Interactive Tools', 'count': 0, 'description': 'Interactive learning tools'},
                        'it_environments': {'name': 'IT Environments', 'count': 0, 'description': 'Programming and sandbox environments'},
                        'learning_paths': {'name': 'Learning Paths', 'count': 0, 'description': 'Structured learning journeys'},
                        'meta_features': {'name': 'Meta Features', 'count': 0, 'description': 'System-level and meta features'},
                        'tutor': {'name': 'Tutor', 'count': 0, 'description': 'AI tutor and assistance'},
                        'visualization': {'name': 'Visualization', 'count': 0, 'description': 'Data visualization and graphics'},
                    }

                    for feature in features:
                        # Process ui_schema if it's a string (PostgreSQL returns as string sometimes)
                        if isinstance(feature.get('ui_schema'), str):
                            try:
                                feature['ui_schema'] = json.loads(feature['ui_schema'])
                            except (json.JSONDecodeError, TypeError):
                                logger.warning(f"Failed to parse ui_schema for feature {feature['feature_code']}")
                                feature['ui_schema'] = {}

                        # Process config similarly
                        if isinstance(feature.get('config'), str):
                            try:
                                feature['config'] = json.loads(feature['config'])
                            except (json.JSONDecodeError, TypeError):
                                feature['config'] = {}

                        # Convert timestamps to ISO format strings
                        if hasattr(feature.get('created_at'), 'isoformat'):
                            feature['created_at'] = feature['created_at'].isoformat()
                        if hasattr(feature.get('updated_at'), 'isoformat'):
                            feature['updated_at'] = feature['updated_at'].isoformat()

                        features_list.append(feature)

                        # Count by category
                        category = feature.get('category')
                        if category in categories_dict:
                            categories_dict[category]['count'] += 1

                    # Build result
                    return {
                        'features': features_list,
                        'total': len(features_list),
                        'categories': categories_dict
                    }

        except Exception as e:
            logger.exception(f"Error fetching system features catalog: {e}")
            return None

    @classmethod
    def get_by_code(cls, feature_code: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get single System Feature by code with UI schema.

        Args:
            feature_code: System feature code (e.g., 'whiteboard_engine')
            use_cache: Use cached result (default: True)

        Returns:
            Dictionary with feature metadata and ui_schema, or None if not found

        Raises:
            ValueError: If feature_code is empty or invalid format

        Example:
            >>> whiteboard = SystemFeaturesCatalogRepository.get_by_code('whiteboard_engine')
            >>> whiteboard['feature_name']
            'Interactive Whiteboard'
        """
        if not feature_code or not isinstance(feature_code, str):
            raise ValueError(f"Invalid feature_code: {feature_code}")

        if use_cache:
            cache_key = CacheService.make_key('CATALOG', 'system_features', f'code_{feature_code}')
            ttl = current_app.config.get('CACHE_CATALOG_TTL', 3600)

            def load_feature():
                return cls._fetch_by_code(feature_code)

            return CacheService.cache_get_or_set(cache_key, ttl, load_feature)

        return cls._fetch_by_code(feature_code)

    @classmethod
    def _fetch_by_code(cls, feature_code: str) -> Optional[Dict[str, Any]]:
        """
        Internal method to fetch single feature from database.

        Args:
            feature_code: System feature code

        Returns:
            Feature dictionary or None if not found
        """
        try:
            with db_pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute("""
                        SELECT
                            feature_id,
                            feature_code,
                            feature_name,
                            description,
                            category,
                            requires_infrastructure,
                            requires_external_service,
                            active,
                            config,
                            ui_schema,
                            icon,
                            created_at,
                            updated_at
                        FROM support_systems.system_features
                        WHERE feature_code = %s AND active = TRUE
                    """, (feature_code,))

                    feature = cur.fetchone()

                    if not feature:
                        logger.warning(f"System feature {feature_code} not found or inactive")
                        return None

                    # Process ui_schema if it's a string
                    if isinstance(feature.get('ui_schema'), str):
                        try:
                            feature['ui_schema'] = json.loads(feature['ui_schema'])
                        except (json.JSONDecodeError, TypeError):
                            logger.warning(f"Failed to parse ui_schema for feature {feature_code}")
                            feature['ui_schema'] = {}

                    # Process config similarly
                    if isinstance(feature.get('config'), str):
                        try:
                            feature['config'] = json.loads(feature['config'])
                        except (json.JSONDecodeError, TypeError):
                            feature['config'] = {}

                    # Convert timestamps to ISO format strings
                    if hasattr(feature.get('created_at'), 'isoformat'):
                        feature['created_at'] = feature['created_at'].isoformat()
                    if hasattr(feature.get('updated_at'), 'isoformat'):
                        feature['updated_at'] = feature['updated_at'].isoformat()

                    return feature

        except Exception as e:
            logger.exception(f"Error fetching system feature {feature_code}: {e}")
            return None

    @classmethod
    def get_by_category(cls, category: str, use_cache: bool = True) -> Optional[List[Dict[str, Any]]]:
        """
        Get all System Features in a specific category with UI schemas.

        Args:
            category: Feature category (audio, collaboration, exam_systems, etc.)
            use_cache: Use cached result (default: True)

        Returns:
            List of features in category, or None if invalid category

        Raises:
            ValueError: If category is not valid

        Example:
            >>> audio_features = SystemFeaturesCatalogRepository.get_by_category('audio')
            >>> len(audio_features)
            2
        """
        valid_categories = [
            'audio', 'collaboration', 'exam_systems', 'gamification',
            'interactive_tools', 'it_environments', 'learning_paths',
            'meta_features', 'tutor', 'visualization'
        ]

        if category not in valid_categories:
            raise ValueError(f"Invalid category: {category}. Must be one of: {', '.join(valid_categories)}")

        if use_cache:
            cache_key = CacheService.make_key('CATALOG', 'system_features', f'category_{category}')
            ttl = current_app.config.get('CACHE_CATALOG_TTL', 3600)

            def load_category():
                return cls._fetch_by_category(category)

            return CacheService.cache_get_or_set(cache_key, ttl, load_category)

        return cls._fetch_by_category(category)

    @classmethod
    def _fetch_by_category(cls, category: str) -> Optional[List[Dict[str, Any]]]:
        """
        Internal method to fetch features by category from database.

        Args:
            category: Feature category

        Returns:
            List of features in category or None if query fails
        """
        try:
            with db_pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute("""
                        SELECT
                            feature_id,
                            feature_code,
                            feature_name,
                            description,
                            category,
                            requires_infrastructure,
                            requires_external_service,
                            active,
                            config,
                            ui_schema,
                            icon,
                            created_at,
                            updated_at
                        FROM support_systems.system_features
                        WHERE category = %s AND active = TRUE
                        ORDER BY feature_code
                    """, (category,))

                    features = cur.fetchall()

                    if not features:
                        logger.warning(f"No system features found in category {category}")
                        return []

                    # Process each feature
                    for feature in features:
                        # Process ui_schema if it's a string
                        if isinstance(feature.get('ui_schema'), str):
                            try:
                                feature['ui_schema'] = json.loads(feature['ui_schema'])
                            except (json.JSONDecodeError, TypeError):
                                feature['ui_schema'] = {}

                        # Process config similarly
                        if isinstance(feature.get('config'), str):
                            try:
                                feature['config'] = json.loads(feature['config'])
                            except (json.JSONDecodeError, TypeError):
                                feature['config'] = {}

                        # Convert timestamps to ISO format strings
                        if hasattr(feature.get('created_at'), 'isoformat'):
                            feature['created_at'] = feature['created_at'].isoformat()
                        if hasattr(feature.get('updated_at'), 'isoformat'):
                            feature['updated_at'] = feature['updated_at'].isoformat()

                    return features

        except Exception as e:
            logger.exception(f"Error fetching system features category {category}: {e}")
            return None

    @classmethod
    def invalidate_cache(cls) -> None:
        """
        Invalidate all system features catalog caches.

        Call this when a feature is added, removed, or configuration changes.

        Example:
            >>> # After updating system features
            >>> SystemFeaturesCatalogRepository.invalidate_cache()
        """
        try:
            # Invalidate full catalog cache
            cache_key = CacheService.make_key('CATALOG', 'system_features', 'all')
            CacheService.delete(cache_key)

            # Invalidate category caches
            categories = [
                'audio', 'collaboration', 'exam_systems', 'gamification',
                'interactive_tools', 'it_environments', 'learning_paths',
                'meta_features', 'tutor', 'visualization'
            ]
            for category in categories:
                cache_key = CacheService.make_key('CATALOG', 'system_features', f'category_{category}')
                CacheService.delete(cache_key)

            # Invalidate individual feature caches (we don't know all codes, so we'll just log)
            logger.info("System features catalog caches invalidated (full + category caches)")

        except Exception as e:
            logger.exception(f"Error invalidating catalog cache: {e}")


__all__ = ['SystemFeaturesCatalogRepository']
