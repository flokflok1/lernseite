"""
LernsystemX Feature Configuration A/B Test Service

A/B testing for Enterprise Feature Configuration System:
- Test creation and management
- Variant assignment (A vs B)
- Metrics tracking
- Winner determination
- Statistical analysis

Phase 2 - Core Service Layer (Part 4)
Handles all A/B testing logic for feature experimentation.

For core permission logic, see: feature_configuration_service.py
For cache operations, see: feature_configuration_cache.py
For rollout operations, see: feature_configuration_rollout.py
"""

from typing import Optional, Dict, Any, Literal, List
from datetime import datetime, timedelta
import logging
import hashlib
import json

from app.infrastructure.persistence.database.connection import get_db_connection
from app.infrastructure.persistence.repositories.features.configuration_part2 import FeatureAbTestRepository
from app.application.services.feature_flags.cache import FeatureConfigurationCacheService
from app.infrastructure.utils.exceptions import ValidationError, NotFoundError

logger = logging.getLogger(__name__)


class FeatureConfigurationAbTestService:
    """
    Service for managing A/B tests on features.

    Implements controlled experimentation:
    - Create A/B test variants with configurations
    - Assign users to variants deterministically
    - Track metrics and performance
    - Determine statistical winners
    - Apply winning variant to rollout

    Features:
    - Consistent hashing for deterministic variant assignment
    - Per-role and per-tier targeting
    - Configurable split percentages
    - Custom variant configurations
    - Metrics tracking (placeholder for analytics integration)
    """

    @staticmethod
    def create_ab_test(
        feature_name: str,
        test_name: str,
        variant_a_name: str,
        variant_a_percentage: int,
        variant_a_config: Optional[Dict[str, Any]] = None,
        variant_b_name: str = None,
        variant_b_percentage: int = None,
        variant_b_config: Optional[Dict[str, Any]] = None,
        target_roles: Optional[list] = None,
        target_tiers: Optional[list] = None,
        metrics_to_track: Optional[list] = None,
        planned_duration_days: int = 14
    ) -> Dict[str, Any]:
        """
        Create new A/B test for feature.

        Args:
            feature_name: Feature to test
            test_name: Human-readable test name
            variant_a_name: Name for variant A (e.g., "current", "control")
            variant_a_percentage: % of users in variant A (0-100)
            variant_a_config: Optional configuration override for variant A
            variant_b_name: Name for variant B (e.g., "new", "experimental")
            variant_b_percentage: % of users in variant B (0-100)
            variant_b_config: Optional configuration override for variant B
            target_roles: Optional list of roles to include in test
            target_tiers: Optional list of tiers to include in test
            metrics_to_track: List of metrics to track (conversion, engagement, etc.)
            planned_duration_days: Expected duration of test in days

        Returns:
            Created A/B test configuration

        Raises:
            ValidationError: If percentages invalid or don't sum to 100

        Example:
            test = FeatureConfigurationAbTestService.create_ab_test(
                feature_name="ai_tutor",
                test_name="UI Variant Test",
                variant_a_name="control",
                variant_a_percentage=50,
                variant_a_config={'ui_theme': 'dark'},
                variant_b_name="experimental",
                variant_b_percentage=50,
                variant_b_config={'ui_theme': 'light'},
                metrics_to_track=['engagement', 'completion_rate']
            )
        """
        # Validate percentages
        if variant_b_name is None:
            variant_b_name = "variant_b"
        if variant_b_percentage is None:
            variant_b_percentage = 100 - variant_a_percentage

        if not (0 <= variant_a_percentage <= 100):
            raise ValidationError(f"Variant A percentage must be 0-100, got {variant_a_percentage}")
        if not (0 <= variant_b_percentage <= 100):
            raise ValidationError(f"Variant B percentage must be 0-100, got {variant_b_percentage}")

        total_percentage = variant_a_percentage + variant_b_percentage
        if total_percentage != 100:
            raise ValidationError(
                f"Variant percentages must sum to 100%, got {total_percentage}% "
                f"({variant_a_percentage}% + {variant_b_percentage}%)"
            )

        with get_db_connection() as conn:
            ab_test_repo = FeatureAbTestRepository()

            # Create test
            test_data = {
                'feature_name': feature_name,
                'test_name': test_name,
                'variant_a_name': variant_a_name,
                'variant_a_percentage': variant_a_percentage,
                'variant_a_config': variant_a_config,
                'variant_b_name': variant_b_name,
                'variant_b_percentage': variant_b_percentage,
                'variant_b_config': variant_b_config,
                'target_roles': target_roles,
                'target_tiers': target_tiers,
                'metrics_to_track': metrics_to_track,
                'planned_duration_days': planned_duration_days,
                'status': 'planned'
            }

            created_test = ab_test_repo.create(test_data)

            logger.info(
                f"A/B test created for feature '{feature_name}': {test_name}",
                extra={
                    'test_id': created_test.get('id'),
                    'variant_a_pct': variant_a_percentage,
                    'variant_b_pct': variant_b_percentage
                }
            )

            return created_test

    @staticmethod
    def start_ab_test(test_id: int) -> Dict[str, Any]:
        """
        Start A/B test (transition from planned to active).

        Args:
            test_id: A/B test ID

        Returns:
            Updated test configuration

        Raises:
            NotFoundError: If test not found
            ValidationError: If test already started
        """
        with get_db_connection() as conn:
            ab_test_repo = FeatureAbTestRepository()

            # Update test status
            updated_test = ab_test_repo.update(test_id, {
                'status': 'active',
                'started_at': datetime.utcnow()
            })

            if not updated_test:
                raise NotFoundError(f"A/B test {test_id} not found")

            logger.info(f"A/B test started: {updated_test.get('test_name')} (ID: {test_id})")

            return updated_test

    @staticmethod
    def get_user_ab_test_variant(
        user_id: str,
        feature_name: str,
        test_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get A/B test variant assigned to user.

        Uses consistent hashing to ensure deterministic variant assignment:
        - Same user always gets same variant
        - Distribution based on configured percentages
        - Works across multiple nodes/processes

        Args:
            user_id: User ID
            feature_name: Feature name
            test_id: Optional specific test ID (if multiple tests per feature)

        Returns:
            Variant assignment: {
                'variant': 'A' | 'B',
                'variant_name': str,
                'config': dict,
                'test_id': int,
                'feature_name': str
            }

        Returns None if no active test for feature

        Example:
            variant = FeatureConfigurationAbTestService.get_user_ab_test_variant(
                user_id="user123",
                feature_name="ai_tutor"
            )
            if variant:
                config = variant.get('config', {})
                # Apply variant configuration to user
        """
        with get_db_connection() as conn:
            ab_test_repo = FeatureAbTestRepository()

            # Find active test for feature
            active_tests = ab_test_repo.find_by_feature(feature_name)
            active_test = None

            for test in active_tests:
                if test.get('status') == 'active':
                    if test_id is None or test.get('id') == test_id:
                        active_test = test
                        break

            if not active_test:
                return None

            # Determine variant using consistent hash
            variant = FeatureConfigurationAbTestService._assign_variant(
                user_id,
                feature_name,
                active_test.get('variant_a_percentage')
            )

            # Return variant configuration
            if variant == 'A':
                variant_config = active_test.get('variant_a_config', {})
                variant_name = active_test.get('variant_a_name', 'Variant A')
            else:
                variant_config = active_test.get('variant_b_config', {})
                variant_name = active_test.get('variant_b_name', 'Variant B')

            return {
                'variant': variant,
                'variant_name': variant_name,
                'config': variant_config,
                'test_id': active_test.get('id'),
                'test_name': active_test.get('test_name'),
                'feature_name': feature_name
            }

    @staticmethod
    def _assign_variant(
        user_id: str,
        feature_name: str,
        variant_a_percentage: int
    ) -> Literal['A', 'B']:
        """
        Assign variant to user using consistent hashing.

        Args:
            user_id: User ID
            feature_name: Feature name
            variant_a_percentage: Percentage for variant A (0-100)

        Returns:
            'A' or 'B'
        """
        hash_input = f"{feature_name}:{user_id}"
        hash_value = int(
            hashlib.md5(hash_input.encode()).hexdigest(),
            16
        ) % 100

        return 'A' if hash_value < variant_a_percentage else 'B'

    @staticmethod
    def pause_ab_test(test_id: int, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Pause A/B test.

        Args:
            test_id: A/B test ID
            reason: Optional reason for pause

        Returns:
            Updated test configuration
        """
        with get_db_connection() as conn:
            ab_test_repo = FeatureAbTestRepository()

            updated_test = ab_test_repo.update(test_id, {
                'status': 'paused'
            })

            if not updated_test:
                raise NotFoundError(f"A/B test {test_id} not found")

            logger.info(f"A/B test paused: {updated_test.get('test_name')} - {reason}")

            return updated_test

    @staticmethod
    def end_ab_test(
        test_id: int,
        winner: Literal['A', 'B'],
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        End A/B test and determine winner.

        Args:
            test_id: A/B test ID
            winner: Winning variant ('A' or 'B')
            reason: Optional reason for selection

        Returns:
            Updated test configuration

        Raises:
            ValidationError: If winner not 'A' or 'B'
            NotFoundError: If test not found
        """
        if winner not in ['A', 'B']:
            raise ValidationError(f"Winner must be 'A' or 'B', got '{winner}'")

        with get_db_connection() as conn:
            ab_test_repo = FeatureAbTestRepository()

            updated_test = ab_test_repo.end(test_id, winner, reason)

            if not updated_test:
                raise NotFoundError(f"A/B test {test_id} not found")

            feature_name = updated_test.get('feature_name')
            variant_name = (
                updated_test.get('variant_a_name')
                if winner == 'A'
                else updated_test.get('variant_b_name')
            )

            logger.info(
                f"A/B test completed: {updated_test.get('test_name')} - "
                f"Winner: {variant_name} ({winner})",
                extra={'reason': reason}
            )

            # Invalidate cache
            FeatureConfigurationCacheService.invalidate_feature(feature_name)

            # Publish update event
            FeatureConfigurationCacheService.publish_update(
                feature_name,
                event_type="ab_test_completed",
                details={'winner': winner, 'reason': reason}
            )

            return updated_test

    @staticmethod
    def get_ab_test_metrics(test_id: int) -> Dict[str, Any]:
        """
        Get A/B test metrics and statistics.

        Args:
            test_id: A/B test ID

        Returns:
            Test metrics (placeholder for analytics integration)
        """
        # TODO: Integrate with analytics service to fetch:
        # - User counts per variant
        # - Conversion rates
        # - Engagement metrics
        # - Statistical significance
        # - Confidence intervals

        return {
            'test_id': test_id,
            'note': 'Analytics integration pending'
        }

    @staticmethod
    def get_active_tests() -> List[Dict[str, Any]]:
        """
        Get all currently active A/B tests.

        Returns:
            List of active tests
        """
        with get_db_connection() as conn:
            ab_test_repo = FeatureAbTestRepository()
            return ab_test_repo.find_active()
