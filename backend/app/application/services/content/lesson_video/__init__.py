"""
LessonVideo Service Package

Modular service for generating and caching lesson explanation videos using Sora 2.

Usage:
    from app.application.services.content.lesson_video import LessonVideoService

    # Generate lesson video with sora-2 (default) or sora-2-pro
    video = await LessonVideoService.generate_lesson_video(
        lesson_id="uuid",
        lesson_title="Bezugskalkulation",
        teaching_steps=[...],
        avatar_style="professional_teacher"
    )

    # Get cached video
    video = LessonVideoService.get_cached_video(lesson_id)
"""

from app.application.services.content.lesson_video.pipeline.orchestration import LessonVideoService
from app.application.services.content.lesson_video.exceptions import VideoGenerationError

__all__ = [
    'LessonVideoService',
    'VideoGenerationError',
]
