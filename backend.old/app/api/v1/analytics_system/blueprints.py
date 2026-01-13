"""
Analytics System Blueprints

Centralized blueprint definitions to avoid circular imports.
"""

from flask import Blueprint

# Admin Time Series Analytics Blueprint
analytics_time_series_bp = Blueprint(
    'analytics_time_series',
    __name__,
    url_prefix='/api/v1/admin/analytics'
)

# Note: admin_rankings.py currently has no endpoints defined
# If endpoints are added later, create analytics_rankings_bp here
