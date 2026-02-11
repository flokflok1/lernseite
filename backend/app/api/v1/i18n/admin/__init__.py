"""
i18n Admin API Module

Admin endpoints for translation management, synchronization, and language drafts.

Consolidated from: api/v1/admin/i18n/ → api/v1/i18n/admin/
Part of: Phase 4 i18n Consolidation

Blueprints:
- i18n_admin_bp: Admin approve/stats/quality (/i18n)
- i18n_sync_bp: Translation synchronization (/api/admin-panel/i18n-sync)
- admin_translations_bp: Language draft helper (/admin/translations)
"""

from app.api.v1.i18n.admin.admin import i18n_admin_bp
from app.api.v1.i18n.admin.sync import bp as i18n_sync_bp
from app.api.v1.i18n.admin.translations import admin_translations_bp

__all__ = ['i18n_admin_bp', 'i18n_sync_bp', 'admin_translations_bp']
