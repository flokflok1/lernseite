"""
Analytics Core Domain

Domain-Driven Design (DDD) core components for the Analytics system.

Components:
- Value Objects: DateRange, TimeRange, TimeSeriesDataPoint, AnalyticsFilter
- Factory: AnalyticsQueryFactory
- Services: AnalyticsAggregationService
"""

from .value_objects import DateRange, TimeRange, TimeSeriesDataPoint, AnalyticsFilter
from .factory import AnalyticsQueryFactory
from .services import AnalyticsAggregationService

__all__ = [
    # Value Objects
    'DateRange',
    'TimeRange',
    'TimeSeriesDataPoint',
    'AnalyticsFilter',
    # Factories
    'AnalyticsQueryFactory',
    # Services
    'AnalyticsAggregationService'
]
