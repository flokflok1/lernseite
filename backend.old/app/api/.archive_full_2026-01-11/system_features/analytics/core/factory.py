"""
Analytics Factories (DDD)

Factory Pattern for creating analytics queries and configurations.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from .value_objects import DateRange, TimeRange, AnalyticsFilter


class AnalyticsQueryFactory:
    """
    Factory for creating analytics query configurations.

    Implements Domain-Driven Design (DDD) Factory Pattern.
    """

    @staticmethod
    def create_time_series_query(
        date_range: Optional[DateRange] = None,
        time_range: Optional[TimeRange] = None,
        from_str: Optional[str] = None,
        to_str: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create time series query configuration.

        Args:
            date_range: DateRange value object (highest priority)
            time_range: TimeRange value object (medium priority)
            from_str: Start date string (low priority, requires to_str)
            to_str: End date string (low priority, requires from_str)

        Returns:
            Query configuration dict

        Business Rules:
        - Date range can be specified via DateRange, TimeRange, or strings
        - Priority: DateRange > TimeRange > strings
        - Defaults to WEEK if nothing specified
        """
        # Determine date range
        if date_range:
            final_range = date_range
        elif time_range:
            final_range = DateRange.from_time_range(time_range)
        elif from_str and to_str:
            final_range = DateRange.from_strings(from_str, to_str)
        else:
            # Default to 7 days
            final_range = DateRange.from_time_range(TimeRange.WEEK)

        return {
            'query_id': str(uuid.uuid4()),
            'from_date': final_range.from_date,
            'to_date': final_range.to_date,
            'days': final_range.days_count(),
            'created_at': datetime.utcnow()
        }

    @staticmethod
    def create_ranking_query(
        limit: int = 10,
        date_range: Optional[DateRange] = None,
        time_range: Optional[TimeRange] = None,
        from_str: Optional[str] = None,
        to_str: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create ranking query configuration (top courses, top methods).

        Args:
            limit: Number of top items (1-100)
            date_range: Optional date range filter
            time_range: Optional time range filter
            from_str: Optional start date string
            to_str: Optional end date string

        Returns:
            Query configuration dict

        Business Rules:
        - Limit must be between 1 and 100
        - Date range is optional (None = all time)
        """
        # Validate limit
        if limit < 1 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")

        # Determine date range (optional)
        final_range = None
        if date_range:
            final_range = date_range
        elif time_range:
            final_range = DateRange.from_time_range(time_range)
        elif from_str and to_str:
            final_range = DateRange.from_strings(from_str, to_str)

        return {
            'query_id': str(uuid.uuid4()),
            'limit': limit,
            'from_date': final_range.from_date if final_range else None,
            'to_date': final_range.to_date if final_range else None,
            'has_date_filter': final_range is not None,
            'created_at': datetime.utcnow()
        }

    @staticmethod
    def create_filter_from_request(
        limit: Optional[int] = None,
        range_param: Optional[str] = None,
        days_param: Optional[int] = None,
        from_str: Optional[str] = None,
        to_str: Optional[str] = None
    ) -> AnalyticsFilter:
        """
        Create AnalyticsFilter from request parameters.

        Args:
            limit: Optional limit (default: 10)
            range_param: Optional range string (e.g., "7d")
            days_param: Optional days count (legacy parameter)
            from_str: Optional start date string
            to_str: Optional end date string

        Returns:
            AnalyticsFilter value object

        Business Rules:
        - Priority: from/to > range_param > days_param > default (7d)
        - Limit defaults to 10, max 100
        """
        # Determine limit
        final_limit = min(limit or 10, 100)

        # Determine date range
        date_range = None
        if from_str and to_str:
            date_range = DateRange.from_strings(from_str, to_str)
        elif range_param:
            time_range = TimeRange.from_string(range_param)
            date_range = DateRange.from_time_range(time_range)
        elif days_param:
            # Legacy support: convert days to range
            range_map = {7: TimeRange.WEEK, 30: TimeRange.MONTH, 90: TimeRange.QUARTER}
            time_range = range_map.get(days_param, TimeRange.WEEK)
            date_range = DateRange.from_time_range(time_range)

        return AnalyticsFilter(
            limit=final_limit,
            date_range=date_range
        )
