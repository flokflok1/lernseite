"""
LernsystemX Dashboard Core Package

Core services and models for dashboard domain.

Services:
    - DashboardLayoutService: Layout management
    - DashboardWidgetService: Widget operations
    - DashboardRecommendationService: KI recommendations

DDD Pattern - Domain-Driven Design
ISO 9001:2015 compliant
"""

from .services import (
    DashboardLayoutService,
    DashboardWidgetService,
    DashboardRecommendationService
)

__all__ = [
    'DashboardLayoutService',
    'DashboardWidgetService',
    'DashboardRecommendationService',
]
