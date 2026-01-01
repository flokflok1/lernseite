"""
LernsystemX Analytics Repository

Handles all analytics event database operations:
- Insert analytics events
- Query events by user, organisation, type
- Aggregate statistics
- Get recent events

Pure psycopg3 - No ORM
ISO 9001:2015 compliant - Repository pattern
"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
import json
import hashlib

from app.repositories.base_repository import BaseRepository
from app.database.connection import fetch_one, fetch_all, execute_query


class AnalyticsRepository(BaseRepository):
    """
    Analytics events repository

    Manages analytics event tracking with pure psycopg3
    """

    table_name = 'analytics_events'
    pk_column = 'event_id'

    @classmethod
    def insert_event(
        cls,
        user_id: int,
        event_type: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        payload: Optional[Dict] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        organisation_id: Optional[int] = None
    ) -> Dict:
        """
        Insert analytics event

        Args:
            user_id: User ID
            event_type: Type of event
            resource_type: Optional resource type (course, module, etc.)
            resource_id: Optional resource ID
            payload: Optional JSONB payload
            session_id: Optional session ID
            ip_address: Optional IP address (will be hashed)
            organisation_id: Optional organisation ID

        Returns:
            Dict with inserted event data

        Example:
            >>> event = AnalyticsRepository.insert_event(
            ...     user_id=123,
            ...     event_type='course_view',
            ...     resource_type='course',
            ...     resource_id=5,
            ...     payload={'duration_seconds': 45}
            ... )
        """
        # Hash IP address for privacy
        ip_hash = None
        if ip_address:
            ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()

        query = """
            INSERT INTO analytics_events (
                user_id,
                organisation_id,
                event_type,
                resource_type,
                resource_id,
                payload,
                session_id,
                ip_address_hash,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """

        result = fetch_one(
            query,
            (
                user_id,
                organisation_id,
                event_type,
                resource_type,
                resource_id,
                json.dumps(payload) if payload else None,
                session_id,
                ip_hash,
                datetime.utcnow()
            )
        )

        # Parse JSONB
        if result and result.get('payload'):
            if isinstance(result['payload'], str):
                result['payload'] = json.loads(result['payload'])

        return result

    @classmethod
    def get_events_by_user(
        cls,
        user_id: int,
        limit: int = 100,
        offset: int = 0,
        event_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Get events for specific user

        Args:
            user_id: User ID
            limit: Maximum number of events
            offset: Offset for pagination
            event_type: Optional filter by event type

        Returns:
            List of event dicts

        Example:
            >>> events = AnalyticsRepository.get_events_by_user(123, limit=10)
        """
        if event_type:
            query = """
                SELECT *
                FROM analytics_events
                WHERE user_id = %s AND event_type = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            params = (user_id, event_type, limit, offset)
        else:
            query = """
                SELECT *
                FROM analytics_events
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            params = (user_id, limit, offset)

        results = fetch_all(query, params)

        # Parse JSONB
        for result in results:
            if result.get('payload') and isinstance(result['payload'], str):
                result['payload'] = json.loads(result['payload'])

        return results

    @classmethod
    def get_events_by_organisation(
        cls,
        organisation_id: int,
        limit: int = 100,
        offset: int = 0,
        event_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Get events for entire organisation

        Args:
            organisation_id: Organisation ID
            limit: Maximum number of events
            offset: Offset for pagination
            event_type: Optional filter by event type

        Returns:
            List of event dicts

        Example:
            >>> events = AnalyticsRepository.get_events_by_organisation(5)
        """
        if event_type:
            query = """
                SELECT *
                FROM analytics_events
                WHERE organisation_id = %s AND event_type = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            params = (organisation_id, event_type, limit, offset)
        else:
            query = """
                SELECT *
                FROM analytics_events
                WHERE organisation_id = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            params = (organisation_id, limit, offset)

        results = fetch_all(query, params)

        # Parse JSONB
        for result in results:
            if result.get('payload') and isinstance(result['payload'], str):
                result['payload'] = json.loads(result['payload'])

        return results

    @classmethod
    def count_events_by_type(cls, user_id: int) -> List[Dict]:
        """
        Count events by type for user

        Args:
            user_id: User ID

        Returns:
            List of dicts with event_type and count

        Example:
            >>> counts = AnalyticsRepository.count_events_by_type(123)
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
    def count_events_by_type_org(cls, organisation_id: int) -> List[Dict]:
        """
        Count events by type for organisation

        Args:
            organisation_id: Organisation ID

        Returns:
            List of dicts with event_type and count

        Example:
            >>> counts = AnalyticsRepository.count_events_by_type_org(5)
        """
        query = """
            SELECT event_type, COUNT(*) as count
            FROM analytics_events
            WHERE organisation_id = %s
            GROUP BY event_type
            ORDER BY count DESC
        """

        return fetch_all(query, (organisation_id,))

    @classmethod
    def get_user_total_events(cls, user_id: int) -> int:
        """
        Get total number of events for user

        Args:
            user_id: User ID

        Returns:
            int: Total event count

        Example:
            >>> total = AnalyticsRepository.get_user_total_events(123)
        """
        query = "SELECT COUNT(*) as count FROM analytics_events WHERE user_id = %s"
        result = fetch_one(query, (user_id,))
        return result['count'] if result else 0

    @classmethod
    def get_org_total_events(cls, organisation_id: int) -> int:
        """
        Get total number of events for organisation

        Args:
            organisation_id: Organisation ID

        Returns:
            int: Total event count
        """
        query = "SELECT COUNT(*) as count FROM analytics_events WHERE organisation_id = %s"
        result = fetch_one(query, (organisation_id,))
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
            >>> timestamps = AnalyticsRepository.get_user_event_timestamps(123)
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
    def get_org_event_timestamps(cls, organisation_id: int) -> Dict:
        """
        Get first and last event timestamps for organisation

        Args:
            organisation_id: Organisation ID

        Returns:
            Dict with first_event_at and last_event_at
        """
        query = """
            SELECT
                MIN(created_at) as first_event_at,
                MAX(created_at) as last_event_at
            FROM analytics_events
            WHERE organisation_id = %s
        """

        result = fetch_one(query, (organisation_id,))
        return result if result else {'first_event_at': None, 'last_event_at': None}

    @classmethod
    def get_active_users_in_org(cls, organisation_id: int, days: int = 30) -> int:
        """
        Get number of active users in organisation within last N days

        Args:
            organisation_id: Organisation ID
            days: Number of days to look back

        Returns:
            int: Number of unique active users

        Example:
            >>> active = AnalyticsRepository.get_active_users_in_org(5, days=30)
        """
        query = """
            SELECT COUNT(DISTINCT user_id) as count
            FROM analytics_events
            WHERE organisation_id = %s
              AND created_at >= %s
        """

        cutoff = datetime.utcnow() - timedelta(days=days)
        result = fetch_one(query, (organisation_id, cutoff))
        return result['count'] if result else 0

    @classmethod
    def get_resource_event_counts(
        cls,
        resource_type: str,
        organisation_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get top resources by event count

        Args:
            resource_type: Type of resource (course, module, etc.)
            organisation_id: Optional organisation filter
            limit: Number of top resources

        Returns:
            List of dicts with resource_id and count

        Example:
            >>> top_courses = AnalyticsRepository.get_resource_event_counts('course', limit=5)
        """
        if organisation_id:
            query = """
                SELECT resource_id, COUNT(*) as count
                FROM analytics_events
                WHERE resource_type = %s
                  AND organisation_id = %s
                  AND resource_id IS NOT NULL
                GROUP BY resource_id
                ORDER BY count DESC
                LIMIT %s
            """
            params = (resource_type, organisation_id, limit)
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

    @classmethod
    def delete_user_events(cls, user_id: int) -> int:
        """
        Delete all events for user (for GDPR compliance)

        Args:
            user_id: User ID

        Returns:
            int: Number of events deleted

        Example:
            >>> deleted = AnalyticsRepository.delete_user_events(123)
        """
        query = "DELETE FROM analytics_events WHERE user_id = %s"
        return execute_query(query, (user_id,))

    @classmethod
    def get_events_in_timerange(
        cls,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[int] = None,
        organisation_id: Optional[int] = None,
        event_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Get events within time range with optional filters

        Args:
            start_date: Start of time range
            end_date: End of time range
            user_id: Optional user filter
            organisation_id: Optional organisation filter
            event_type: Optional event type filter

        Returns:
            List of event dicts

        Example:
            >>> from datetime import datetime, timedelta
            >>> start = datetime.utcnow() - timedelta(days=7)
            >>> end = datetime.utcnow()
            >>> events = AnalyticsRepository.get_events_in_timerange(start, end, user_id=123)
        """
        conditions = ["created_at BETWEEN %s AND %s"]
        params = [start_date, end_date]

        if user_id:
            conditions.append("user_id = %s")
            params.append(user_id)

        if organisation_id:
            conditions.append("organisation_id = %s")
            params.append(organisation_id)

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

    # ========================================================================
    # Phase B10: Advanced Analytics Repository Methods
    # ========================================================================

    @classmethod
    def get_events_time_series(
        cls,
        from_date: datetime,
        to_date: datetime,
        organisation_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get events aggregated by day (time series)

        Args:
            from_date: Start date
            to_date: End date
            organisation_id: Optional org filter (None = system-wide)

        Returns:
            List of dicts with date and count

        Example:
            >>> series = AnalyticsRepository.get_events_time_series(start, end)
            >>> # [{'date': '2025-01-15', 'count': 245}, ...]
        """
        if organisation_id:
            query = """
                SELECT
                    DATE(created_at) as date,
                    COUNT(*) as count
                FROM analytics_events
                WHERE created_at BETWEEN %s AND %s
                  AND organisation_id = %s
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """
            params = (from_date, to_date, organisation_id)
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
        organisation_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get count of unique active users per day (time series)

        Args:
            from_date: Start date
            to_date: End date
            organisation_id: Optional org filter

        Returns:
            List of dicts with date and count

        Example:
            >>> series = AnalyticsRepository.get_active_users_time_series(start, end)
        """
        if organisation_id:
            query = """
                SELECT
                    DATE(created_at) as date,
                    COUNT(DISTINCT user_id) as count
                FROM analytics_events
                WHERE created_at BETWEEN %s AND %s
                  AND organisation_id = %s
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """
            params = (from_date, to_date, organisation_id)
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
        organisation_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get top courses by event count with enrollments and completions

        Args:
            limit: Number of top courses to return
            from_date: Optional start date
            to_date: Optional end date
            organisation_id: Optional org filter

        Returns:
            List of dicts with course data

        Example:
            >>> top = AnalyticsRepository.get_top_courses(limit=10)
        """
        conditions = ["ae.resource_type = 'course'", "ae.resource_id IS NOT NULL"]
        params = []

        if from_date and to_date:
            conditions.append("ae.created_at BETWEEN %s AND %s")
            params.extend([from_date, to_date])

        if organisation_id:
            conditions.append("ae.organisation_id = %s")
            params.append(organisation_id)

        where_clause = " AND ".join(conditions)
        params.append(limit)

        query = f"""
            SELECT
                ae.resource_id as course_id,
                c.title,
                COUNT(*) as events_count,
                COALESCE(
                    (SELECT COUNT(*)
                     FROM course_enrollments ce
                     WHERE ce.course_id = CAST(ae.resource_id AS INTEGER)),
                    0
                ) as enrollments,
                COALESCE(
                    (SELECT COUNT(*)
                     FROM course_enrollments ce
                     WHERE ce.course_id = CAST(ae.resource_id AS INTEGER)
                       AND ce.completion_percentage = 100),
                    0
                ) as completions
            FROM analytics_events ae
            LEFT JOIN courses c ON c.course_id = CAST(ae.resource_id AS INTEGER)
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
            >>> methods = AnalyticsRepository.get_top_methods(limit=10)
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
        organisation_id: int,
        limit: int = 10,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get top courses for organisation

        Args:
            organisation_id: Organisation ID
            limit: Number of top courses
            from_date: Optional start date
            to_date: Optional end date

        Returns:
            List of dicts with course data
        """
        conditions = [
            "ae.resource_type = 'course'",
            "ae.resource_id IS NOT NULL",
            "ae.organisation_id = %s"
        ]
        params = [organisation_id]

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
                     FROM course_enrollments ce
                     WHERE ce.course_id = CAST(ae.resource_id AS INTEGER)
                       AND ce.completion_percentage = 100
                       AND ce.user_id IN (
                           SELECT user_id FROM users WHERE organisation_id = %s
                       )),
                    0
                ) * 100.0 / NULLIF(COUNT(DISTINCT ae.user_id), 0) as completion_rate,
                COUNT(*) as events_count
            FROM analytics_events ae
            LEFT JOIN courses c ON c.course_id = CAST(ae.resource_id AS INTEGER)
            WHERE {where_clause}
            GROUP BY ae.resource_id, c.title
            ORDER BY events_count DESC
            LIMIT %s
        """

        # Add organisation_id again for completion_rate subquery
        final_params = [organisation_id] + params
        return fetch_all(query, tuple(final_params))

    @classmethod
    def get_org_top_modules(
        cls,
        organisation_id: int,
        limit: int = 10,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get top modules for organisation

        Args:
            organisation_id: Organisation ID
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
            "ae.organisation_id = %s"
        ]
        params = [organisation_id]

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
            LEFT JOIN chapters ch ON ch.chapter_id = CAST(ae.resource_id AS UUID)
            LEFT JOIN courses c ON c.course_id = ch.course_id
            WHERE {where_clause}
            GROUP BY ae.resource_id, ch.title, c.title
            ORDER BY completions DESC
            LIMIT %s
        """

        return fetch_all(query, tuple(params))
