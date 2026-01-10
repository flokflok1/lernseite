"""Tutor Domain - User Journey Routes"""

from .chat import tutor_chat_bp
from .tts import tutor_tts_bp

__all__ = [
    'tutor_chat_bp',
    'tutor_tts_bp',
]
