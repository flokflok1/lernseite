"""
User Feedback Entity (DDD Domain Entity)

Represents user feedback with AI-powered processing and admin responses.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class UserFeedback:
    """
    User Feedback domain entity.

    Tracks user feedback with AI summarization and admin workflow.

    Attributes:
        feedback_id: UUID
        user_id: User UUID (optional for anonymous feedback)
        is_anonymous: Whether feedback is anonymous
        email: Contact email (for anonymous feedback)
        feedback_type: Type (question, bug, suggestion, praise, other)
        title: Feedback title
        message: Feedback message
        context_course_id: Related course UUID
        context_lesson_id: Related lesson ID
        context_page: Page where feedback was given
        context_url: Full URL
        context_user_agent: Browser user agent
        context_data: Additional JSONB context
        status: Workflow status (new, read, in_progress, resolved, closed)
        priority: Priority (low, normal, high, urgent)
        assigned_to: Assigned admin user UUID
        ai_summary: AI-generated summary
        ai_category: AI-detected category
        ai_sentiment: AI-detected sentiment (positive, neutral, negative, mixed)
        ai_tags: AI-extracted tags
        ai_processed_at: When AI processing completed
        admin_response: Admin response text
        admin_responded_by: Admin who responded UUID
        admin_responded_at: When admin responded
        created_at: Feedback creation timestamp
        updated_at: Last update timestamp
        resolved_at: Resolution timestamp
    """

    feedback_id: str
    feedback_type: str
    message: str
    user_id: Optional[str] = None
    is_anonymous: bool = False
    email: Optional[str] = None
    title: Optional[str] = None
    context_course_id: Optional[str] = None
    context_lesson_id: Optional[str] = None
    context_page: Optional[str] = None
    context_url: Optional[str] = None
    context_user_agent: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None
    status: str = 'new'
    priority: str = 'normal'
    assigned_to: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_category: Optional[str] = None
    ai_sentiment: Optional[str] = None
    ai_tags: Optional[List[str]] = None
    ai_processed_at: Optional[datetime] = None
    admin_response: Optional[str] = None
    admin_responded_by: Optional[str] = None
    admin_responded_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate user feedback entity."""
        if not self.feedback_type or self.feedback_type not in ('question', 'bug', 'suggestion', 'praise', 'other'):
            raise ValueError("Invalid feedback type")

        if not self.message or not self.message.strip():
            raise ValueError("Message cannot be empty")

        if self.status not in ('new', 'read', 'in_progress', 'resolved', 'closed'):
            raise ValueError("Invalid status")

        if self.priority not in ('low', 'normal', 'high', 'urgent'):
            raise ValueError("Invalid priority")

        if self.ai_sentiment and self.ai_sentiment not in ('positive', 'neutral', 'negative', 'mixed'):
            raise ValueError("Invalid AI sentiment")

        if self.is_anonymous and not self.email:
            raise ValueError("Anonymous feedback requires email address")

    def is_resolved(self) -> bool:
        """Check if feedback is resolved."""
        return self.status in ('resolved', 'closed')

    def is_open(self) -> bool:
        """Check if feedback is still open."""
        return self.status in ('new', 'read', 'in_progress')

    def is_urgent(self) -> bool:
        """Check if feedback is urgent."""
        return self.priority == 'urgent'

    def is_high_priority(self) -> bool:
        """Check if feedback is high priority or urgent."""
        return self.priority in ('high', 'urgent')

    def has_ai_processing(self) -> bool:
        """Check if AI processing has been completed."""
        return self.ai_processed_at is not None

    def has_admin_response(self) -> bool:
        """Check if admin has responded."""
        return self.admin_response is not None

    def has_course_context(self) -> bool:
        """Check if feedback has course context."""
        return self.context_course_id is not None

    def mark_as_read(self) -> None:
        """Mark feedback as read."""
        if self.status == 'new':
            self.status = 'read'
            self.updated_at = datetime.utcnow()

    def mark_as_in_progress(self, assigned_to: str) -> None:
        """Mark feedback as in progress and assign."""
        self.status = 'in_progress'
        self.assigned_to = assigned_to
        self.updated_at = datetime.utcnow()

    def mark_as_resolved(self) -> None:
        """
        Mark feedback as resolved.

        Raises:
            ValueError: If feedback is already resolved
        """
        if self.is_resolved():
            raise ValueError("Feedback already resolved")

        self.status = 'resolved'
        self.resolved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def add_admin_response(self, response: str, admin_id: str) -> None:
        """Add admin response to feedback."""
        self.admin_response = response
        self.admin_responded_by = admin_id
        self.admin_responded_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def process_with_ai(self, summary: str, category: str, sentiment: str, tags: List[str]) -> None:
        """Add AI processing results."""
        self.ai_summary = summary
        self.ai_category = category
        self.ai_sentiment = sentiment
        self.ai_tags = tags
        self.ai_processed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
