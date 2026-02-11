"""
AI Admin Module

Admin AI management endpoints (models, providers, jobs, pricing, profiles, stats, core).

Structure:
- models/: AI model management (CRUD, defaults, sync, usage)
- providers/: AI provider management (API keys, CRUD, health, testing)
- jobs/: AI job management (creation, management, finalization)
- pricing/: AI pricing configuration
- profiles/: AI model profile management
- stats/: AI usage statistics
- core/: Core AI services (events, factory, services, value_objects)

All routes: /api/v1/admin/settings/ai/* (→ consolidated into /api/v1/ai/admin/*)

Part of: Phase 2 AI Consolidation (Feature-based structure)
"""

# Import all modules
from app.api.v1.ai.admin import (
    models, providers, jobs, pricing, profiles, stats, core
)

# Import all blueprints from their new locations
from app.api.v1.ai.admin.models.crud import models_crud_bp
from app.api.v1.ai.admin.models.defaults import models_defaults_bp
from app.api.v1.ai.admin.models.sync import models_sync_bp
from app.api.v1.ai.admin.models.usage import models_usage_bp

from app.api.v1.ai.admin.providers.api_keys import providers_api_keys_bp
from app.api.v1.ai.admin.providers.crud import providers_crud_bp
from app.api.v1.ai.admin.providers.health import providers_health_bp
from app.api.v1.ai.admin.providers.testing import providers_testing_bp

from app.api.v1.ai.admin.jobs.creation import jobs_creation_bp
from app.api.v1.ai.admin.jobs.management import jobs_management_bp
from app.api.v1.ai.admin.jobs.finalization import jobs_finalization_bp

from app.api.v1.ai.admin.pricing.pricing import pricing_calculator_bp, pricing_plans_bp
from app.api.v1.ai.admin.profiles.profiles import profiles_crud_bp

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
    'models', 'providers', 'jobs', 'pricing', 'profiles', 'stats', 'core',
    'jobs_creation_bp', 'jobs_finalization_bp', 'jobs_management_bp',
    'models_crud_bp', 'models_defaults_bp', 'models_sync_bp', 'models_usage_bp',
    'pricing_calculator_bp', 'pricing_plans_bp', 'profiles_crud_bp',
    'providers_api_keys_bp', 'providers_crud_bp', 'providers_health_bp', 'providers_testing_bp'
]
