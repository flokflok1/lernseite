"""
Advanced Analytics Repository

Handles advanced analytics queries:
- Time series analysis (events and active users per day)
- Top courses and learning methods
- Organisation-specific analytics (top courses, top modules)
- Time range event queries

Pure psycopg3 - No ORM
ISO 9001:2015 compliant - Repository pattern
"""

from typing import Optional, Dict, List
from datetime import datetime
import json

from app.repositories.base_repository import BaseRepository
from app.database.connection import fetch_one, fetch_all


class AdvancedAnalyticsRepository(BaseRepository):
    """
    Advanced analytics repository

    Manages complex analytical queries and time series data.
    """

    table_name = 'analytics_events'
    pk_column = 'event_id'

    @classmethod
    def get_events_in_timerange(
        cls,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[int] = None,
        organization_id: Optional[int] = None,
        event_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Get events within time range with optional filters

        Args:
            start_date: Start of time range
            end_date: End of time range
            user_id: Optional user filter
            organization_id: Optional organisation filter
            event_type: Optional event type filter

        Returns:
            List of event dicts

        Example:
            >>> from datetime import datetime, timedelta
            >>> start = datetime.utcnow() - timedelta(days=7)
            >>> end = datetime.utcnow()
            >>> events = AdvancedAnalyticsRepository.get_events_in_timerange(start, end, user_id=123)
        """
        conditions = ["created_at BETWEEN %s AND %s"]
        params = [start_date, end_date]

        if user_id:
            conditions.append("user_id = %s")
            params.append(user_id)

        if organization_id:
            conditions.append("organization_id = %s")
            params.append(organization_id)

        if event_type:
            conditions.append("event_type = %s")
            params.append(event_type)

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT *
            FROM analytics_events
            WHERE {where_clause}
            ORDER BY created_at DESC
        """

        results = fetch_all(query, tuple(params))

        # Parse JSONB
        for result in results:
            if result.get('payload') and isinstance(result['payload'], str):
                result['payload'] = json.loads(result['payload'])

        return results

    @classmethod
    def get_events_time_series(
        cls,
        from_date: datetime,
        to_date: datetime,
        organization_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get events aggregated by day (time series)

        Args:
            from_date: Start date
            to_date: End date
            organization_id: Optional org filter (None = system-wide)

        Returns:
            List of dicts with date and count

        Example:
            >>> series = AdvancedAnalyticsRepository.get_events_time_series(start, end)
            >>> # [{'date': '2025-01-15', 'count': 245}, ...]
        """
        if organization_id:
            query = """
                SELECT
                    DATE(created_at) as date,
                    COUNT(*) as count
                FROM analytics_events
                WHERE created_at BETWEEN %s AND %s
                  AND organization_id = %s
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """
            params = (from_date, to_date, organization_id)
        else:
            query = """
                SELECT
                    DATE(created_at) as date,
                    COUNT(*) as count
                FROM analytics_events
                WHERE created_at BETWEEN %s AND %s
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """
            params = (from_date, to_date)

        return fetch_all(query, params)

    @classmethod
    def get_active_users_time_series(
        cls,
        from_date: datetime,
        to_date: datetime,
        organization_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get count of unique active users per day (time series)

        Args:
            from_date: Start date
            to_date: End date
            organization_id: Optional org filter

        Returns:
            List of dicts with date and count

        Example:
            >>> series = AdvancedAnalyticsRepository.get_active_users_time_series(start, end)
        """
        if organization_id:
            query = """
                SELECT
                    DATE(created_at) as date,
                    COUNT(DISTINCT user_id) as count
                FROM analytics_events
                WHERE created_at BETWEEN %s AND %s
                  AND organization_id = %s
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """
            params = (from_date, to_date, organization_id)
        else:
            query = """
                SELECT
                    DATE(created_at) as date,
                    COUNT(DISTINCT user_id) as count
                FROM analytics_events
                WHERE created_at BETWEEN %s AND %s
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """
            params = (from_date, to_date)

        return fetch_all(query, params)

    @classmethod
    def get_top_courses(
        cls,
        limit: int = 10,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        organization_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get top courses by event count with enrollments and completions

        Args:
            limit: Number of top courses to return
            from_date: Optional start date
            to_date: Optional end date
            organization_id: Optional org filter

        Returns:
            List of dicts with course data

        Example:
            >>> top = AdvancedAnalyticsRepository.get_top_courses(limit=10)
        """
        conditions = ["ae.resource_type = 'course'", "ae.resource_id IS NOT NULL"]
        params = []

        if from_date and to_date:
            conditions.append("ae.created_at BETWEEN %s AND %s")
            params.extend([from_date, to_date])

        if organization_id:
            conditions.append("ae.organization_id = %s")
            params.append(organization_id)

        where_clause = " AND ".join(conditions)
        params.append(limit)

        query = f"""
            SELECT
                ae.resource_id as course_id,
                c.title,
                COUNT(*) as events_count,
                COALESCE(
                    (SELECT COUNT(*)
                     FROM courses.course_enrollments ce
                     WHERE ce.course_id = CAST(ae.resource_id AS INTEGER)),
                    0
                ) as enrollments,
                COALESCE(
                    (SELECT COUNT(*)
                     FROM courses.course_enrollments ce
                     WHERE ce.course_id = CAST(ae.resource_id AS INTEGER)
                       AND ce.completion_percentage = 100),
                    0
                ) as completions
            FROM analytics_events ae
            LEFT JOIN courses.courses c ON c.course_id = CAST(ae.resource_id AS INTEGER)
            WHERE {where_clause}
            GROUP BY ae.resource_id, c.title
            ORDER BY events_count DESC
            LIMIT %s
        """

        return fetch_all(query, tuple(params))

    @classmethod
    def get_top_methods(
        cls,
        limit: int = 10,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get top learning methods by usage

        Args:
            limit: Number of top methods to return
            from_date: Optional start date
            to_date: Optional end date

        Returns:
            List of dicts with method data

        Example:
            >>> methods = AdvancedAnalyticsRepository.get_top_methods(limit=10)
        """
        conditions = ["ae.event_type = 'method_execute'", "ae.resource_id IS NOT NULL"]
        params = []

        if from_date and to_date:
            conditions.append("ae.created_at BETWEEN %s AND %s")
            params.extend([from_date, to_date])

        where_clause = " AND ".join(conditions)
        params.append(limit)

        query = f"""
            SELECT
                ae.resource_id as method_id,
                lm.name,
                COUNT(*) as calls,
                COALESCE(SUM(CAST(ae.payload->>'tokens_used' AS INTEGER)), 0) as tokens_used,
                COALESCE(AVG(CAST(ae.payload->>'tokens_used' AS INTEGER)), 0) as avg_tokens
            FROM analytics_events ae
            LEFT JOIN learning_methods lm ON lm.method_id = CAST(ae.resource_id AS INTEGER)
            WHERE {where_clause}
            GROUP BY ae.resource_id, lm.name
            ORDER BY calls DESC
            LIMIT %s
        """

        return fetch_all(query, tuple(params))

    @classmethod
    def get_org_top_courses(
        cls,
        organization_id: int,
        limit: int = 10,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get top courses for organisation

        Args:
            organization_id: Organisation ID
            limit: Number of top courses
            from_date: Optional start date
            to_date: Optional end date

        Returns:
            List of dicts with course data
        """
        conditions = [
            "ae.resource_type = 'course'",
            "ae.resource_id IS NOT NULL",
            "ae.organization_id = %s"
        ]
        params = [organization_id]

        if from_date and to_date:
            conditions.append("ae.created_at BETWEEN %s AND %s")
            params.extend([from_date, to_date])

        where_clause = " AND ".join(conditions)
        params.append(limit)

        query = f"""
            SELECT
                ae.resource_id as course_id,
                c.title,
                COUNT(DISTINCT ae.user_id) as enrolled_count,
                COALESCE(AVG(
                    CASE
                        WHEN ae.event_type = 'module_complete'
                        THEN CAST(ae.payload->>'progress_percentage' AS FLOAT)
                        ELSE NULL
                    END
                ), 0) as avg_progress,
                COALESCE(
                    (SELECT COUNT(*)
                     FROM courses.course_enrollments ce
                     WHERE ce.course_id = CAST(ae.resource_id AS INTEGER)
                       AND ce.completion_percentage = 100
                       AND ce.user_id IN (
                           SELECT user_id FROM core.users WHERE organization_id = %s
                       )),
                    0
                ) * 100.0 / NULLIF(COUNT(DISTINCT ae.user_id), 0) as completion_rate,
                COUNT(*) as events_count
            FROM analytics_events ae
            LEFT JOIN courses.courses c ON c.course_id = CAST(ae.resource_id AS INTEGER)
            WHERE {where_clause}
            GROUP BY ae.resource_id, c.title
            ORDER BY events_count DESC
            LIMIT %s
        """

        # Add organization_id again for completion_rate subquery
        final_params = [organization_id] + params
        return fetch_all(query, tuple(final_params))

    @classmethod
    def get_org_top_modules(
        cls,
        organization_id: int,
        limit: int = 10,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get top modules for organisation

        Args:
            organization_id: Organisation ID
            limit: Number of top modules
            from_date: Optional start date
            to_date: Optional end date

        Returns:
            List of dicts with module data
        """
        conditions = [
            "ae.event_type = 'module_complete'",
            "ae.resource_type = 'module'",
            "ae.resource_id IS NOT NULL",
            "ae.organization_id = %s"
        ]
        params = [organization_id]

        if from_date and to_date:
            conditions.append("ae.created_at BETWEEN %s AND %s")
            params.extend([from_date, to_date])

        where_clause = " AND ".join(conditions)
        params.append(limit)

        query = f"""
            SELECT
                ae.resource_id as chapter_id,
                ch.title as chapter_title,
                c.title as course_title,
                COUNT(*) as completions,
                COALESCE(AVG(CAST(ae.payload->>'time_spent_minutes' AS INTEGER)), 0) as avg_time_spent
            FROM analytics_events ae
            LEFT JOIN courses.chapters ch ON ch.chapter_id = CAST(ae.resource_id AS UUID)
            LEFT JOIN courses.courses c ON c.course_id = ch.course_id
            WHERE {where_clause}
            GROUP BY ae.resource_id, ch.title, c.title
            ORDER BY completions DESC
            LIMIT %s
        """

        return fetch_all(query, tuple(params))
