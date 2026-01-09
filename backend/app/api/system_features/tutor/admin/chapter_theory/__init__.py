"""
Chapter Theory Generation (DDD)

Admin endpoints for AI-powered chapter theory generation.
Uses TutorGenerationFactory and TutorKnowledgeService.
"""

from flask import Blueprint

tutor_chapter_theory_bp = Blueprint(
    'tutor_chapter_theory',
    __name__,
    url_prefix='/api/v1/admin/ai'
)

from . import generation

__all__ = ['tutor_chapter_theory_bp']
