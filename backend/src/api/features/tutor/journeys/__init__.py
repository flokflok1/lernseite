"""Tutor Domain - All Journeys"""

from .admin import (
    tutor_chapter_theory_bp,
    tutor_lesson_explanation_bp,
)
from .user import (
    tutor_chat_bp,
    tutor_tts_bp,
)

ALL_JOURNEY_BLUEPRINTS = [
    # Admin Journey (2 endpoints)
    tutor_chapter_theory_bp,
    tutor_lesson_explanation_bp,
    # User Journey (5 endpoints)
    tutor_chat_bp,
    tutor_tts_bp,
]

__all__ = [
    'ALL_JOURNEY_BLUEPRINTS',
    'tutor_chapter_theory_bp',
    'tutor_lesson_explanation_bp',
    'tutor_chat_bp',
    'tutor_tts_bp',
]
