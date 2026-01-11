"""Dashboard Domain - All Journeys"""

from .admin import dashboard_admin_bp
from .user import (
    dashboard_layouts_bp,
    dashboard_widgets_bp,
    dashboard_recommendations_bp,
)

ALL_JOURNEY_BLUEPRINTS = [
    # Admin Journey (1 endpoint)
    dashboard_admin_bp,
    # User Journey (12 endpoints)
    dashboard_layouts_bp,
    dashboard_widgets_bp,
    dashboard_recommendations_bp,
]

__all__ = [
    'ALL_JOURNEY_BLUEPRINTS',
    'dashboard_admin_bp',
    'dashboard_layouts_bp',
    'dashboard_widgets_bp',
    'dashboard_recommendations_bp',
]
