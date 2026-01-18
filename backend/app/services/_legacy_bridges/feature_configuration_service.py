"""Backward Compatibility Bridge: feature_configuration_service
DEPRECATED: Use 'from app.services.feature_flags.service import FeatureConfigurationService' instead
This bridge maintains backward compatibility with old import paths.
"""
from app.services.feature_flags.service import FeatureConfigurationService
__all__ = ['FeatureConfigurationService']
