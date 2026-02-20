"""
Feature Flag Manager - Core of Dark Launch Strategy

Manages feature flags with support for:
- Global flags
- User-specific overrides
- Organization-specific overrides
- Percentage rollout (5% → 25% → 100%)
- User segments (beta, premium, etc.)

Priority Order:
1. User-specific override
2. Organization-specific override
3. User segment (beta, premium)
4. Percentage rollout
5. Global flag
"""

import hashlib
from typing import Optional, Dict
from app.core.bootstrap.extensions import redis_client
from app.infrastructure.persistence.repositories.feature_flags.core import FeatureFlagRepository


class FeatureFlagManager:
    """
    Feature Flag Manager for Progressive Rollout

    Example:
        flag_manager = FeatureFlagManager()
        is_enabled = flag_manager.is_enabled('user_posts', user_id='123')
    """

    def __init__(self):
        self.redis = redis_client
        self.cache_ttl = 300  # 5 minutes

    def is_enabled(
        self,
        feature_name: str,
        user_id: Optional[str] = None,
        organisation_id: Optional[str] = None,
        user_segment: Optional[str] = None
    ) -> bool:
        """
        Check if feature is enabled for given context

        Args:
            feature_name: Name of feature flag (e.g., 'user_posts')
            user_id: Optional user ID to check
            organisation_id: Optional organisation ID
            user_segment: Optional user segment (e.g., 'beta', 'premium')

        Returns:
            bool: True if feature is enabled, False otherwise
        """

        # Check cache
        if self.redis:
            cache_key = f"feature_flag:{feature_name}:{user_id}:{organisation_id}"
            cached = self.redis.get(cache_key)
            if cached is not None:
                return cached == 'true'

        # 1. Check user-specific override (highest priority)
        if user_id:
            user_override = self._get_user_override(feature_name, user_id)
            if user_override is not None:
                if self.redis:
                    self._cache_result(cache_key, user_override)
                return user_override

        # 2. Check organisation-specific override
        if organisation_id:
            org_override = self._get_org_override(feature_name, organisation_id)
            if org_override is not None:
                if self.redis:
                    self._cache_result(cache_key, org_override)
                return org_override

        # 3. Check user segment
        if user_segment:
            segment_enabled = self._check_user_segment(feature_name, user_segment)
            if segment_enabled is not None:
                if self.redis:
                    self._cache_result(cache_key, segment_enabled)
                return segment_enabled

        # 4. Check percentage rollout
        if user_id:
            percentage_enabled = self._check_percentage_rollout(feature_name, user_id)
            if percentage_enabled is not None:
                if self.redis:
                    self._cache_result(cache_key, percentage_enabled)
                return percentage_enabled

        # 5. Check global flag (lowest priority)
        global_enabled = self._get_global_flag(feature_name)
        if self.redis:
            self._cache_result(cache_key, global_enabled)
        return global_enabled

    def _get_global_flag(self, feature_name: str) -> bool:
        """Get global feature flag from database"""
        flag = FeatureFlagRepository.get_global_flag(feature_name)
        return flag['is_enabled'] if flag else False

    def _get_user_override(self, feature_name: str, user_id: str) -> Optional[bool]:
        """Check if user has specific override"""
        override = FeatureFlagRepository.get_user_override(feature_name, user_id)
        return override['is_enabled'] if override else None

    def _get_org_override(self, feature_name: str, org_id: str) -> Optional[bool]:
        """Check if organisation has specific override"""
        override = FeatureFlagRepository.get_org_override(feature_name, org_id)
        return override['is_enabled'] if override else None

    def _check_user_segment(self, feature_name: str, segment: str) -> Optional[bool]:
        """Check if feature is enabled for user segment (beta, premium, etc.)"""
        segment_config = FeatureFlagRepository.get_segment_config(feature_name, segment)
        return segment_config['is_enabled'] if segment_config else None

    def _check_percentage_rollout(self, feature_name: str, user_id: str) -> Optional[bool]:
        """
        Check if user is in percentage rollout using deterministic hash

        Example: 25% rollout means first 25% of users based on hash
        """
        rollout = FeatureFlagRepository.get_rollout_percentage(feature_name)

        if not rollout:
            return None

        # Deterministic hash-based rollout
        hash_value = int(hashlib.md5(f"{feature_name}:{user_id}".encode()).hexdigest(), 16)
        user_percentage = (hash_value % 100) + 1

        return user_percentage <= rollout['percentage']

    def _cache_result(self, cache_key: str, value: bool):
        """Cache feature flag result in Redis"""
        if self.redis:
            self.redis.setex(cache_key, self.cache_ttl, 'true' if value else 'false')

    def enable_feature(
        self,
        feature_name: str,
        globally: bool = False,
        user_id: Optional[str] = None,
        organisation_id: Optional[str] = None
    ):
        """
        Enable a feature (Admin API)

        Args:
            feature_name: Feature flag name
            globally: Enable for all users
            user_id: Enable for specific user
            organisation_id: Enable for specific organisation
        """
        if globally:
            FeatureFlagRepository.upsert_global_flag(feature_name, True)
        elif user_id:
            FeatureFlagRepository.upsert_user_override(feature_name, user_id, True)
        elif organisation_id:
            FeatureFlagRepository.upsert_org_override(feature_name, organisation_id, True)

        self._clear_cache(feature_name)

    def disable_feature(
        self,
        feature_name: str,
        globally: bool = False,
        user_id: Optional[str] = None,
        organisation_id: Optional[str] = None
    ):
        """Disable a feature (Admin API)"""
        if globally:
            FeatureFlagRepository.update_global_flag(feature_name, False)
        elif user_id:
            FeatureFlagRepository.update_user_override(feature_name, user_id, False)
        elif organisation_id:
            FeatureFlagRepository.update_org_override(feature_name, organisation_id, False)

        self._clear_cache(feature_name)

    def set_percentage_rollout(self, feature_name: str, percentage: int):
        """
        Set percentage rollout for feature

        Args:
            feature_name: Feature flag name
            percentage: 0-100 (e.g., 25 for 25% rollout)
        """
        if not 0 <= percentage <= 100:
            raise ValueError("Percentage must be between 0 and 100")

        FeatureFlagRepository.upsert_rollout_percentage(feature_name, percentage)
        self._clear_cache(feature_name)

    def _clear_cache(self, feature_name: str):
        """Clear all cached results for feature"""
        if self.redis:
            pattern = f"feature_flag:{feature_name}:*"
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)

    def get_all_flags(self) -> Dict[str, Dict]:
        """
        Get all feature flags with their status (Admin API)

        Returns:
            Dict with feature name as key and status dict as value
        """
        results = FeatureFlagRepository.get_all_flags()
        flags = {}

        for row in results:
            flags[row['name']] = {
                'is_enabled': row['is_enabled'],
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
            }

        return flags
