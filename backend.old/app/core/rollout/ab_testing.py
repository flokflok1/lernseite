"""
A/B Testing System

Run controlled experiments to compare feature variants
"""

import hashlib
from typing import Optional, Dict, Any, List
from app.repositories.base_repository import BaseRepository


class ABTestingRepository(BaseRepository):
    """Repository for A/B tests"""
    
    @staticmethod
    def get_active_test(feature_name: str) -> Optional[Dict[str, Any]]:
        """Get active A/B test for feature"""
        query = """
            SELECT * FROM feature_flags.ab_tests
            WHERE feature_name = %s 
              AND status = 'active'
              AND start_date <= CURRENT_TIMESTAMP
              AND (end_date IS NULL OR end_date >= CURRENT_TIMESTAMP)
            LIMIT 1
        """
        return ABTestingRepository.fetch_one(query, (feature_name,))


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
        query = """
            INSERT INTO feature_flags.ab_test_exposures 
            (feature_name, user_id, variant, exposed_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (feature_name, user_id) 
            DO UPDATE SET exposed_at = CURRENT_TIMESTAMP, variant = EXCLUDED.variant
        """
        ABTestingRepository.execute(query, (feature_name, user_id, variant))
