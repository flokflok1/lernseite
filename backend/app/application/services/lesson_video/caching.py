"""
Video caching and persistence module.

Manages caching of generated videos in agent_media_cache and agent_video_cache tables.
"""

import uuid
import hashlib
from typing import Dict, Any, Optional

from app.infrastructure.persistence.repositories.base_repository import BaseRepository
from app.application.services.lesson_video.exceptions import VideoGenerationError
from app.application.services.lesson_video.models import DEFAULT_MODEL


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
            query = """
                SELECT
                    v.video_id,
                    v.video_type,
                    v.resolution,
                    v.thumbnail_path,
                    v.render_time_ms,
                    v.generation_cost,
                    v.avatar_id as avatar_style,
                    m.storage_path,
                    m.file_size_bytes,
                    m.duration_ms,
                    m.status,
                    m.access_count,
                    m.generation_model as model,
                    m.created_at
                FROM agent_video_cache v
                JOIN agent_media_cache m ON v.media_id = m.media_id
                WHERE m.source_id = %s
                  AND m.status = 'ready'
            """

            params = [lesson_id]

            if model:
                query += " AND m.generation_model = %s"
                params.append(model)

            query += " ORDER BY m.created_at DESC LIMIT 1"

            result = BaseRepository.fetch_one(query, tuple(params))

            if result:
                # Update access count
                update_query = """
                    UPDATE agent_media_cache
                    SET access_count = access_count + 1,
                        last_accessed_at = NOW()
                    WHERE media_id = (
                        SELECT media_id FROM agent_video_cache WHERE video_id = %s
                    )
                """
                BaseRepository.execute(update_query, (result['video_id'],))

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
            media_query = """
                INSERT INTO agent_media_cache (
                    media_id, content_hash, media_type, source_type, source_id,
                    storage_path, file_size_bytes, duration_ms, generation_model,
                    generation_cost, status, quality_tier, never_expire
                ) VALUES (
                    %s, %s, 'video_explanation', 'lesson', %s,
                    %s, %s, %s, %s, %s, 'ready', 3, true
                )
            """

            BaseRepository.execute(media_query, (
                media_id,
                content_hash,
                lesson_id,
                video_path,
                metadata.get('file_size', 0),
                metadata.get('duration_ms', 0),
                model,
                metadata.get('cost', 0)
            ))

            # Insert into agent_video_cache
            video_query = """
                INSERT INTO agent_video_cache (
                    video_id, media_id, video_type, source_text,
                    avatar_id, avatar_provider, resolution, framerate,
                    render_time_ms, generation_cost
                ) VALUES (
                    %s, %s, 'explanation', %s,
                    %s, 'openai_sora', %s, %s, %s, %s
                )
            """

            BaseRepository.execute(video_query, (
                video_id,
                media_id,
                metadata.get('source_text', ''),
                metadata.get('avatar_style', 'professional_teacher'),
                metadata.get('resolution', '1080p'),
                metadata.get('framerate', 30),
                metadata.get('render_time_ms', 0),
                metadata.get('cost', 0)
            ))

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
            query = """
                DELETE FROM agent_media_cache
                WHERE source_id = %s
                  AND source_type = 'lesson'
                  AND media_type = 'video_explanation'
            """
            params = [lesson_id]

            if model:
                query += " AND generation_model = %s"
                params.append(model)

            result = BaseRepository.execute(query, tuple(params))
            return result > 0

        except Exception as e:
            print(f'Error deleting cached video: {e}')
            return False
