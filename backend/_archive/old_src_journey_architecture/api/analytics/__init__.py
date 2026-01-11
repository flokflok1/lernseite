"""
Analytics Domain (DDD + Journey-Based Architecture)

Analytics and Feedback system with DDD layers and journey-based API routes.
ALL data loaded dynamically from database - NO hardcoded values.

Architecture:
- domain/ - Domain entities (7 entities for 7 tables)
- application/ - Business logic services
- infrastructure/ - Database repositories (2 parts)
- journeys/ - Journey-based API routes (admin)

7 Analytics Tables:
1. analytics_sessions - User session tracking with device info
2. analytics_aggregates - Pre-aggregated metrics for dashboards
3. analytics_events - Granular event tracking
4. user_feedback - User feedback with AI processing
5. feedback_summary_batches - Periodic AI summaries
6. feedback_attachments - File attachments (screenshots)
7. feedback_notes - Internal team notes

Usage:
    from src.api.analytics import AnalyticsService, admin_analytics_bp

Exports:
- AnalyticsSession - Domain entity for session
- AnalyticsAggregate - Domain entity for aggregate
- AnalyticsEvent - Domain entity for event
- UserFeedback - Domain entity for feedback
- FeedbackSummaryBatch - Domain entity for summary batch
- FeedbackAttachment - Domain entity for attachment
- FeedbackNote - Domain entity for note
- AnalyticsService - Business logic
- AnalyticsRepository - Database access (part 1)
- AnalyticsRepositoryPart2 - Database access (part 2)
- admin_analytics_bp - Admin journey routes
"""

from src.api.analytics.core.domain.entities.analytics_session import AnalyticsSession
from src.api.analytics.core.domain.entities.analytics_aggregate import AnalyticsAggregate
from src.api.analytics.core.domain.entities.analytics_event import AnalyticsEvent
from src.api.analytics.core.domain.entities.user_feedback import UserFeedback
from src.api.analytics.core.domain.entities.feedback_summary_batch import FeedbackSummaryBatch
from src.api.analytics.core.domain.entities.feedback_attachment import FeedbackAttachment
from src.api.analytics.core.domain.entities.feedback_note import FeedbackNote
from src.api.analytics.core.application.services.analytics_service import AnalyticsService
from src.api.analytics.core.infrastructure.repositories.analytics_repository import AnalyticsRepository
from src.api.analytics.core.infrastructure.repositories.analytics_repository_part2 import AnalyticsRepositoryPart2
from src.api.analytics.core.journeys.admin.api.routes.analytics import admin_analytics_bp

__all__ = [
    # Domain Entities
    'AnalyticsSession',
    'AnalyticsAggregate',
    'AnalyticsEvent',
    'UserFeedback',
    'FeedbackSummaryBatch',
    'FeedbackAttachment',
    'FeedbackNote',

    # Application
    'AnalyticsService',

    # Infrastructure
    'AnalyticsRepository',
    'AnalyticsRepositoryPart2',

    # Journeys
    'admin_analytics_bp',
]
