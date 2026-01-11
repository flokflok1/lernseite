"""
Time Utilities

Datetime handling and timezone utilities.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import time


class TimeUtils:
    """
    Time and datetime utility functions.

    All timestamps in UTC. Frontend handles timezone conversion.
    """

    @staticmethod
    def now_utc() -> datetime:
        """
        Get current UTC datetime.

        Returns:
            Current datetime in UTC
        """
        return datetime.now(timezone.utc)

    @staticmethod
    def unix_timestamp() -> int:
        """
        Get current Unix timestamp.

        Returns:
            Unix timestamp (seconds since epoch)
        """
        return int(time.time())

    @staticmethod
    def unix_timestamp_ms() -> int:
        """
        Get current Unix timestamp in milliseconds.

        Returns:
            Unix timestamp in milliseconds
        """
        return int(time.time() * 1000)

    @staticmethod
    def from_unix_timestamp(timestamp: int) -> datetime:
        """
        Convert Unix timestamp to datetime.

        Args:
            timestamp: Unix timestamp (seconds)

        Returns:
            Datetime object in UTC
        """
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    @staticmethod
    def to_unix_timestamp(dt: datetime) -> int:
        """
        Convert datetime to Unix timestamp.

        Args:
            dt: Datetime object

        Returns:
            Unix timestamp (seconds)
        """
        return int(dt.timestamp())

    @staticmethod
    def add_days(dt: datetime, days: int) -> datetime:
        """
        Add days to datetime.

        Args:
            dt: Datetime object
            days: Number of days to add (can be negative)

        Returns:
            New datetime
        """
        return dt + timedelta(days=days)

    @staticmethod
    def add_hours(dt: datetime, hours: int) -> datetime:
        """
        Add hours to datetime.

        Args:
            dt: Datetime object
            hours: Number of hours to add (can be negative)

        Returns:
            New datetime
        """
        return dt + timedelta(hours=hours)

    @staticmethod
    def add_minutes(dt: datetime, minutes: int) -> datetime:
        """
        Add minutes to datetime.

        Args:
            dt: Datetime object
            minutes: Number of minutes to add (can be negative)

        Returns:
            New datetime
        """
        return dt + timedelta(minutes=minutes)

    @staticmethod
    def is_expired(dt: datetime, expiry_hours: int = 24) -> bool:
        """
        Check if datetime is expired.

        Args:
            dt: Datetime to check
            expiry_hours: Expiry period in hours

        Returns:
            True if expired
        """
        now = TimeUtils.now_utc()
        expiry = dt + timedelta(hours=expiry_hours)
        return now > expiry

    @staticmethod
    def time_ago(dt: datetime) -> str:
        """
        Get human-readable time difference.

        Args:
            dt: Datetime to compare

        Returns:
            Human-readable string (e.g., "2 hours ago")
        """
        now = TimeUtils.now_utc()
        diff = now - dt

        seconds = diff.total_seconds()

        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days > 1 else ''} ago"
        elif seconds < 2592000:
            weeks = int(seconds / 604800)
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        elif seconds < 31536000:
            months = int(seconds / 2592000)
            return f"{months} month{'s' if months > 1 else ''} ago"
        else:
            years = int(seconds / 31536000)
            return f"{years} year{'s' if years > 1 else ''} ago"

    @staticmethod
    def format_iso(dt: datetime) -> str:
        """
        Format datetime as ISO 8601 string.

        Args:
            dt: Datetime object

        Returns:
            ISO 8601 string (e.g., "2025-01-09T23:00:00Z")
        """
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    @staticmethod
    def parse_iso(iso_string: str) -> datetime:
        """
        Parse ISO 8601 string to datetime.

        Args:
            iso_string: ISO 8601 formatted string

        Returns:
            Datetime object in UTC
        """
        return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))

    @staticmethod
    def start_of_day(dt: Optional[datetime] = None) -> datetime:
        """
        Get start of day (00:00:00).

        Args:
            dt: Datetime object (default: now)

        Returns:
            Datetime at start of day
        """
        if dt is None:
            dt = TimeUtils.now_utc()
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def end_of_day(dt: Optional[datetime] = None) -> datetime:
        """
        Get end of day (23:59:59).

        Args:
            dt: Datetime object (default: now)

        Returns:
            Datetime at end of day
        """
        if dt is None:
            dt = TimeUtils.now_utc()
        return dt.replace(hour=23, minute=59, second=59, microsecond=999999)
