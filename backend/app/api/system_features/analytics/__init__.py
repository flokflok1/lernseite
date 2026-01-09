"""
Analytics System Feature (DDD)

Analytics for admins and users: time series, rankings, event tracking.

Package Structure:
- core/ - Core domain (Value Objects, Factories, Services)
- admin/ - Admin endpoints (Time Series, Rankings)
- user/ - User endpoints (Event tracking, user/org analytics)

Blueprints:
Admin:
- analytics_time_series_bp: /api/v1/admin/analytics/events/time-series, /active-users/time-series
- analytics_rankings_bp: /api/v1/admin/analytics/top-courses, /top-methods

User:
- User endpoints from user/tracking.py (POST /event, GET /user, /organisation, /health)

DDD Components:
- Value Objects: DateRange, TimeRange, TimeSeriesDataPoint, AnalyticsFilter
- Factories: AnalyticsQueryFactory
- Services: AnalyticsAggregationService

Migration Status: ✅ COMPLETE (merged with old analytics/user/)
"""

# Admin blueprints
from .admin import (
    analytics_time_series_bp,
    analytics_rankings_bp
)

# User layer (merged from old analytics/)
from .user import (
    track_event,
    get_user_analytics,
    get_organisation_analytics,
    analytics_health
)

# Core domain exports (for internal use)
from .core import (
    DateRange,
    TimeRange,
    TimeSeriesDataPoint,
    AnalyticsFilter,
    AnalyticsQueryFactory,
    AnalyticsAggregationService
)

__all__ = [
    # Admin Blueprints
    'analytics_time_series_bp',
    'analytics_rankings_bp',
    # User Layer
    'track_event',
    'get_user_analytics',
    'get_organisation_analytics',
    'analytics_health',
    # Core Domain (exported for internal use)
    'DateRange',
    'TimeRange',
    'TimeSeriesDataPoint',
    'AnalyticsFilter',
    'AnalyticsQueryFactory',
    'AnalyticsAggregationService'
]
