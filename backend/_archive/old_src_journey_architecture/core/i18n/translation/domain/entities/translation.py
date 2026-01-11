"""
Translation Entity (DDD Domain Entity)

Represents a single translation in the system.
Supports 20 languages via DeepL API.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Translation:
    """
    Translation domain entity.

    Attributes:
        translation_id: UUID
        key: Translation key (e.g., 'common.save')
        language_code: ISO 639-1 code (de, en, es, fr, etc.)
        translated_text: Translated text
        context: Optional context for better translation
        created_at: Creation timestamp
        updated_at: Last update timestamp
        source_language: Source language code
    """

    translation_id: str
    key: str
    language_code: str
    translated_text: str
    context: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    source_language: str = 'de'  # Default: German

    def __post_init__(self):
        """Validate translation entity."""
        if not self.key or not self.key.strip():
            raise ValueError("Translation key cannot be empty")
        if not self.language_code or len(self.language_code) != 2:
            raise ValueError("Language code must be 2-letter ISO 639-1 code")
        if not self.translated_text:
            raise ValueError("Translated text cannot be empty")

    def update_translation(self, new_text: str) -> None:
        """
        Update translation text.

        Args:
            new_text: New translated text
        """
        if not new_text or not new_text.strip():
            raise ValueError("Translation text cannot be empty")
        self.translated_text = new_text
        self.updated_at = datetime.utcnow()

    def is_outdated(self, days: int = 365) -> bool:
        """
        Check if translation is outdated.

        Args:
            days: Number of days to consider outdated

        Returns:
            True if translation is older than specified days
        """
        if not self.updated_at:
            return False
        age_days = (datetime.utcnow() - self.updated_at).days
        return age_days > days
