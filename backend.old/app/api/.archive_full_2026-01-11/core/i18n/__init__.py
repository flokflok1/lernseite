"""
LernsystemX i18n API Package
============================

Public and admin endpoints for internationalization.
Refactored from monolithic i18n.py (962 lines) into focused packages.

Packages:
    - translation/  - AI translation & language management
    - management/   - Translation keys & user suggestions
    - moderation/   - Admin moderation dashboard & queue
    - public/       - Public bundle retrieval

Structure:
    translation/
        ├── __init__.py
        ├── ai.py          ~285 LOC  - /admin/ai/translate, /admin/seed-keys, /admin/seed-all-locales
        └── languages.py   ~350 LOC  - /admin/languages/*, /admin/export

    management/
        ├── __init__.py
        ├── keys.py        ~180 LOC  - /admin/namespaces, /admin/keys/*
        └── suggestions.py ~170 LOC  - /suggestions (CRUD), /vote, /request-translation

    moderation/
        ├── __init__.py
        └── content.py     ~220 LOC  - /admin/moderation/*, /admin/config, /admin/cache

    public/
        ├── __init__.py
        └── api.py         ~85 LOC   - /bundle, /languages, /languages/<code>/progress

Route Registration:
    All routes are registered on api_v1 blueprint via nested blueprint pattern.
    When this package is imported, blueprints are auto-registered on api_v1.
    Final URLs: /api/v1/i18n/...

Refactored: 2026-01-08 per Developer-Guide-KI Section 10
"""

from .translation import i18n_ai_translation_bp, i18n_languages_bp
from .management import i18n_keys_bp, i18n_suggestions_bp
from .moderation import i18n_moderation_bp
from .public import i18n_public_bp

# All blueprints in this package
ALL_BLUEPRINTS = [
    i18n_public_bp,
    i18n_suggestions_bp,
    i18n_moderation_bp,
    i18n_keys_bp,
    i18n_ai_translation_bp,
    i18n_languages_bp,
]

# Register all sub-blueprints on api_v1 (nested blueprint pattern)
# This is executed when the package is imported
from app.api import api_v1

for bp in ALL_BLUEPRINTS:
    api_v1.register_blueprint(bp)


# Export all blueprints for direct import
__all__ = [
    'i18n_public_bp',
    'i18n_suggestions_bp',
    'i18n_moderation_bp',
    'i18n_keys_bp',
    'i18n_ai_translation_bp',
    'i18n_languages_bp',
    'ALL_BLUEPRINTS',
]
