"""
Backward Compatibility Bridge: feature_configuration_ab_test

DEPRECATED: Use 'from app.application.services.feature_flags.ab_test import FeatureConfigurationAbTestService' instead
This bridge maintains backward compatibility with old import paths.
"""

from app.application.services.feature_flags.ab_test import FeatureConfigurationAbTestService

__all__ = ['FeatureConfigurationAbTestService']
