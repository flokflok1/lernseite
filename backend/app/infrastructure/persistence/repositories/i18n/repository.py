"""
i18n Repository - Unified Access to i18n Data Layer

This module provides unified repository access for i18n operations by combining
all four specialized repositories (languages, translations, community, import).

Split modules:
- i18n_repository_languages.py - Language, namespace, and key management
- i18n_repository_translations.py - Translation storage, retrieval, and bundling
- i18n_repository_community.py - Community suggestions, AI reviews, and caching
- i18n_import_repository.py - Bulk import operations and statistics

Usage (for backward compatibility with existing code):
    from app.infrastructure.persistence.repositories.i18n_repository import I18nRepository
    repo = I18nRepository(connection)
    # Use any method from languages, translations, community, or import repositories
"""

from .languages import I18nLanguagesRepository
from .translations import I18nTranslationsRepository
from .import_repository import I18nImportRepository
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
        self.import_ops = I18nImportRepository

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

    # =============================================================================
    # IMPORT OPERATIONS (delegated to I18nImportRepository)
    # =============================================================================

    def get_namespace_id(self, namespace_code: str):
        """
        Get namespace ID by code.

        Args:
            namespace_code: e.g. 'admin', 'common', 'windows'

        Returns:
            namespace_id (int) or None if not found
        """
        return self.import_ops.get_namespace_id(namespace_code)

    def get_all_namespaces(self):
        """
        Get all namespaces as mapping code → id.

        Returns:
            {'admin': 1, 'common': 2, 'windows': 3, ...}
        """
        return self.import_ops.get_all_namespaces()

    def create_key(self, namespace_id: int, key_path: str, context: str = None):
        """
        Create i18n_key entry (idempotent).

        Args:
            namespace_id: Namespace ID
            key_path: e.g. 'admin.roles.loadFailed'
            context: Optional context for translation

        Returns:
            key_id (UUID string) or None on failure
        """
        return self.import_ops.create_key(namespace_id, key_path, context)

    def create_import_translation(
        self,
        key_id: str,
        language_code: str,
        value: str,
        source: str = 'import',
        status: str = 'active'
    ):
        """
        Create i18n_translation entry (idempotent).

        Args:
            key_id: UUID of i18n_key
            language_code: e.g. 'de', 'en', 'pl'
            value: The translated text
            source: 'manual' | 'deepl' | 'google' | 'community' | 'ai' | 'import'
            status: 'draft' | 'active' | 'needs_review' | 'outdated'

        Returns:
            translation_id (UUID string) or None on failure
        """
        return self.import_ops.create_translation(key_id, language_code, value, source, status)

    def get_import_statistics(self):
        """
        Get current i18n import statistics.

        Returns:
            Dictionary with keys: total_keys, total_translations, languages_count,
            namespaces_count, keys_by_namespace, translations_by_language
        """
        return self.import_ops.get_import_statistics()

    def validate_import_complete(self):
        """
        Validate that import is complete for all primary languages.

        Returns:
            {'is_complete': bool, 'issues': [...], 'summary': {...}}
        """
        return self.import_ops.validate_import_complete()

    def delete_all_imports(self):
        """
        Delete all imported translations (for cleanup/reimport).

        WARNING: This deletes all i18n_translations and i18n_keys!

        Returns:
            True if successful
        """
        return self.import_ops.delete_all_imports()


__all__ = [
    'I18nRepository',
    'I18nLanguagesRepository',
    'I18nTranslationsRepository',
    'I18nCommunityRepository',
    'I18nImportRepository',
]
