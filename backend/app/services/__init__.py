"""
LernsystemX Services Package

Service layer for business logic and external integrations:
- AI Adapter: Multi-provider AI integration
- Billing Service: Token and subscription management
- Email Service: Email sending and templating
- File Service: File upload and processing
- Analytics Service: Usage analytics and reporting
- Course Publishing Service: Publishing workflow state machine
- Moderation Service: Course moderation and AI analysis workflow

ISO 9001:2015 compliant - Service layer architecture
"""

from app.services.ai_adapter import AIAdapter
from app.services.billing_service import BillingService
from app.services.moderation_service import ModerationService
from app.services.content_translation_service import ContentTranslationService
from app.services.content_translation_service_part2 import ContentTranslationJobProcessor

# NOTE: CoursePublishingService intentionally NOT imported here to avoid circular dependency:
# repositories.courses -> cache_service -> services.__init__ -> course_publishing_service -> repositories.courses
# Import CoursePublishingService directly where needed instead

__all__ = [
    'AIAdapter',
    'BillingService',
    'ModerationService',
    'ContentTranslationService',
    'ContentTranslationJobProcessor'
    # CoursePublishingService removed - import directly where needed
]
