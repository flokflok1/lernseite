"""
Status checking and comparison module.

Provides video generation status tracking and model comparison utilities.
"""

from typing import Dict, Any

from app.services.lesson_video.models import SORA_MODELS, DEFAULT_MODEL
from app.services.lesson_video.caching import VideoCache


class StatusChecker:
    """Handles status checking for video generation."""

    @staticmethod
    def get_generation_status(lesson_id: str) -> Dict[str, Any]:
        """
        Get the status of video generation for a lesson.

        Args:
            lesson_id: UUID of the lesson

        Returns:
            {
                'status': 'pending' | 'generating' | 'ready' | 'failed',
                'progress': 0-100,
                'video_id': str or None,
                'model': str or None,
                'error': str or None
            }
        """
        cached = VideoCache.get_cached_video(lesson_id)

        if cached:
            return {
                'status': cached.get('status', 'ready'),
                'progress': 100,
                'video_id': cached['video_id'],
                'model': cached.get('model'),
                'has_audio': True,
                'error': None
            }

        # Check if generation is in progress (would check job queue in production)
        return {
            'status': 'pending',
            'progress': 0,
            'video_id': None,
            'model': None,
            'has_audio': None,
            'error': None
        }

    @staticmethod
    def compare_models() -> Dict[str, Any]:
        """
        Compare available Sora models.

        Returns:
            Comparison information for UI selection
        """
        return {
            'models': SORA_MODELS,
            'default': DEFAULT_MODEL,
            'recommendation': {
                'for_quick_preview': 'sora-2',
                'for_production': 'sora-2-pro',
                'description': 'sora-2 is faster and cheaper, sora-2-pro has higher quality'
            }
        }
