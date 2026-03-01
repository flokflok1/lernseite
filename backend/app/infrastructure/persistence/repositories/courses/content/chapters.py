"""
LernsystemX Chapter Repository

Data access layer for course chapters:
- CRUD operations for chapters
- Chapter ordering and structure
- Chapter-to-course relationship management

ISO 27001:2013 compliant - Secure chapter data management
Updated: 2025-11-27 (Refactoring: modules → chapters)
"""

from typing import Optional, Dict, List, Any
from datetime import datetime

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query, insert_returning
from app.infrastructure.persistence.repositories.core.base import BaseRepository


class ChapterRepository(BaseRepository):
    """
    Repository for Chapter entity

    Handles all database operations for course chapters including:
    - Chapter creation and management
    - Chapter ordering
    - Lesson count tracking
    """

    table_name = 'courses.chapters'

    @classmethod
    def create(cls, chapter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new chapter

        Args:
            chapter_data: Chapter data including:
                - course_id: UUID (required)
                - title: str (required)
                - description: str
                - order_index: int (auto-assigned if not provided)
                - duration_minutes: int

        Returns:
            Created chapter with chapter_id

        Example:
            >>> chapter = ChapterRepository.create({
            ...     'course_id': 'uuid-here',
            ...     'title': 'Einführung',
            ...     'description': 'Grundlagen und erste Schritte'
            ... })
        """
        # Auto-assign order_index if not provided
        if 'order_index' not in chapter_data:
            max_order_query = """
                SELECT COALESCE(MAX(order_index), 0) + 1 AS next_order
                FROM courses.chapters
                WHERE course_id = %s
            """
            result = fetch_one(max_order_query, (chapter_data['course_id'],))
            chapter_data['order_index'] = result['next_order'] if result else 1

        defaults = {
            'description': None,
            'duration_minutes': 0,
            'has_video': False,
            'has_quiz': False,
            'has_exam': False,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }

        params = {**defaults, **chapter_data}

        return insert_returning(
            'courses.chapters',
            params,
            'chapter_id, course_id, title, description, order_index, duration_minutes, has_video, has_quiz, has_exam, created_at, updated_at'
        )

    @classmethod
    def find_by_id(cls, chapter_id: str) -> Optional[Dict[str, Any]]:
        """
        Find chapter by ID with lesson count

        Args:
            chapter_id: Chapter UUID

        Returns:
            Chapter dict with lesson_count or None
        """
        query = """
            SELECT
                c.*,
                cr.title AS course_title,
                (SELECT COUNT(*) FROM courses.lessons WHERE chapter_id = c.chapter_id) AS lesson_count
            FROM courses.chapters c
            LEFT JOIN courses.courses cr ON c.course_id = cr.course_id
            WHERE c.chapter_id = %s
        """

        return fetch_one(query, (chapter_id,))

    @classmethod
    def find_by_course(cls, course_id: str) -> List[Dict[str, Any]]:
        """
        Find all chapters for a course, ordered by order_index

        Args:
            course_id: Course UUID

        Returns:
            List of chapters with lesson counts
        """
        query = """
            SELECT
                c.*,
                (SELECT COUNT(*) FROM courses.lessons WHERE chapter_id = c.chapter_id) AS lesson_count,
                (SELECT SUM(duration_minutes) FROM courses.lessons WHERE chapter_id = c.chapter_id) AS total_lesson_duration
            FROM courses.chapters c
            WHERE c.course_id = %s
            ORDER BY c.order_index ASC
        """

        return fetch_all(query, (course_id,))

    @classmethod
    def update(cls, chapter_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update chapter

        Args:
            chapter_id: Chapter UUID
            update_data: Fields to update

        Returns:
            Updated chapter or None
        """
        # Don't allow updating these fields directly
        restricted_fields = ['chapter_id', 'course_id', 'created_at']
        update_data = {k: v for k, v in update_data.items() if k not in restricted_fields}

        if not update_data:
            return cls.find_by_id(chapter_id)

        # Always update updated_at
        update_data['updated_at'] = datetime.utcnow()

        # Build SET clause with positional placeholders
        keys = list(update_data.keys())
        set_parts = [f"{key} = %s" for key in keys]
        set_clause = ", ".join(set_parts)

        query = f"""
            UPDATE courses.chapters
            SET {set_clause}
            WHERE chapter_id = %s
            RETURNING *
        """

        # Build params as tuple (values in order, then chapter_id)
        params = tuple(update_data[k] for k in keys) + (chapter_id,)

        return fetch_one(query, params)

    @classmethod
    def reorder(cls, course_id: str, chapter_orders: List[Dict[str, Any]]) -> bool:
        """
        Reorder chapters in a course

        Args:
            course_id: Course UUID
            chapter_orders: List of dicts with 'chapter_id' and 'order_index'

        Returns:
            True if successful

        Example:
            >>> ChapterRepository.reorder('uuid', [
            ...     {'chapter_id': 'uuid-3', 'order_index': 1},
            ...     {'chapter_id': 'uuid-1', 'order_index': 2},
            ...     {'chapter_id': 'uuid-2', 'order_index': 3}
            ... ])
        """
        # Update each chapter's order_index
        for item in chapter_orders:
            query = """
                UPDATE courses.chapters
                SET order_index = %s, updated_at = NOW()
                WHERE chapter_id = %s AND course_id = %s
            """
            execute_query(query, (item['order_index'], item['chapter_id'], course_id))

        return True

    @classmethod
    def delete(cls, chapter_id: str) -> bool:
        """
        Delete a chapter (cascades to lessons)

        Args:
            chapter_id: Chapter UUID

        Returns:
            True if deleted, False otherwise
        """
        query = "DELETE FROM courses.chapters WHERE chapter_id = %s"
        return execute_query(query, (chapter_id,))

    @classmethod
    def get_chapter_progress(cls, chapter_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get user's progress for a specific chapter

        Args:
            chapter_id: Chapter UUID
            user_id: User UUID

        Returns:
            Progress dict with completion stats
        """
        query = """
            SELECT
                c.chapter_id,
                c.title,
                COUNT(l.lesson_id) AS total_lessons,
                COUNT(CASE WHEN lc.completed_at IS NOT NULL THEN 1 END) AS completed_lessons,
                CASE
                    WHEN COUNT(l.lesson_id) > 0
                    THEN (COUNT(CASE WHEN lc.completed_at IS NOT NULL THEN 1 END)::FLOAT / COUNT(l.lesson_id)::FLOAT * 100)
                    ELSE 0
                END AS progress_percentage
            FROM courses.chapters c
            LEFT JOIN courses.lessons l ON c.chapter_id = l.chapter_id
            LEFT JOIN courses.lesson_completions lc ON l.lesson_id = lc.lesson_id AND lc.user_id = %s
            WHERE c.chapter_id = %s
            GROUP BY c.chapter_id, c.title
        """

        result = fetch_one(query, (user_id, chapter_id))

        if not result:
            return {}

        return {
            'chapter_id': result['chapter_id'],
            'title': result['title'],
            'total_lessons': result['total_lessons'] or 0,
            'completed_lessons': result['completed_lessons'] or 0,
            'progress_percentage': float(result['progress_percentage']) if result['progress_percentage'] else 0.0
        }
