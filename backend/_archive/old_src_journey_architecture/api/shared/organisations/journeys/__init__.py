"""
Organisations Domain - Journeys Layer

Journeys organize routes by user type/flow:
- admin: Organisation management (CRUD, members) - 6 endpoints
- analytics: Organisation analytics (stats, time-series, reports) - 5 endpoints

Total: 11 endpoints

Architecture: Journey-Based DDD
"""

from src.api.organisations.journeys.admin.api.routes import (
    organisations_core_bp,
    organisations_members_bp,
)
from src.api.organisations.journeys.analytics.api.routes import (
    organisations_stats_bp,
    time_series_bp,
    reports_bp,
)

ALL_JOURNEY_BLUEPRINTS = [
    # Admin Journey (6 endpoints)
    organisations_core_bp,
    organisations_members_bp,
    # Analytics Journey (5 endpoints)
    organisations_stats_bp,
    time_series_bp,
    reports_bp,
]

__all__ = ['ALL_JOURNEY_BLUEPRINTS']
