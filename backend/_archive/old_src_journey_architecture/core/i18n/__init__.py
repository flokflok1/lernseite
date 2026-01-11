"""
i18n Core Module

Multi-language support system with translation services and caching.

Supports 20 languages:
- European: de, en, es, fr, it, pt, ru, pl, nl, sv, no, da, fi, el
- Asian: zh, ja, ko, hi
- Middle Eastern: ar, tr

Features:
- Translation service with DeepL API integration
- Redis-based permanent translation cache
- Language management (add, update, delete)
- Context-aware translations
- AI-powered translation generation

Structure:
- translation/: Translation domain with DDD structure
  - domain/: Translation entities and value objects
  - application/services/: Translation services, DeepL adapter, AI generation
- cache/: Redis-based translation cache

Usage:
    from src.core.i18n import LanguageCode, TranslationCache

    # Language code
    lang = LanguageCode.from_string('de')

    # Cache
    TranslationCache.set('common.save', 'de', 'Speichern')
    text = TranslationCache.get('common.save', 'de')
"""

from src.core.i18n.translation.domain.entities.translation import Translation
from src.core.i18n.translation.domain.value_objects.language_code import LanguageCode
from src.core.i18n.cache.translation_cache import TranslationCache

# Legacy error codes (kept for backward compatibility)
try:
    from src.core.i18n.error_codes import ErrorCode, error_response, success_response
    from src.core.i18n.message_codes import MessageCode
    LEGACY_CODES_AVAILABLE = True
except ImportError:
    LEGACY_CODES_AVAILABLE = False

__all__ = [
    # Domain
    'Translation',
    'LanguageCode',

    # Cache
    'TranslationCache',
]

# Add legacy exports if available
if LEGACY_CODES_AVAILABLE:
    __all__.extend(['ErrorCode', 'MessageCode', 'error_response', 'success_response'])
