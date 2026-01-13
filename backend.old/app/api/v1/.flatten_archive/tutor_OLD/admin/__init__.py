"""
Tutor Admin Package (DDD)

Admin endpoints for tutor content generation using DDD patterns.

Endpoints:
- Chapter Theory Generation (admin layer for theory sheets)
- Lesson Explanation Generation (admin layer for lesson content)
"""

from .chapter_theory import tutor_chapter_theory_bp
from .lesson_explanation import tutor_lesson_explanation_bp

__all__ = [
    'tutor_chapter_theory_bp',
    'tutor_lesson_explanation_bp'
]
