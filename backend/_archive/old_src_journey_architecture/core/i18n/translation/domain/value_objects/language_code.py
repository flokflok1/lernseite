"""
Language Code Value Object (DDD Value Object)

ISO 639-1 language codes for supported languages.
"""

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class LanguageCode:
    """
    Language Code value object.

    Immutable language code following ISO 639-1 standard.
    Supported: 20 languages via DeepL API.
    """

    code: str

    # Supported language codes (ISO 639-1)
    SUPPORTED_LANGUAGES: ClassVar[tuple[str, ...]] = (
        'de',  # German
        'en',  # English
        'es',  # Spanish
        'fr',  # French
        'it',  # Italian
        'pt',  # Portuguese
        'ru',  # Russian
        'zh',  # Chinese
        'ja',  # Japanese
        'ko',  # Korean
        'ar',  # Arabic
        'tr',  # Turkish
        'pl',  # Polish
        'nl',  # Dutch
        'sv',  # Swedish
        'no',  # Norwegian
        'da',  # Danish
        'fi',  # Finnish
        'el',  # Greek
        'hi',  # Hindi
    )

    def __post_init__(self):
        """Validate language code."""
        if not self.code or len(self.code) != 2:
            raise ValueError(f"Invalid language code: {self.code}. Must be 2-letter ISO 639-1 code.")
        if self.code not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language: {self.code}. "
                f"Supported languages: {', '.join(self.SUPPORTED_LANGUAGES)}"
            )

    @classmethod
    def from_string(cls, code: str) -> 'LanguageCode':
        """
        Create LanguageCode from string.

        Args:
            code: 2-letter language code

        Returns:
            LanguageCode instance

        Raises:
            ValueError: If code is invalid
        """
        return cls(code=code.lower())

    def is_rtl(self) -> bool:
        """
        Check if language is right-to-left.

        Returns:
            True for RTL languages (Arabic, Hebrew)
        """
        return self.code in ('ar',)

    def get_native_name(self) -> str:
        """
        Get language name in native language.

        Returns:
            Native language name
        """
        names = {
            'de': 'Deutsch',
            'en': 'English',
            'es': 'Español',
            'fr': 'Français',
            'it': 'Italiano',
            'pt': 'Português',
            'ru': 'Русский',
            'zh': '中文',
            'ja': '日本語',
            'ko': '한국어',
            'ar': 'العربية',
            'tr': 'Türkçe',
            'pl': 'Polski',
            'nl': 'Nederlands',
            'sv': 'Svenska',
            'no': 'Norsk',
            'da': 'Dansk',
            'fi': 'Suomi',
            'el': 'Ελληνικά',
            'hi': 'हिन्दी',
        }
        return names.get(self.code, self.code.upper())
