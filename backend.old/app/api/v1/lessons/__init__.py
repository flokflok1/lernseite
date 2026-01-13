"""
Lesson Management API

Lesson videos, explanations, and content management.

Modules:
    - explanations/: Lesson explanation generation
    - videos/: Video generation and playback with Sora 2
        - operations: Video CRUD operations (generate, get, delete, status, audio)
        - config: Configuration endpoints (avatar styles, models, Sora status)

Structure (all under 300 lines):
    explanations/generation.py ~240 lines - Generate lesson explanations
    videos/operations.py       ~290 lines - Video operations endpoints
    videos/config.py           ~150 lines - Video config endpoints

Example usage:
    >>> from app.api.user.lessons.videos import video_operations_bp, video_config_bp
    >>> from app.api.user.lessons.explanations import explanations_bp

Updated: 2026-01-08 - Split videos.py (475 LOC) into operations.py + config.py
"""

from .videos.operations import video_operations_bp
from .videos.config import video_config_bp

# All blueprints in this package
ALL_BLUEPRINTS = [
    video_operations_bp,
    video_config_bp,
]

# Register all sub-blueprints on api_v1
from app.api import api_v1

for bp in ALL_BLUEPRINTS:
    api_v1.register_blueprint(bp)

__all__ = [
    'video_operations_bp',
    'video_config_bp',
    'ALL_BLUEPRINTS',
]
