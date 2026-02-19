"""
Agent Video Cache Repository

Database access for video caching operations:
- Cached video lookup (agent_video_cache + agent_media_cache)
- Video caching (insert into both tables)
- Cache deletion
- Access count tracking
"""

from typing import Dict, Optional, Any, List

from app.infrastructure.persistence.database.connection import (
    fetch_one, execute_query
)


class AgentVideoCacheRepository:
    """Repository for agent_video_cache and agent_media_cache tables."""

    @staticmethod
    def get_cached_video(
        lesson_id: str,
        model: str = None
    ) -> Optional[Dict]:
        """
        Find cached video for a lesson.

        Args:
            lesson_id: Source lesson UUID
            model: Optional model filter (e.g. sora-2, sora-2-pro)

        Returns:
            Video cache row or None
        """
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

        params: List[Any] = [lesson_id]

        if model:
            query += " AND m.generation_model = %s"
            params.append(model)

        query += " ORDER BY m.created_at DESC LIMIT 1"

        return fetch_one(query, tuple(params))

    @staticmethod
    def increment_access_count(video_id: str) -> None:
        """
        Increment access_count and update last_accessed_at for a video.

        Args:
            video_id: Video UUID
        """
        query = """
            UPDATE agent_media_cache
            SET access_count = access_count + 1,
                last_accessed_at = NOW()
            WHERE media_id = (
                SELECT media_id FROM agent_video_cache WHERE video_id = %s
            )
        """
        execute_query(query, (video_id,))

    @staticmethod
    def insert_media_cache(
        media_id: str,
        content_hash: str,
        lesson_id: str,
        storage_path: str,
        file_size_bytes: int,
        duration_ms: int,
        generation_model: str,
        generation_cost: float
    ) -> None:
        """
        Insert a row into agent_media_cache.

        Args:
            media_id: Media UUID
            content_hash: SHA256 content hash
            lesson_id: Source lesson UUID
            storage_path: Path to stored file
            file_size_bytes: File size in bytes
            duration_ms: Media duration in milliseconds
            generation_model: AI model used
            generation_cost: Cost of generation
        """
        query = """
            INSERT INTO agent_media_cache (
                media_id, content_hash, media_type, source_type, source_id,
                storage_path, file_size_bytes, duration_ms, generation_model,
                generation_cost, status, quality_tier, never_expire
            ) VALUES (
                %s, %s, 'video_explanation', 'lesson', %s,
                %s, %s, %s, %s, %s, 'ready', 3, true
            )
        """
        execute_query(query, (
            media_id, content_hash, lesson_id,
            storage_path, file_size_bytes, duration_ms,
            generation_model, generation_cost
        ))

    @staticmethod
    def insert_video_cache(
        video_id: str,
        media_id: str,
        source_text: str,
        avatar_style: str,
        resolution: str,
        framerate: int,
        render_time_ms: int,
        generation_cost: float
    ) -> None:
        """
        Insert a row into agent_video_cache.

        Args:
            video_id: Video UUID
            media_id: Media UUID (FK to agent_media_cache)
            source_text: Source text used for generation
            avatar_style: Avatar style identifier
            resolution: Video resolution (e.g. '1080p')
            framerate: Video framerate
            render_time_ms: Render time in milliseconds
            generation_cost: Cost of generation
        """
        query = """
            INSERT INTO agent_video_cache (
                video_id, media_id, video_type, source_text,
                avatar_id, avatar_provider, resolution, framerate,
                render_time_ms, generation_cost
            ) VALUES (
                %s, %s, 'explanation', %s,
                %s, 'openai_sora', %s, %s, %s, %s
            )
        """
        execute_query(query, (
            video_id, media_id, source_text,
            avatar_style, resolution, framerate,
            render_time_ms, generation_cost
        ))

    @staticmethod
    def delete_media_cache_for_lesson(
        lesson_id: str,
        model: str = None
    ) -> int:
        """
        Delete cached media for a lesson.

        Args:
            lesson_id: Source lesson UUID
            model: Optional model filter

        Returns:
            Number of rows affected
        """
        query = """
            DELETE FROM agent_media_cache
            WHERE source_id = %s
              AND source_type = 'lesson'
              AND media_type = 'video_explanation'
        """
        params: List[Any] = [lesson_id]

        if model:
            query += " AND generation_model = %s"
            params.append(model)

        return execute_query(query, tuple(params))
