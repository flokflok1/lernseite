"""Rollout Configuration Management"""

from typing import Dict, List


class RolloutConfig:
    """Rollout strategy configuration"""
    
    # Standard rollout stages
    ROLLOUT_STAGES = [
        {'name': 'alpha', 'percentage': 5},
        {'name': 'early_beta', 'percentage': 10},
        {'name': 'beta', 'percentage': 25},
        {'name': 'half', 'percentage': 50},
        {'name': 'late', 'percentage': 75},
        {'name': 'full', 'percentage': 100},
    ]
    
    @staticmethod
    def get_next_stage(current_percentage: int) -> Dict[str, int]:
        """Get next rollout stage"""
        for stage in RolloutConfig.ROLLOUT_STAGES:
            if stage['percentage'] > current_percentage:
                return stage
        return {'name': 'full', 'percentage': 100}
