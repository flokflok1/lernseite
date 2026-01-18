"""
LernsystemX Feature Configuration Rollout Service

Rollout management for Enterprise Feature Configuration System:
- Progressive rollout planning (4-phase)
- Phase advancement and scheduling
- Canary deployment (5% → 25% → 50% → 100%)
- Rollback capabilities
- User eligibility checks

Phase 2 - Core Service Layer (Part 3)
Handles all progressive rollout logic for feature deployments.

For core permission logic, see: feature_configuration_service.py
For cache operations, see: feature_configuration_cache.py
For A/B test operations, see: feature_configuration_ab_test.py
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging
import hashlib

from app.database.connection import get_db_connection
from app.repositories.feature_configuration_part2 import FeatureRolloutPlanRepository
from app.services.feature_flags.cache import FeatureConfigurationCacheService
from app.infrastructure.utils.exceptions import ValidationError, NotFoundError

logger = logging.getLogger(__name__)


class FeatureConfigurationRolloutService:
    """
    Service for managing progressive feature rollouts.

    Implements 4-phase canary deployment strategy:
    - Phase 1: 5% of users (default) for 12 hours
    - Phase 2: 25% of users (default) for 24 hours
    - Phase 3: 50% of users (default) for 48 hours
    - Phase 4: 100% of users (full rollout)

    Features:
    - Automatic or manual phase advancement
    - Per-role and per-tier rollout targeting
    - Pause/resume capability
    - Rollback with audit trail
    - User eligibility calculation via consistent hashing
    """

    @staticmethod
    def create_rollout_plan(
        feature_name: str,
        plan_name: str,
        phase_1_percentage: int = 5,
        phase_1_duration_hours: int = 12,
        phase_2_percentage: int = 25,
        phase_2_duration_hours: int = 24,
        phase_3_percentage: int = 50,
        phase_3_duration_hours: int = 48,
        target_roles: Optional[List[str]] = None,
        target_tiers: Optional[List[str]] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create new rollout plan for feature.

        Args:
            feature_name: Feature to rollout (must be unique per feature)
            plan_name: Human-readable plan name
            phase_1_percentage: % of users in phase 1 (default 5)
            phase_1_duration_hours: Duration of phase 1 in hours (default 12)
            phase_2_percentage: % of users in phase 2 (default 25)
            phase_2_duration_hours: Duration of phase 2 in hours (default 24)
            phase_3_percentage: % of users in phase 3 (default 50)
            phase_3_duration_hours: Duration of phase 3 in hours (default 48)
            target_roles: Optional list of roles (if not specified, all roles included)
            target_tiers: Optional list of tiers (if not specified, all tiers included)
            reason: Reason for rollout (for audit)

        Returns:
            Created rollout plan

        Raises:
            ValidationError: If percentages invalid or plan already exists

        Example:
            plan = FeatureConfigurationRolloutService.create_rollout_plan(
                feature_name="ai_tutor",
                plan_name="AI Tutor Beta Launch",
                phase_1_percentage=5,
                reason="Beta testing with early adopters"
            )
        """
        # Validate percentages
        if not (0 < phase_1_percentage <= 100):
            raise ValidationError(f"Phase 1 percentage must be 1-100, got {phase_1_percentage}")
        if not (0 < phase_2_percentage <= 100):
            raise ValidationError(f"Phase 2 percentage must be 1-100, got {phase_2_percentage}")
        if not (0 < phase_3_percentage <= 100):
            raise ValidationError(f"Phase 3 percentage must be 1-100, got {phase_3_percentage}")

        # Percentages should be progressive
        if not (phase_1_percentage <= phase_2_percentage <= phase_3_percentage):
            raise ValidationError(
                "Phase percentages should be progressive: "
                f"phase1({phase_1_percentage}) <= phase2({phase_2_percentage}) <= phase3({phase_3_percentage})"
            )

        with get_db_connection() as conn:
            rollout_repo = FeatureRolloutPlanRepository()

            # Check if plan already exists
            existing = rollout_repo.find_by_feature(feature_name)
            if existing:
                raise ValidationError(
                    f"Rollout plan already exists for feature '{feature_name}'"
                )

            # Create plan
            plan_data = {
                'feature_name': feature_name,
                'plan_name': plan_name,
                'phase_1_percentage': phase_1_percentage,
                'phase_1_duration_hours': phase_1_duration_hours,
                'phase_2_percentage': phase_2_percentage,
                'phase_2_duration_hours': phase_2_duration_hours,
                'phase_3_percentage': phase_3_percentage,
                'phase_3_duration_hours': phase_3_duration_hours,
                'status': 'planned',
                'current_phase': 0,
                'target_roles': target_roles,
                'target_tiers': target_tiers,
                'reason': reason
            }

            created_plan = rollout_repo.create(plan_data)

            logger.info(
                f"Rollout plan created for feature '{feature_name}'",
                extra={'plan': created_plan}
            )

            return created_plan

    @staticmethod
    def start_rollout(feature_name: str) -> Dict[str, Any]:
        """
        Start rollout (begin phase 1).

        Args:
            feature_name: Feature name

        Returns:
            Updated rollout plan

        Raises:
            NotFoundError: If rollout plan not found
            ValidationError: If rollout already started
        """
        with get_db_connection() as conn:
            rollout_repo = FeatureRolloutPlanRepository()
            plan = rollout_repo.find_by_feature(feature_name)

            if not plan:
                raise NotFoundError(f"Rollout plan not found for feature '{feature_name}'")

            if plan.get('status') == 'active':
                raise ValidationError(f"Rollout already active for feature '{feature_name}'")

            # Start rollout
            updated_plan = rollout_repo.start(feature_name)

            # Invalidate cache
            FeatureConfigurationCacheService.invalidate_feature(feature_name)

            logger.info(f"Rollout started for feature '{feature_name}' (Phase 1)")

            return updated_plan

    @staticmethod
    def advance_phase(feature_name: str, new_phase: int) -> Dict[str, Any]:
        """
        Advance rollout to next phase.

        Args:
            feature_name: Feature name
            new_phase: Phase to advance to (1, 2, 3, or 4)

        Returns:
            Updated rollout plan

        Raises:
            NotFoundError: If rollout plan not found
            ValidationError: If phase invalid
        """
        if not (1 <= new_phase <= 4):
            raise ValidationError(f"Invalid phase {new_phase}, must be 1-4")

        with get_db_connection() as conn:
            rollout_repo = FeatureRolloutPlanRepository()
            plan = rollout_repo.find_by_feature(feature_name)

            if not plan:
                raise NotFoundError(f"Rollout plan not found for feature '{feature_name}'")

            current_phase = plan.get('current_phase', 0)

            if new_phase <= current_phase:
                raise ValidationError(
                    f"Cannot advance from phase {current_phase} to phase {new_phase}"
                )

            # Advance phase
            updated_plan = rollout_repo.advance_phase(feature_name, new_phase)

            # Invalidate cache
            FeatureConfigurationCacheService.invalidate_feature(feature_name)

            logger.info(
                f"Rollout advanced for feature '{feature_name}' "
                f"from phase {current_phase} to phase {new_phase}"
            )

            # Publish update event
            FeatureConfigurationCacheService.publish_update(
                feature_name,
                event_type="rollout_phase_advanced",
                details={'from_phase': current_phase, 'to_phase': new_phase}
            )

            return updated_plan

    @staticmethod
    def pause_rollout(feature_name: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Pause rollout (temporary stop).

        Args:
            feature_name: Feature name
            reason: Reason for pause

        Returns:
            Updated rollout plan

        Raises:
            NotFoundError: If rollout plan not found
        """
        with get_db_connection() as conn:
            rollout_repo = FeatureRolloutPlanRepository()
            plan = rollout_repo.find_by_feature(feature_name)

            if not plan:
                raise NotFoundError(f"Rollout plan not found for feature '{feature_name}'")

            updated_plan = rollout_repo.update(
                feature_name,
                {'status': 'paused', 'reason': reason}
            )

            logger.warning(f"Rollout paused for feature '{feature_name}': {reason}")

            return updated_plan

    @staticmethod
    def resume_rollout(feature_name: str) -> Dict[str, Any]:
        """
        Resume paused rollout.

        Args:
            feature_name: Feature name

        Returns:
            Updated rollout plan

        Raises:
            NotFoundError: If rollout plan not found
        """
        with get_db_connection() as conn:
            rollout_repo = FeatureRolloutPlanRepository()
            plan = rollout_repo.find_by_feature(feature_name)

            if not plan:
                raise NotFoundError(f"Rollout plan not found for feature '{feature_name}'")

            updated_plan = rollout_repo.update(
                feature_name,
                {'status': 'active'}
            )

            logger.info(f"Rollout resumed for feature '{feature_name}'")

            return updated_plan

    @staticmethod
    def rollback_rollout(
        feature_name: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Rollback rollout to previous state.

        Args:
            feature_name: Feature name
            reason: Reason for rollback (required)

        Returns:
            Updated rollout plan

        Raises:
            NotFoundError: If rollout plan not found
            ValidationError: If reason not provided
        """
        if not reason:
            raise ValidationError("Reason is required for rollout rollback")

        with get_db_connection() as conn:
            rollout_repo = FeatureRolloutPlanRepository()
            plan = rollout_repo.find_by_feature(feature_name)

            if not plan:
                raise NotFoundError(f"Rollout plan not found for feature '{feature_name}'")

            # Rollback
            updated_plan = rollout_repo.rollback(feature_name, reason)

            # Invalidate cache
            FeatureConfigurationCacheService.invalidate_feature(feature_name)

            logger.warning(
                f"Rollout rolled back for feature '{feature_name}': {reason}"
            )

            # Publish update event
            FeatureConfigurationCacheService.publish_update(
                feature_name,
                event_type="rollout_rolled_back",
                details={'reason': reason}
            )

            return updated_plan

    # ==================== USER ELIGIBILITY ====================

    @staticmethod
    def is_user_eligible_for_rollout(
        user_id: str,
        feature_name: str
    ) -> bool:
        """
        Check if user is eligible for rollout percentage.

        Uses consistent hashing to ensure deterministic assignment:
        - Same user always gets same rollout status
        - Distribution: hash(user_id) % 100 < rollout_percentage
        - Works across multiple nodes/processes

        Args:
            user_id: User ID
            feature_name: Feature name

        Returns:
            True if user is in rollout percentage, False otherwise

        Example:
            if FeatureConfigurationRolloutService.is_user_eligible_for_rollout(
                user_id="user123",
                feature_name="ai_tutor"
            ):
                # Show new feature to user
        """
        with get_db_connection() as conn:
            rollout_repo = FeatureRolloutPlanRepository()
            plan = rollout_repo.find_by_feature(feature_name)

            if not plan:
                return False

            # Check if rollout is active
            if plan.get('status') != 'active':
                return False

            # Get current phase percentage
            current_phase = plan.get('current_phase', 0)

            if current_phase == 0:
                return False  # Rollout not started
            elif current_phase == 1:
                target_percentage = plan.get('phase_1_percentage', 5)
            elif current_phase == 2:
                target_percentage = plan.get('phase_2_percentage', 25)
            elif current_phase == 3:
                target_percentage = plan.get('phase_3_percentage', 50)
            else:  # Phase 4 or later
                return True  # 100% rollout

            # Consistent hash to determine eligibility
            hash_input = f"{feature_name}:{user_id}"
            hash_value = int(
                hashlib.md5(hash_input.encode()).hexdigest(),
                16
            ) % 100

            return hash_value < target_percentage

    @staticmethod
    def get_rollout_stats(feature_name: str) -> Dict[str, Any]:
        """
        Get rollout statistics.

        Args:
            feature_name: Feature name

        Returns:
            Rollout statistics (phase, percentage, estimated users, etc.)
        """
        with get_db_connection() as conn:
            rollout_repo = FeatureRolloutPlanRepository()
            plan = rollout_repo.find_by_feature(feature_name)

            if not plan:
                return {'status': 'not_found'}

            return {
                'feature_name': feature_name,
                'plan_name': plan.get('plan_name'),
                'status': plan.get('status'),
                'current_phase': plan.get('current_phase'),
                'phase_1_percentage': plan.get('phase_1_percentage'),
                'phase_2_percentage': plan.get('phase_2_percentage'),
                'phase_3_percentage': plan.get('phase_3_percentage'),
                'phase_1_started': plan.get('phase_1_start_at'),
                'phase_2_started': plan.get('phase_2_start_at'),
                'phase_3_started': plan.get('phase_3_start_at'),
                'target_roles': plan.get('target_roles'),
                'target_tiers': plan.get('target_tiers')
            }
