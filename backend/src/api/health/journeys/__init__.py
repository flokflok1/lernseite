"""
Health Domain - Journeys Layer

Journeys organize routes by user type/flow:
- public: Public health monitoring (no auth required)

Architecture: Journey-Based (Utility)
Pattern: Standalone functions (no blueprints)
"""

from .public.api.routes import health_check, health_check_detailed

# Health routes are standalone functions (not blueprints)
ALL_HEALTH_ROUTES = {
    'health_check': health_check,
    'health_check_detailed': health_check_detailed,
}

__all__ = [
    'ALL_HEALTH_ROUTES',
    'health_check',
    'health_check_detailed',
]
