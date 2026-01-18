"""
LernsystemX Feature Configuration Repositories - Part 2

Continuation of feature configuration repositories:
- Tier-based limits
- Progressive rollout plans
- A/B testing
- Cache status management

Phase 1b - Repository Layer Implementation (Part 2)
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
import json

from app.database.connection import (
    fetch_one,
    fetch_all,
    insert_returning,
    update_returning,
    execute_query
)


# ==================== TIER LIMIT REPOSITORY ====================

class FeatureTierLimitRepository:
    """
    Repository for subscription tier-based feature limits
    (feature_flag_tier_limits table)

    Manages tier-specific quotas (free, premium, enterprise).
    """

    table_name = 'feature_flag_tier_limits'

    @classmethod
    def create(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create tier limit

        Args:
            data: {
                'feature_name': str,
                'tier_code': str ('free', 'premium', 'enterprise'),
                'is_enabled': bool,
                'max_concurrent_usage': int (optional),
                'max_monthly_quota': int (optional),
                'max_per_day': int (optional),
                'max_storage_gb': float (optional)
            }
        """
        return insert_returning(cls.table_name, data)

    @classmethod
    def find_by_feature_and_tier(
        cls,
        feature_name: str,
        tier_code: str
    ) -> Optional[Dict[str, Any]]:
        """Find tier limit for specific feature and tier"""
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE feature_name = %s AND tier_code = %s
        """
        return fetch_one(query, (feature_name, tier_code))

    @classmethod
    def find_by_feature(cls, feature_name: str) -> List[Dict[str, Any]]:
        """Get all tier limits for a feature"""
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE feature_name = %s
            ORDER BY tier_code
        """
        return fetch_all(query, (feature_name,))

    @classmethod
    def update(
        cls,
        feature_name: str,
        tier_code: str,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update tier limit"""
        if 'updated_at' not in data:
            data['updated_at'] = datetime.utcnow()

        query = f"""
            UPDATE {cls.table_name}
            SET {', '.join(f'{k} = %s' for k in data.keys())}
            WHERE feature_name = %s AND tier_code = %s
            RETURNING *
        """
        params = list(data.values()) + [feature_name, tier_code]
        return fetch_one(query, params)

    @classmethod
    def delete(cls, feature_name: str, tier_code: str) -> bool:
        """Delete tier limit"""
        query = f"""
            DELETE FROM {cls.table_name}
            WHERE feature_name = %s AND tier_code = %s
        """
        return execute_query(query, (feature_name, tier_code)) > 0


# ==================== ROLLOUT PLAN REPOSITORY ====================

class FeatureRolloutPlanRepository:
    """
    Repository for progressive feature rollout plans
    (feature_flag_rollout_plans table)

    Manages 4-phase rollout strategies (5% → 25% → 50% → 100%).
    """

    table_name = 'feature_flag_rollout_plans'

    @classmethod
    def create(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create rollout plan

        Args:
            data: {
                'feature_name': str (unique per feature),
                'plan_name': str,
                'phase_1_percentage': int (default 5),
                'phase_1_duration_hours': int (default 12),
                'phase_2_percentage': int (default 25),
                'phase_2_duration_hours': int (default 24),
                'phase_3_percentage': int (default 50),
                'phase_3_duration_hours': int (default 48),
                'status': str ('planned', 'active', 'paused', 'completed', 'rolled_back'),
                'target_roles': list (optional),
                'target_tiers': list (optional),
                'reason': str (optional),
                'created_by': str (optional)
            }
        """
        return insert_returning(cls.table_name, data)

    @classmethod
    def find_by_feature(cls, feature_name: str) -> Optional[Dict[str, Any]]:
        """Find active rollout plan for feature"""
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE feature_name = %s
        """
        return fetch_one(query, (feature_name,))

    @classmethod
    def find_active(cls) -> List[Dict[str, Any]]:
        """Find all active rollout plans"""
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE status = 'active'
            ORDER BY phase_1_start_at DESC
        """
        return fetch_all(query)

    @classmethod
    def update(
        cls,
        feature_name: str,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update rollout plan"""
        if 'updated_at' not in data:
            data['updated_at'] = datetime.utcnow()

        query = f"""
            UPDATE {cls.table_name}
            SET {', '.join(f'{k} = %s' for k in data.keys())}
            WHERE feature_name = %s
            RETURNING *
        """
        params = list(data.values()) + [feature_name]
        return fetch_one(query, params)

    @classmethod
    def advance_phase(cls, feature_name: str, new_phase: int) -> Optional[Dict[str, Any]]:
        """Advance rollout to next phase"""
        now = datetime.utcnow()

        phase_start_column = f"phase_{new_phase}_start_at"

        query = f"""
            UPDATE {cls.table_name}
            SET current_phase = %s, {phase_start_column} = %s
            WHERE feature_name = %s
            RETURNING *
        """
        return fetch_one(query, (new_phase, now, feature_name))

    @classmethod
    def start(cls, feature_name: str) -> Optional[Dict[str, Any]]:
        """Start rollout (phase 1)"""
        now = datetime.utcnow()
        query = f"""
            UPDATE {cls.table_name}
            SET status = 'active', current_phase = 1, phase_1_start_at = %s
            WHERE feature_name = %s
            RETURNING *
        """
        return fetch_one(query, (now, feature_name))

    @classmethod
    def rollback(cls, feature_name: str, reason: str) -> Optional[Dict[str, Any]]:
        """Rollback rollout"""
        query = f"""
            UPDATE {cls.table_name}
            SET status = 'rolled_back', current_phase = 0, reason = %s
            WHERE feature_name = %s
            RETURNING *
        """
        return fetch_one(query, (reason, feature_name))


# ==================== A/B TEST REPOSITORY ====================

class FeatureAbTestRepository:
    """
    Repository for A/B testing
    (feature_flag_ab_tests table)

    Manages variant assignment and test tracking.
    """

    table_name = 'feature_flag_ab_tests'

    @classmethod
    def create(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create A/B test

        Args:
            data: {
                'feature_name': str,
                'test_name': str,
                'variant_a_name': str,
                'variant_a_percentage': int (0-100),
                'variant_a_config': dict (optional),
                'variant_b_name': str,
                'variant_b_percentage': int (0-100),
                'variant_b_config': dict (optional),
                'target_roles': list (optional),
                'target_tiers': list (optional),
                'metrics_to_track': list (optional),
                'planned_duration_days': int (default 14),
                'status': str ('planned', 'active', 'paused', 'completed'),
                'created_by': str (optional)
            }
        """
        if data.get('variant_a_config'):
            data['variant_a_config'] = json.dumps(data['variant_a_config'])
        if data.get('variant_b_config'):
            data['variant_b_config'] = json.dumps(data['variant_b_config'])

        return insert_returning(cls.table_name, data)

    @classmethod
    def find_by_feature(cls, feature_name: str) -> List[Dict[str, Any]]:
        """Find all A/B tests for a feature"""
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE feature_name = %s
            ORDER BY created_at DESC
        """
        return fetch_all(query, (feature_name,))

    @classmethod
    def find_active(cls) -> List[Dict[str, Any]]:
        """Find all active A/B tests"""
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE status = 'active'
            ORDER BY started_at DESC
        """
        return fetch_all(query)

    @classmethod
    def update(
        cls,
        test_id: int,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update A/B test"""
        if 'updated_at' not in data:
            data['updated_at'] = datetime.utcnow()

        if data.get('variant_a_config') and isinstance(data['variant_a_config'], dict):
            data['variant_a_config'] = json.dumps(data['variant_a_config'])
        if data.get('variant_b_config') and isinstance(data['variant_b_config'], dict):
            data['variant_b_config'] = json.dumps(data['variant_b_config'])

        query = f"""
            UPDATE {cls.table_name}
            SET {', '.join(f'{k} = %s' for k in data.keys())}
            WHERE id = %s
            RETURNING *
        """
        params = list(data.values()) + [test_id]
        return fetch_one(query, params)

    @classmethod
    def end(
        cls,
        test_id: int,
        winner: str,
        reason: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """End A/B test and announce winner"""
        query = f"""
            UPDATE {cls.table_name}
            SET status = 'completed', ended_at = %s, winner = %s
            WHERE id = %s
            RETURNING *
        """
        return fetch_one(query, (datetime.utcnow(), winner, test_id))


# ==================== CACHE STATUS REPOSITORY ====================

class FeatureCacheStatusRepository:
    """
    Repository for cache status tracking
    (feature_flag_cache_status table)

    Manages Redis cache invalidation for feature configurations.
    """

    table_name = 'feature_flag_cache_status'

    @classmethod
    def get_status(cls, feature_name: str) -> Optional[Dict[str, Any]]:
        """Get cache status for feature"""
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE feature_name = %s
        """
        return fetch_one(query, (feature_name,))

    @classmethod
    def update_status(
        cls,
        feature_name: str
    ) -> Optional[Dict[str, Any]]:
        """Update cache status (mark as invalidated)"""
        query = f"""
            INSERT INTO {cls.table_name}
            (feature_name, last_config_change, cache_invalidated_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (feature_name) DO UPDATE SET
                last_config_change = EXCLUDED.last_config_change,
                cache_invalidated_at = EXCLUDED.cache_invalidated_at
            RETURNING *
        """
        now = datetime.utcnow()
        return fetch_one(query, (feature_name, now, now))

    @classmethod
    def needs_invalidation(cls, feature_name: str) -> bool:
        """Check if cache needs invalidation"""
        status = cls.get_status(feature_name)
        if not status:
            return True

        # Cache is invalid if:
        # 1. cache_invalidated_at is None (never cached)
        # 2. cache_invalidated_at is older than last_config_change
        return (
            status['cache_invalidated_at'] is None or
            status['last_config_change'] > status['cache_invalidated_at']
        )

    @classmethod
    def mark_cached(cls, feature_name: str) -> Optional[Dict[str, Any]]:
        """Mark cache as valid (recently cached)"""
        query = f"""
            UPDATE {cls.table_name}
            SET cache_invalidated_at = %s
            WHERE feature_name = %s
            RETURNING *
        """
        return fetch_one(query, (datetime.utcnow(), feature_name))
