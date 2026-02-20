"""
A/B Testing System

Run controlled experiments to compare feature variants
"""

import hashlib
from app.infrastructure.persistence.repositories.feature_flags.ab_testing import ABTestingRepository


class ABTesting:
    """A/B testing for features"""

    @staticmethod
    def get_variant(feature_name: str, user_id: str) -> str:
        """
        Get A/B test variant for user.

        Returns:
            'control' or 'variant_a', 'variant_b', etc.
        """
        test = ABTestingRepository.get_active_test(feature_name)

        if not test:
            return 'control'

        # Deterministic hash to assign user to variant
        hash_input = f"{test['test_id']}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        variant_index = hash_value % 100

        # Split based on variant distribution
        # Example: 50/50 split -> variant_index < 50 = control, >= 50 = variant_a
        if variant_index < test.get('control_percentage', 50):
            return 'control'
        else:
            return 'variant_a'

    @staticmethod
    def is_variant(feature_name: str, user_id: str, variant_name: str) -> bool:
        """Check if user is in specific variant"""
        return ABTesting.get_variant(feature_name, user_id) == variant_name

    @staticmethod
    def track_exposure(feature_name: str, user_id: str, variant: str):
        """Track that user was exposed to variant (for analytics)"""
        ABTestingRepository.upsert_exposure(feature_name, user_id, variant)
