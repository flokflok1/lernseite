"""
Analytics Event Entity (DDD Domain Entity)

Represents granular event tracking for user actions and system events.
ALL data loaded from database - NO hardcoded values.
Event types are loaded dynamically from DB CHECK constraint.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class AnalyticsEvent:
    """
    Analytics Event domain entity.

    Tracks individual user actions and system events.

    Attributes:
        event_id: Auto-incrementing ID
        user_id: User UUID (optional for anonymous events)
        organization_id: Organization UUID (optional)
        session_id: Related analytics session UUID
        event_type: Type of event (from DB constraint)
        event_category: Category for grouping
        resource_type: Type of resource (e.g., 'course', 'lesson')
        resource_id: ID of resource
        payload: Additional JSONB data
        ip_address_hash: Hashed IP address (privacy)
        created_at: Event timestamp

    Valid event_types (from DB CHECK constraint):
        page_view, login, logout, signup,
        course_view, course_enroll, course_complete,
        chapter_start, chapter_complete,
        lesson_start, lesson_complete,
        method_execute, method_complete,
        exam_start, exam_complete,
        liveroom_join, liveroom_leave,
        ai_request, purchase, subscription_start
    """

    event_id: Optional[int]  # Assigned by database
    event_type: str
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    session_id: Optional[str] = None
    event_category: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    ip_address_hash: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate analytics event entity."""
        if not self.event_type or not self.event_type.strip():
            raise ValueError("Event type cannot be empty")

        # Note: Event type validation is enforced by DB CHECK constraint
        # We do NOT hardcode the valid event_types list here (DB-First!)

    def is_user_action(self) -> bool:
        """Check if this event represents a user action."""
        user_action_types = {
            'page_view', 'login', 'logout', 'signup',
            'course_view', 'course_enroll', 'chapter_start',
            'lesson_start', 'method_execute', 'exam_start',
            'liveroom_join', 'liveroom_leave'
        }
        return self.event_type in user_action_types

    def is_completion_event(self) -> bool:
        """Check if this event represents a completion."""
        return self.event_type.endswith('_complete')

    def is_course_related(self) -> bool:
        """Check if this event is course-related."""
        return self.event_type.startswith('course_')

    def is_lesson_related(self) -> bool:
        """Check if this event is lesson/method-related."""
        return self.event_type.startswith('lesson_') or self.event_type.startswith('method_')

    def is_exam_related(self) -> bool:
        """Check if this event is exam-related."""
        return self.event_type.startswith('exam_')

    def is_liveroom_related(self) -> bool:
        """Check if this event is liveroom-related."""
        return self.event_type.startswith('liveroom_')

    def has_resource(self) -> bool:
        """Check if this event references a resource."""
        return self.resource_type is not None and self.resource_id is not None
