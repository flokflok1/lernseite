"""
LernsystemX Lesson Repository

Data access layer for lessons:
- CRUD operations for lessons
- Lesson content management (video, text, quiz, etc.)
- Lesson ordering within chapters
- Lesson progress tracking

ISO 27001:2013 compliant - Secure lesson data management
Updated: 2025-11-27 (Refactoring: modules → chapters)
"""

from typing import Optional, Dict, List, Any
from datetime import datetime

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query, insert_returning
from app.infrastructure.persistence.repositories.base_repository import BaseRepository


class LessonRepository(BaseRepository):
    """
    Repository for Lesson entity

    Handles all database operations for lessons including:
    - Lesson creation and management
    - Content type support (video, text, quiz, assignment, file)
    - Lesson ordering within chapters
    - Progress tracking
    """

    table_name = 'courses.lessons'

    @classmethod
    def create(cls, lesson_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new lesson

        Args:
            lesson_data: Lesson data including:
                - chapter_id: UUID (required)
                - title: str (required)
                - content_type: str (video, text, quiz, assignment, file)
                - content_url: str (for video/file)
                - content_text: str (for text)
                - quiz_data: dict (for quiz)
                - order_index: int (auto-assigned if not provided)
                - duration_minutes: int
                - is_preview: bool (free preview lesson)

        Returns:
            Created lesson with lesson_id

        Example:
            >>> lesson = LessonRepository.create({
            ...     'chapter_id': 'uuid-here',
            ...     'title': 'Was ist Python?',
            ...     'content_type': 'video',
            ...     'content_url': 'https://...',
            ...     'duration_minutes': 15
            ... })
        """
        # Auto-assign order_index if not provided
        if 'order_index' not in lesson_data:
            max_order_query = """
                SELECT COALESCE(MAX(order_index), 0) + 1 AS next_order
                FROM courses.lessons
                WHERE chapter_id = %s
            """
            result = fetch_one(max_order_query, (lesson_data['chapter_id'],))
            lesson_data['order_index'] = result['next_order'] if result else 1

        query = """
            INSERT INTO lessons (
                chapter_id, title, lesson_type, content,
                order_index, duration_minutes, published, free_preview,
                created_at, updated_at
            ) VALUES (
                %(chapter_id)s, %(title)s, %(lesson_type)s, %(content)s,
                %(order_index)s, %(duration_minutes)s, %(published)s, %(free_preview)s,
                NOW(), NOW()
            )
            RETURNING
                lesson_id, chapter_id, title, lesson_type, content,
                order_index, duration_minutes, published, free_preview,
                created_at, updated_at
        """

        defaults = {
            'lesson_type': 'text',
            'content': None,
            'duration_minutes': 0,
            'published': False,
            'free_preview': False
        }

        params = {**defaults, **lesson_data}

        return insert_returning(query, params)

    @classmethod
    def find_by_id(cls, lesson_id: int) -> Optional[Dict[str, Any]]:
        """
        Find lesson by ID with chapter and course info

        Args:
            lesson_id: Lesson ID

        Returns:
            Lesson dict or None
        """
        query = """
            SELECT
                l.*,
                ch.title AS chapter_title,
                ch.course_id,
                c.title AS course_title
            FROM courses.lessons l
            LEFT JOIN courses.chapters ch ON l.chapter_id = ch.chapter_id
            LEFT JOIN courses.courses c ON ch.course_id = c.course_id
            WHERE l.lesson_id = %s
        """

        return fetch_one(query, (lesson_id,))

    @classmethod
    def find_by_chapter(cls, chapter_id: str) -> List[Dict[str, Any]]:
        """
        Find all lessons for a chapter, ordered by order_index

        Args:
            chapter_id: Chapter UUID

        Returns:
            List of lessons
        """
        query = """
            SELECT l.*
            FROM courses.lessons l
            WHERE l.chapter_id = %s
            ORDER BY l.order_index ASC
        """

        return fetch_all(query, (chapter_id,))

    @classmethod
    def find_by_course(cls, course_id: int) -> List[Dict[str, Any]]:
        """
        Find all lessons for a course, grouped by chapter

        Args:
            course_id: Course ID

        Returns:
            List of lessons with chapter info
        """
        query = """
            SELECT
                l.*,
                ch.title AS chapter_title,
                ch.order_index AS chapter_order
            FROM courses.lessons l
            LEFT JOIN courses.chapters ch ON l.chapter_id = ch.chapter_id
            WHERE ch.course_id = %s
            ORDER BY ch.order_index ASC, l.order_index ASC
        """

        return fetch_all(query, (course_id,))

    @classmethod
    def update(cls, lesson_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update lesson

        Args:
            lesson_id: Lesson ID
            update_data: Fields to update

        Returns:
            Updated lesson or None
        """
        # Don't allow updating these fields directly
        restricted_fields = ['lesson_id', 'chapter_id', 'created_at']
        update_data = {k: v for k, v in update_data.items() if k not in restricted_fields}

        if not update_data:
            return cls.find_by_id(lesson_id)

        # Always update updated_at
        update_data['updated_at'] = datetime.utcnow()

        # Build SET clause
        set_parts = [f"{key} = %({key})s" for key in update_data.keys()]
        set_clause = ", ".join(set_parts)

        query = f"""
            UPDATE courses.lessons
            SET {set_clause}
            WHERE lesson_id = %(lesson_id)s
            RETURNING *
        """

        params = {**update_data, 'lesson_id': lesson_id}

        return insert_returning(query, params)

    @classmethod
    def reorder(cls, chapter_id: int, lesson_orders: List[Dict[str, int]]) -> bool:
        """
        Reorder lessons in a chapter

        Args:
            chapter_id: Chapter UUID
            lesson_orders: List of dicts with 'lesson_id' and 'order_index'

        Returns:
            True if successful

        Example:
            >>> LessonRepository.reorder(1, [
            ...     {'lesson_id': 5, 'order_index': 1},
            ...     {'lesson_id': 3, 'order_index': 2},
            ...     {'lesson_id': 4, 'order_index': 3}
            ... ])
        """
        # Update each lesson's order_index
        for item in lesson_orders:
            query = """
                UPDATE courses.lessons
                SET order_index = %s, updated_at = NOW()
                WHERE lesson_id = %s AND chapter_id = %s
            """
            execute_query(query, (item['order_index'], item['lesson_id'], chapter_id))

        return True

    @classmethod
    def delete(cls, lesson_id: int) -> bool:
        """
        Delete a lesson (cascades to lesson_progress)

        Args:
            lesson_id: Lesson ID

        Returns:
            True if deleted, False otherwise
        """
        query = "DELETE FROM courses.lessons WHERE lesson_id = %s"
        return execute_query(query, (lesson_id,))

    @classmethod
    def mark_completed(cls, lesson_id: int, user_id: int) -> Dict[str, Any]:
        """
        Mark a lesson as completed for a user

        Args:
            lesson_id: Lesson ID
            user_id: User ID

        Returns:
            Lesson progress record
        """
        query = """
            INSERT INTO lesson_progress (
                user_id, lesson_id, completed_at, completion_percentage
            ) VALUES (
                %s, %s, NOW(), 100
            )
            ON CONFLICT (user_id, lesson_id)
            DO UPDATE SET
                completed_at = NOW(),
                completion_percentage = 100
            RETURNING *
        """

        return fetch_one(query, (user_id, lesson_id))

    @classmethod
    def mark_started(cls, lesson_id: str, user_id: str) -> Dict[str, Any]:
        """
        Mark a lesson as started for a user

        Args:
            lesson_id: Lesson ID (UUID string)
            user_id: User ID (UUID string)

        Returns:
            Lesson progress record
        """
        query = """
            INSERT INTO lesson_progress (
                user_id, lesson_id, started_at
            ) VALUES (
                %s, %s, NOW()
            )
            ON CONFLICT (user_id, lesson_id)
            DO UPDATE SET
                started_at = COALESCE(lesson_progress.started_at, NOW())
            RETURNING *
        """

        return fetch_one(query, (user_id, lesson_id))

    @classmethod
    def update_progress(
        cls,
        lesson_id: str,
        user_id: str,
        progress_percentage: float,
        time_spent_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Update progress for a lesson

        Args:
            lesson_id: Lesson ID (UUID string)
            user_id: User ID (UUID string)
            progress_percentage: Progress percentage (0-100)
            time_spent_seconds: Optional time spent in seconds

        Returns:
            Updated lesson progress record
        """
        if time_spent_seconds is not None:
            query = """
                INSERT INTO lesson_progress (
                    user_id, lesson_id, completion_percentage, time_spent_seconds,
                    started_at
                ) VALUES (
                    %s, %s, %s, %s, NOW()
                )
                ON CONFLICT (user_id, lesson_id)
                DO UPDATE SET
                    completion_percentage = %s,
                    time_spent_seconds = COALESCE(lesson_progress.time_spent_seconds, 0) + %s
                RETURNING *
            """
            return fetch_one(query, (
                user_id, lesson_id, progress_percentage, time_spent_seconds,
                progress_percentage, time_spent_seconds
            ))
        else:
            query = """
                INSERT INTO lesson_progress (
                    user_id, lesson_id, completion_percentage, started_at
                ) VALUES (
                    %s, %s, %s, NOW()
                )
                ON CONFLICT (user_id, lesson_id)
                DO UPDATE SET
                    completion_percentage = %s
                RETURNING *
            """
            return fetch_one(query, (user_id, lesson_id, progress_percentage, progress_percentage))

    @classmethod
    def get_user_progress(cls, lesson_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user's progress for a specific lesson

        Args:
            lesson_id: Lesson ID
            user_id: User ID

        Returns:
            Progress dict or None if not started
        """
        query = """
            SELECT lp.*
            FROM lesson_progress lp
            WHERE lp.lesson_id = %s AND lp.user_id = %s
        """

        return fetch_one(query, (lesson_id, user_id))

    @classmethod
    def get_next_lesson(cls, current_lesson_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the next lesson in the course sequence

        Args:
            current_lesson_id: Current lesson ID

        Returns:
            Next lesson dict or None if last lesson
        """
        # First, get current lesson info
        current = cls.find_by_id(current_lesson_id)
        if not current:
            return None

        # Try to get next lesson in same chapter
        query = """
            SELECT l.*
            FROM courses.lessons l
            WHERE l.chapter_id = %s AND l.order_index > %s
            ORDER BY l.order_index ASC
            LIMIT 1
        """

        next_lesson = fetch_one(query, (current['chapter_id'], current['order_index']))

        if next_lesson:
            return next_lesson

        # If no next lesson in chapter, get first lesson of next chapter
        query = """
            SELECT l.*
            FROM courses.lessons l
            INNER JOIN courses.chapters ch ON l.chapter_id = ch.chapter_id
            WHERE ch.course_id = %s AND ch.order_index > %s
            ORDER BY ch.order_index ASC, l.order_index ASC
            LIMIT 1
        """

        chapter_query = "SELECT order_index FROM courses.chapters WHERE chapter_id = %s"
        chapter_result = fetch_one(chapter_query, (current['chapter_id'],))

        if not chapter_result:
            return None

        return fetch_one(query, (current['course_id'], chapter_result['order_index']))

    @classmethod
    def get_previous_lesson(cls, current_lesson_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the previous lesson in the course sequence

        Args:
            current_lesson_id: Current lesson ID

        Returns:
            Previous lesson dict or None if first lesson
        """
        # First, get current lesson info
        current = cls.find_by_id(current_lesson_id)
        if not current:
            return None

        # Try to get previous lesson in same chapter
        query = """
            SELECT l.*
            FROM courses.lessons l
            WHERE l.chapter_id = %s AND l.order_index < %s
            ORDER BY l.order_index DESC
            LIMIT 1
        """

        prev_lesson = fetch_one(query, (current['chapter_id'], current['order_index']))

        if prev_lesson:
            return prev_lesson

        # If no previous lesson in chapter, get last lesson of previous chapter
        query = """
            SELECT l.*
            FROM courses.lessons l
            INNER JOIN courses.chapters ch ON l.chapter_id = ch.chapter_id
            WHERE ch.course_id = %s AND ch.order_index < %s
            ORDER BY ch.order_index DESC, l.order_index DESC
            LIMIT 1
        """

        chapter_query = "SELECT order_index FROM courses.chapters WHERE chapter_id = %s"
        chapter_result = fetch_one(chapter_query, (current['chapter_id'],))

        if not chapter_result:
            return None

        return fetch_one(query, (current['course_id'], chapter_result['order_index']))
