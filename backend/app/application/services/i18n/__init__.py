"""
i18n Service Package
====================
Comprehensive internationalization service for LernSystemX.

Modules:
  - translations: Core translation CRUD and caching
  - languages: Language metadata and progress tracking
  - keys: i18n keys and namespace management
  - suggestions: Translation suggestions and community voting
  - ai_generation: AI-powered translation generation
  - config: AI moderation configuration and dashboard
  - bridge: Backward-compatible I18nService facade (for migration)
"""

from .translations import TranslationManager
from .languages import LanguageManager
from .keys import KeyManager
from .suggestions import SuggestionManager
from .ai_generation import AITranslationGenerator
from .config import ConfigManager

__all__ = [
    'TranslationManager',
    'LanguageManager',
    'KeyManager',
    'SuggestionManager',
    'AITranslationGenerator',
    'ConfigManager',
]
