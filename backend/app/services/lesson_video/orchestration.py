"""
High-level orchestration for lesson video generation.

Main service class that coordinates prompt generation, video synthesis, and caching.
"""

from typing import Dict, Any, List

from app.services.lesson_video.generation import SoraVideoGenerator
from app.services.lesson_video.caching import VideoCache
from app.services.lesson_video.status import StatusChecker
from app.services.lesson_video.helpers import (
    generate_content_hash,
    generate_video_prompt,
    combine_teaching_steps,
    estimate_video_duration
)
from app.services.lesson_video.models import DEFAULT_MODEL, SORA_MODELS


class LessonVideoService:
    """
    Service for generating and caching lesson explanation videos.

    Uses Sora 2 for video + audio generation (synced together).
    Videos are cached and can be replayed without regeneration.
    """

    # Delegate to model/helper classes
    @classmethod
    def get_available_models(cls) -> Dict[str, Any]:
        """
        Get available Sora models with specifications.

        Returns:
            Dictionary of model info
        """
        return SoraVideoGenerator.get_available_models()

    @classmethod
    def generate_video_prompt(
        cls,
        lesson_title: str,
        speech_text: str,
        whiteboard_content: str,
        avatar_style: str = 'professional_teacher',
        language: str = 'de'
    ) -> str:
        """
        Generate a Sora 2 video prompt for a teaching step.

        Args:
            lesson_title: Title of the lesson
            speech_text: What the teacher should say (will be spoken!)
            whiteboard_content: What should be written on the board
            avatar_style: Style of the avatar teacher
            language: Language for speech (default: German)

        Returns:
            Sora 2 prompt string
        """
        return generate_video_prompt(
            lesson_title=lesson_title,
            speech_text=speech_text,
            whiteboard_content=whiteboard_content,
            avatar_style=avatar_style,
            language=language
        )

    @classmethod
    async def generate_sora_video(
        cls,
        prompt: str,
        duration_seconds: int = 15,
        resolution: str = None,
        model: str = 'sora-2'
    ) -> Dict[str, Any]:
        """
        Generate video with synced audio using OpenAI Sora 2.

        Args:
            prompt: Video generation prompt (includes speech text)
            duration_seconds: Video duration (5-60s for sora-2, up to 120s for pro)
            resolution: Video resolution (720p, 1080p, 4k)
            model: Sora model ('sora-2' or 'sora-2-pro')

        Returns:
            {
                'video_url': str,
                'video_id': str,
                'duration_seconds': int,
                'resolution': str,
                'model': str,
                'has_audio': True,
                'generation_time_ms': int,
                'cost': float,
                'status': str
            }
        """
        return await SoraVideoGenerator.generate_sora_video(
            prompt=prompt,
            duration_seconds=duration_seconds,
            resolution=resolution,
            model=model
        )

    @classmethod
    def get_cached_video(cls, lesson_id: str, model: str = None) -> Dict[str, Any]:
        """
        Get cached video for a lesson if it exists.

        Args:
            lesson_id: UUID of the lesson
            model: Optional model filter (sora-2 or sora-2-pro)

        Returns:
            Cached video info or None if not cached
        """
        return VideoCache.get_cached_video(lesson_id, model)

    @classmethod
    def cache_video(
        cls,
        lesson_id: str,
        video_path: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Cache a generated video for a lesson.

        Args:
            lesson_id: UUID of the lesson
            video_path: Path to the video file (includes audio)
            metadata: Video metadata (duration, resolution, model, etc.)

        Returns:
            video_id of the cached video
        """
        return VideoCache.cache_video(lesson_id, video_path, metadata)

    @classmethod
    def delete_cached_video(cls, lesson_id: str, model: str = None) -> bool:
        """
        Delete cached video for a lesson.

        Args:
            lesson_id: UUID of the lesson
            model: Optional - delete only for specific model

        Returns:
            True if deleted, False if not found
        """
        return VideoCache.delete_cached_video(lesson_id, model)

    @classmethod
    def get_generation_status(cls, lesson_id: str) -> Dict[str, Any]:
        """
        Get the status of video generation for a lesson.

        Args:
            lesson_id: UUID of the lesson

        Returns:
            Status dictionary with progress and video info
        """
        return StatusChecker.get_generation_status(lesson_id)

    @classmethod
    def compare_models(cls) -> Dict[str, Any]:
        """
        Compare available Sora models.

        Returns:
            Comparison information for UI selection
        """
        return StatusChecker.compare_models()

    @classmethod
    async def generate_lesson_video(
        cls,
        lesson_id: str,
        lesson_title: str,
        teaching_steps: List[Dict[str, Any]],
        avatar_style: str = 'professional_teacher',
        model: str = 'sora-2',
        force_regenerate: bool = False,
        language: str = 'de'
    ) -> Dict[str, Any]:
        """
        Generate a complete lesson video with Sora 2.

        Sora 2 generates video WITH synced audio, so everything
        comes out as one file - no separate TTS needed!

        Args:
            lesson_id: UUID of the lesson
            lesson_title: Title of the lesson
            teaching_steps: List of teaching step dictionaries with:
                - speech: Text the teacher speaks
                - whiteboard: List of whiteboard actions
                - animation: Teacher animation type
            avatar_style: Style of the teacher avatar
            model: Sora model ('sora-2' or 'sora-2-pro')
            force_regenerate: If True, regenerate even if cached
            language: Language for speech (default: 'de' for German)

        Returns:
            {
                'video_id': str,
                'video_url': str,       # Video includes audio!
                'duration_ms': int,
                'model': str,
                'from_cache': bool,
                'cost': float,
                'status': str
            }
        """
        # Validate model
        if model not in SORA_MODELS:
            model = DEFAULT_MODEL

        # Check cache first
        if not force_regenerate:
            cached = cls.get_cached_video(lesson_id, model)
            if cached:
                return {
                    'video_id': cached['video_id'],
                    'video_url': cached['storage_path'],
                    'duration_ms': cached['duration_ms'],
                    'model': cached.get('model', model),
                    'avatar_style': cached.get('avatar_style', avatar_style),
                    'from_cache': True,
                    'cost': 0,
                    'status': 'ready',
                    'has_audio': True
                }

        # Combine teaching steps into unified content
        combined_speech, combined_whiteboard = combine_teaching_steps(teaching_steps)

        # Estimate duration based on speech length
        estimated_duration = estimate_video_duration(combined_speech, model)

        # Generate the video prompt
        video_prompt = cls.generate_video_prompt(
            lesson_title=lesson_title,
            speech_text=combined_speech,
            whiteboard_content=combined_whiteboard,
            avatar_style=avatar_style,
            language=language
        )

        # Generate video with Sora (includes synced audio!)
        video_result = await cls.generate_sora_video(
            prompt=video_prompt,
            duration_seconds=estimated_duration,
            model=model
        )

        # Generate content hash for caching
        content_hash = generate_content_hash(lesson_id, teaching_steps, avatar_style, model)

        result = {
            'lesson_id': lesson_id,
            'lesson_title': lesson_title,
            'video_id': video_result['video_id'],
            'video_url': video_result.get('video_url'),
            'duration_ms': video_result['duration_seconds'] * 1000,
            'model': model,
            'model_info': SORA_MODELS[model],
            'avatar_style': avatar_style,
            'content_hash': content_hash,
            'has_audio': True,  # Sora 2 always includes synced audio
            'from_cache': False,
            'cost': video_result['cost'],
            'status': video_result['status']
        }

        # Handle different statuses
        if video_result['status'] == 'ready' and video_result.get('video_url'):
            result['message'] = 'Video generated successfully with synchronized audio'

        elif video_result['status'] == 'api_not_available':
            result['message'] = video_result.get('message', 'Sora 2 API not available. Using fallback rendering.')
            result['fallback'] = True

        elif video_result['status'] == 'api_error':
            result['message'] = video_result.get('error', 'API error occurred')
            result['error'] = video_result.get('error')

        elif video_result['status'] == 'timeout':
            result['message'] = 'Video generation timed out. Please try again.'
            result['error'] = 'timeout'

        return result
