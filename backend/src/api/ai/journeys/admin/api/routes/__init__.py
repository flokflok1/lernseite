"""
AI Domain - Admin Journey Routes

All 27 AI administration endpoints organized by function.
"""

# Jobs Management (8 endpoints)
from .jobs import (
    jobs_creation_bp,
    jobs_management_bp,
    jobs_finalization_bp,
)

# Models Management (10 endpoints)
from .models import (
    models_crud_bp,
    models_defaults_bp,
    models_sync_bp,
    models_usage_bp,
)

# Providers Management (8 endpoints)
from .providers import (
    providers_crud_bp,
    providers_api_keys_bp,
    providers_health_bp,
    providers_testing_bp,
)

# Profiles Management (5 endpoints)
from .profiles import (
    profiles_crud_bp,
)

# Pricing Management (4 endpoints)
from .pricing import (
    pricing_calculator_bp,
    pricing_plans_bp,
)

__all__ = [
    # Jobs (8 endpoints)
    'jobs_creation_bp',
    'jobs_management_bp',
    'jobs_finalization_bp',
    # Models (10 endpoints)
    'models_crud_bp',
    'models_defaults_bp',
    'models_sync_bp',
    'models_usage_bp',
    # Providers (8 endpoints)
    'providers_crud_bp',
    'providers_api_keys_bp',
    'providers_health_bp',
    'providers_testing_bp',
    # Profiles (5 endpoints)
    'profiles_crud_bp',
    # Pricing (4 endpoints)
    'pricing_calculator_bp',
    'pricing_plans_bp',
]
