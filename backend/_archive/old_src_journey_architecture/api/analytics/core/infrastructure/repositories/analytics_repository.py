"""
Analytics Repository (Infrastructure Layer - Part 1)

Database access for:
- analytics_sessions
- analytics_aggregates
- analytics_events

ALL queries use parameterized statements for security.
NO hardcoded values - everything loaded from database.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
import json
from src.core.database import get_db_connection
from src.api.analytics.core.domain.entities.analytics_session import AnalyticsSession
from src.api.analytics.core.domain.entities.analytics_aggregate import AnalyticsAggregate
from src.api.analytics.core.domain.entities.analytics_event import AnalyticsEvent


class AnalyticsRepository:
    """
    Analytics Repository - Sessions, Aggregates, Events.
    """

    # ============================================================================
    # ANALYTICS SESSIONS
    # ============================================================================

    @staticmethod
    def find_session_by_id(session_id: str) -> Optional[AnalyticsSession]:
        """Find analytics session by ID."""
        query = """
            SELECT session_id, session_token, user_id, organization_id,
                   ip_address_hash, user_agent, device_type, browser, os,
                   country, city, started_at, last_activity_at, ended_at,
                   duration_seconds, page_views
            FROM public.analytics_sessions
            WHERE session_id = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (session_id,))
                row = cur.fetchone()

                if not row:
                    return None

                return AnalyticsSession(
                    session_id=row[0],
                    session_token=row[1],
                    user_id=row[2],
                    organization_id=row[3],
                    ip_address_hash=row[4],
                    user_agent=row[5],
                    device_type=row[6] or 'unknown',
                    browser=row[7],
                    os=row[8],
                    country=row[9],
                    city=row[10],
                    started_at=row[11],
                    last_activity_at=row[12],
                    ended_at=row[13],
                    duration_seconds=row[14],
                    page_views=row[15] or 0
                )

    @staticmethod
    def find_sessions_by_user(
        user_id: str,
        limit: int = 50
    ) -> List[AnalyticsSession]:
        """Find analytics sessions for a user."""
        query = """
            SELECT session_id, session_token, user_id, organization_id,
                   ip_address_hash, user_agent, device_type, browser, os,
                   country, city, started_at, last_activity_at, ended_at,
                   duration_seconds, page_views
            FROM public.analytics_sessions
            WHERE user_id = %s
            ORDER BY started_at DESC
            LIMIT %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id, limit))
                rows = cur.fetchall()

                return [
                    AnalyticsSession(
                        session_id=row[0],
                        session_token=row[1],
                        user_id=row[2],
                        organization_id=row[3],
                        ip_address_hash=row[4],
                        user_agent=row[5],
                        device_type=row[6] or 'unknown',
                        browser=row[7],
                        os=row[8],
                        country=row[9],
                        city=row[10],
                        started_at=row[11],
                        last_activity_at=row[12],
                        ended_at=row[13],
                        duration_seconds=row[14],
                        page_views=row[15] or 0
                    )
                    for row in rows
                ]

    @staticmethod
    def create_session(session: AnalyticsSession) -> AnalyticsSession:
        """Create new analytics session."""
        query = """
            INSERT INTO public.analytics_sessions
            (session_id, session_token, user_id, organization_id,
             ip_address_hash, user_agent, device_type, browser, os,
             country, city, started_at, last_activity_at, page_views)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING session_id, session_token, user_id, organization_id,
                      ip_address_hash, user_agent, device_type, browser, os,
                      country, city, started_at, last_activity_at, ended_at,
                      duration_seconds, page_views
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    session.session_id,
                    session.session_token,
                    session.user_id,
                    session.organization_id,
                    session.ip_address_hash,
                    session.user_agent,
                    session.device_type,
                    session.browser,
                    session.os,
                    session.country,
                    session.city,
                    session.started_at or datetime.utcnow(),
                    session.last_activity_at or datetime.utcnow(),
                    session.page_views
                ))

                row = cur.fetchone()
                conn.commit()

                return AnalyticsSession(
                    session_id=row[0],
                    session_token=row[1],
                    user_id=row[2],
                    organization_id=row[3],
                    ip_address_hash=row[4],
                    user_agent=row[5],
                    device_type=row[6] or 'unknown',
                    browser=row[7],
                    os=row[8],
                    country=row[9],
                    city=row[10],
                    started_at=row[11],
                    last_activity_at=row[12],
                    ended_at=row[13],
                    duration_seconds=row[14],
                    page_views=row[15] or 0
                )

    @staticmethod
    def update_session(session: AnalyticsSession) -> AnalyticsSession:
        """Update existing analytics session."""
        query = """
            UPDATE public.analytics_sessions
            SET last_activity_at = %s,
                ended_at = %s,
                duration_seconds = %s,
                page_views = %s
            WHERE session_id = %s
            RETURNING session_id, session_token, user_id, organization_id,
                      ip_address_hash, user_agent, device_type, browser, os,
                      country, city, started_at, last_activity_at, ended_at,
                      duration_seconds, page_views
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    session.last_activity_at,
                    session.ended_at,
                    session.duration_seconds,
                    session.page_views,
                    session.session_id
                ))

                row = cur.fetchone()
                conn.commit()

                return AnalyticsSession(
                    session_id=row[0],
                    session_token=row[1],
                    user_id=row[2],
                    organization_id=row[3],
                    ip_address_hash=row[4],
                    user_agent=row[5],
                    device_type=row[6] or 'unknown',
                    browser=row[7],
                    os=row[8],
                    country=row[9],
                    city=row[10],
                    started_at=row[11],
                    last_activity_at=row[12],
                    ended_at=row[13],
                    duration_seconds=row[14],
                    page_views=row[15] or 0
                )

    # ============================================================================
    # ANALYTICS AGGREGATES
    # ============================================================================

    @staticmethod
    def find_aggregates(
        metric_type: str,
        start_date: date,
        end_date: date,
        dimension: Optional[str] = None,
        dimension_value: Optional[str] = None
    ) -> List[AnalyticsAggregate]:
        """Find analytics aggregates with filters."""
        query = """
            SELECT aggregate_id, metric_type, dimension, dimension_value,
                   date, hour, value, count, metadata, created_at
            FROM public.analytics_aggregates
            WHERE metric_type = %s
              AND date BETWEEN %s AND %s
        """
        params = [metric_type, start_date, end_date]

        if dimension:
            query += " AND dimension = %s"
            params.append(dimension)

        if dimension_value:
            query += " AND dimension_value = %s"
            params.append(dimension_value)

        query += " ORDER BY date ASC, hour ASC"

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

                return [
                    AnalyticsAggregate(
                        aggregate_id=row[0],
                        metric_type=row[1],
                        dimension=row[2],
                        dimension_value=row[3],
                        date=row[4],
                        hour=row[5],
                        value=row[6],
                        count=row[7] or 1,
                        metadata=row[8],
                        created_at=row[9]
                    )
                    for row in rows
                ]

    @staticmethod
    def create_aggregate(aggregate: AnalyticsAggregate) -> AnalyticsAggregate:
        """Create new analytics aggregate."""
        query = """
            INSERT INTO public.analytics_aggregates
            (metric_type, dimension, dimension_value, date, hour,
             value, count, metadata, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING aggregate_id, metric_type, dimension, dimension_value,
                      date, hour, value, count, metadata, created_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    aggregate.metric_type,
                    aggregate.dimension,
                    aggregate.dimension_value,
                    aggregate.date,
                    aggregate.hour,
                    aggregate.value,
                    aggregate.count,
                    json.dumps(aggregate.metadata) if aggregate.metadata else None,
                    aggregate.created_at or datetime.utcnow()
                ))

                row = cur.fetchone()
                conn.commit()

                return AnalyticsAggregate(
                    aggregate_id=row[0],
                    metric_type=row[1],
                    dimension=row[2],
                    dimension_value=row[3],
                    date=row[4],
                    hour=row[5],
                    value=row[6],
                    count=row[7] or 1,
                    metadata=row[8],
                    created_at=row[9]
                )

    # ============================================================================
    # ANALYTICS EVENTS
    # ============================================================================

    @staticmethod
    def find_event_by_id(event_id: int) -> Optional[AnalyticsEvent]:
        """Find analytics event by ID."""
        query = """
            SELECT event_id, user_id, organization_id, session_id,
                   event_type, event_category, resource_type, resource_id,
                   payload, ip_address_hash, created_at
            FROM public.analytics_events
            WHERE event_id = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (event_id,))
                row = cur.fetchone()

                if not row:
                    return None

                return AnalyticsEvent(
                    event_id=row[0],
                    user_id=row[1],
                    organization_id=row[2],
                    session_id=row[3],
                    event_type=row[4],
                    event_category=row[5],
                    resource_type=row[6],
                    resource_id=row[7],
                    payload=row[8],
                    ip_address_hash=row[9],
                    created_at=row[10]
                )

    @staticmethod
    def find_events_by_user(
        user_id: str,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[AnalyticsEvent]:
        """Find analytics events for a user."""
        query = """
            SELECT event_id, user_id, organization_id, session_id,
                   event_type, event_category, resource_type, resource_id,
                   payload, ip_address_hash, created_at
            FROM public.analytics_events
            WHERE user_id = %s
        """
        params = [user_id]

        if event_type:
            query += " AND event_type = %s"
            params.append(event_type)

        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

                return [
                    AnalyticsEvent(
                        event_id=row[0],
                        user_id=row[1],
                        organization_id=row[2],
                        session_id=row[3],
                        event_type=row[4],
                        event_category=row[5],
                        resource_type=row[6],
                        resource_id=row[7],
                        payload=row[8],
                        ip_address_hash=row[9],
                        created_at=row[10]
                    )
                    for row in rows
                ]

    @staticmethod
    def create_event(event: AnalyticsEvent) -> AnalyticsEvent:
        """Create new analytics event."""
        query = """
            INSERT INTO public.analytics_events
            (user_id, organization_id, session_id, event_type, event_category,
             resource_type, resource_id, payload, ip_address_hash, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING event_id, user_id, organization_id, session_id,
                      event_type, event_category, resource_type, resource_id,
                      payload, ip_address_hash, created_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    event.user_id,
                    event.organization_id,
                    event.session_id,
                    event.event_type,
                    event.event_category,
                    event.resource_type,
                    event.resource_id,
                    json.dumps(event.payload) if event.payload else None,
                    event.ip_address_hash,
                    event.created_at or datetime.utcnow()
                ))

                row = cur.fetchone()
                conn.commit()

                return AnalyticsEvent(
                    event_id=row[0],
                    user_id=row[1],
                    organization_id=row[2],
                    session_id=row[3],
                    event_type=row[4],
                    event_category=row[5],
                    resource_type=row[6],
                    resource_id=row[7],
                    payload=row[8],
                    ip_address_hash=row[9],
                    created_at=row[10]
                )
