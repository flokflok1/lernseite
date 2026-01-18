"""
LernsystemX Dashboard Services

Modular service package for dashboard-related business logic.
"""

from .widget_service import WidgetService
from .recommendation_service import RecommendationService

__all__ = [
    'WidgetService',
    'RecommendationService'
]
