"""
Feature Service - Feature-Based Authorization Business Logic

Implements feature access control with caching:
- User feature availability calculation
- Feature metadata caching
- Context-aware feature filtering (admin/user/community contexts)

RBAC 2.0: Combines role-based features + organization subscriptions.
Caches results in Redis (TTL: 5 minutes) for performance.
"""

from typing import List, Optional, Dict, Any
import logging

from app.repositories.feature_repository import FeatureRepository
from app.repositories.user import UserRepository
from app.services.cache_service import CacheService
from app.database import get_connection

logger = logging.getLogger(__name__)


class FeatureService:
    """
    Feature-based authorization service.

    Provides high-level feature access control:
    - Get available features for user (role + org tier)
    - Check single feature access
    - Get feature metadata with caching
    - Filter features by context (admin, user, community)

    Example:
        >>> features = FeatureService.get_available_features(user_id='user-123')
        >>> FeatureService.can_access_feature('user-123', 'ai_editor')
        True
    """

    # Cache configuration
    CACHE_TTL = 300  # 5 minutes
    CACHE_PREFIX_FEATURES = "CACHE:FEATURES"
    CACHE_PREFIX_METADATA = "CACHE:FEATURE_METADATA"

    @classmethod
    def get_available_features(cls, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all features available to a user.

        Combines:
        - Role-based features (from roles.role_features)
        - Organization subscription features (from organisations.feature_subscriptions)

        Args:
            user_id: User UUID

        Returns:
            List of available feature dictionaries with metadata

        Example:
            >>> features = FeatureService.get_available_features('user-123')
            >>> [f['feature_code'] for f in features]
            ['ai_editor', 'code_sandbox', 'learning_journal', ...]
        """
        # Check cache first
        cache_key = f"{cls.CACHE_PREFIX_FEATURES}:{user_id}:available"
        cached = CacheService.cache_get(cache_key)

        if cached is not None:
            return cached

        try:
            # Get user's role and organization
            with get_connection() as conn:
                user_repo = UserRepository(conn)
                user_data = user_repo.find_by_id(user_id)

                if not user_data:
                    logger.warning(f"User {user_id} not found")
                    return []

                role_id = user_data.get('role_id')
                org_id = user_data.get('organisation_id')

                # Get role features
                feature_repo = FeatureRepository(conn)
                role_features = feature_repo.get_role_features(role_id)

                # Get org subscription features
                org_features = []
                if org_id:
                    org_features = feature_repo.get_org_subscribed_features(
                        org_id,
                        active_only=True
                    )

                # Merge and deduplicate by feature_code
                features_dict = {}

                for feature in role_features:
                    code = feature['feature_code']
                    if code not in features_dict:
                        features_dict[code] = feature

                for feature in org_features:
                    code = feature['feature_code']
                    if code not in features_dict:
                        features_dict[code] = feature

                features = list(features_dict.values())

            # Cache the result
            CacheService.cache_set(cache_key, features, ttl=cls.CACHE_TTL)

            return features

        except Exception as e:
            logger.error(
                f"Error getting available features for user {user_id}: {e}"
            )
            return []

    @classmethod
    def can_access_feature(
        cls,
        user_id: str,
        feature_code: str,
        require_active: bool = True
    ) -> bool:
        """
        Check if user can access a specific feature.

        Args:
            user_id: User UUID
            feature_code: Feature code to check
            require_active: Require feature to be active (default: True)

        Returns:
            True if user can access feature, False otherwise

        Example:
            >>> FeatureService.can_access_feature('user-123', 'ai_editor')
            True
            >>> FeatureService.can_access_feature('user-456', 'ai_editor')
            False  # User role doesn't have ai_editor
        """
        # Check cache
        cache_key = f"{cls.CACHE_PREFIX_FEATURES}:{user_id}:{feature_code}"
        cached = CacheService.cache_get(cache_key)

        if cached is not None:
            return cached

        try:
            # Get available features for user
            features = cls.get_available_features(user_id)

            # Check if feature is in the list
            has_access = any(
                f['feature_code'] == feature_code for f in features
            )

            # Cache the result
            CacheService.cache_set(cache_key, has_access, ttl=cls.CACHE_TTL)

            return has_access

        except Exception as e:
            logger.error(
                f"Error checking feature access ({user_id}, {feature_code}): {e}"
            )
            return False

    @classmethod
    def get_feature_metadata(cls, feature_code: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific feature.

        Includes name, description, category, icon, and infrastructure requirements.
        Results cached in Redis.

        Args:
            feature_code: Feature code

        Returns:
            Feature metadata dictionary or None if not found

        Example:
            >>> metadata = FeatureService.get_feature_metadata('ai_editor')
            >>> metadata['feature_name']
            'AI-Studio'
            >>> metadata['category']
            'ai'
        """
        # Check cache first
        cache_key = f"{cls.CACHE_PREFIX_METADATA}:{feature_code}"
        cached = CacheService.cache_get(cache_key)

        if cached is not None:
            return cached

        try:
            feature = FeatureRepository.find_by_code(feature_code)

            if feature:
                # Cache the result
                CacheService.cache_set(cache_key, feature, ttl=cls.CACHE_TTL)

            return feature

        except Exception as e:
            logger.error(f"Error getting feature metadata for {feature_code}: {e}")
            return None

    @classmethod
    def get_user_context_features(
        cls,
        user_id: str,
        context: str = "user"
    ) -> List[Dict[str, Any]]:
        """
        Get features filtered by user context.

        Contexts:
        - 'user': Learning and personal features
        - 'admin': Administration and management features
        - 'community': Public and social features

        Args:
            user_id: User UUID
            context: Context type ('user', 'admin', 'community')

        Returns:
            Filtered list of features

        Example:
            >>> admin_features = FeatureService.get_user_context_features(
            ...     'user-123', context='admin'
            ... )
            >>> [f['feature_code'] for f in admin_features]
            ['course_management', 'student_management', ...]
        """
        all_features = cls.get_available_features(user_id)

        if not all_features:
            return []

        # Filter by category based on context
        context_categories = {
            'user': [
                'learning_paths',
                'visualization',
                'audio',
                'gamification',
                'collaboration',
                'tutor'
            ],
            'admin': [
                'learning_paths',
                'collaboration'
            ],
            'community': [
                'collaboration',
                'visualization'
            ]
        }

        categories = context_categories.get(context, [])

        if not categories:
            return all_features

        filtered = [
            f for f in all_features
            if f.get('category') in categories
        ]

        return filtered

    @classmethod
    def get_feature_permission(
        cls,
        user_id: str,
        feature_code: str,
        permission_key: str
    ) -> Optional[bool]:
        """
        Get specific permission within a feature for user.

        Permissions are specific capabilities within features:
        - 'ai_editor.execute': Can use AI features
        - 'ai_editor.manage': Can create AI content
        - 'analytics.export': Can export analytics data

        Args:
            user_id: User UUID
            feature_code: Feature code
            permission_key: Permission key (e.g., 'ai_editor.execute')

        Returns:
            True if allowed, False if denied, None if not defined

        Example:
            >>> allowed = FeatureService.get_feature_permission(
            ...     'user-123', 'ai_editor', 'ai_editor.execute'
            ... )
            >>> allowed
            True
        """
        cache_key = (
            f"{cls.CACHE_PREFIX_FEATURES}:{user_id}:{feature_code}:{permission_key}"
        )
        cached = CacheService.cache_get(cache_key)

        if cached is not None:
            return cached

        try:
            with get_connection() as conn:
                user_repo = UserRepository(conn)
                user_data = user_repo.find_by_id(user_id)
                if not user_data:
                    return None

                role_id = user_data.get('role_id')

                # Get permission from repository
                feature_repo = FeatureRepository(conn)
                allowed = feature_repo.get_feature_permission(
                    role_id,
                    feature_code,
                    permission_key
                )

            # Cache the result
            CacheService.cache_set(cache_key, allowed, ttl=cls.CACHE_TTL)

            return allowed

        except Exception as e:
            logger.error(
                f"Error getting feature permission ({user_id}, {feature_code}, {permission_key}): {e}"
            )
            return None

    @classmethod
    def invalidate_user_cache(cls, user_id: str) -> None:
        """
        Invalidate cached features for a user.

        Call this when user's role or organization changes.

        Args:
            user_id: User UUID

        Example:
            >>> FeatureService.invalidate_user_cache('user-123')
        """
        try:
            # Delete user's feature cache entries
            cache_keys = [
                f"{cls.CACHE_PREFIX_FEATURES}:{user_id}:*"
            ]

            for key_pattern in cache_keys:
                CacheService.cache_delete_pattern(key_pattern)

            logger.info(f"Invalidated feature cache for user {user_id}")

        except Exception as e:
            logger.error(f"Error invalidating cache for user {user_id}: {e}")

    @classmethod
    def get_all_features_summary(cls) -> Dict[str, Any]:
        """
        Get summary of all system features.

        Returns feature counts by category and status.

        Returns:
            Summary dictionary

        Example:
            >>> summary = FeatureService.get_all_features_summary()
            >>> summary['total_features']
            25
            >>> summary['by_category']['ai']
            5
        """
        try:
            features = FeatureRepository.list_all_features(active_only=True)

            summary = {
                'total_features': len(features),
                'by_category': {},
                'features': []
            }

            for feature in features:
                category = feature.get('category', 'unknown')

                if category not in summary['by_category']:
                    summary['by_category'][category] = 0

                summary['by_category'][category] += 1

                summary['features'].append({
                    'code': feature['feature_code'],
                    'name': feature['feature_name'],
                    'category': category
                })

            return summary

        except Exception as e:
            logger.error(f"Error getting features summary: {e}")
            return {'total_features': 0, 'by_category': {}, 'features': []}
