"""
LernsystemX Widget Repositories

Modular repository package for widget-related database operations.
"""

from .widget_repository import WidgetRepository
from .widget_instance_repository import WidgetInstanceRepository
from .recommendation_repository import RecommendationRepository

__all__ = [
    'WidgetRepository',
    'WidgetInstanceRepository',
    'RecommendationRepository'
]
