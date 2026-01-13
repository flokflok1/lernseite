"""
Analytics Services (DDD)

Domain services for analytics aggregation and transformation.
"""

from typing import List, Dict, Any
import logging

from .value_objects import TimeSeriesDataPoint

logger = logging.getLogger(__name__)


class AnalyticsAggregationService:
    """
    Service for aggregating and transforming analytics data.

    Domain Service: Handles complex business logic for analytics.
    """

    @staticmethod
    def aggregate_time_series(
        raw_data: List[Dict[str, Any]],
        date_key: str = 'date',
        value_key: str = 'count'
    ) -> tuple[List[TimeSeriesDataPoint], int]:
        """
        Aggregate raw time series data.

        Args:
            raw_data: Raw data from repository
            date_key: Key for date field in raw data
            value_key: Key for value field in raw data

        Returns:
            Tuple of (data_points, total)

        Business Rules:
        - Dates are converted to strings
        - Values are summed for total
        """
        data_points = [
            TimeSeriesDataPoint(
                date=str(row[date_key]),
                value=int(row[value_key])
            )
            for row in raw_data
        ]

        total = sum(point.value for point in data_points)

        return data_points, total

    @staticmethod
    def calculate_total_unique_users(data_points: List[TimeSeriesDataPoint]) -> int:
        """
        Calculate total unique users from time series.

        Args:
            data_points: Time series data points

        Returns:
            Maximum daily count (approximate unique users)

        Business Rules:
        - For active users, we use max daily count as approximation
        - This assumes users are counted uniquely per day
        """
        if not data_points:
            return 0

        return max((point.value for point in data_points), default=0)

    @staticmethod
    def calculate_completion_rate(completions: int, enrollments: int) -> float:
        """
        Calculate completion rate percentage.

        Args:
            completions: Number of completions
            enrollments: Number of enrollments

        Returns:
            Completion rate as percentage (0-100)

        Business Rules:
        - Returns 0.0 if no enrollments
        - Rounded to 1 decimal place
        """
        if enrollments == 0:
            return 0.0

        rate = (completions / enrollments) * 100
        return round(rate, 1)

    @staticmethod
    def calculate_average_tokens(total_tokens: int, calls: int) -> int:
        """
        Calculate average tokens per call.

        Args:
            total_tokens: Total tokens used
            calls: Number of calls

        Returns:
            Average tokens per call

        Business Rules:
        - Returns 0 if no calls
        - Rounded to integer
        """
        if calls == 0:
            return 0

        return round(total_tokens / calls)
