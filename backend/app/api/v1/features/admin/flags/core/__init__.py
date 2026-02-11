"""
Feature Flags Core Module

Provides core feature flag management functionality including routes and schemas.
"""

# Route functions
from app.api.v1.admin.settings.feature_flags.core.routes import (
    list_feature_flags,
    get_feature_flag,
    create_feature_flag,
    update_feature_flag,
    delete_feature_flag,
    enable_feature_flag,
    disable_feature_flag
)

# Pydantic schemas and enums
from app.api.v1.admin.settings.feature_flags.core.schemas import (
    FeatureCategoryEnum,
    RolloutStatusEnum,
    FeatureFlagCreateSchema,
    FeatureFlagUpdateSchema,
    RolloutPlanSchema,
    FeatureFlagResponseSchema
)

__all__ = [
    # Routes
    'list_feature_flags',
    'get_feature_flag',
    'create_feature_flag',
    'update_feature_flag',
    'delete_feature_flag',
    'enable_feature_flag',
    'disable_feature_flag',

    # Schemas & Enums
    'FeatureCategoryEnum',
    'RolloutStatusEnum',
    'FeatureFlagCreateSchema',
    'FeatureFlagUpdateSchema',
    'RolloutPlanSchema',
    'FeatureFlagResponseSchema'
]
