"""
Analytics Core Metrics Module

Shared metric calculation helpers and utility functions for analytics domain.

Functions:
    - parse_date_range: Parse date range parameters ('7d', '30d', '90d')
    - calculate_completion_rate: Calculate completion percentage
    - calculate_avg_time: Calculate average time from duration data
    - aggregate_by_type: Aggregate counts by type/category

ISO 9001:2015 compliant - Core utilities
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, List


def parse_date_range(range_param: str) -> Tuple[datetime, datetime]:
    """
    Parse range parameter to from_date and to_date

    Args:
        range_param: '7d', '30d', or '90d'

    Returns:
        tuple: (from_date, to_date)

    Raises:
        ValueError: If range_param is invalid

    Example:
        >>> from_date, to_date = parse_date_range('7d')
        >>> isinstance(from_date, datetime)
        True
    """
    range_map = {
        '7d': 7,
        '30d': 30,
        '90d': 90
    }

    days = range_map.get(range_param)
    if days is None:
        raise ValueError(f"Invalid range parameter: {range_param}. Must be one of: 7d, 30d, 90d")

    to_date = datetime.utcnow()
    from_date = to_date - timedelta(days=days)

    return from_date, to_date


def calculate_completion_rate(completed: int, total: int) -> float:
    """
    Calculate completion rate percentage

    Args:
        completed: Number of completed items
        total: Total number of items

    Returns:
        float: Completion rate as percentage (0-100)

    Example:
        >>> calculate_completion_rate(67, 145)
        46.2
        >>> calculate_completion_rate(0, 100)
        0.0
        >>> calculate_completion_rate(10, 0)
        0.0
    """
    if total <= 0:
        return 0.0
    return round((completed / total) * 100, 1)


def calculate_avg_value(values: List[float]) -> float:
    """
    Calculate average value from list

    Args:
        values: List of numeric values

    Returns:
        float: Average value, rounded to 1 decimal

    Example:
        >>> calculate_avg_value([10.5, 20.3, 15.7])
        15.5
        >>> calculate_avg_value([])
        0.0
    """
    if not values:
        return 0.0
    return round(sum(values) / len(values), 1)


def aggregate_by_type(items: List[Dict], type_key: str = 'type', count_key: str = 'count') -> Dict[str, int]:
    """
    Aggregate items by type into count dictionary

    Args:
        items: List of items with type and count
        type_key: Key name for type field (default: 'type')
        count_key: Key name for count field (default: 'count')

    Returns:
        dict: Mapping of type -> total count

    Example:
        >>> items = [
        ...     {'type': 'course_view', 'count': 50},
        ...     {'type': 'module_complete', 'count': 10}
        ... ]
        >>> aggregate_by_type(items)
        {'course_view': 50, 'module_complete': 10}
    """
    result = {}
    for item in items:
        item_type = item.get(type_key)
        count = item.get(count_key, 0)
        if item_type:
            result[item_type] = result.get(item_type, 0) + count
    return result


def clamp_value(value: int, min_val: int, max_val: int) -> int:
    """
    Clamp value between min and max

    Args:
        value: Value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        int: Clamped value

    Example:
        >>> clamp_value(150, 1, 100)
        100
        >>> clamp_value(5, 10, 50)
        10
        >>> clamp_value(25, 1, 100)
        25
    """
    return max(min_val, min(value, max_val))


def format_timestamp(dt: Optional[datetime]) -> Optional[str]:
    """
    Format datetime to ISO 8601 string

    Args:
        dt: Datetime object or None

    Returns:
        str: ISO formatted datetime string or None

    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2025, 1, 15, 10, 30, 0)
        >>> format_timestamp(dt)
        '2025-01-15T10:30:00'
        >>> format_timestamp(None)
        None
    """
    if dt is None:
        return None
    return dt.isoformat()


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safe division with default value for zero denominator

    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value if denominator is zero (default: 0.0)

    Returns:
        float: Division result or default

    Example:
        >>> safe_divide(100, 20)
        5.0
        >>> safe_divide(100, 0)
        0.0
        >>> safe_divide(100, 0, default=float('inf'))
        inf
    """
    if denominator == 0:
        return default
    return numerator / denominator
