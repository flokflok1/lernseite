"""
Analytics Repository Package

Refactored analytics repository split into logical modules:
- core_events.py: Basic event operations (insert, get by user/org, delete)
- aggregation.py: Event counting and statistics (counts, totals, timestamps)
- advanced_analytics.py: Time series and advanced analytics (top courses, time series, org analytics)

Pure psycopg3 - No ORM
ISO 9001:2015 compliant - Repository pattern
"""

from .core_events import CoreEventsRepository
from .aggregation import AggregationRepository
from .advanced_analytics import AdvancedAnalyticsRepository



class AnalyticsRepository(
    CoreEventsRepository,
    AggregationRepository,
    AdvancedAnalyticsRepository
):
    """
    Unified AnalyticsRepository combining all functionality
    This class uses multiple inheritance to aggregate methods from specialized modules.
    """
    pass


__all__ = [
    'CoreEventsRepository',
    'AggregationRepository',
    'AdvancedAnalyticsRepository',
]
