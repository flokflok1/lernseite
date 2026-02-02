"""
Admin Settings - Feature Flags Management

Feature flag configuration for progressive rollouts, A/B testing, and rollout planning.

Modules:
- routes.py: Feature flags CRUD endpoints
- rollout_plans.py: Rollout plan management
- schemas.py: Request/response validation schemas

All blueprints are auto-registered on import.

Endpoints:
- /api/v1/admin/settings/feature-flags/* - Feature flags CRUD
- /api/v1/admin/settings/rollout-plans/* - Rollout plan management
"""

# Import modules to trigger blueprint creation
from . import routes, rollout_plans_crud, rollout_plans_actions

# Import blueprints for export (registration happens in app/api/v1/__init__.py)
from .routes import feature_flags_bp
from .rollout_plans_crud import rollout_plans_crud_bp
from .rollout_plans_actions import rollout_plans_actions_bp

__all__ = [
    'routes',
    'rollout_plans_crud',
    'rollout_plans_actions',
    'feature_flags_bp',
    'rollout_plans_crud_bp',
    'rollout_plans_actions_bp'
]
