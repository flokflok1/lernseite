"""Feature Configuration Management"""

from typing import Dict, Any, List


class FeatureConfig:
    """Central feature configuration"""
    
    # Default feature configuration
    DEFAULT_CONFIG = {
        'cache_ttl': 300,  # 5 minutes
        'max_retries': 3,
        'timeout': 30,
    }
    
    @staticmethod
    def get_config(feature_name: str) -> Dict[str, Any]:
        """Get configuration for feature"""
        return FeatureConfig.DEFAULT_CONFIG.copy()
