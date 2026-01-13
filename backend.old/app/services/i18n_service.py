"""
i18n Service (Refactored)
=========================
Bridge module for backward compatibility.

This module has been refactored into a modular package at:
  app/services/i18n/

The original monolithic I18nService class is now a facade that delegates
to specialized manager classes:
  - TranslationManager: Translation CRUD and caching
  - LanguageManager: Language metadata and progress
  - KeyManager: i18n keys and namespaces
  - SuggestionManager: Community suggestions and voting
  - AITranslationGenerator: AI-powered translations
  - ConfigManager: AI configuration and moderation

This file re-exports the I18nService class for backward compatibility.
Existing imports continue to work without modification.

Migration path:
  Legacy: from app.services.i18n_service import I18nService
  New:    from app.services.i18n import TranslationManager, LanguageManager, ...
"""

# Backward-compatible re-export
from app.services.i18n.bridge import I18nService

__all__ = ['I18nService']
