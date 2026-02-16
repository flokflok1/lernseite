"""
Admin Settings - Feature Flags Management

Feature flag configuration for progressive rollouts, A/B testing, and rollout planning.

Moved from: api/v1/admin/settings/feature_flags/ → api/v1/features/admin/flags/
Part of: Phase 5 Admin Consolidation

Subdirectories:
- core/: Core feature flag CRUD operations (routes + schemas)
- rollout_plans/: Rollout plan management (CRUD + actions)

All blueprints are auto-registered on import.

Endpoints:
- /api/v1/admin/settings/feature-flags/* - Feature flags CRUD
- /api/v1/admin/settings/rollout-plans/* - Rollout plan management
"""

# Core feature flags (routes + schemas)
from .core import (
    # Routes
    list_feature_flags,
    get_feature_flag,
    create_feature_flag,
    update_feature_flag,
    delete_feature_flag,
    enable_feature_flag,
    disable_feature_flag,
    # Schemas & Enums
    FeatureCategoryEnum,
    RolloutStatusEnum,
    FeatureFlagCreateSchema,
    FeatureFlagUpdateSchema,
    RolloutPlanSchema,
    FeatureFlagResponseSchema
)

# Rollout plans (CRUD + actions)
from .rollout_plans import (
    # CRUD
    list_rollout_plans,
    get_rollout_plan,
    create_rollout_plan,
    update_rollout_plan,
    delete_rollout_plan,
    # Actions
    execute_rollout_stage,
    pause_rollout,
    rollback_deployment
)

# Import blueprints for registration
from .core.routes import feature_flags_bp
from .rollout_plans.crud import rollout_plans_crud_bp
from .rollout_plans.actions import rollout_plans_actions_bp

__all__ = [
    # Core routes
    'list_feature_flags',
    'get_feature_flag',
    'create_feature_flag',
    'update_feature_flag',
    'delete_feature_flag',
    'enable_feature_flag',
    'disable_feature_flag',

    # Core schemas & enums
    'FeatureCategoryEnum',
    'RolloutStatusEnum',
    'FeatureFlagCreateSchema',
    'FeatureFlagUpdateSchema',
    'RolloutPlanSchema',
    'FeatureFlagResponseSchema',

    # Rollout plans CRUD
    'list_rollout_plans',
    'get_rollout_plan',
    'create_rollout_plan',
    'update_rollout_plan',
    'delete_rollout_plan',

    # Rollout plans actions
    'execute_rollout_stage',
    'pause_rollout',
    'rollback_deployment',

    # Blueprints
    'feature_flags_bp',
    'rollout_plans_crud_bp',
    'rollout_plans_actions_bp'
]
