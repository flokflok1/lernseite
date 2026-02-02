"""
Feature Configuration & Flags Service

Enterprise Feature Management (Phase 2):
- Progressive rollout management
- A/B testing and multivariate tests
- Feature flag caching
- Central configuration service

Modules:
  - service: Core FeatureConfigurationService
  - cache: Caching layer for feature configurations
  - rollout: Progressive rollout strategy
  - ab_test: A/B and multivariate testing
"""

from .service import FeatureConfigurationService
from .cache import FeatureConfigurationCacheService
from .rollout import FeatureConfigurationRolloutService
from .ab_test import FeatureConfigurationAbTestService

__all__ = [
    'FeatureConfigurationService',
    'FeatureConfigurationCacheService',
    'FeatureConfigurationRolloutService',
    'FeatureConfigurationAbTestService',
]
