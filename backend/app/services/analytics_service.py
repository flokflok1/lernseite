"""
LernsystemX Analytics Service

Business logic for analytics event tracking and statistics:
- Track analytics events with validation
- Get user statistics
- Get organisation statistics
- Permission checks for analytics access

Pure psycopg3 - No ORM
ISO 9001:2015 compliant - Service layer
"""

from typing import Dict, Optional, List
from datetime import datetime

from app.repositories.analytics_repository import AnalyticsRepository
from app.models.analytics import (
    AnalyticsEventBase,
    AnalyticsEventResponse,
    AnalyticsUserStats,
    AnalyticsOrgStats,
    EventType,
    ResourceType
)
from app.services.cache_service import CacheService
from flask import current_app

# Import monitoring (if available)
try:
    from app.monitoring import record_analytics_event
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False


class AnalyticsService:
    """
    Analytics service layer

    Implements business logic for analytics operations
    """

    # Roles that can view detailed analytics
    ANALYTICS_VIEWER_ROLES = [
        'premium', 'creator', 'teacher',
        'school_admin', 'company_admin',
        'admin', 'superadmin'
    ]

    # Roles that can view organisation-wide analytics
    ORG_ANALYTICS_ROLES = [
        'teacher', 'school_admin', 'company_admin',
        'admin', 'superadmin'
    ]

    @classmethod
    def track_event(
        cls,
        user: Dict,
        event_type: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[any] = None,  # Can be int or UUID string
        payload: Optional[Dict] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> AnalyticsEventResponse:
        """
        Track analytics event

        Args:
            user: User dict from JWT (contains user_id, role, organisation_id)
            event_type: Type of event
            resource_type: Optional resource type
            resource_id: Optional resource ID
            payload: Optional event payload
            session_id: Optional session ID
            ip_address: Optional IP address (will be hashed)

        Returns:
            AnalyticsEventResponse: Created event

        Raises:
            ValueError: If event_type or resource_type invalid

        Example:
            >>> user = {'user_id': 123, 'role': 'premium', 'organisation_id': 5}
            >>> event = AnalyticsService.track_event(
            ...     user=user,
            ...     event_type='course_view',
            ...     resource_type='course',
            ...     resource_id=42,
            ...     payload={'duration_seconds': 120}
            ... )
        """
        user_id = user['user_id']
        organisation_id = user.get('organisation_id')

        # Validate event type
        try:
            EventType(event_type)
        except ValueError:
            raise ValueError(f"Invalid event_type: {event_type}")

        # Validate resource type if provided
        if resource_type:
            try:
                ResourceType(resource_type)
            except ValueError:
                raise ValueError(f"Invalid resource_type: {resource_type}")

        # Insert event
        db_event = AnalyticsRepository.insert_event(
            user_id=user_id,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            payload=payload,
            session_id=session_id,
            ip_address=ip_address,
            organisation_id=organisation_id
        )

        # Record analytics event metric
        if MONITORING_AVAILABLE:
            user_type = user.get('role', 'unknown')
            record_analytics_event(event_type=event_type, user_type=user_type)

        # Convert to response model (ensure UUIDs are converted to strings)
        return AnalyticsEventResponse(
            event_id=db_event['event_id'],
            user_id=str(db_event['user_id']) if db_event.get('user_id') else None,
            organisation_id=str(db_event['organisation_id']) if db_event.get('organisation_id') else None,
            event_type=db_event['event_type'],
            resource_type=db_event.get('resource_type'),
            resource_id=str(db_event['resource_id']) if db_event.get('resource_id') else None,
            payload=db_event.get('payload', {}),
            session_id=db_event.get('session_id'),
            ip_address_hash=db_event.get('ip_address_hash'),
            created_at=db_event['created_at'].isoformat() if db_event.get('created_at') else None
        )

    @classmethod
    def get_user_statistics(cls, user: Dict) -> AnalyticsUserStats:
        """
        Get statistics for user

        Args:
            user: User dict from JWT

        Returns:
            AnalyticsUserStats: User statistics

        Example:
            >>> user = {'user_id': 123, 'role': 'premium'}
            >>> stats = AnalyticsService.get_user_statistics(user)
        """
        user_id = user['user_id']

        # Get total events
        total_events = AnalyticsRepository.get_user_total_events(user_id)

        # Get event counts by type
        event_counts_raw = AnalyticsRepository.count_events_by_type(user_id)
        event_counts_by_type = {row['event_type']: row['count'] for row in event_counts_raw}

        # Get recent events
        recent_events_raw = AnalyticsRepository.get_events_by_user(user_id, limit=10)
        recent_events = [
            AnalyticsEventResponse(
                event_id=event['event_id'],
                user_id=str(event['user_id']) if event.get('user_id') else None,
                organisation_id=str(event['organisation_id']) if event.get('organisation_id') else None,
                event_type=event['event_type'],
                resource_type=event.get('resource_type'),
                resource_id=str(event['resource_id']) if event.get('resource_id') else None,
                payload=event.get('payload', {}),
                session_id=event.get('session_id'),
                ip_address_hash=event.get('ip_address_hash'),
                created_at=event['created_at'].isoformat() if event.get('created_at') else None
            )
            for event in recent_events_raw
        ]

        # Get first and last event timestamps
        timestamps = AnalyticsRepository.get_user_event_timestamps(user_id)
        first_event_at = timestamps['first_event_at'].isoformat() if timestamps.get('first_event_at') else None
        last_event_at = timestamps['last_event_at'].isoformat() if timestamps.get('last_event_at') else None

        # Course-specific stats
        courses_viewed = event_counts_by_type.get('course_view', 0)
        courses_enrolled = event_counts_by_type.get('course_enroll', 0)
        modules_completed = event_counts_by_type.get('module_complete', 0)
        lessons_completed = event_counts_by_type.get('lesson_complete', 0)

        return AnalyticsUserStats(
            user_id=str(user_id) if user_id else None,
            total_events=total_events,
            event_counts_by_type=event_counts_by_type,
            recent_events=recent_events,
            first_event_at=first_event_at,
            last_event_at=last_event_at,
            courses_viewed=courses_viewed,
            courses_enrolled=courses_enrolled,
            modules_completed=modules_completed,
            lessons_completed=lessons_completed
        )

    @classmethod
    def get_organisation_statistics(cls, user: Dict, use_cache: bool = True) -> AnalyticsOrgStats:
        """
        Get statistics for organisation

        Requires user to be org admin, teacher, or system admin

        Args:
            user: User dict from JWT
            use_cache: Use cache with short TTL (default: True)

        Returns:
            AnalyticsOrgStats: Organisation statistics

        Raises:
            PermissionError: If user doesn't have org analytics access
            ValueError: If user not in organisation

        Example:
            >>> user = {'user_id': 123, 'role': 'school_admin', 'organisation_id': 5}
            >>> stats = AnalyticsService.get_organisation_statistics(user)
        """
        # Permission check
        if not cls.can_view_org_analytics(user):
            raise PermissionError(
                f"Role '{user.get('role')}' cannot view organisation analytics. "
                f"Requires: Teacher, School Admin, Company Admin, or Admin."
            )

        organisation_id = user.get('organisation_id')
        if not organisation_id:
            raise ValueError("User not in organisation")

        # Try cache first (short TTL for analytics - 1 minute)
        if use_cache:
            cache_key = CacheService.make_key('ANALYTICS', 'org', str(organisation_id), 'stats')
            ttl = current_app.config.get('CACHE_ANALYTICS_TTL', 60)

            def load_stats():
                return cls._compute_organisation_statistics(organisation_id)

            return CacheService.cache_get_or_set(cache_key, ttl, load_stats)

        # Bypass cache
        return cls._compute_organisation_statistics(organisation_id)

    @classmethod
    def _compute_organisation_statistics(cls, organisation_id: int) -> AnalyticsOrgStats:
        """
        Internal method to compute organisation statistics

        Args:
            organisation_id: Organisation ID

        Returns:
            AnalyticsOrgStats: Computed statistics
        """

        # Get total events
        total_events = AnalyticsRepository.get_org_total_events(organisation_id)

        # Get event counts by type
        event_counts_raw = AnalyticsRepository.count_events_by_type_org(organisation_id)
        event_counts_by_type = {row['event_type']: row['count'] for row in event_counts_raw}

        # Get first and last event timestamps
        timestamps = AnalyticsRepository.get_org_event_timestamps(organisation_id)
        first_event_at = timestamps['first_event_at'].isoformat() if timestamps.get('first_event_at') else None
        last_event_at = timestamps['last_event_at'].isoformat() if timestamps.get('last_event_at') else None

        # Get active users (last 30 days)
        active_users_30d = AnalyticsRepository.get_active_users_in_org(organisation_id, days=30)

        # Get top courses
        top_courses_raw = AnalyticsRepository.get_resource_event_counts(
            'course',
            organisation_id=organisation_id,
            limit=10
        )
        top_courses = [
            {'course_id': row['resource_id'], 'event_count': row['count']}
            for row in top_courses_raw
        ]

        # Organisation-specific stats
        total_course_enrollments = event_counts_by_type.get('course_enroll', 0)
        total_modules_completed = event_counts_by_type.get('module_complete', 0)
        total_exams_completed = event_counts_by_type.get('exam_complete', 0)

        # Calculate average completion rate
        # (modules completed / modules started * 100)
        modules_started = event_counts_by_type.get('module_start', 0)
        avg_completion_rate = 0.0
        if modules_started > 0:
            avg_completion_rate = (total_modules_completed / modules_started) * 100

        return AnalyticsOrgStats(
            organisation_id=organisation_id,
            total_events=total_events,
            total_users=0,  # TODO: Get from organisation_users table
            active_users_30d=active_users_30d,
            event_counts_by_type=event_counts_by_type,
            top_courses=top_courses,
            first_event_at=first_event_at,
            last_event_at=last_event_at,
            total_course_enrollments=total_course_enrollments,
            total_modules_completed=total_modules_completed,
            total_exams_completed=total_exams_completed,
            avg_completion_rate=round(avg_completion_rate, 2)
        )

    @classmethod
    def can_view_analytics(cls, user: Dict) -> bool:
        """
        Check if user can view detailed analytics

        Args:
            user: User dict with role

        Returns:
            bool: True if user can view analytics

        Example:
            >>> user = {'role': 'premium'}
            >>> AnalyticsService.can_view_analytics(user)
            True
            >>> user = {'role': 'user'}
            >>> AnalyticsService.can_view_analytics(user)
            False
        """
        role = user.get('role', 'user')
        return role in cls.ANALYTICS_VIEWER_ROLES

    @classmethod
    def can_view_org_analytics(cls, user: Dict) -> bool:
        """
        Check if user can view organisation-wide analytics

        Args:
            user: User dict with role

        Returns:
            bool: True if user can view org analytics

        Example:
            >>> user = {'role': 'school_admin'}
            >>> AnalyticsService.can_view_org_analytics(user)
            True
        """
        role = user.get('role', 'user')
        return role in cls.ORG_ANALYTICS_ROLES

    @classmethod
    def delete_user_data(cls, user_id: int) -> int:
        """
        Delete all analytics data for user (GDPR compliance)

        Args:
            user_id: User ID

        Returns:
            int: Number of events deleted

        Example:
            >>> deleted = AnalyticsService.delete_user_data(123)
        """
        return AnalyticsRepository.delete_user_events(user_id)

    @classmethod
    def get_events_by_resource(
        cls,
        resource_type: str,
        resource_id: int,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get all events for specific resource

        Args:
            resource_type: Resource type (course, module, etc.)
            resource_id: Resource ID
            limit: Maximum events to return

        Returns:
            List of event dicts

        Example:
            >>> events = AnalyticsService.get_events_by_resource('course', 42)
        """
        # This would require a new repository method
        # For now, return empty list
        # TODO: Implement in future phase
        return []
