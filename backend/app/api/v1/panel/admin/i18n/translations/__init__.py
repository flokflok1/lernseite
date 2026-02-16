"""
i18n Admin Translations API Module

Admin translation management endpoints (multi-part file for >500 LOC).

Moved from: api/v1/admin/i18n/translations*.py → api/v1/i18n/admin/translations/
Part of: Phase 4 i18n Consolidation

Blueprint: admin_translations_bp
URL Prefix: /admin/translations
"""

from .translations import bp as admin_translations_bp

__all__ = ['admin_translations_bp']
