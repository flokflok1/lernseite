"""
Feedback Core Package

Core utilities and factory for feedback domain.

Example usage:
    >>> from app.api.shared.feedback.core.factory import FeedbackFactory
    >>> feedback_data = FeedbackFactory.create_feedback_data(
    ...     feedback_type='bug',
    ...     message='Something is broken',
    ...     user_id='user-123'
    ... )
"""

from app.api.shared.feedback.core.factory import FeedbackFactory

__all__ = ['FeedbackFactory']
