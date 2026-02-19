"""
Lesson Content Repository

Database access for lesson explanations and audio cache:
- List explanations for a lesson
- Get/update/delete individual explanations
- Get cached audio for a lesson
"""

from typing import Optional, List, Dict, Any

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all


class LessonContentRepository:
    """Repository for lesson explanations and audio cache."""

    @staticmethod
    def list_explanations(lesson_id: str) -> List[Dict[str, Any]]:
        """
        List all explanations for a lesson.

        Args:
            lesson_id: Lesson UUID

        Returns:
            List of explanation records ordered by created_at DESC
        """
        query = """
            SELECT
                explanation_id,
                title,
                style,
                audio_url,
                tokens_used,
                created_at,
                updated_at
            FROM lesson_explanations
            WHERE lesson_id = %s
            ORDER BY created_at DESC
        """
        return fetch_all(query, (lesson_id,))

    @staticmethod
    def get_explanation(explanation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific lesson explanation by ID.

        Args:
            explanation_id: Explanation UUID

        Returns:
            Explanation record or None
        """
        query = """
            SELECT
                explanation_id,
                lesson_id,
                title,
                style,
                explanation_data,
                audio_url,
                audio_duration_seconds,
                tokens_used,
                model_used,
                created_at,
                updated_at
            FROM lesson_explanations
            WHERE explanation_id = %s
        """
        return fetch_one(query, (explanation_id,))

    @staticmethod
    def update_explanation_title(
        explanation_id: str, title: str
    ) -> Optional[Dict[str, Any]]:
        """
        Update lesson explanation title.

        Args:
            explanation_id: Explanation UUID
            title: New title

        Returns:
            Updated record with explanation_id and title, or None
        """
        query = """
            UPDATE lesson_explanations
            SET title = %s
            WHERE explanation_id = %s
            RETURNING explanation_id, title
        """
        return fetch_one(query, (title, explanation_id))

    @staticmethod
    def delete_explanation(explanation_id: str) -> Optional[Dict[str, Any]]:
        """
        Delete a lesson explanation.

        Args:
            explanation_id: Explanation UUID

        Returns:
            Deleted record with explanation_id, or None
        """
        query = """
            DELETE FROM lesson_explanations
            WHERE explanation_id = %s
            RETURNING explanation_id
        """
        return fetch_one(query, (explanation_id,))

    @staticmethod
    def get_cached_audio(lesson_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached audio for a lesson from TTS/media cache.

        Args:
            lesson_id: Lesson UUID (used as source_id)

        Returns:
            Audio cache record or None
        """
        query = """
            SELECT
                t.tts_id,
                m.storage_path,
                m.file_size_bytes,
                m.duration_ms
            FROM agent_tts_cache t
            JOIN agent_media_cache m ON t.media_id = m.media_id
            WHERE m.source_id = %s
              AND m.status = 'ready'
            ORDER BY m.created_at DESC
            LIMIT 1
        """
        return fetch_one(query, (lesson_id,))
