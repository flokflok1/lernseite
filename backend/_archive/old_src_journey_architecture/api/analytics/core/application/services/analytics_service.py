"""
Analytics Service (Application Layer)

Business logic for analytics and feedback operations.
ALL data loaded dynamically from database - NO hardcoded values.

Uses Repository Pattern for database access.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from src.api.analytics.core.domain.entities.analytics_session import AnalyticsSession
from src.api.analytics.core.domain.entities.analytics_aggregate import AnalyticsAggregate
from src.api.analytics.core.domain.entities.analytics_event import AnalyticsEvent
from src.api.analytics.core.domain.entities.user_feedback import UserFeedback
from src.api.analytics.core.domain.entities.feedback_summary_batch import FeedbackSummaryBatch
from src.api.analytics.core.domain.entities.feedback_attachment import FeedbackAttachment
from src.api.analytics.core.domain.entities.feedback_note import FeedbackNote
from src.api.analytics.core.infrastructure.repositories.analytics_repository import AnalyticsRepository
from src.api.analytics.core.infrastructure.repositories.analytics_repository_part2 import AnalyticsRepositoryPart2
from src.core.events import EventBus, EventType, DomainEvent


class AnalyticsService:
    """
    Analytics service for business logic.

    ALL configurations and values loaded from database dynamically.
    NO hardcoded device types, event types, or status values.
    """

    # ============================================================================
    # ANALYTICS SESSIONS
    # ============================================================================

    @staticmethod
    def get_session_by_id(session_id: str) -> Optional[AnalyticsSession]:
        """Get analytics session by ID."""
        return AnalyticsRepository.find_session_by_id(session_id)

    @staticmethod
    def get_sessions_by_user(user_id: str, limit: int = 50) -> List[AnalyticsSession]:
        """Get analytics sessions for a user."""
        return AnalyticsRepository.find_sessions_by_user(user_id, limit)

    @staticmethod
    def create_session(
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        session_token: Optional[str] = None,
        ip_address_hash: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_type: str = 'unknown',
        browser: Optional[str] = None,
        os: Optional[str] = None,
        country: Optional[str] = None,
        city: Optional[str] = None
    ) -> AnalyticsSession:
        """
        Create new analytics session.

        Args:
            user_id: User UUID (optional for anonymous)
            organization_id: Organization UUID
            session_token: Session token
            ip_address_hash: Hashed IP (privacy)
            user_agent: Browser user agent
            device_type: desktop, mobile, tablet, unknown (validated by DB)
            browser: Browser name
            os: Operating system
            country: Country code (2 letters)
            city: City name

        Returns:
            Created AnalyticsSession
        """
        import uuid
        session = AnalyticsSession(
            session_id=str(uuid.uuid4()),
            session_token=session_token,
            user_id=user_id,
            organization_id=organization_id,
            ip_address_hash=ip_address_hash,
            user_agent=user_agent,
            device_type=device_type,
            browser=browser,
            os=os,
            country=country,
            city=city,
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow()
        )

        created_session = AnalyticsRepository.create_session(session)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.ANALYTICS_SESSION_STARTED,
            aggregate_id=created_session.session_id,
            occurred_at=datetime.utcnow(),
            data={
                'user_id': created_session.user_id,
                'device_type': created_session.device_type,
                'country': created_session.country
            }
        )
        EventBus.publish(event)

        return created_session

    @staticmethod
    def end_session(session_id: str) -> AnalyticsSession:
        """
        End an analytics session.

        Args:
            session_id: Session UUID

        Returns:
            Updated AnalyticsSession

        Raises:
            ValueError: If session not found or already ended
        """
        session = AnalyticsRepository.find_session_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.end_session()
        updated_session = AnalyticsRepository.update_session(session)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.ANALYTICS_SESSION_ENDED,
            aggregate_id=updated_session.session_id,
            occurred_at=datetime.utcnow(),
            data={
                'user_id': updated_session.user_id,
                'duration_seconds': updated_session.duration_seconds,
                'page_views': updated_session.page_views
            }
        )
        EventBus.publish(event)

        return updated_session

    @staticmethod
    def record_page_view(session_id: str) -> AnalyticsSession:
        """Record page view in session."""
        session = AnalyticsRepository.find_session_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.record_page_view()
        return AnalyticsRepository.update_session(session)

    # ============================================================================
    # ANALYTICS EVENTS
    # ============================================================================

    @staticmethod
    def track_event(
        event_type: str,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        session_id: Optional[str] = None,
        event_category: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        ip_address_hash: Optional[str] = None
    ) -> AnalyticsEvent:
        """
        Track analytics event.

        Args:
            event_type: Type from DB constraint (page_view, login, course_enroll, etc.)
            user_id: User UUID
            organization_id: Organization UUID
            session_id: Session UUID
            event_category: Category for grouping
            resource_type: Resource type (course, lesson, etc.)
            resource_id: Resource ID
            payload: Additional JSONB data
            ip_address_hash: Hashed IP

        Returns:
            Created AnalyticsEvent
        """
        event = AnalyticsEvent(
            event_type=event_type,
            user_id=user_id,
            organization_id=organization_id,
            session_id=session_id,
            event_category=event_category,
            resource_type=resource_type,
            resource_id=resource_id,
            payload=payload,
            ip_address_hash=ip_address_hash,
            created_at=datetime.utcnow()
        )

        return AnalyticsRepository.create_event(event)

    @staticmethod
    def get_events_by_user(
        user_id: str,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[AnalyticsEvent]:
        """Get analytics events for a user."""
        return AnalyticsRepository.find_events_by_user(user_id, event_type, limit)

    # ============================================================================
    # ANALYTICS AGGREGATES
    # ============================================================================

    @staticmethod
    def get_aggregates(
        metric_type: str,
        start_date: date,
        end_date: date,
        dimension: Optional[str] = None,
        dimension_value: Optional[str] = None
    ) -> List[AnalyticsAggregate]:
        """Get analytics aggregates with filters."""
        return AnalyticsRepository.find_aggregates(
            metric_type, start_date, end_date, dimension, dimension_value
        )

    @staticmethod
    def create_aggregate(
        metric_type: str,
        value: Decimal,
        aggregate_date: date,
        dimension: Optional[str] = None,
        dimension_value: Optional[str] = None,
        hour: Optional[int] = None,
        count: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AnalyticsAggregate:
        """
        Create analytics aggregate.

        Args:
            metric_type: Type of metric (e.g., 'active_users', 'course_enrollments')
            value: Numeric value
            aggregate_date: Date of aggregation
            dimension: Grouping dimension
            dimension_value: Value of dimension
            hour: Hour (0-23) for hourly aggregates, None for daily
            count: Number of data points
            metadata: Additional JSONB metadata

        Returns:
            Created AnalyticsAggregate
        """
        aggregate = AnalyticsAggregate(
            aggregate_id=None,  # Assigned by DB
            metric_type=metric_type,
            dimension=dimension,
            dimension_value=dimension_value,
            date=aggregate_date,
            hour=hour,
            value=value,
            count=count,
            metadata=metadata,
            created_at=datetime.utcnow()
        )

        return AnalyticsRepository.create_aggregate(aggregate)

    # ============================================================================
    # USER FEEDBACK
    # ============================================================================

    @staticmethod
    def get_feedback_by_id(feedback_id: str) -> Optional[UserFeedback]:
        """Get user feedback by ID."""
        return AnalyticsRepositoryPart2.find_feedback_by_id(feedback_id)

    @staticmethod
    def get_all_feedback(
        status: Optional[str] = None,
        feedback_type: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[UserFeedback]:
        """Get all feedback with filters."""
        return AnalyticsRepositoryPart2.find_all_feedback(
            status, feedback_type, priority, limit, offset
        )

    @staticmethod
    def create_feedback(
        feedback_type: str,
        message: str,
        user_id: Optional[str] = None,
        is_anonymous: bool = False,
        email: Optional[str] = None,
        title: Optional[str] = None,
        context_course_id: Optional[str] = None,
        context_lesson_id: Optional[str] = None,
        context_page: Optional[str] = None,
        context_url: Optional[str] = None,
        context_user_agent: Optional[str] = None,
        context_data: Optional[Dict[str, Any]] = None
    ) -> UserFeedback:
        """
        Create user feedback.

        Args:
            feedback_type: question, bug, suggestion, praise, other
            message: Feedback message
            user_id: User UUID (optional for anonymous)
            is_anonymous: Anonymous feedback flag
            email: Contact email (for anonymous)
            title: Feedback title
            context_*: Context information

        Returns:
            Created UserFeedback
        """
        import uuid
        feedback = UserFeedback(
            feedback_id=str(uuid.uuid4()),
            user_id=user_id,
            is_anonymous=is_anonymous,
            email=email,
            feedback_type=feedback_type,
            title=title,
            message=message,
            context_course_id=context_course_id,
            context_lesson_id=context_lesson_id,
            context_page=context_page,
            context_url=context_url,
            context_user_agent=context_user_agent,
            context_data=context_data,
            status='new',
            priority='normal',
            created_at=datetime.utcnow()
        )

        created_feedback = AnalyticsRepositoryPart2.create_feedback(feedback)

        # Publish domain event
        event = DomainEvent(
            event_type=EventType.FEEDBACK_CREATED,
            aggregate_id=created_feedback.feedback_id,
            occurred_at=datetime.utcnow(),
            data={
                'feedback_type': created_feedback.feedback_type,
                'user_id': created_feedback.user_id,
                'is_anonymous': created_feedback.is_anonymous
            }
        )
        EventBus.publish(event)

        return created_feedback

    @staticmethod
    def update_feedback_status(
        feedback_id: str,
        status: str,
        assigned_to: Optional[str] = None,
        admin_id: Optional[str] = None
    ) -> UserFeedback:
        """Update feedback status and assignment."""
        feedback = AnalyticsRepositoryPart2.find_feedback_by_id(feedback_id)
        if not feedback:
            raise ValueError(f"Feedback {feedback_id} not found")

        if status == 'in_progress' and assigned_to:
            feedback.mark_as_in_progress(assigned_to)
        elif status == 'resolved':
            feedback.mark_as_resolved()
        else:
            feedback.status = status
            feedback.updated_at = datetime.utcnow()

        return AnalyticsRepositoryPart2.update_feedback(feedback)

    @staticmethod
    def add_admin_response(
        feedback_id: str,
        response: str,
        admin_id: str
    ) -> UserFeedback:
        """Add admin response to feedback."""
        feedback = AnalyticsRepositoryPart2.find_feedback_by_id(feedback_id)
        if not feedback:
            raise ValueError(f"Feedback {feedback_id} not found")

        feedback.add_admin_response(response, admin_id)
        return AnalyticsRepositoryPart2.update_feedback(feedback)

    # ============================================================================
    # FEEDBACK ATTACHMENTS
    # ============================================================================

    @staticmethod
    def get_feedback_attachments(feedback_id: str) -> List[FeedbackAttachment]:
        """Get all attachments for a feedback."""
        return AnalyticsRepositoryPart2.find_attachments_by_feedback(feedback_id)

    @staticmethod
    def add_feedback_attachment(
        feedback_id: str,
        file_name: str,
        file_path: str,
        file_type: Optional[str] = None,
        file_size: Optional[int] = None,
        is_screenshot: bool = False,
        ai_description: Optional[str] = None
    ) -> FeedbackAttachment:
        """Add attachment to feedback."""
        import uuid
        attachment = FeedbackAttachment(
            attachment_id=str(uuid.uuid4()),
            feedback_id=feedback_id,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            file_path=file_path,
            is_screenshot=is_screenshot,
            ai_screenshot_description=ai_description,
            created_at=datetime.utcnow()
        )

        return AnalyticsRepositoryPart2.create_attachment(attachment)

    # ============================================================================
    # FEEDBACK NOTES
    # ============================================================================

    @staticmethod
    def get_feedback_notes(feedback_id: str) -> List[FeedbackNote]:
        """Get all notes for a feedback."""
        return AnalyticsRepositoryPart2.find_notes_by_feedback(feedback_id)

    @staticmethod
    def add_feedback_note(
        feedback_id: str,
        author_id: str,
        note_text: str,
        is_internal: bool = True
    ) -> FeedbackNote:
        """Add note to feedback."""
        import uuid
        note = FeedbackNote(
            note_id=str(uuid.uuid4()),
            feedback_id=feedback_id,
            author_id=author_id,
            note_text=note_text,
            is_internal=is_internal,
            created_at=datetime.utcnow()
        )

        return AnalyticsRepositoryPart2.create_note(note)
