"""
Tutor User Package (DDD)

User-facing tutor endpoints: Chat, TTS, Voices.
"""

from flask import Blueprint

# Define blueprints
tutor_user_chat_bp = Blueprint(
    'tutor_user_chat',
    __name__,
    url_prefix='/api/v1/tutor'
)

tutor_user_tts_bp = Blueprint(
    'tutor_user_tts',
    __name__,
    url_prefix='/api/v1/tutor'
)

# Import routes (registers endpoints with blueprints)
from . import chat, tts

__all__ = [
    'tutor_user_chat_bp',
    'tutor_user_tts_bp'
]
