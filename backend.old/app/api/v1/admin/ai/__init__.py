"""
Admin AI API Package

Flat structure matching 05_Backend-Struktur.md documentation.

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
- pricing_calculator.py: Token cost calculations
- pricing_plans.py: Subscription plans

Profiles:
- profiles_crud.py: AI model profile management

Providers:
- providers_api_keys.py: Provider API key management
- providers_crud.py: Provider CRUD operations
- providers_health.py: Provider health checks
- providers_testing.py: Provider connection testing

All routes: /api/v1/admin/ai/*
"""

# Import all route handlers
from app.api.v1.admin.ai import (
    jobs_creation,
    jobs_finalization,
    jobs_management,
    models_crud,
    models_defaults,
    models_sync,
    models_usage,
    pricing_calculator,
    pricing_plans,
    profiles_crud,
    providers_api_keys,
    providers_crud,
    providers_health,
    providers_testing
)

__all__ = [
    'jobs_creation',
    'jobs_finalization',
    'jobs_management',
    'models_crud',
    'models_defaults',
    'models_sync',
    'models_usage',
    'pricing_calculator',
    'pricing_plans',
    'profiles_crud',
    'providers_api_keys',
    'providers_crud',
    'providers_health',
    'providers_testing'
]
