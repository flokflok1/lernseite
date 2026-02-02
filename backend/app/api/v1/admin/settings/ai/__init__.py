"""
Admin Settings - AI Configuration

AI system configuration for providers, models, jobs, pricing, and profiles.

Modules:
Jobs Management:
- jobs_creation.py: Create AI jobs
- jobs_finalization.py: Finalize AI jobs
- jobs_management.py: Manage AI jobs

Models Management:
- models_crud.py: Model CRUD operations
- models_defaults.py: Default model settings
- models_sync.py: Sync models from providers
- models_usage.py: Model usage tracking

Pricing:
- ai_pricing.py: Token cost calculations & pricing plans

Profiles:
- ai_model_profiles.py: AI model profile management

Providers:
- providers_api_keys.py: Provider API key management
- providers_crud.py: Provider CRUD operations
- providers_health.py: Provider health checks
- providers_testing.py: Provider connection testing

All routes: /api/v1/admin/settings/ai/*
"""

# Import blueprints for registration
# Direct imports from current package (no subpackage reference)
from . import (
    jobs_creation,
    jobs_finalization,
    jobs_management,
    models_crud,
    models_defaults,
    models_sync,
    models_usage,
    ai_pricing,
    ai_model_profiles,
    providers_api_keys,
    providers_crud,
    providers_health,
    providers_testing,
    ai_usage_stats
)

from .jobs_creation import jobs_creation_bp
from .jobs_finalization import jobs_finalization_bp
from .jobs_management import jobs_management_bp
from .models_crud import models_crud_bp
from .models_defaults import models_defaults_bp
from .models_sync import models_sync_bp
from .models_usage import models_usage_bp
from .ai_pricing import pricing_calculator_bp, pricing_plans_bp
from .ai_model_profiles import profiles_crud_bp
from .providers_api_keys import providers_api_keys_bp
from .providers_crud import providers_crud_bp
from .providers_health import providers_health_bp
from .providers_testing import providers_testing_bp

# Register all blueprints with api_v1
from app.api.v1 import api_v1

api_v1.register_blueprint(jobs_creation_bp)
api_v1.register_blueprint(jobs_finalization_bp)
api_v1.register_blueprint(jobs_management_bp)
api_v1.register_blueprint(models_crud_bp)
api_v1.register_blueprint(models_defaults_bp)
api_v1.register_blueprint(models_sync_bp)
api_v1.register_blueprint(models_usage_bp)
api_v1.register_blueprint(pricing_calculator_bp)
api_v1.register_blueprint(pricing_plans_bp)
api_v1.register_blueprint(profiles_crud_bp)
api_v1.register_blueprint(providers_api_keys_bp)
api_v1.register_blueprint(providers_crud_bp)
api_v1.register_blueprint(providers_health_bp)
api_v1.register_blueprint(providers_testing_bp)

__all__ = [
    'jobs_creation', 'jobs_creation_bp',
    'jobs_finalization', 'jobs_finalization_bp',
    'jobs_management', 'jobs_management_bp',
    'models_crud', 'models_crud_bp',
    'models_defaults', 'models_defaults_bp',
    'models_sync', 'models_sync_bp',
    'models_usage', 'models_usage_bp',
    'pricing_calculator', 'pricing_calculator_bp',
    'pricing_plans', 'pricing_plans_bp',
    'profiles_crud', 'profiles_crud_bp',
    'providers_api_keys', 'providers_api_keys_bp',
    'providers_crud', 'providers_crud_bp',
    'providers_health', 'providers_health_bp',
    'providers_testing', 'providers_testing_bp',
    'usage_stats'
]
