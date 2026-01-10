"""Tutor Domain - Admin Journey Routes"""

from .chapter_theory.generation import tutor_chapter_theory_bp
from .lesson_explanation.generation import tutor_lesson_explanation_bp

__all__ = [
    'tutor_chapter_theory_bp',
    'tutor_lesson_explanation_bp',
]
