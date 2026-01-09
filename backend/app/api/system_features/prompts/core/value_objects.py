"""
Prompts Value Objects (DDD)

Immutable value objects for the Prompts domain.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class PromptCategory(Enum):
    """
    Prompt template categories.

    Value Object: Immutable category definitions.
    """
    THEORY = "theory"
    LESSON = "lesson"
    QUIZ = "quiz"
    FLASHCARD = "flashcard"
    TUTOR = "tutor"
    SUMMARY = "summary"
    EXAM = "exam"

    @property
    def display_name(self) -> str:
        """Human-readable display name."""
        names = {
            self.THEORY: "Theorieblatt",
            self.LESSON: "Lektions-Erklärung",
            self.QUIZ: "Quiz-Generator",
            self.FLASHCARD: "Karteikarten",
            self.TUTOR: "Tutor-Dialog",
            self.SUMMARY: "Zusammenfassung",
            self.EXAM: "Prüfungsaufgabe"
        }
        return names.get(self, self.value)


class PromptStyle(Enum):
    """
    Prompt generation styles.

    Value Object: Immutable style definitions.
    """
    ADHS = "adhs"
    DETAILED = "detailed"
    SHORT = "short"
    EXAM_FOCUS = "exam_focus"

    @property
    def display_name(self) -> str:
        """Human-readable display name."""
        names = {
            self.ADHS: "ADHS-freundlich",
            self.DETAILED: "Ausführlich",
            self.SHORT: "Kurz & Knapp",
            self.EXAM_FOCUS: "Prüfungsfokus"
        }
        return names.get(self, self.value)


@dataclass(frozen=True)
class PromptMetadata:
    """
    Metadata for a prompt template.

    Value Object: Immutable prompt metadata.
    """
    category: PromptCategory
    style: PromptStyle
    version: str = "1.0"
    author: Optional[str] = None
    is_default: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'category': self.category.value,
            'style': self.style.value,
            'version': self.version,
            'author': self.author,
            'is_default': self.is_default
        }
