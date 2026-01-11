"""
Analytics Aggregate Entity (DDD Domain Entity)

Represents pre-aggregated analytics data for fast dashboard queries.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, Any


@dataclass
class AnalyticsAggregate:
    """
    Analytics Aggregate domain entity.

    Pre-aggregated metrics for dashboards (daily/hourly).

    Attributes:
        aggregate_id: Auto-incrementing ID
        metric_type: Type of metric (e.g., 'course_enrollments', 'active_users')
        dimension: Dimension for grouping (e.g., 'course', 'organization')
        dimension_value: Value of dimension (e.g., course_id, org_id)
        date: Aggregation date
        hour: Hour of day (0-23) for hourly aggregates, NULL for daily
        value: Numeric value (count, sum, avg, etc.)
        count: Number of data points aggregated
        metadata: Additional JSONB metadata
        created_at: When aggregate was created
    """

    aggregate_id: Optional[int]  # Assigned by database
    metric_type: str
    date: date
    value: Decimal
    dimension: Optional[str] = None
    dimension_value: Optional[str] = None
    hour: Optional[int] = None
    count: int = 1
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate analytics aggregate entity."""
        if not self.metric_type or not self.metric_type.strip():
            raise ValueError("Metric type cannot be empty")

        if self.hour is not None and (self.hour < 0 or self.hour > 23):
            raise ValueError("Hour must be between 0 and 23")

        if self.count < 0:
            raise ValueError("Count cannot be negative")

    def is_hourly(self) -> bool:
        """Check if this is an hourly aggregate."""
        return self.hour is not None

    def is_daily(self) -> bool:
        """Check if this is a daily aggregate."""
        return self.hour is None

    def has_dimension(self) -> bool:
        """Check if this aggregate has a dimension."""
        return self.dimension is not None and self.dimension_value is not None

    def get_average_value(self) -> Optional[Decimal]:
        """
        Get average value per data point.

        Returns:
            Average value or None if count is 0
        """
        if self.count == 0:
            return None
        return self.value / Decimal(self.count)
