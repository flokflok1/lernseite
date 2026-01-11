"""
Admin AI Operations

Proxies to system_features/ai/

Struktur:
- authoring/ - Content-Authoring (Kurs-Builder, Tutor) [TODO]
- management/ - AI-Management (Jobs, Models, Pricing, Prompts)
- settings/ - AI-Settings (Global Settings, Exams, Models) [TODO]
- studio/ - AI-Studio (Main Studio Interface) [TODO]

Note: Most AI blueprints are still in development. Only core admin endpoints are available.
"""

# Import AI Studio Actions endpoints (registers routes on api_v1)
try:
    from app.api.admin.ai_operations import actions
except ImportError as e:
    print(f"Warning: AI Studio Actions import failed: {e}")
    actions = None

# Import available blueprints from system_features/ai/admin
try:
    # Import from system_features/ai/admin - these are the actual implementations
    from app.api.system_features.ai.admin.jobs import (
        jobs_creation_bp,
        jobs_finalization_bp,
        jobs_management_bp
    )
    from app.api.system_features.ai.admin.models import (
        models_crud_bp,
        models_defaults_bp,
        models_sync_bp,
        models_usage_bp
    )
    from app.api.system_features.ai.admin.pricing import (
        pricing_calculator_bp,
        pricing_plans_bp
    )
    from app.api.system_features.ai.admin.profiles import (
        profiles_crud_bp
    )

    # Combined blueprints for export
    jobs_bp = [jobs_creation_bp, jobs_finalization_bp, jobs_management_bp]
    models_bp = [models_crud_bp, models_defaults_bp, models_sync_bp, models_usage_bp]
    pricing_bp = [pricing_calculator_bp, pricing_plans_bp]
    profiles_bp = [profiles_crud_bp]

    # These don't exist yet - authoring, generation, studio, tutor
    authoring_bp = None
    generation_bp = None
    studio_bp = None
    tutor_bp = None

except ImportError as e:
    print(f"Warning: AI Operations blueprints not available: {e}")
    import traceback
    traceback.print_exc()
    authoring_bp = generation_bp = jobs_bp = models_bp = None
    pricing_bp = profiles_bp = studio_bp = tutor_bp = None

__all__ = [
    'authoring_bp',
    'generation_bp',
    'jobs_bp',
    'models_bp',
    'pricing_bp',
    'profiles_bp',
    'studio_bp',
    'tutor_bp'
]
