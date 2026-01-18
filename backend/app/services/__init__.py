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
# LEGACY BRIDGE REGISTRATION (MUST BE FIRST!)
# ============================================
# Register legacy bridge modules IMMEDIATELY so old import paths work
# This must happen before any other imports in this package

import sys
import importlib.util
from pathlib import Path

def _register_legacy_bridges():
    """Register legacy bridge modules in sys.modules for backward compatibility."""
    bridges_dir = Path(__file__).parent / '_legacy_bridges'
    if not bridges_dir.exists():
        return

    legacy_bridges = [
        'ai_adapter', 'ai_job_service', 'audit_service', 'content_translation_service',
        'course_ai_settings_service', 'course_authoring_service', 'feature_configuration_ab_test',
        'feature_configuration_rollout', 'feature_configuration_service', 'file_context_service',
        'i18n_service', 'math_toolkit_service', 'permission_service', 'prompt_resolver',
        'role_studio_service', 'tts_service',
    ]

    for bridge_name in legacy_bridges:
        bridge_file = bridges_dir / f'{bridge_name}.py'
        if bridge_file.exists():
            module_path = f'app.services.{bridge_name}'
            spec = importlib.util.spec_from_file_location(module_path, bridge_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                sys.modules[module_path] = module

_register_legacy_bridges()

# ============================================
# ROOT-LEVEL UTILITY SERVICES (Cross-cutting concerns)
# ============================================
from app.services.ai.adapter import AIAdapter
from app.services.analytics.service import AnalyticsService
from app.services.system.billing.service import BillingService
from app.infrastructure.cache.service import CacheService
from app.services.dashboard.feedback.service import FeedbackService
from app.services.system.features.service import FeatureService

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
# PUBLISHING SERVICE (Handled separately)
# ============================================
# NOTE: CoursePublishingService moved to content/publishing/service.py
# Import directly: from app.services.content.publishing.service import CoursePublishingService
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
