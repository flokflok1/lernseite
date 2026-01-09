"""
Analytics Aggregation Repository

Handles event counting and aggregation operations:
- Count events by type (user and org level)
- Get total event counts
- Get event timestamps (first/last)
- Get active user counts
- Get resource event counts

Pure psycopg3 - No ORM
ISO 9001:2015 compliant - Repository pattern
"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
import json

from app.repositories.base_repository import BaseRepository
from app.database.connection import fetch_one, fetch_all


class AggregationRepository(BaseRepository):
    """
    Analytics aggregation repository

    Manages event counting and statistics operations.
    """

    table_name = 'analytics_events'
    pk_column = 'event_id'

    @classmethod
    def count_events_by_type(cls, user_id: int) -> List[Dict]:
        """
        Count events by type for user

        Args:
            user_id: User ID

        Returns:
            List of dicts with event_type and count

        Example:
            >>> counts = AggregationRepository.count_events_by_type(123)
            >>> # [{'event_type': 'login', 'count': 15}, ...]
        """
        query = """
            SELECT event_type, COUNT(*) as count
            FROM analytics_events
            WHERE user_id = %s
            GROUP BY event_type
            ORDER BY count DESC
        """

        return fetch_all(query, (user_id,))

    @classmethod
    def count_events_by_type_org(cls, organization_id: int) -> List[Dict]:
        """
        Count events by type for organisation

        Args:
            organization_id: Organisation ID

        Returns:
            List of dicts with event_type and count

        Example:
            >>> counts = AggregationRepository.count_events_by_type_org(5)
        """
        query = """
            SELECT event_type, COUNT(*) as count
            FROM analytics_events
            WHERE organization_id = %s
            GROUP BY event_type
            ORDER BY count DESC
        """

        return fetch_all(query, (organization_id,))

    @classmethod
    def get_user_total_events(cls, user_id: int) -> int:
        """
        Get total number of events for user

        Args:
            user_id: User ID

        Returns:
            int: Total event count

        Example:
            >>> total = AggregationRepository.get_user_total_events(123)
        """
        query = "SELECT COUNT(*) as count FROM analytics_events WHERE user_id = %s"
        result = fetch_one(query, (user_id,))
        return result['count'] if result else 0

    @classmethod
    def get_org_total_events(cls, organization_id: int) -> int:
        """
        Get total number of events for organisation

        Args:
            organization_id: Organisation ID

        Returns:
            int: Total event count
        """
        query = "SELECT COUNT(*) as count FROM analytics_events WHERE organization_id = %s"
        result = fetch_one(query, (organization_id,))
        return result['count'] if result else 0

    @classmethod
    def get_user_event_timestamps(cls, user_id: int) -> Dict:
        """
        Get first and last event timestamps for user

        Args:
            user_id: User ID

        Returns:
            Dict with first_event_at and last_event_at

        Example:
            >>> timestamps = AggregationRepository.get_user_event_timestamps(123)
        """
        query = """
            SELECT
                MIN(created_at) as first_event_at,
                MAX(created_at) as last_event_at
            FROM analytics_events
            WHERE user_id = %s
        """

        result = fetch_one(query, (user_id,))
        return result if result else {'first_event_at': None, 'last_event_at': None}

    @classmethod
    def get_org_event_timestamps(cls, organization_id: int) -> Dict:
        """
        Get first and last event timestamps for organisation

        Args:
            organization_id: Organisation ID

        Returns:
            Dict with first_event_at and last_event_at
        """
        query = """
            SELECT
                MIN(created_at) as first_event_at,
                MAX(created_at) as last_event_at
            FROM analytics_events
            WHERE organization_id = %s
        """

        result = fetch_one(query, (organization_id,))
        return result if result else {'first_event_at': None, 'last_event_at': None}

    @classmethod
    def get_active_users_in_org(cls, organization_id: int, days: int = 30) -> int:
        """
        Get number of active users in organisation within last N days

        Args:
            organization_id: Organisation ID
            days: Number of days to look back

        Returns:
            int: Number of unique active users

        Example:
            >>> active = AggregationRepository.get_active_users_in_org(5, days=30)
        """
        query = """
            SELECT COUNT(DISTINCT user_id) as count
            FROM analytics_events
            WHERE organization_id = %s
              AND created_at >= %s
        """

        cutoff = datetime.utcnow() - timedelta(days=days)
        result = fetch_one(query, (organization_id, cutoff))
        return result['count'] if result else 0

    @classmethod
    def get_resource_event_counts(
        cls,
        resource_type: str,
        organization_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get top resources by event count

        Args:
            resource_type: Type of resource (course, module, etc.)
            organization_id: Optional organisation filter
            limit: Number of top resources

        Returns:
            List of dicts with resource_id and count

        Example:
            >>> top_courses = AggregationRepository.get_resource_event_counts('course', limit=5)
        """
        if organization_id:
            query = """
                SELECT resource_id, COUNT(*) as count
                FROM analytics_events
                WHERE resource_type = %s
                  AND organization_id = %s
                  AND resource_id IS NOT NULL
                GROUP BY resource_id
                ORDER BY count DESC
                LIMIT %s
            """
            params = (resource_type, organization_id, limit)
        else:
            query = """
                SELECT resource_id, COUNT(*) as count
                FROM analytics_events
                WHERE resource_type = %s
                  AND resource_id IS NOT NULL
                GROUP BY resource_id
                ORDER BY count DESC
                LIMIT %s
            """
            params = (resource_type, limit)

        return fetch_all(query, params)
