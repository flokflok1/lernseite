"""
Feedback Factory - DDD Factory Pattern for feedback instance creation.

Implements Domain-Driven Design (DDD) Factory Pattern for creating
feedback instances with validation and business rules.
"""

from typing import Optional, Dict, Any
from datetime import datetime


class FeedbackFactory:
    """
    Factory for creating Feedback instances.
    Implements Domain-Driven Design (DDD) Factory Pattern.
    """

    # Valid feedback types
    VALID_TYPES = ['question', 'bug', 'suggestion', 'praise', 'other']

    # Valid statuses
    VALID_STATUSES = ['new', 'read', 'in_progress', 'resolved', 'closed']

    # Valid priorities
    VALID_PRIORITIES = ['low', 'normal', 'high', 'urgent']

    @staticmethod
    def create_feedback_data(
        feedback_type: str,
        message: str,
        title: Optional[str] = None,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        is_anonymous: bool = False,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create feedback data dictionary for submission.

        Args:
            feedback_type: Type of feedback (question, bug, suggestion, praise, other)
            message: Feedback message
            title: Optional title
            user_id: Optional user ID (if authenticated)
            email: Optional email (for anonymous feedback)
            is_anonymous: Whether feedback is anonymous
            context: Optional context data (course_id, lesson_id, page, url, etc.)

        Returns:
            Dictionary with validated feedback data

        Raises:
            ValueError: If validation fails
        """
        # Validate type
        if feedback_type not in FeedbackFactory.VALID_TYPES:
            raise ValueError(
                f"Invalid feedback type '{feedback_type}'. "
                f"Must be one of: {', '.join(FeedbackFactory.VALID_TYPES)}"
            )

        # Validate message
        if not message or len(message.strip()) < 10:
            raise ValueError("Message must be at least 10 characters long")

        if len(message) > 10000:
            raise ValueError("Message is too long (max 10,000 characters)")

        # If anonymous, clear user info
        if is_anonymous:
            user_id = None
            email = None

        # Extract context
        ctx = context or {}

        return {
            'feedback_type': feedback_type,
            'message': message.strip(),
            'title': title.strip() if title else None,
            'user_id': user_id,
            'email': email,
            'is_anonymous': is_anonymous,
            'context_course_id': ctx.get('course_id'),
            'context_lesson_id': ctx.get('lesson_id'),
            'context_page': ctx.get('page_context'),
            'context_url': ctx.get('url'),
            'context_user_agent': ctx.get('user_agent'),
            'context_data': ctx
        }

    @staticmethod
    def create_anonymous_feedback(
        feedback_type: str,
        message: str,
        title: Optional[str] = None,
        email: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create anonymous feedback data.

        Convenience method for creating anonymous feedback.

        Args:
            feedback_type: Type of feedback
            message: Feedback message
            title: Optional title
            email: Optional contact email
            context: Optional context data

        Returns:
            Dictionary with anonymous feedback data
        """
        return FeedbackFactory.create_feedback_data(
            feedback_type=feedback_type,
            message=message,
            title=title,
            user_id=None,
            email=email,
            is_anonymous=True,
            context=context
        )

    @staticmethod
    def create_note_data(
        feedback_id: str,
        author_id: str,
        note_text: str,
        is_internal: bool = True
    ) -> Dict[str, Any]:
        """
        Create note data for feedback.

        Args:
            feedback_id: Feedback ID
            author_id: Author user ID
            note_text: Note text
            is_internal: Whether note is internal (not visible to user)

        Returns:
            Dictionary with validated note data

        Raises:
            ValueError: If validation fails
        """
        if not note_text or len(note_text.strip()) < 3:
            raise ValueError("Note must be at least 3 characters long")

        return {
            'feedback_id': feedback_id,
            'author_id': author_id,
            'note_text': note_text.strip(),
            'is_internal': is_internal
        }

    @staticmethod
    def validate_status(status: str) -> bool:
        """
        Validate feedback status.

        Args:
            status: Status to validate

        Returns:
            True if valid

        Raises:
            ValueError: If status is invalid
        """
        if status not in FeedbackFactory.VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'. "
                f"Must be one of: {', '.join(FeedbackFactory.VALID_STATUSES)}"
            )
        return True

    @staticmethod
    def validate_priority(priority: str) -> bool:
        """
        Validate feedback priority.

        Args:
            priority: Priority to validate

        Returns:
            True if valid

        Raises:
            ValueError: If priority is invalid
        """
        if priority not in FeedbackFactory.VALID_PRIORITIES:
            raise ValueError(
                f"Invalid priority '{priority}'. "
                f"Must be one of: {', '.join(FeedbackFactory.VALID_PRIORITIES)}"
            )
        return True

    @staticmethod
    def create_batch_summary_data(
        period_start: datetime,
        period_end: datetime,
        total: int,
        questions: int = 0,
        bugs: int = 0,
        suggestions: int = 0,
        praise: int = 0,
        other: int = 0
    ) -> Dict[str, Any]:
        """
        Create summary batch data.

        Args:
            period_start: Start of period
            period_end: End of period
            total: Total feedback count
            questions: Questions count
            bugs: Bugs count
            suggestions: Suggestions count
            praise: Praise count
            other: Other count

        Returns:
            Dictionary with summary batch data
        """
        return {
            'period_start': period_start,
            'period_end': period_end,
            'total': total,
            'questions': questions,
            'bugs': bugs,
            'suggestions': suggestions,
            'praise': praise,
            'other': other
        }
