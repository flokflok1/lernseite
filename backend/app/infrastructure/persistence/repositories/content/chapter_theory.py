"""
Chapter Theory Repository

Repository for managing chapter theory records in the database.
Chapter theories are AI-generated educational content with different styles
(adhs, detailed, short, exam_focus, standard).

DB Table: courses.chapter_theory
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.database.connection import (
    fetch_one,
    fetch_all,
    execute_query
)

logger = logging.getLogger(__name__)


class ChapterTheoryRepository(BaseRepository):
    """Repository for chapter theory operations."""

    @staticmethod
    def list_by_chapter(chapter_id: str) -> List[Dict[str, Any]]:
        """
        List all theories for a chapter.

        Args:
            chapter_id: UUID of the chapter

        Returns:
            List of theory records, ordered by created_at DESC
        """
        query = """
            SELECT
                theory_id, chapter_id, style, theory_data,
                audio_url, audio_duration_seconds, tokens_used,
                model_used, generated_by,
                created_at, updated_at
            FROM courses.chapter_theory
            WHERE chapter_id = %s
            ORDER BY created_at DESC
        """
        return fetch_all(query, (chapter_id,))

    @staticmethod
    def get_by_id(theory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get chapter theory by ID.

        Args:
            theory_id: UUID of the theory record

        Returns:
            Theory record or None if not found
        """
        query = """
            SELECT
                theory_id, chapter_id, style, theory_data,
                audio_url, audio_duration_seconds, tokens_used,
                model_used, generated_by,
                created_at, updated_at
            FROM courses.chapter_theory
            WHERE theory_id = %s
        """
        return fetch_one(query, (theory_id,))

    @staticmethod
    def get_by_chapter_and_style(chapter_id: str, style: str) -> Optional[Dict[str, Any]]:
        """
        Get chapter theory by chapter ID and style.

        Args:
            chapter_id: UUID of the chapter
            style: Theory style (adhs, detailed, short, exam_focus, standard)

        Returns:
            Theory record or None if not found
        """
        query = """
            SELECT
                theory_id, chapter_id, style, theory_data,
                audio_url, audio_duration_seconds, tokens_used,
                model_used, generated_by,
                created_at, updated_at
            FROM courses.chapter_theory
            WHERE chapter_id = %s AND style = %s
            ORDER BY created_at DESC
            LIMIT 1
        """
        return fetch_one(query, (chapter_id, style))

    @staticmethod
    def create(chapter_id: str, style: str, theory_data: Dict,
               audio_url: Optional[str] = None, audio_duration_seconds: Optional[int] = None,
               tokens_used: int = 0, model_used: Optional[str] = None,
               generated_by: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new chapter theory record.

        Args:
            chapter_id: UUID of the chapter
            style: Theory style
            theory_data: JSONB theory content
            audio_url: Optional audio URL
            audio_duration_seconds: Optional audio duration
            tokens_used: Token cost for generation
            model_used: AI model used for generation
            generated_by: User ID who generated this

        Returns:
            Created theory record
        """
        query = """
            INSERT INTO courses.chapter_theory
            (chapter_id, style, theory_data, audio_url, audio_duration_seconds,
             tokens_used, model_used, generated_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING
                theory_id, chapter_id, style, theory_data,
                audio_url, audio_duration_seconds, tokens_used,
                model_used, generated_by,
                created_at, updated_at
        """
        return fetch_one(query, (
            chapter_id, style, theory_data, audio_url,
            audio_duration_seconds, tokens_used, model_used, generated_by
        ))

    @staticmethod
    def delete_by_id(theory_id: str) -> bool:
        """
        Delete a specific theory by ID.

        Args:
            theory_id: UUID of the theory

        Returns:
            True if deleted, False if not found
        """
        query = """
            DELETE FROM courses.chapter_theory
            WHERE theory_id = %s
        """
        result = execute_query(query, (theory_id,))
        return result.rowcount > 0 if result else False

    @staticmethod
    def delete_by_chapter_and_style(chapter_id: str, style: Optional[str] = None) -> bool:
        """
        Delete chapter theory by chapter and optional style.

        Args:
            chapter_id: UUID of the chapter
            style: Optional style filter (if None, deletes ALL styles)

        Returns:
            True if any deleted, False otherwise
        """
        if style:
            query = """
                DELETE FROM courses.chapter_theory
                WHERE chapter_id = %s AND style = %s
            """
            params = (chapter_id, style)
        else:
            query = """
                DELETE FROM courses.chapter_theory
                WHERE chapter_id = %s
            """
            params = (chapter_id,)

        result = execute_query(query, params)
        return result.rowcount > 0 if result else False
