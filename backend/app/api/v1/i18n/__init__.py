"""
i18n API Package - Internationalization and Translation Endpoints
================================================================

All i18n blueprints live here (DDD: API layer owns all route definitions).

Consolidated from: api/v1/admin/i18n/ → api/v1/i18n/admin/ (Phase 4)

Blueprints:
    i18n_public_bp         - Public bundle/languages (no auth)
    i18n_admin_bp          - Admin approve/stats/quality
    i18n_sync_bp           - Admin translation synchronization (NEW - Phase 4)
    admin_translations_bp  - Admin language draft helper (NEW - Phase 4)
    i18n_keys_bp           - Admin key & namespace management
    i18n_suggestions_bp    - User translation suggestions & voting
    i18n_moderation_bp     - Admin moderation dashboard/queue/config/cache
    i18n_ai_translation_bp - Admin AI translation & seeding
    i18n_languages_bp      - Admin language CRUD & export
    translation_bp         - Content translation (courses/materials)
"""

from app.api.v1.i18n.admin import i18n_admin_bp, i18n_sync_bp, admin_translations_bp
from app.api.v1.i18n.translation import i18n_ai_translation_bp, translation_bp
from app.api.v1.i18n.public import i18n_keys_bp, i18n_languages_bp, i18n_public_bp
from app.api.v1.i18n.moderation import i18n_moderation_bp, i18n_suggestions_bp

# All blueprints for registration by api/v1/__init__.py
I18N_BLUEPRINTS = [
    i18n_public_bp,
    i18n_admin_bp,
    i18n_sync_bp,           # NEW - Phase 4: Translation synchronization
    admin_translations_bp,  # NEW - Phase 4: Language draft helper
    i18n_keys_bp,
    i18n_suggestions_bp,
    i18n_moderation_bp,
    i18n_ai_translation_bp,
    i18n_languages_bp,
    translation_bp,
]

__all__ = [
    'i18n_public_bp',
    'i18n_admin_bp',
    'i18n_sync_bp',
    'admin_translations_bp',
    'i18n_keys_bp',
    'i18n_suggestions_bp',
    'i18n_moderation_bp',
    'i18n_ai_translation_bp',
    'i18n_languages_bp',
    'translation_bp',
    'I18N_BLUEPRINTS',
]
