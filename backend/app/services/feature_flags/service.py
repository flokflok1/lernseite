"""
LernsystemX Feature Configuration Service - Core Layer

Service layer for Enterprise Feature Configuration System:
- Permission checking (7-point system)
- Feature access logic
- User feature discovery
- Rollout management
- A/B test variant assignment
- Organization overrides
- Audit logging

Phase 2 - Core Service Layer (Part 1)
Handles all business logic for feature access control.

For cache operations, see: feature_configuration_cache.py
For rollout operations, see: feature_configuration_rollout.py
For A/B test operations, see: feature_configuration_ab_test.py
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import json
import logging

from app.database.connection import get_db_connection
from app.repositories.feature_configuration import (
    FeatureConfigurationRepository,
    FeatureRoleMappingRepository
)
from app.repositories.feature_configuration_part2 import (
    FeatureTierLimitRepository,
    FeatureCacheStatusRepository
)
from app.infrastructure.utils.exceptions import ValidationError, NotFoundError

logger = logging.getLogger(__name__)


class FeatureConfigurationService:
    """
    Core service for feature configuration and access control.

    Implements enterprise feature flag system with:
    - Multi-level permission checking (user, role, tier, org)
    - Progressive rollout support (canary deployments)
    - A/B testing capabilities
    - Organization overrides
    - Complete audit trail
    """

    # ==================== CORE PERMISSION CHECKING ====================

    @staticmethod
    def can_user_access_feature(
        user_id: str,
        feature_name: str,
        user_role: str,
        user_tier: str,
        organization_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Check if user can access feature (7-point permission system).

        Permission checks (in order):
        1. Feature exists and is globally enabled
        2. User's role has feature enabled
        3. User's subscription tier has feature available
        4. User hasn't exceeded daily/monthly quotas
        5. Organization hasn't exceeded quotas (if org-scoped)
        6. Progressive rollout percentage allows access
        7. A/B test variant assignment (if active)

        Args:
            user_id: User ID
            feature_name: Feature name to check
            user_role: User's role (admin, teacher, student, etc.)
            user_tier: User's subscription tier (free, premium, enterprise)
            organization_id: Optional organization ID for org-scoped features

        Returns:
            Tuple[bool, str]: (can_access, reason)
            - (True, "allowed") if all checks pass
            - (False, reason) if any check fails

        Example:
            can_access, reason = FeatureConfigurationService.can_user_access_feature(
                user_id="user123",
                feature_name="ai_tutor",
                user_role="student",
                user_tier="premium"
            )
            if not can_access:
                logger.info(f"Feature access denied: {reason}")
        """

        with get_db_connection() as conn:
            feature_repo = FeatureConfigurationRepository()
            role_repo = FeatureRoleMappingRepository()
            tier_repo = FeatureTierLimitRepository()

            # CHECK 1: Feature exists and is globally enabled
            feature = feature_repo.find_by_name(feature_name)
            if not feature:
                return False, f"Feature '{feature_name}' not found"

            if not feature.get('is_enabled', False):
                return False, f"Feature '{feature_name}' is globally disabled"

            # CHECK 2: Role has feature enabled
            role_mapping = role_repo.find_by_feature_and_role(feature_name, user_role)
            if not role_mapping:
                return False, f"Role '{user_role}' not configured for feature '{feature_name}'"

            if not role_mapping.get('is_enabled', False):
                return False, f"Feature '{feature_name}' disabled for role '{user_role}'"

            # CHECK 3: Tier has feature available
            tier_limit = tier_repo.find_by_feature_and_tier(feature_name, user_tier)
            if not tier_limit:
                return False, f"Tier '{user_tier}' not configured for feature '{feature_name}'"

            if not tier_limit.get('is_enabled', False):
                return False, f"Feature '{feature_name}' not available in tier '{user_tier}'"

            # CHECK 4: User hasn't exceeded quotas
            quota_check, quota_reason = FeatureConfigurationService._check_user_quotas(
                user_id, feature_name, role_mapping
            )
            if not quota_check:
                return False, quota_reason

            # CHECK 5: Organization hasn't exceeded quotas (if org-scoped)
            if organization_id:
                org_check, org_reason = FeatureConfigurationService._check_org_quotas(
                    organization_id, feature_name, tier_limit
                )
                if not org_check:
                    return False, org_reason

            # CHECK 6: Progressive rollout percentage allows access
            rollout_check, rollout_reason = FeatureConfigurationService._check_rollout_eligibility(
                user_id, feature_name
            )
            if not rollout_check:
                return False, rollout_reason

            # CHECK 7: A/B test variant assignment
            # Note: A/B test access is allowed for all users, but variant is tracked
            # This check only fails if test is active and user is excluded
            ab_test_check, ab_test_reason = FeatureConfigurationService._check_ab_test_eligibility(
                user_id, feature_name
            )
            if not ab_test_check:
                return False, ab_test_reason

        return True, "allowed"

    @staticmethod
    def _check_user_quotas(
        user_id: str,
        feature_name: str,
        role_mapping: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Check if user has exceeded daily/monthly quotas.

        Args:
            user_id: User ID
            feature_name: Feature name
            role_mapping: Role mapping config with quota limits

        Returns:
            Tuple[bool, str]: (within_quota, reason)
        """
        max_daily = role_mapping.get('max_usage_per_day')
        max_monthly = role_mapping.get('max_creation_per_month')

        # TODO: Query usage tracking table to check quotas
        # For now, return True (quota checking requires usage tracking table)

        return True, ""

    @staticmethod
    def _check_org_quotas(
        organization_id: str,
        feature_name: str,
        tier_limit: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Check if organization has exceeded tier-based quotas.

        Args:
            organization_id: Organization ID
            feature_name: Feature name
            tier_limit: Tier limit config with resource limits

        Returns:
            Tuple[bool, str]: (within_quota, reason)
        """
        max_monthly = tier_limit.get('max_monthly_quota')
        max_storage = tier_limit.get('max_storage_gb')
        max_concurrent = tier_limit.get('max_concurrent_usage')

        # TODO: Query organization usage table to check quotas
        # For now, return True

        return True, ""

    @staticmethod
    def _check_rollout_eligibility(
        user_id: str,
        feature_name: str
    ) -> Tuple[bool, str]:
        """
        Check if user is in active rollout percentage for feature.

        Args:
            user_id: User ID
            feature_name: Feature name

        Returns:
            Tuple[bool, str]: (eligible, reason)
        """
        # TODO: Implement rollout percentage check
        # For now, return True

        return True, ""

    @staticmethod
    def _check_ab_test_eligibility(
        user_id: str,
        feature_name: str
    ) -> Tuple[bool, str]:
        """
        Check if user is eligible for active A/B test.

        Args:
            user_id: User ID
            feature_name: Feature name

        Returns:
            Tuple[bool, str]: (eligible, reason)
        """
        # TODO: Implement A/B test eligibility check
        # For now, return True

        return True, ""

    # ==================== FEATURE ACCESS DISCOVERY ====================

    @staticmethod
    def get_user_features(
        user_id: str,
        user_role: str,
        user_tier: str,
        organization_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all features accessible to user.

        Filters features based on:
        - User role permissions
        - Subscription tier availability
        - Progressive rollout status
        - Organization overrides

        Args:
            user_id: User ID
            user_role: User's role
            user_tier: User's subscription tier
            organization_id: Optional organization ID
            limit: Max features to return

        Returns:
            List of accessible features with metadata
        """
        accessible_features = []

        with get_db_connection() as conn:
            feature_repo = FeatureConfigurationRepository()
            role_repo = FeatureRoleMappingRepository()

            # Get all enabled features
            features = feature_repo.find_enabled(limit=limit)

            for feature in features:
                feature_name = feature.get('name')

                # Check if user can access this feature
                can_access, _ = FeatureConfigurationService.can_user_access_feature(
                    user_id=user_id,
                    feature_name=feature_name,
                    user_role=user_role,
                    user_tier=user_tier,
                    organization_id=organization_id
                )

                if can_access:
                    # Get role-specific metadata
                    role_mapping = role_repo.find_by_feature_and_role(
                        feature_name, user_role
                    )

                    feature_data = {
                        'name': feature_name,
                        'category': feature.get('category'),
                        'description': feature.get('description'),
                        'quotas': {
                            'daily': role_mapping.get('max_usage_per_day') if role_mapping else None,
                            'monthly': role_mapping.get('max_creation_per_month') if role_mapping else None
                        }
                    }

                    accessible_features.append(feature_data)

        return accessible_features

    # ==================== FEATURE MANAGEMENT ====================

    @staticmethod
    def enable_feature(feature_name: str) -> Dict[str, Any]:
        """
        Enable a feature globally.

        Args:
            feature_name: Feature to enable

        Returns:
            Updated feature configuration

        Raises:
            NotFoundError: If feature not found
        """
        with get_db_connection() as conn:
            feature_repo = FeatureConfigurationRepository()
            feature = feature_repo.find_by_name(feature_name)

            if not feature:
                raise NotFoundError(f"Feature '{feature_name}' not found")

            updated = feature_repo.enable(feature['id'])

            # Invalidate cache
            FeatureConfigurationService._invalidate_feature_cache(feature_name)

            # Log audit event
            FeatureConfigurationService._log_audit_event(
                feature_name=feature_name,
                action="FEATURE_ENABLED",
                change_details={'from': False, 'to': True}
            )

            return updated

    @staticmethod
    def disable_feature(feature_name: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Disable a feature globally.

        Args:
            feature_name: Feature to disable
            reason: Optional reason for disabling

        Returns:
            Updated feature configuration

        Raises:
            NotFoundError: If feature not found
        """
        with get_db_connection() as conn:
            feature_repo = FeatureConfigurationRepository()
            feature = feature_repo.find_by_name(feature_name)

            if not feature:
                raise NotFoundError(f"Feature '{feature_name}' not found")

            updated = feature_repo.disable(feature['id'])

            # Invalidate cache
            FeatureConfigurationService._invalidate_feature_cache(feature_name)

            # Log audit event
            FeatureConfigurationService._log_audit_event(
                feature_name=feature_name,
                action="FEATURE_DISABLED",
                change_details={'from': True, 'to': False, 'reason': reason}
            )

            return updated

    # ==================== CACHE MANAGEMENT ====================

    @staticmethod
    def _invalidate_feature_cache(feature_name: str) -> None:
        """
        Invalidate cache for feature configuration.

        Args:
            feature_name: Feature name
        """
        # TODO: Implement Redis cache invalidation
        # Update cache_status table to mark cache as stale
        # Publish Redis Pub/Sub event for real-time updates
        pass

    # ==================== AUDIT LOGGING ====================

    @staticmethod
    def _log_audit_event(
        feature_name: str,
        action: str,
        change_details: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> None:
        """
        Log feature configuration change to audit log.

        Args:
            feature_name: Feature name
            action: Action type (FEATURE_ENABLED, FEATURE_DISABLED, etc.)
            change_details: Details of what changed
            user_id: User who made the change
            organization_id: Organization affected
        """
        # TODO: Implement audit logging to feature_flag_audit_log_enhanced table
        logger.info(
            f"Feature audit: {action} on '{feature_name}'",
            extra={
                'feature_name': feature_name,
                'action': action,
                'changes': change_details
            }
        )
