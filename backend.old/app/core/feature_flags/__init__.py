"""
Feature Flags Module - Dark Launch Strategy

Core components for progressive feature rollout:
- FeatureFlagManager: Manages feature flags with caching
- @require_feature: Decorator to protect endpoints
- @optional_feature: Decorator with fallback
- @feature_gate: Decorator that adds metadata

Usage:
    from app.core.feature_flags import FeatureFlagManager, require_feature

    flag_manager = FeatureFlagManager()
    is_enabled = flag_manager.is_enabled('user_posts', user_id='123')

    @require_feature('user_posts')
    def create_post():
        ...
"""

from app.core.feature_flags.flag_manager import FeatureFlagManager
from app.core.feature_flags.flag_decorators import (
    require_feature,
    optional_feature,
    feature_gate
)

__all__ = [
    'FeatureFlagManager',
    'require_feature',
    'optional_feature',
    'feature_gate'
]
