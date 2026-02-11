"""
Core Analytics Events Repository

Handles fundamental analytics event operations:
- Insert analytics events
- Retrieve events by user and organisation
- Delete events (GDPR compliance)
- Parse JSONB payloads

Pure psycopg3 - No ORM
ISO 9001:2015 compliant - Repository pattern
"""

from typing import Optional, Dict, List
from datetime import datetime
import json
import hashlib

from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query


class CoreEventsRepository(BaseRepository):
    """
    Core analytics events repository

    Manages basic analytics event tracking operations.
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
            >>> event = CoreEventsRepository.insert_event(
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
            >>> events = CoreEventsRepository.get_events_by_user(123, limit=10)
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
            >>> events = CoreEventsRepository.get_events_by_organisation(5)
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
    def delete_user_events(cls, user_id: int) -> int:
        """
        Delete all events for user (for GDPR compliance)

        Args:
            user_id: User ID

        Returns:
            int: Number of events deleted

        Example:
            >>> deleted = CoreEventsRepository.delete_user_events(123)
        """
        query = "DELETE FROM analytics_events WHERE user_id = %s"
        return execute_query(query, (user_id,))
