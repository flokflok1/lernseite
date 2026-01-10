"""
AI Domain - All Journeys

Exports all AI domain journey blueprints.
"""

from .admin import (
    # Jobs Management (8 endpoints)
    jobs_creation_bp,
    jobs_management_bp,
    jobs_finalization_bp,
    # Models Management (10 endpoints)
    models_crud_bp,
    models_defaults_bp,
    models_sync_bp,
    models_usage_bp,
    # Providers Management (8 endpoints)
    providers_crud_bp,
    providers_api_keys_bp,
    providers_health_bp,
    providers_testing_bp,
    # Profiles Management (5 endpoints)
    profiles_crud_bp,
    # Pricing Management (4 endpoints)
    pricing_calculator_bp,
    pricing_plans_bp,
)

# Aggregate all blueprints for registration
ALL_JOURNEY_BLUEPRINTS = [
    # Jobs Management (8 endpoints)
    jobs_creation_bp,
    jobs_management_bp,
    jobs_finalization_bp,
    # Models Management (10 endpoints)
    models_crud_bp,
    models_defaults_bp,
    models_sync_bp,
    models_usage_bp,
    # Providers Management (8 endpoints)
    providers_crud_bp,
    providers_api_keys_bp,
    providers_health_bp,
    providers_testing_bp,
    # Profiles Management (5 endpoints)
    profiles_crud_bp,
    # Pricing Management (4 endpoints)
    pricing_calculator_bp,
    pricing_plans_bp,
]

__all__ = [
    'ALL_JOURNEY_BLUEPRINTS',
    # Jobs
    'jobs_creation_bp',
    'jobs_management_bp',
    'jobs_finalization_bp',
    # Models
    'models_crud_bp',
    'models_defaults_bp',
    'models_sync_bp',
    'models_usage_bp',
    # Providers
    'providers_crud_bp',
    'providers_api_keys_bp',
    'providers_health_bp',
    'providers_testing_bp',
    # Profiles
    'profiles_crud_bp',
    # Pricing
    'pricing_calculator_bp',
    'pricing_plans_bp',
]
