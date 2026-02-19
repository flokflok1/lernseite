"""
Video caching and persistence module.

Manages caching of generated videos in agent_media_cache and agent_video_cache tables.
"""

import uuid
import hashlib
from typing import Dict, Any, Optional

from app.infrastructure.persistence.repositories.agent.video_cache import AgentVideoCacheRepository
from app.application.services.content.lesson_video.exceptions import VideoGenerationError
from app.application.services.content.lesson_video.models import DEFAULT_MODEL


class VideoCache:
    """Handles video caching operations."""

    @staticmethod
    def get_cached_video(lesson_id: str, model: str = None) -> Optional[Dict[str, Any]]:
        """
        Get cached video for a lesson if it exists.

        Args:
            lesson_id: UUID of the lesson
            model: Optional model filter (sora-2 or sora-2-pro)

        Returns:
            Cached video info or None if not cached
        """
        try:
            result = AgentVideoCacheRepository.get_cached_video(lesson_id, model)

            if result:
                # Update access count
                AgentVideoCacheRepository.increment_access_count(result['video_id'])
                return dict(result)

            return None

        except Exception as e:
            print(f'Error getting cached video: {e}')
            return None

    @staticmethod
    def cache_video(
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

        Raises:
            VideoGenerationError: If caching fails
        """
        try:
            media_id = str(uuid.uuid4())
            video_id = str(uuid.uuid4())
            content_hash = metadata.get('content_hash', hashlib.sha256(lesson_id.encode()).hexdigest())
            model = metadata.get('model', DEFAULT_MODEL)

            # Insert into agent_media_cache
            AgentVideoCacheRepository.insert_media_cache(
                media_id=media_id,
                content_hash=content_hash,
                lesson_id=lesson_id,
                storage_path=video_path,
                file_size_bytes=metadata.get('file_size', 0),
                duration_ms=metadata.get('duration_ms', 0),
                generation_model=model,
                generation_cost=metadata.get('cost', 0)
            )

            # Insert into agent_video_cache
            AgentVideoCacheRepository.insert_video_cache(
                video_id=video_id,
                media_id=media_id,
                source_text=metadata.get('source_text', ''),
                avatar_style=metadata.get('avatar_style', 'professional_teacher'),
                resolution=metadata.get('resolution', '1080p'),
                framerate=metadata.get('framerate', 30),
                render_time_ms=metadata.get('render_time_ms', 0),
                generation_cost=metadata.get('cost', 0)
            )

            return video_id

        except Exception as e:
            raise VideoGenerationError(f'Failed to cache video: {str(e)}')

    @staticmethod
    def delete_cached_video(lesson_id: str, model: str = None) -> bool:
        """
        Delete cached video for a lesson.

        Args:
            lesson_id: UUID of the lesson
            model: Optional - delete only for specific model

        Returns:
            True if deleted, False if not found
        """
        try:
            result = AgentVideoCacheRepository.delete_media_cache_for_lesson(
                lesson_id, model
            )
            return result > 0

        except Exception as e:
            print(f'Error deleting cached video: {e}')
            return False
