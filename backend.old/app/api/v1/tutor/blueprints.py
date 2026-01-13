"""
Tutor Blueprints

Centralized blueprint definitions for tutor API.
Avoids circular imports by defining all blueprints in one place.
"""

from flask import Blueprint

# Admin: Chapter Theory Generation
tutor_chapter_theory_bp = Blueprint(
    'tutor_chapter_theory',
    __name__,
    url_prefix='/api/v1/admin/tutor'
)

# Admin: Lesson Explanation Generation
tutor_lesson_explanation_bp = Blueprint(
    'tutor_lesson_explanation',
    __name__,
    url_prefix='/api/v1/admin/tutor'
)

# User: Chat
tutor_user_chat_bp = Blueprint(
    'tutor_user_chat',
    __name__,
    url_prefix='/api/v1/tutor'
)

# User: TTS
tutor_user_tts_bp = Blueprint(
    'tutor_user_tts',
    __name__,
    url_prefix='/api/v1/tutor'
)
