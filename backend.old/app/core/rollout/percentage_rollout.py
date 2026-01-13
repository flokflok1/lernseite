"""
Percentage-Based Rollout

Gradually enables features for increasing percentages of users.
Strategy: 5% → 10% → 25% → 50% → 75% → 100%
"""

import hashlib
from typing import Optional


class PercentageRollout:
    """Progressive rollout based on user percentage"""
    
    @staticmethod
    def is_enabled_for_user(feature_name: str, user_id: str, percentage: int) -> bool:
        """
        Check if feature is enabled for user based on percentage.
        
        Uses deterministic hashing to ensure same user always gets same result.
        
        Args:
            feature_name: Feature flag name
            user_id: User ID
            percentage: Rollout percentage (0-100)
            
        Returns:
            True if user is in the rollout percentage
        """
        if percentage >= 100:
            return True
        if percentage <= 0:
            return False
            
        # Deterministic hash
        hash_input = f"{feature_name}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        user_percentage = hash_value % 100
        
        return user_percentage < percentage
    
    @staticmethod
    def get_rollout_stage(percentage: int) -> str:
        """Get rollout stage name"""
        if percentage == 0:
            return 'disabled'
        elif percentage <= 5:
            return 'alpha'
        elif percentage <= 10:
            return 'early_beta'
        elif percentage <= 25:
            return 'beta'
        elif percentage <= 50:
            return 'half_rollout'
        elif percentage < 100:
            return 'late_rollout'
        else:
            return 'full_rollout'
