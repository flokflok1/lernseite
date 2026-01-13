"""
AI System Features API Package

AI-related system features including:
- AI Models Management (CRUD, defaults, sync, usage)
- AI Jobs Management (creation, finalization, management)
- AI Pricing (calculator, plans)
- AI Profiles (model routing profiles)

Structure:
├── admin/          # Admin AI endpoints
│   ├── models/     # AI Models CRUD (4 blueprints)
│   ├── jobs/       # AI Jobs Management (3 blueprints)
│   ├── pricing/    # Pricing Management (2 blueprints)
│   └── profiles/   # Model Profiles (1 blueprint)
└── core/           # Core AI functionality

All blueprints use DDD patterns with:
- Repository Pattern for database access
- Factory Pattern for business logic
- Domain Events for state changes
"""

from flask import current_app

# Import AI Admin blueprints
try:
    from app.api.system_features.ai.admin.models import (
        models_crud_bp,
        models_defaults_bp,
        models_sync_bp,
        models_usage_bp
    )

    from app.api.system_features.ai.admin.jobs import (
        jobs_creation_bp,
        jobs_finalization_bp,
        jobs_management_bp
    )

    from app.api.system_features.ai.admin.pricing import (
        pricing_calculator_bp,
        pricing_plans_bp
    )

    from app.api.system_features.ai.admin.profiles import (
        profiles_crud_bp
    )

    # Combined exports for easy registration
    models_bp = [models_crud_bp, models_defaults_bp, models_sync_bp, models_usage_bp]
    jobs_bp = [jobs_creation_bp, jobs_finalization_bp, jobs_management_bp]
    pricing_bp = [pricing_calculator_bp, pricing_plans_bp]
    profiles_bp = [profiles_crud_bp]

    # All AI admin blueprints (10 total)
    all_ai_blueprints = models_bp + jobs_bp + pricing_bp + profiles_bp

except ImportError as e:
    print(f"Warning: AI admin blueprints import failed: {e}")
    import traceback
    traceback.print_exc()
    models_bp = []
    jobs_bp = []
    pricing_bp = []
    profiles_bp = []
    all_ai_blueprints = []

__all__ = [
    'models_bp',
    'jobs_bp',
    'pricing_bp',
    'profiles_bp',
    'all_ai_blueprints',
    # Individual blueprints
    'models_crud_bp',
    'models_defaults_bp',
    'models_sync_bp',
    'models_usage_bp',
    'jobs_creation_bp',
    'jobs_finalization_bp',
    'jobs_management_bp',
    'pricing_calculator_bp',
    'pricing_plans_bp',
    'profiles_crud_bp'
]


def register_ai_blueprints(app):
    """
    Register all AI-related blueprints with the Flask app.

    Args:
        app: Flask application instance
    """
    for bp in all_ai_blueprints:
        if bp is not None:
            app.register_blueprint(bp)
            app.logger.info(f"✓ Registered AI blueprint: {bp.name} at {bp.url_prefix}")

    app.logger.info(f"✓ Total AI blueprints registered: {len([bp for bp in all_ai_blueprints if bp is not None])}")
