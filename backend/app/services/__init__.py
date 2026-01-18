"""
LernsystemX Services Package

Service layer for business logic and external integrations:
- AI Services: Multi-provider AI integration (ai/adapter, ai/models, ai/prompts, ai/context)
- Authentication & Authorization: Auth and role management (system/auth)
- Audit & Compliance: Audit logging (system/audit)
- File Management: File context and operations (system/files)
- Learning Methods: Learning method utilities (lm/)
- Content Management: Content operations and translations (content/)
- Moderation: Course moderation and AI analysis (moderation/)
- Feature Flags: Enterprise feature management (feature_flags/)
- Internationalization: Legacy i18n services (i18n/legacy)
- Utilities: Analytics, billing, cache (root level)
- Course Publishing: Publishing workflow state machine (root - special handling)

ISO 9001:2015 compliant - Service layer architecture

BACKWARD COMPATIBILITY NOTES:
- All services previously at root level can still be imported from this package
- New imports from organized subpackages are recommended for new code
- Example: 'from app.services import AIAdapter' still works (uses ai_adapter bridge)
"""

# ============================================
# ROOT-LEVEL UTILITY SERVICES (Cross-cutting concerns)
# ============================================
from app.services.ai_adapter import AIAdapter
from app.services.analytics_service import AnalyticsService
from app.services.billing_service import BillingService
from app.services.cache_service import CacheService
from app.services.feedback_service import FeedbackService
from app.services.feature_service import FeatureService

# ============================================
# ORGANIZED DOMAIN SERVICES
# ============================================

# Authentication & Authorization (system/auth)
from app.services.system.auth import (
    PermissionService,
    RolesService,
    RoleStudioService,
)

# Audit & Compliance (system/audit)
from app.services.system.audit import AuditService

# File Management (system/files)
from app.services.system.files import FileContextService

# Learning Methods (lm/)
from app.services.lm import (
    LMModelResolver,
    LMSlotResolver,
    LMSuggestionService,
    MathToolkitService,
)

# Content Services (content/)
from app.services.content import (
    ContentTranslationService,
    ContentTranslationJobProcessor,
)

# Moderation (moderation/)
from app.services.moderation import ModerationService

# Feature Flags (feature_flags/)
from app.services.feature_flags import (
    FeatureConfigurationService,
    FeatureConfigurationCacheService,
    FeatureConfigurationRolloutService,
    FeatureConfigurationAbTestService,
)

# i18n Legacy (i18n/legacy)
from app.services.i18n.legacy import (
    I18nService,
    I18nImportService,
    I18nSyncService,
    I18nSyncAnalyticsService,
    I18nSyncApplyService,
)

# AI Services (ai/ and subpackages)
from app.services.ai.models import (
    AIModelProfilesService,
    AIModelSyncService,
)
from app.services.ai.prompts import PromptResolver
from app.services.ai.context import ExamContextDetector

# ============================================
# CIRCULAR DEPENDENCY HANDLING
# ============================================
# NOTE: CoursePublishingService intentionally NOT imported here to avoid circular dependency:
# repositories.courses -> cache_service -> services.__init__ -> course_publishing_service -> repositories.courses
# Import CoursePublishingService directly where needed instead

# ============================================
# EXPORTS FOR BACKWARD COMPATIBILITY
# ============================================
__all__ = [
    # Utility Services (root-level, cross-cutting)
    'AIAdapter',
    'AnalyticsService',
    'BillingService',
    'CacheService',
    'FeedbackService',
    'FeatureService',

    # Auth & Authorization
    'PermissionService',
    'RolesService',
    'RoleStudioService',

    # Audit
    'AuditService',

    # File Management
    'FileContextService',

    # Learning Methods
    'LMModelResolver',
    'LMSlotResolver',
    'LMSuggestionService',
    'MathToolkitService',

    # Content
    'ContentTranslationService',
    'ContentTranslationJobProcessor',

    # Moderation
    'ModerationService',

    # Feature Flags
    'FeatureConfigurationService',
    'FeatureConfigurationCacheService',
    'FeatureConfigurationRolloutService',
    'FeatureConfigurationAbTestService',

    # i18n
    'I18nService',
    'I18nImportService',
    'I18nSyncService',
    'I18nSyncAnalyticsService',
    'I18nSyncApplyService',

    # AI
    'AIModelProfilesService',
    'AIModelSyncService',
    'PromptResolver',
    'ExamContextDetector',
]
