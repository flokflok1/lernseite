"""
Chapter Repository (DB-First Architecture)

All chapter data loaded dynamically from database.
NO hardcoded values or configurations.

Uses Repository Pattern with direct SQL (NO ORM).
"""

from typing import List, Optional, Dict, Any
from src.infrastructure.database.base_repository import BaseRepository
from src.api.content.courses.chapters.domain.entities.chapter import Chapter


class ChapterRepository(BaseRepository):
    """
    Chapter repository for database access.

    ALL data loaded from database dynamically.
    NO hardcoded chapter lists or configurations.
    """

    @staticmethod
    def find_by_id(chapter_id: str) -> Optional[Chapter]:
        """
        Find chapter by ID.

        Args:
            chapter_id: Chapter UUID

        Returns:
            Chapter entity or None
        """
        query = """
            SELECT
                chapter_id, course_id, title, slug, description,
                order_index, duration_minutes, estimated_duration,
                prerequisite_chapter_id, published,
                has_video, has_quiz, has_exam,
                created_at, updated_at
            FROM courses.chapters
            WHERE chapter_id = %s
        """
        row = ChapterRepository.fetch_one(query, (chapter_id,))

        if row:
            return Chapter(**row)
        return None

    @staticmethod
    def find_by_course_id(
        course_id: str,
        published_only: bool = False
    ) -> List[Chapter]:
        """
        Find chapters by course ID.

        Args:
            course_id: Course UUID
            published_only: Only return published chapters

        Returns:
            List of chapters ordered by order_index
        """
        query = """
            SELECT
                chapter_id, course_id, title, slug, description,
                order_index, duration_minutes, estimated_duration,
                prerequisite_chapter_id, published,
                has_video, has_quiz, has_exam,
                created_at, updated_at
            FROM courses.chapters
            WHERE course_id = %s
        """
        params = [course_id]

        if published_only:
            query += " AND published = TRUE"

        query += " ORDER BY order_index ASC"

        rows = ChapterRepository.fetch_all(query, tuple(params))
        return [Chapter(**row) for row in rows]

    @staticmethod
    def find_all(
        course_id: Optional[str] = None,
        published: Optional[bool] = None,
        has_video: Optional[bool] = None,
        has_quiz: Optional[bool] = None,
        has_exam: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Chapter]:
        """
        Find chapters with dynamic filters.

        ALL filter values come from database or parameters.
        NO hardcoded filter lists.

        Args:
            course_id: Filter by course
            published: Filter by published status
            has_video: Filter by video content
            has_quiz: Filter by quiz content
            has_exam: Filter by exam content
            limit: Result limit
            offset: Result offset

        Returns:
            List of chapter entities
        """
        query = """
            SELECT
                chapter_id, course_id, title, slug, description,
                order_index, duration_minutes, estimated_duration,
                prerequisite_chapter_id, published,
                has_video, has_quiz, has_exam,
                created_at, updated_at
            FROM courses.chapters
            WHERE 1=1
        """
        params = []

        # Dynamic filters - NO hardcoded values
        if course_id:
            query += " AND course_id = %s"
            params.append(course_id)

        if published is not None:
            query += " AND published = %s"
            params.append(published)

        if has_video is not None:
            query += " AND has_video = %s"
            params.append(has_video)

        if has_quiz is not None:
            query += " AND has_quiz = %s"
            params.append(has_quiz)

        if has_exam is not None:
            query += " AND has_exam = %s"
            params.append(has_exam)

        query += " ORDER BY course_id, order_index ASC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        rows = ChapterRepository.fetch_all(query, tuple(params))
        return [Chapter(**row) for row in rows]

    @staticmethod
    def create(chapter: Chapter) -> Chapter:
        """
        Create new chapter.

        Args:
            chapter: Chapter entity to create

        Returns:
            Created chapter with DB-generated fields
        """
        query = """
            INSERT INTO courses.chapters (
                chapter_id, course_id, title, slug, description,
                order_index, duration_minutes, estimated_duration,
                prerequisite_chapter_id, published,
                has_video, has_quiz, has_exam,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
            )
            RETURNING
                chapter_id, course_id, title, slug, description,
                order_index, duration_minutes, estimated_duration,
                prerequisite_chapter_id, published,
                has_video, has_quiz, has_exam,
                created_at, updated_at
        """
        params = (
            chapter.chapter_id,
            chapter.course_id,
            chapter.title,
            chapter.slug,
            chapter.description,
            chapter.order_index,
            chapter.duration_minutes,
            chapter.estimated_duration,
            chapter.prerequisite_chapter_id,
            chapter.published,
            chapter.has_video,
            chapter.has_quiz,
            chapter.has_exam,
        )

        row = ChapterRepository.execute_returning(query, params)
        return Chapter(**row) if row else chapter

    @staticmethod
    def update(chapter: Chapter) -> Chapter:
        """
        Update existing chapter.

        Args:
            chapter: Chapter entity with updates

        Returns:
            Updated chapter
        """
        query = """
            UPDATE courses.chapters SET
                title = %s,
                slug = %s,
                description = %s,
                order_index = %s,
                duration_minutes = %s,
                estimated_duration = %s,
                prerequisite_chapter_id = %s,
                published = %s,
                has_video = %s,
                has_quiz = %s,
                has_exam = %s,
                updated_at = NOW()
            WHERE chapter_id = %s
            RETURNING
                chapter_id, course_id, title, slug, description,
                order_index, duration_minutes, estimated_duration,
                prerequisite_chapter_id, published,
                has_video, has_quiz, has_exam,
                created_at, updated_at
        """
        params = (
            chapter.title,
            chapter.slug,
            chapter.description,
            chapter.order_index,
            chapter.duration_minutes,
            chapter.estimated_duration,
            chapter.prerequisite_chapter_id,
            chapter.published,
            chapter.has_video,
            chapter.has_quiz,
            chapter.has_exam,
            chapter.chapter_id,
        )

        row = ChapterRepository.execute_returning(query, params)
        return Chapter(**row) if row else chapter

    @staticmethod
    def delete(chapter_id: str) -> bool:
        """
        Delete chapter (hard delete - cascade to lessons).

        Args:
            chapter_id: Chapter UUID

        Returns:
            True if deleted
        """
        query = """
            DELETE FROM courses.chapters
            WHERE chapter_id = %s
        """
        affected = ChapterRepository.execute(query, (chapter_id,))
        return affected > 0

    @staticmethod
    def count(course_id: Optional[str] = None, published: Optional[bool] = None) -> int:
        """
        Count chapters with dynamic filters.

        Args:
            course_id: Filter by course
            published: Filter by published status

        Returns:
            Chapter count
        """
        query = "SELECT COUNT(*) as count FROM courses.chapters WHERE 1=1"
        params = []

        if course_id:
            query += " AND course_id = %s"
            params.append(course_id)

        if published is not None:
            query += " AND published = %s"
            params.append(published)

        row = ChapterRepository.fetch_one(query, tuple(params))
        return row['count'] if row else 0

    @staticmethod
    def reorder_chapters(course_id: str, chapter_order: List[tuple[str, int]]) -> bool:
        """
        Reorder chapters within a course.

        Args:
            course_id: Course UUID
            chapter_order: List of (chapter_id, new_order_index) tuples

        Returns:
            True if successful
        """
        query = """
            UPDATE courses.chapters
            SET order_index = %s, updated_at = NOW()
            WHERE chapter_id = %s AND course_id = %s
        """

        try:
            for chapter_id, order_index in chapter_order:
                ChapterRepository.execute(query, (order_index, chapter_id, course_id))
            return True
        except Exception:
            return False

    @staticmethod
    def get_next_order_index(course_id: str) -> int:
        """
        Get next available order index for a course.

        Args:
            course_id: Course UUID

        Returns:
            Next order index (max + 1, or 1 if no chapters)
        """
        query = """
            SELECT COALESCE(MAX(order_index), 0) + 1 as next_index
            FROM courses.chapters
            WHERE course_id = %s
        """
        row = ChapterRepository.fetch_one(query, (course_id,))
        return row['next_index'] if row else 1
