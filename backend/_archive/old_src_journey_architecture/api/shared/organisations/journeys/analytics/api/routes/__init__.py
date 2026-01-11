"""
Organisations Domain - Analytics Journey Routes

Routes:
- stats.py: GET /organisations/:id/stats
- time_series.py: GET /organisations/:id/analytics/events/time-series,
                  GET /organisations/:id/analytics/active-members/time-series
- reports.py: GET /organisations/:id/analytics/top-courses,
              GET /organisations/:id/analytics/top-modules

Total: 5 endpoints
"""

from .stats import organisations_stats_bp
from .time_series import time_series_bp
from .reports import reports_bp

__all__ = [
    'organisations_stats_bp',
    'time_series_bp',
    'reports_bp',
]
