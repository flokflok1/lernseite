"""
Backward Compatibility Bridge: feature_configuration_rollout

DEPRECATED: Use 'from app.services.feature_flags.rollout import FeatureConfigurationRolloutService' instead
This bridge maintains backward compatibility with old import paths.
"""

from app.services.feature_flags.rollout import FeatureConfigurationRolloutService

__all__ = ['FeatureConfigurationRolloutService']
