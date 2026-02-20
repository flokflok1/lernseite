"""
A/B Testing Repository - Feature Flag System

Database access for A/B test experiments.
"""

from typing import Optional, Dict, Any
from app.infrastructure.persistence.repositories.core.base import BaseRepository


class ABTestingRepository(BaseRepository):
    """Repository for A/B tests in the feature flag system."""

    @staticmethod
    def get_active_test(feature_name: str) -> Optional[Dict[str, Any]]:
        """Get active A/B test for feature."""
        query = """
            SELECT * FROM feature_flags.ab_tests
            WHERE feature_name = %s
              AND status = 'active'
              AND start_date <= CURRENT_TIMESTAMP
              AND (end_date IS NULL OR end_date >= CURRENT_TIMESTAMP)
            LIMIT 1
        """
        return ABTestingRepository.fetch_one(query, (feature_name,))

    @staticmethod
    def upsert_exposure(feature_name: str, user_id: str, variant: str) -> None:
        """Record that user was exposed to a variant (for analytics)."""
        query = """
            INSERT INTO feature_flags.ab_test_exposures
            (feature_name, user_id, variant, exposed_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (feature_name, user_id)
            DO UPDATE SET exposed_at = CURRENT_TIMESTAMP, variant = EXCLUDED.variant
        """
        ABTestingRepository.execute(query, (feature_name, user_id, variant))
