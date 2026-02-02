"""
i18n Bridge Module
==================
Backward-compatible I18nService facade for seamless migration.

This module provides the original I18nService interface while delegating
to the modular service classes. This allows existing code to continue
working without modification during the migration period.
"""

from typing import Optional, Dict, Any, List
from .translations import TranslationManager
from .languages import LanguageManager
from .keys import KeyManager
from .suggestions import SuggestionManager
from .ai_generation import AITranslationGenerator
from .config import ConfigManager


class I18nService:
    """
    Backward-compatible facade for i18n operations.

    Delegates to modular service classes:
    - TranslationManager: Bundle retrieval, translation CRUD
    - LanguageManager: Language metadata, progress tracking
    - KeyManager: i18n keys, namespace management
    - SuggestionManager: Suggestions and community voting
    - AITranslationGenerator: AI translation generation
    - ConfigManager: AI configuration and moderation
    """

    # Expose Cache TTL for backward compatibility
    BUNDLE_CACHE_TTL = TranslationManager.BUNDLE_CACHE_TTL

    # ===== Language Methods =====

    @staticmethod
    def get_primary_language() -> str:
        """Get the primary language code from database (cached)."""
        return LanguageManager.get_primary_language()

    @staticmethod
    def invalidate_primary_language_cache():
        """Clear cached primary language."""
        LanguageManager.invalidate_primary_language_cache()

    @staticmethod
    def get_languages() -> List[Dict[str, Any]]:
        """Get all available languages with progress statistics."""
        return LanguageManager.get_languages()

    @staticmethod
    def get_language_progress(language_code: str) -> Optional[Dict[str, Any]]:
        """Get detailed progress for a specific language."""
        return LanguageManager.get_language_progress(language_code)

    # ===== Translation Methods =====

    @staticmethod
    def get_bundle(language_code: str, namespace: Optional[str] = None) -> Dict[str, str]:
        """Get translation bundle for a language."""
        return TranslationManager.get_bundle(language_code, namespace)

    @staticmethod
    def get_key_translations(key_id: str) -> List[Dict[str, Any]]:
        """Get all translations for a key."""
        return TranslationManager.get_key_translations(key_id)

    @staticmethod
    def set_translation(
        key_id: str,
        language_code: str,
        value: str,
        translator_id: Optional[str] = None,
        is_machine_translated: bool = False
    ) -> bool:
        """Set or update a translation."""
        return TranslationManager.set_translation(
            key_id, language_code, value, translator_id, is_machine_translated
        )

    # ===== Key Methods =====

    @staticmethod
    def get_namespaces() -> List[Dict[str, Any]]:
        """Get all i18n namespaces."""
        return KeyManager.get_namespaces()

    @staticmethod
    def get_keys(
        namespace_id: Optional[int] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get translation keys with pagination."""
        primary_language = LanguageManager.get_primary_language()
        return KeyManager.get_keys(namespace_id, search, limit, offset, primary_language)

    @staticmethod
    def create_key(
        namespace_id: int,
        key_path: str,
        description: Optional[str] = None,
        context_hint: Optional[str] = None,
        max_length: Optional[int] = None,
        placeholders: Optional[List[str]] = None
    ) -> Optional[int]:
        """Create a new translation key."""
        return KeyManager.create_key(
            namespace_id, key_path, description, context_hint, max_length, placeholders
        )

    # ===== Suggestion Methods =====

    @staticmethod
    def submit_suggestion(
        user_id: str,
        language_code: str,
        suggested_value: str,
        translation_id: Optional[str] = None,
        key_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Optional[str]:
        """Submit a translation suggestion."""
        return SuggestionManager.submit_suggestion(
            user_id, language_code, suggested_value, translation_id, key_id, reason,
            invalidate_cache=TranslationManager.invalidate_cache
        )

    @staticmethod
    def vote_suggestion(user_id: str, suggestion_id: str, vote_type: str) -> bool:
        """Vote for a translation suggestion."""
        return SuggestionManager.vote_suggestion(user_id, suggestion_id, vote_type)

    @staticmethod
    def get_suggestions(
        language_code: Optional[str] = None,
        status: str = 'pending',
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get translation suggestions."""
        return SuggestionManager.get_suggestions(language_code, status, limit)

    @staticmethod
    def request_translation(
        user_id: str,
        target_language: str,
        scope: str = 'full',
        namespace_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Request translation for a language (on-demand)."""
        return SuggestionManager.request_translation(user_id, target_language, scope, namespace_id)

    # ===== AI Generation Methods =====

    @staticmethod
    def generate_ai_translation(
        key_id: int,
        target_language: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Generate AI translation for a key."""
        primary_language = LanguageManager.get_primary_language()
        return AITranslationGenerator.generate_ai_translation(
            key_id, target_language, user_id, primary_language,
            set_translation_fn=TranslationManager.set_translation
        )

    @staticmethod
    def bulk_generate_translations(
        target_language: str,
        namespace_id: Optional[int] = None,
        user_id: str = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Generate AI translations for multiple missing keys."""
        primary_language = LanguageManager.get_primary_language()
        result = AITranslationGenerator.bulk_generate_translations(
            target_language, namespace_id, user_id, limit, primary_language,
            generate_fn=AITranslationGenerator.generate_ai_translation
        )
        TranslationManager.invalidate_cache(target_language)
        return result

    # ===== Configuration Methods =====

    @staticmethod
    def get_ai_config() -> Dict[str, Any]:
        """Get AI moderation configuration."""
        return ConfigManager.get_ai_config()

    @staticmethod
    def update_ai_config(config_key: str, config_value: Any, user_id: str) -> bool:
        """Update a single AI config value."""
        return ConfigManager.update_ai_config(config_key, config_value, user_id)

    @staticmethod
    def get_moderation_dashboard() -> List[Dict[str, Any]]:
        """Get moderation dashboard data."""
        return ConfigManager.get_moderation_dashboard()

    @staticmethod
    def get_moderation_queue(
        status: Optional[str] = None,
        language_code: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get moderation queue items."""
        return ConfigManager.get_moderation_queue(status, language_code, limit)

    @staticmethod
    def review_queue_item(
        queue_id: str,
        user_id: str,
        decision: str,
        comment: Optional[str] = None
    ) -> bool:
        """Human review of a queue item."""
        return ConfigManager.review_queue_item(queue_id, user_id, decision, comment)

    # ===== Cache Methods =====

    @staticmethod
    def invalidate_cache(language_code: Optional[str] = None):
        """Invalidate i18n cache."""
        TranslationManager.invalidate_cache(language_code)
