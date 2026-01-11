"""
Analytics Domain Entities (DDD)

ALL data loaded dynamically from database - NO hardcoded values.

Entities:
- AnalyticsSession - User session tracking
- AnalyticsAggregate - Pre-aggregated metrics
- AnalyticsEvent - Granular event tracking
- UserFeedback - User feedback with AI processing
- FeedbackSummaryBatch - Periodic AI summaries
- FeedbackAttachment - File attachments
- FeedbackNote - Internal team notes
"""

from src.api.analytics.core.domain.entities.analytics_session import AnalyticsSession
from src.api.analytics.core.domain.entities.analytics_aggregate import AnalyticsAggregate
from src.api.analytics.core.domain.entities.analytics_event import AnalyticsEvent
from src.api.analytics.core.domain.entities.user_feedback import UserFeedback
from src.api.analytics.core.domain.entities.feedback_summary_batch import FeedbackSummaryBatch
from src.api.analytics.core.domain.entities.feedback_attachment import FeedbackAttachment
from src.api.analytics.core.domain.entities.feedback_note import FeedbackNote

__all__ = [
    'AnalyticsSession',
    'AnalyticsAggregate',
    'AnalyticsEvent',
    'UserFeedback',
    'FeedbackSummaryBatch',
    'FeedbackAttachment',
    'FeedbackNote',
]
