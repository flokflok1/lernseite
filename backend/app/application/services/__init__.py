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
- Example: 'from app.application.services import AIAdapter' still works (uses ai_adapter bridge)
"""

# ============================================
# ROOT-LEVEL UTILITY SERVICES (Cross-cutting concerns)
# ============================================
from app.application.services.ai.adapter import AIAdapter
from app.application.services.analytics.service import AnalyticsService
from app.application.services.system.billing.service import BillingService
from app.infrastructure.cache.service import CacheService
from app.application.services.dashboard.feedback.service import FeedbackService
from app.application.services.system.features.service import FeatureService

# ============================================
# ORGANIZED DOMAIN SERVICES
# ============================================

# Authentication & Authorization (system/auth)
from app.application.services.system.auth import (
    PermissionService,
)

# Group Management (system/group_management) - RBAC 3.0 group-based authorization
from app.application.services.system.group_management import GroupManagementService

# PHASE B: RolesService removed (replaced with Groups system)

# Audit & Compliance (system/audit)
from app.application.services.system.audit import AuditService

# File Management (system/files)
from app.application.services.system.files import FileContextService

# Learning Methods (lm/)
from app.application.services.lm import (
    LMModelResolver,
    LMSlotResolver,
    LMSuggestionService,
    MathToolkitService,
)

# Content Services (content/)
from app.application.services.content import (
    ContentTranslationService,
    ContentTranslationJobProcessor,
)

# Moderation (moderation/)
from app.application.services.moderation import ModerationService

# Feature Flags (feature_flags/)
from app.application.services.feature_flags import (
    FeatureConfigurationService,
    FeatureConfigurationCacheService,
    FeatureConfigurationRolloutService,
    FeatureConfigurationAbTestService,
)

# i18n Legacy (i18n/legacy)
from app.application.services.i18n.legacy import (
    I18nService,
    I18nImportService,
    I18nSyncService,
    I18nSyncAnalyticsService,
    I18nSyncApplyService,
)

# AI Services (ai/ and subpackages)
from app.application.services.ai.models import (
    AIModelProfilesService,
    AIModelSyncService,
)
from app.application.services.ai.prompts import PromptResolver
from app.application.services.ai.context import ExamContextDetector

# ============================================
# PUBLISHING SERVICE (Handled separately)
# ============================================
# NOTE: CoursePublishingService moved to content/publishing/service.py
# Import directly: from app.application.services.content.publishing.service import CoursePublishingService
# NOT imported here to avoid circular dependency:
# repositories.courses -> cache_service -> services.__init__ -> course_publishing_service -> repositories.courses

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
    'GroupManagementService',  # RBAC 3.0 group-based authorization

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
