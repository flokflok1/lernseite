"""
Analytics User API

User-level analytics endpoints for tracking and statistics.

Endpoints:
    - POST /api/v1/analytics/event
    - GET  /api/v1/analytics/user
    - GET  /api/v1/analytics/organisation
    - GET  /api/v1/analytics/health

Example usage:
    >>> from app.api.analytics.user.tracking import (
    ...     track_event,
    ...     get_user_analytics,
    ...     get_organisation_analytics,
    ...     analytics_health
    ... )
"""

from app.api.analytics.user.tracking import (
    track_event,
    get_user_analytics,
    get_organisation_analytics,
    analytics_health
)

__all__ = [
    'track_event',
    'get_user_analytics',
    'get_organisation_analytics',
    'analytics_health'
]
