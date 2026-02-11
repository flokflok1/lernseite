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

# Re-export from management
from app.core.feature_flags.management import FeatureFlagManager

# Re-export from decorators
from app.core.feature_flags.decorators import (
    require_feature,
    optional_feature,
    feature_gate
)

# Re-export from config (utilities)
from app.core.feature_flags.config import (
    get_feature_flag_status,
    get_all_feature_flags,
    get_feature_group,
    seed_feature_flags,
    seed_feature_groups,
    enable_feature_for_beta_users,
    set_percentage_rollout
)

__all__ = [
    # Management
    'FeatureFlagManager',

    # Decorators
    'require_feature',
    'optional_feature',
    'feature_gate',

    # Configuration utilities
    'get_feature_flag_status',
    'get_all_feature_flags',
    'get_feature_group',
    'seed_feature_flags',
    'seed_feature_groups',
    'enable_feature_for_beta_users',
    'set_percentage_rollout'
]
