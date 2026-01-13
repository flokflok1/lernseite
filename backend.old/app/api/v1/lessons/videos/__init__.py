"""
Lesson Video Module

Provides video generation and playback with Sora 2:
- Video operations (generate, get, delete, status)
- Configuration endpoints (avatar styles, models, Sora status)

Sora 2 generates VIDEO + AUDIO together (synced!), no separate TTS needed.
"""

from flask import Blueprint
from .operations import video_operations_bp
from .config import video_config_bp

# Create main videos blueprint
videos_bp = Blueprint(
    'lesson_videos',
    __name__
)

# Import and re-export route functions for backward compatibility
from .operations import (
    get_lesson_video,
    generate_lesson_video,
    get_video_generation_status,
    delete_lesson_video,
    get_lesson_audio
)

from .config import (
    get_avatar_styles,
    get_sora_status,
    get_video_models
)

__all__ = [
    'videos_bp',
    'video_operations_bp',
    'video_config_bp',
    'get_lesson_video',
    'generate_lesson_video',
    'get_video_generation_status',
    'delete_lesson_video',
    'get_lesson_audio',
    'get_avatar_styles',
    'get_sora_status',
    'get_video_models'
]
