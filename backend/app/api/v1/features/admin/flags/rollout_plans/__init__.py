"""
Feature Flags Rollout Plans Module

Provides rollout plan management with CRUD operations and action controls.
"""

# CRUD operations
from app.api.v1.features.admin.flags.rollout_plans.crud import (
    list_rollout_plans,
    get_rollout_plan,
    create_rollout_plan,
    update_rollout_plan,
    delete_rollout_plan
)

# Action controls
from app.api.v1.features.admin.flags.rollout_plans.actions import (
    execute_rollout_stage,
    pause_rollout,
    rollback_deployment
)

__all__ = [
    # CRUD
    'list_rollout_plans',
    'get_rollout_plan',
    'create_rollout_plan',
    'update_rollout_plan',
    'delete_rollout_plan',

    # Actions
    'execute_rollout_stage',
    'pause_rollout',
    'rollback_deployment'
]
