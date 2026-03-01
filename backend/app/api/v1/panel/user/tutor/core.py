"""
LernsystemX Tutor Core - Shared Components

Value objects, enums, constants, and helper functions for the tutor system.
Used by both user-facing and admin endpoints.

ISO 9001:2015 compliant - AI Tutor Core Layer
"""

from typing import Dict, Any, Tuple, Optional, List
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import logging
import uuid
import json

from app.application.services.system_features.tutor_knowledge import TutorKnowledgeService as BaseTutorKnowledgeService

logger = logging.getLogger(__name__)


# =============================================================================
# VALUE OBJECTS & ENUMS
# =============================================================================

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


# Initialize OpenAI voices
AVAILABLE_VOICES = [
    TTSVoice("alloy", "Alloy", "Neutral, balanced voice"),
    TTSVoice("echo", "Echo", "Clear, articulate voice", gender="male"),
    TTSVoice("fable", "Fable", "Warm, expressive voice", gender="female"),
    TTSVoice("onyx", "Onyx", "Deep, authoritative voice", gender="male"),
    TTSVoice("nova", "Nova", "Energetic, upbeat voice", gender="female"),
    TTSVoice("shimmer", "Shimmer", "Soft, gentle voice", display_name_de="Schimmer", gender="female")
]


# =============================================================================
# CONSTANTS & PROMPTS
# =============================================================================

DEFAULT_TUTOR_PROMPT = """Du bist ein freundlicher und hilfreicher KI-Tutor auf LernsystemX.
Du begleitest Lernende durch ihre Lernreise und hilfst bei Fragen zu Kursen und Lernmethoden.
Du bist geduldig, ermutigend und erklärst Konzepte klar und verständlich.
Antworte immer auf Deutsch, es sei denn der User spricht eine andere Sprache.
Halte deine Antworten prägnant aber hilfreich - idealerweise 2-4 Sätze.

Wenn der User Fragen zum aktuellen Lerninhalt hat, beziehe dich auf den bereitgestellten Kurs-Kontext.
Du kannst Konzepte erklären, Beispiele geben und bei Übungen helfen."""


# Style configurations for content generation
STYLE_CONFIGS = {
    GenerationStyle.ADHS: {
        'temperature': 0.7,
        'instructions': [
            'Verwende kurze Sätze (max. 10-15 Wörter)',
            'Strukturiere klar mit Aufzählungen und Absätzen',
            'Verwende relevante Emojis zur Auflockerung (max. 3 pro Abschnitt)',
            'Hebe Schlüsselwörter hervor (Fettdruck)',
            'Verwende Eselsbrücken und Merkhilfen'
        ]
    },
    GenerationStyle.DETAILED: {
        'temperature': 0.6,
        'instructions': [
            'Erkläre Konzepte ausführlich und detailliert',
            'Verwende Beispiele zur Veranschaulichung',
            'Erläutere Zusammenhänge und Hintergründe',
            'Gehe auf Randthemen und Details ein',
            'Verwende Fachbegriffe und erkläre sie'
        ]
    },
    GenerationStyle.SHORT: {
        'temperature': 0.5,
        'instructions': [
            'Fasse dich kurz und prägnant',
            'Konzentriere dich auf die Kernpunkte',
            'Verwende Stichpunkte statt langer Texte',
            'Verzichte auf Beispiele wenn nicht essentiell',
            'Maximal 3-4 Sätze pro Abschnitt'
        ]
    },
    GenerationStyle.EXAM_FOCUS: {
        'temperature': 0.6,
        'instructions': [
            'Fokus auf prüfungsrelevante Inhalte',
            'Verwende Prüfungssprache und -format',
            'Betone wichtige Konzepte für IHK-Prüfung',
            'Füge Übungsfragen hinzu',
            'Verwende Checklisten für Lernziele'
        ]
    }
}


# =============================================================================
# HELPER FUNCTIONS (Factory & Service Logic)
# =============================================================================

def create_chat_session(
    user_id: str,
    message: str,
    context: Optional[TutorContext] = None,
    history: Optional[list] = None
) -> Dict[str, Any]:
    """
    Create tutor chat session configuration.

    Factory method with business rules:
    - History limited to last 10 messages
    - Context is optional
    - Session ID is generated
    """
    session_id = str(uuid.uuid4())

    # Limit history to last 10 messages
    if history and len(history) > 10:
        history = history[-10:]

    return {
        'session_id': session_id,
        'user_id': user_id,
        'message': message,
        'context': context.to_dict() if context else {},
        'history': history or [],
        'created_at': datetime.utcnow(),
        'has_context': context is not None and context.has_course_context() if context else False
    }


def create_tts_request(user_id: str, text: str, voice: str = 'alloy') -> Dict[str, Any]:
    """
    Create TTS request configuration.

    Business Rules:
    - Text limited to 4096 characters
    - Voice must be valid
    """
    # Validate text length
    if len(text) > 4096:
        raise ValueError("Text too long (max 4096 characters)")

    # Validate voice
    valid_voices = [v.voice_id for v in AVAILABLE_VOICES]
    if voice not in valid_voices:
        raise ValueError(f"Invalid voice: {voice}. Valid voices: {', '.join(valid_voices)}")

    return {
        'user_id': user_id,
        'text': text.strip(),
        'voice': voice
    }


def build_context_for_chat(
    context: TutorContext,
    include_files: bool = True,
    include_progress: bool = True
) -> str:
    """
    Build knowledge context for tutor chat.

    Loads course/chapter/lesson content if IDs provided.
    """
    if not context.has_course_context():
        return "Kein spezifischer Kurs-Kontext verfügbar."

    try:
        knowledge_context = BaseTutorKnowledgeService.build_tutor_context_prompt(
            course_id=context.course_id,
            chapter_id=context.chapter_id,
            lesson_id=context.lesson_id,
            method_id=context.method_id,
            user_id=context.user_id,
            include_files=include_files,
            include_progress=include_progress
        )
        return knowledge_context
    except Exception as e:
        logger.warning(f"Could not load tutor knowledge context: {e}")
        return "Kein spezifischer Kurs-Kontext verfügbar."


def build_context_for_generation(
    course_title: str,
    chapter_title: str,
    chapter_description: Optional[str] = None,
    lesson_titles: Optional[List[str]] = None
) -> Dict[str, str]:
    """
    Build context for content generation (theory, explanations).
    """
    return {
        'course_title': course_title,
        'chapter_title': chapter_title,
        'chapter_description': chapter_description or '',
        'lesson_titles': ', '.join(lesson_titles) if lesson_titles else 'Keine spezifischen Lektionen',
        'target_audience': 'Fachinformatiker Systemintegration (FISI) in Prüfungsvorbereitung'
    }


def parse_json_response(output_text: str, fallback_title: str = "Generierter Inhalt") -> dict:
    """
    Parse JSON response from AI, with fallback for malformed JSON.
    """
    try:
        # Try direct JSON parse
        data = json.loads(output_text)
        return data
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        if '```json' in output_text:
            start = output_text.find('```json') + 7
            end = output_text.find('```', start)
            json_str = output_text[start:end].strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # Fallback: Return as plain text
        logger.warning("Could not parse AI response as JSON, using fallback")
        return {
            'title': fallback_title,
            'introduction': '',
            'sections': [{
                'title': 'Inhalt',
                'content': output_text,
                'subsections': []
            }],
            'summary': '',
            'key_points': []
        }


def get_style_config(style: GenerationStyle) -> dict:
    """Get style configuration for AI generation."""
    return STYLE_CONFIGS.get(style, STYLE_CONFIGS[GenerationStyle.ADHS])


def save_chapter_theory(chapter_id: str, style: str, theory_data: dict, tokens_used: int, user_id: str):
    """Save generated theory to database."""
    try:
        from app.infrastructure.persistence.repositories.content.chapter_theory import ChapterTheoryRepository
        ChapterTheoryRepository.create({
            'chapter_id': chapter_id,
            'style': style,
            'theory_data': theory_data,
            'title': theory_data.get('title'),
            'tokens_used': tokens_used,
            'created_by': user_id
        })
    except Exception as e:
        logger.warning(f"Could not save chapter theory to DB: {e}")
