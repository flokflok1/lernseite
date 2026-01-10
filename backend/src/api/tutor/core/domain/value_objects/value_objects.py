"""
Tutor Value Objects (DDD)

Immutable value objects for the Tutor domain.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List


class GenerationStyle(Enum):
    """
    Available generation styles for AI tutor content.

    Value Object: Immutable, defines valid style values.
    """
    ADHS = "adhs"              # ADHS-friendly: Short, structured, emoji
    DETAILED = "detailed"       # Detailed: Comprehensive explanations
    SHORT = "short"            # Short: Brief summaries
    EXAM_FOCUS = "exam_focus"  # Exam-focused: Practice-oriented

    @classmethod
    def from_string(cls, style_str: str) -> 'GenerationStyle':
        """
        Convert string to GenerationStyle enum.

        Args:
            style_str: Style string (e.g., "adhs")

        Returns:
            GenerationStyle enum

        Raises:
            ValueError: If style is invalid
        """
        try:
            return cls(style_str.lower())
        except ValueError:
            raise ValueError(
                f"Invalid generation style: {style_str}. "
                f"Valid options: {', '.join([s.value for s in cls])}"
            )

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

    @property
    def description(self) -> str:
        """Style description."""
        descriptions = {
            self.ADHS: "Strukturiert, kurz, mit Emojis - optimal für ADHS",
            self.DETAILED: "Umfassende Erklärungen mit vielen Details",
            self.SHORT: "Kompakte Zusammenfassungen auf den Punkt",
            self.EXAM_FOCUS: "Fokus auf Prüfungsvorbereitung und Übungen"
        }
        return descriptions.get(self, "")


@dataclass(frozen=True)
class TutorContext:
    """
    Context for tutor interactions.

    Value Object: Immutable context data for tutor sessions.

    Attributes:
        user_id: User ID
        course_id: Optional course context
        chapter_id: Optional chapter context
        lesson_id: Optional lesson context
        method_id: Optional learning method context
        page_context: Optional page/location context (e.g., "Dashboard", "Lesson Player")
    """
    user_id: str
    course_id: Optional[str] = None
    chapter_id: Optional[str] = None
    lesson_id: Optional[int] = None
    method_id: Optional[str] = None
    page_context: Optional[str] = None

    def has_course_context(self) -> bool:
        """Check if context has course-related information."""
        return any([self.course_id, self.chapter_id, self.lesson_id, self.method_id])

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'user_id': self.user_id,
            'course_id': self.course_id,
            'chapter_id': self.chapter_id,
            'lesson_id': self.lesson_id,
            'method_id': self.method_id,
            'page_context': self.page_context
        }


@dataclass(frozen=True)
class TTSVoice:
    """
    Text-to-Speech voice configuration.

    Value Object: Immutable voice settings.
    """
    voice_id: str
    display_name: str
    description: str
    display_name_de: Optional[str] = None
    language: str = "en"
    gender: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            'voice_id': self.voice_id,
            'display_name': self.display_name,
            'display_name_de': self.display_name_de or self.display_name,
            'description': self.description,
            'language': self.language,
            'gender': self.gender
        }

    # OpenAI TTS voices
    ALLOY = None
    ECHO = None
    FABLE = None
    ONYX = None
    NOVA = None
    SHIMMER = None


# Initialize OpenAI voices
TTSVoice.ALLOY = TTSVoice("alloy", "Alloy", "Neutral, balanced voice")
TTSVoice.ECHO = TTSVoice("echo", "Echo", "Clear, articulate voice", gender="male")
TTSVoice.FABLE = TTSVoice("fable", "Fable", "Warm, expressive voice", gender="female")
TTSVoice.ONYX = TTSVoice("onyx", "Onyx", "Deep, authoritative voice", gender="male")
TTSVoice.NOVA = TTSVoice("nova", "Nova", "Energetic, upbeat voice", gender="female")
TTSVoice.SHIMMER = TTSVoice("shimmer", "Shimmer", "Soft, gentle voice", display_name_de="Schimmer", gender="female")


AVAILABLE_VOICES = [
    TTSVoice.ALLOY,
    TTSVoice.ECHO,
    TTSVoice.FABLE,
    TTSVoice.ONYX,
    TTSVoice.NOVA,
    TTSVoice.SHIMMER
]


def get_voice_by_id(voice_id: str) -> Optional[TTSVoice]:
    """
    Get TTSVoice by ID.

    Args:
        voice_id: Voice identifier

    Returns:
        TTSVoice or None if not found
    """
    for voice in AVAILABLE_VOICES:
        if voice.voice_id == voice_id:
            return voice
    return None
