"""
Lesson Explanation Generation (DDD)

Admin endpoints for AI-powered lesson explanations.
"""

from flask import Blueprint

tutor_lesson_explanation_bp = Blueprint(
    'tutor_lesson_explanation',
    __name__,
    url_prefix='/api/v1/admin/ai'
)

from . import generation

__all__ = ['tutor_lesson_explanation_bp']
