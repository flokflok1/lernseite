"""
Analytics Value Objects (DDD)

Immutable value objects for analytics domain.
"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Tuple


class TimeRange(Enum):
    """
    Predefined time ranges for analytics.

    Value Object: Immutable time range values.
    """
    WEEK = "7d"
    MONTH = "30d"
    QUARTER = "90d"

    @classmethod
    def from_string(cls, range_str: str) -> 'TimeRange':
        """
        Convert string to TimeRange enum.

        Args:
            range_str: Range string (e.g., "7d", "30d", "90d")

        Returns:
            TimeRange enum

        Raises:
            ValueError: If range is invalid
        """
        try:
            return cls(range_str)
        except ValueError:
            raise ValueError(
                f"Invalid time range: {range_str}. "
                f"Valid options: {', '.join([r.value for r in cls])}"
            )

    @property
    def days(self) -> int:
        """Number of days in this range."""
        days_map = {
            self.WEEK: 7,
            self.MONTH: 30,
            self.QUARTER: 90
        }
        return days_map[self]

    @property
    def display_name(self) -> str:
        """Human-readable display name."""
        names = {
            self.WEEK: "Letzte 7 Tage",
            self.MONTH: "Letzte 30 Tage",
            self.QUARTER: "Letzte 90 Tage"
        }
        return names[self]


@dataclass(frozen=True)
class DateRange:
    """
    Date range for analytics queries.

    Value Object: Immutable date range with validation.
    """
    from_date: datetime
    to_date: datetime

    def __post_init__(self):
        """Validate date range."""
        if self.from_date > self.to_date:
            raise ValueError("from_date must be before to_date")

    @classmethod
    def from_time_range(cls, time_range: TimeRange) -> 'DateRange':
        """
        Create DateRange from TimeRange.

        Args:
            time_range: Predefined time range

        Returns:
            DateRange instance
        """
        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=time_range.days)
        return cls(from_date=from_date, to_date=to_date)

    @classmethod
    def from_strings(cls, from_str: str, to_str: str) -> 'DateRange':
        """
        Create DateRange from date strings.

        Args:
            from_str: Start date (YYYY-MM-DD)
            to_str: End date (YYYY-MM-DD)

        Returns:
            DateRange instance

        Raises:
            ValueError: If date format is invalid
        """
        try:
            from_date = datetime.strptime(from_str, '%Y-%m-%d')
            to_date = datetime.strptime(to_str, '%Y-%m-%d')
            return cls(from_date=from_date, to_date=to_date)
        except ValueError as e:
            raise ValueError(f"Invalid date format. Expected YYYY-MM-DD: {e}")

    def days_count(self) -> int:
        """Number of days in this range."""
        return (self.to_date - self.from_date).days

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'from_date': self.from_date.strftime('%Y-%m-%d'),
            'to_date': self.to_date.strftime('%Y-%m-%d'),
            'days': self.days_count()
        }


@dataclass(frozen=True)
class TimeSeriesDataPoint:
    """
    Single data point in a time series.

    Value Object: Immutable time series data point.
    """
    date: str
    value: int

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'date': self.date,
            'value': self.value
        }


@dataclass(frozen=True)
class AnalyticsFilter:
    """
    Filter for analytics queries.

    Value Object: Immutable filter configuration.
    """
    limit: int = 10
    date_range: DateRange = None

    def __post_init__(self):
        """Validate filter."""
        if self.limit < 1 or self.limit > 100:
            raise ValueError("Limit must be between 1 and 100")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'limit': self.limit,
            'date_range': self.date_range.to_dict() if self.date_range else None
        }
