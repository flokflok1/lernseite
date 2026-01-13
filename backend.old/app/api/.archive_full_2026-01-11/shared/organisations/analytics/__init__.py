"""
Organisation Analytics Module

Provides organisation-level analytics with multi-tenancy support:
- Time series analytics (events, active members)
- Top reports (courses, modules)

All endpoints require VIEW_ORG_ANALYTICS permission.
"""

from flask import Blueprint
from .time_series import time_series_bp
from .reports import reports_bp

# Create main analytics blueprint
analytics_bp = Blueprint(
    'org_analytics',
    __name__
)

# Import and register route functions from sub-blueprints
# This allows the routes to be accessible via the parent module
from .time_series import (
    org_get_events_time_series,
    org_get_active_members_time_series
)

from .reports import (
    org_get_top_courses,
    org_get_top_modules
)

# Export utility functions
from .time_series import parse_date_range, check_org_access

__all__ = [
    'analytics_bp',
    'time_series_bp',
    'reports_bp',
    'org_get_events_time_series',
    'org_get_active_members_time_series',
    'org_get_top_courses',
    'org_get_top_modules',
    'parse_date_range',
    'check_org_access'
]
