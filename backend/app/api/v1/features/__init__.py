"""
Features API Package

Feature management and feature flag configuration endpoints.

Phase 5: Consolidated from admin/feature-configuration/ and admin/settings/feature_flags/
"""

# Public features endpoints
from app.api.v1.features.core import features_bp
from app.api.v1.features.catalog import catalog_bp as features_catalog_bp

# Admin: Feature Flags Management
from app.api.v1.features.admin.flags import (
    feature_flags_bp,
    rollout_plans_crud_bp,
    rollout_plans_actions_bp
)

# Admin: Feature Configuration
from app.api.v1.features.admin.configuration import (
    feature_config_core_bp,
    feature_config_core_part2_bp,
    feature_config_rollout_bp,
    feature_config_ab_tests_bp,
    feature_config_audit_bp
)

__all__ = [
    # Public
    'features_bp',
    'features_catalog_bp',
    # Admin: Feature Flags
    'feature_flags_bp',
    'rollout_plans_crud_bp',
    'rollout_plans_actions_bp',
    # Admin: Feature Configuration
    'feature_config_core_bp',
    'feature_config_core_part2_bp',
    'feature_config_rollout_bp',
    'feature_config_ab_tests_bp',
    'feature_config_audit_bp'
]
