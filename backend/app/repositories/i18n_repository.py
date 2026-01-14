"""
i18n Repository - Unified Access to i18n Data Layer

This module provides unified repository access for i18n operations by combining
all three specialized repositories (languages, translations, community).

Split modules:
- i18n_repository_languages.py - Language, namespace, and key management
- i18n_repository_translations.py - Translation storage, retrieval, and bundling
- i18n_repository_community.py - Community suggestions, AI reviews, and caching

Usage (for backward compatibility with existing code):
    from app.repositories.i18n_repository import I18nRepository
    repo = I18nRepository(connection)
    # Use any method from languages, translations, or community repositories
"""

from app.repositories.i18n_repository_languages import I18nLanguagesRepository
from app.repositories.i18n_repository_translations import I18nTranslationsRepository
from app.repositories.i18n_repository_community import I18nCommunityRepository
import psycopg


class I18nRepository:
    """
    Unified i18n Repository facade.

    Combines all three specialized repositories for backward compatibility.
    Delegates method calls to the appropriate specialized repository.

    This class allows existing code to continue using I18nRepository
    while the actual implementation is split across three specialized classes.
    """

    def __init__(self, connection: psycopg.Connection):
        """
        Initialize unified repository with component repositories.

        Args:
            connection: Database connection
        """
        self.connection = connection
        self.languages = I18nLanguagesRepository(connection)
        self.translations = I18nTranslationsRepository(connection)
        self.community = I18nCommunityRepository(connection)

    # =============================================================================
    # LANGUAGES & NAMESPACES (delegated to I18nLanguagesRepository)
    # =============================================================================

    def get_supported_languages(self):
        """Get all supported languages."""
        return self.languages.get_supported_languages()

    def get_language(self, language_code):
        """Get language by code."""
        return self.languages.get_language(language_code)

    def get_primary_languages(self):
        """Get primary languages for translation."""
        return self.languages.get_primary_languages()

    def get_namespaces(self):
        """Get all i18n namespaces."""
        return self.languages.get_namespaces()

    def get_or_create_namespace(self, namespace_code, namespace_name=None):
        """Get or create namespace."""
        return self.languages.get_or_create_namespace(namespace_code, namespace_name)

    def get_namespace(self, namespace_code):
        """Get namespace by code."""
        return self.languages.get_namespace(namespace_code)

    def get_or_create_key(self, namespace_code, key_path, context=None):
        """Get or create translation key."""
        return self.languages.get_or_create_key(namespace_code, key_path, context)

    def get_key(self, namespace_code, key_path):
        """Get key by namespace and path."""
        return self.languages.get_key(namespace_code, key_path)

    # =============================================================================
    # TRANSLATIONS (delegated to I18nTranslationsRepository)
    # =============================================================================

    def get_translation(self, namespace_code, key_path, language_code):
        """Get translation."""
        return self.translations.get_translation(namespace_code, key_path, language_code)

    def get_translations_for_language(self, language_code, namespace_code=None, limit=100, offset=0):
        """Get translations for a language."""
        return self.translations.get_translations_for_language(language_code, namespace_code, limit, offset)

    def create_translation(self, namespace_code, key_path, language_code, translation_text, translated_by):
        """Create translation."""
        return self.translations.create_translation(namespace_code, key_path, language_code, translation_text, translated_by)

    def approve_translation(self, translation_id, reviewed_by):
        """Approve translation."""
        return self.translations.approve_translation(translation_id, reviewed_by)

    def get_translation_bundle(self, language_code, namespace_code=None):
        """Get translation bundle for frontend."""
        return self.translations.get_translation_bundle(language_code, namespace_code)

    # =============================================================================
    # COMMUNITY SUGGESTIONS & VOTING (delegated to I18nCommunityRepository)
    # =============================================================================

    def create_suggestion(self, namespace_code, key_path, language_code, suggested_text, user_id, reason=''):
        """Create translation suggestion."""
        return self.community.create_suggestion(namespace_code, key_path, language_code, suggested_text, user_id, reason)

    def get_pending_suggestions(self, language_code=None, limit=100):
        """Get pending suggestions."""
        return self.community.get_pending_suggestions(language_code, limit)

    def vote_on_suggestion(self, suggestion_id, user_id, vote_value):
        """Vote on suggestion."""
        return self.community.vote_on_suggestion(suggestion_id, user_id, vote_value)

    # =============================================================================
    # AI MODERATION (delegated to I18nCommunityRepository)
    # =============================================================================

    def create_ai_review(self, translation_id, quality_score, issues, suggestions=''):
        """Create AI review."""
        return self.community.create_ai_review(translation_id, quality_score, issues, suggestions)

    def get_low_quality_translations(self, quality_threshold=0.7, language_code=None, limit=100):
        """Get low-quality translations."""
        return self.community.get_low_quality_translations(quality_threshold, language_code, limit)

    # =============================================================================
    # CACHE MANAGEMENT (delegated to I18nCommunityRepository)
    # =============================================================================

    def invalidate_language_cache(self, language_code):
        """Invalidate cache for language."""
        return self.community.invalidate_language_cache(language_code)

    def invalidate_all_caches(self):
        """Invalidate all caches."""
        return self.community.invalidate_all_caches()


__all__ = [
    'I18nRepository',
    'I18nLanguagesRepository',
    'I18nTranslationsRepository',
    'I18nCommunityRepository',
]
