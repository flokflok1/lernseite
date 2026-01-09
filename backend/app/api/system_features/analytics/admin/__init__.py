"""
Analytics Admin Package (DDD)

Admin endpoints for system-wide analytics.

Endpoints:
- Time Series (events, active users)
- Rankings (top courses, top methods)
"""

from flask import Blueprint

# Define blueprints
analytics_time_series_bp = Blueprint(
    'analytics_time_series',
    __name__,
    url_prefix='/api/v1/admin/analytics'
)

analytics_rankings_bp = Blueprint(
    'analytics_rankings',
    __name__,
    url_prefix='/api/v1/admin/analytics'
)

# Import routes (registers endpoints with blueprints)
from . import time_series, rankings

__all__ = [
    'analytics_time_series_bp',
    'analytics_rankings_bp'
]
