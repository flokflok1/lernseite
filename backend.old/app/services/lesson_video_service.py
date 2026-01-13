"""
DEPRECATED: Bridge module for backward compatibility.

This module is maintained for backward compatibility only.
New code should import directly from app.services.lesson_video package.

Legacy usage:
    from app.services.lesson_video_service import LessonVideoService

New usage (preferred):
    from app.services.lesson_video import LessonVideoService

This bridge will be removed in version 3.0.
"""

import warnings

# Re-export for backward compatibility
from app.services.lesson_video import (
    LessonVideoService,
    VideoGenerationError
)

__all__ = [
    'LessonVideoService',
    'VideoGenerationError',
]

# Show deprecation warning when this module is imported
warnings.warn(
    'lesson_video_service module is deprecated. '
    'Use app.services.lesson_video instead.',
    DeprecationWarning,
    stacklevel=2
)
