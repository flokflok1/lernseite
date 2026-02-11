"""
Tutor Interfaces Module

Provides admin, core, and user interfaces for tutor functionality.
"""

# Admin interface - content generation
from app.api.v1.tutor.interfaces.admin import (
    generate_chapter_theory,
    generate_lesson_steps,
    generate_lesson_detailed,
    tutor_admin_bp
)

# Core interface - shared types and utilities
from app.api.v1.tutor.interfaces.core import (
    # Classes
    GenerationStyle,
    TutorContext,
    TTSVoice,
    # Constants
    AVAILABLE_VOICES,
    DEFAULT_TUTOR_PROMPT,
    STYLE_CONFIGS,
    # Functions
    create_chat_session,
    create_tts_request,
    build_context_for_chat,
    build_context_for_generation,
    parse_json_response,
    get_style_config,
    save_chapter_theory
)

# User interface - interactive features
from app.api.v1.tutor.interfaces.user import (
    tutor_chat,
    tutor_tts,
    get_tts_voices,
    tutor_bp
)

__all__ = [
    # Admin
    'generate_chapter_theory',
    'generate_lesson_steps',
    'generate_lesson_detailed',
    'tutor_admin_bp',

    # Core - Classes
    'GenerationStyle',
    'TutorContext',
    'TTSVoice',

    # Core - Constants
    'AVAILABLE_VOICES',
    'DEFAULT_TUTOR_PROMPT',
    'STYLE_CONFIGS',

    # Core - Functions
    'create_chat_session',
    'create_tts_request',
    'build_context_for_chat',
    'build_context_for_generation',
    'parse_json_response',
    'get_style_config',
    'save_chapter_theory',

    # User
    'tutor_chat',
    'tutor_tts',
    'get_tts_voices',
    'tutor_bp'
]
