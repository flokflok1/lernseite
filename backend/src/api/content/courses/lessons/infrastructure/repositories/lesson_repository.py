"""
Lesson Repository (DB-First Architecture)

All lesson data loaded dynamically from database.
NO hardcoded values or configurations.

Uses Repository Pattern with direct SQL (NO ORM).
"""

from typing import List, Optional, Dict, Any
import json
from src.infrastructure.database.base_repository import BaseRepository
from src.api.content.courses.lessons.domain.entities.lesson import Lesson


class LessonRepository(BaseRepository):
    """
    Lesson repository for database access.

    ALL data loaded from database dynamically.
    NO hardcoded lesson lists or configurations.
    """

    @staticmethod
    def find_by_id(lesson_id: str) -> Optional[Lesson]:
        """
        Find lesson by ID.

        Args:
            lesson_id: Lesson UUID

        Returns:
            Lesson entity or None
        """
        query = """
            SELECT
                lesson_id, chapter_id, title, slug, lesson_type,
                content, duration_minutes, order_index,
                published, free_preview,
                created_at, updated_at
            FROM courses.lessons
            WHERE lesson_id = %s
        """
        row = LessonRepository.fetch_one(query, (lesson_id,))

        if row:
            # Parse JSONB content
            if row.get('content'):
                row['content'] = row['content'] if isinstance(row['content'], dict) else json.loads(row['content'])
            return Lesson(**row)
        return None

    @staticmethod
    def find_by_chapter_id(
        chapter_id: str,
        published_only: bool = False
    ) -> List[Lesson]:
        """
        Find lessons by chapter ID.

        Args:
            chapter_id: Chapter UUID
            published_only: Only return published lessons

        Returns:
            List of lessons ordered by order_index
        """
        query = """
            SELECT
                lesson_id, chapter_id, title, slug, lesson_type,
                content, duration_minutes, order_index,
                published, free_preview,
                created_at, updated_at
            FROM courses.lessons
            WHERE chapter_id = %s
        """
        params = [chapter_id]

        if published_only:
            query += " AND published = TRUE"

        query += " ORDER BY order_index ASC"

        rows = LessonRepository.fetch_all(query, tuple(params))

        # Parse JSONB content for each row
        for row in rows:
            if row.get('content'):
                row['content'] = row['content'] if isinstance(row['content'], dict) else json.loads(row['content'])

        return [Lesson(**row) for row in rows]

    @staticmethod
    def find_all(
        chapter_id: Optional[str] = None,
        lesson_type: Optional[str] = None,  # From DB, not hardcoded
        published: Optional[bool] = None,
        free_preview: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Lesson]:
        """
        Find lessons with dynamic filters.

        ALL filter values come from database or parameters.
        NO hardcoded filter lists.

        Args:
            chapter_id: Filter by chapter
            lesson_type: Filter by lesson type (from DB)
            published: Filter by published status
            free_preview: Filter by free preview status
            limit: Result limit
            offset: Result offset

        Returns:
            List of lesson entities
        """
        query = """
            SELECT
                lesson_id, chapter_id, title, slug, lesson_type,
                content, duration_minutes, order_index,
                published, free_preview,
                created_at, updated_at
            FROM courses.lessons
            WHERE 1=1
        """
        params = []

        # Dynamic filters - NO hardcoded values
        if chapter_id:
            query += " AND chapter_id = %s"
            params.append(chapter_id)

        if lesson_type:
            query += " AND lesson_type = %s"
            params.append(lesson_type)

        if published is not None:
            query += " AND published = %s"
            params.append(published)

        if free_preview is not None:
            query += " AND free_preview = %s"
            params.append(free_preview)

        query += " ORDER BY chapter_id, order_index ASC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        rows = LessonRepository.fetch_all(query, tuple(params))

        # Parse JSONB content
        for row in rows:
            if row.get('content'):
                row['content'] = row['content'] if isinstance(row['content'], dict) else json.loads(row['content'])

        return [Lesson(**row) for row in rows]

    @staticmethod
    def create(lesson: Lesson) -> Lesson:
        """
        Create new lesson.

        Args:
            lesson: Lesson entity to create

        Returns:
            Created lesson with DB-generated fields
        """
        query = """
            INSERT INTO courses.lessons (
                lesson_id, chapter_id, title, slug, lesson_type,
                content, duration_minutes, order_index,
                published, free_preview,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
            )
            RETURNING
                lesson_id, chapter_id, title, slug, lesson_type,
                content, duration_minutes, order_index,
                published, free_preview,
                created_at, updated_at
        """

        # Convert content dict to JSONB
        content_json = json.dumps(lesson.content) if lesson.content else None

        params = (
            lesson.lesson_id,
            lesson.chapter_id,
            lesson.title,
            lesson.slug,
            lesson.lesson_type,
            content_json,
            lesson.duration_minutes,
            lesson.order_index,
            lesson.published,
            lesson.free_preview,
        )

        row = LessonRepository.execute_returning(query, params)

        if row:
            # Parse JSONB content
            if row.get('content'):
                row['content'] = row['content'] if isinstance(row['content'], dict) else json.loads(row['content'])
            return Lesson(**row)
        return lesson

    @staticmethod
    def update(lesson: Lesson) -> Lesson:
        """
        Update existing lesson.

        Args:
            lesson: Lesson entity with updates

        Returns:
            Updated lesson
        """
        query = """
            UPDATE courses.lessons SET
                title = %s,
                slug = %s,
                lesson_type = %s,
                content = %s,
                duration_minutes = %s,
                order_index = %s,
                published = %s,
                free_preview = %s,
                updated_at = NOW()
            WHERE lesson_id = %s
            RETURNING
                lesson_id, chapter_id, title, slug, lesson_type,
                content, duration_minutes, order_index,
                published, free_preview,
                created_at, updated_at
        """

        # Convert content dict to JSONB
        content_json = json.dumps(lesson.content) if lesson.content else None

        params = (
            lesson.title,
            lesson.slug,
            lesson.lesson_type,
            content_json,
            lesson.duration_minutes,
            lesson.order_index,
            lesson.published,
            lesson.free_preview,
            lesson.lesson_id,
        )

        row = LessonRepository.execute_returning(query, params)

        if row:
            # Parse JSONB content
            if row.get('content'):
                row['content'] = row['content'] if isinstance(row['content'], dict) else json.loads(row['content'])
            return Lesson(**row)
        return lesson

    @staticmethod
    def delete(lesson_id: str) -> bool:
        """
        Delete lesson (hard delete - cascade to completions).

        Args:
            lesson_id: Lesson UUID

        Returns:
            True if deleted
        """
        query = """
            DELETE FROM courses.lessons
            WHERE lesson_id = %s
        """
        affected = LessonRepository.execute(query, (lesson_id,))
        return affected > 0

    @staticmethod
    def count(
        chapter_id: Optional[str] = None,
        lesson_type: Optional[str] = None,
        published: Optional[bool] = None
    ) -> int:
        """
        Count lessons with dynamic filters.

        Args:
            chapter_id: Filter by chapter
            lesson_type: Filter by lesson type
            published: Filter by published status

        Returns:
            Lesson count
        """
        query = "SELECT COUNT(*) as count FROM courses.lessons WHERE 1=1"
        params = []

        if chapter_id:
            query += " AND chapter_id = %s"
            params.append(chapter_id)

        if lesson_type:
            query += " AND lesson_type = %s"
            params.append(lesson_type)

        if published is not None:
            query += " AND published = %s"
            params.append(published)

        row = LessonRepository.fetch_one(query, tuple(params))
        return row['count'] if row else 0

    @staticmethod
    def reorder_lessons(chapter_id: str, lesson_order: List[tuple[str, int]]) -> bool:
        """
        Reorder lessons within a chapter.

        Args:
            chapter_id: Chapter UUID
            lesson_order: List of (lesson_id, new_order_index) tuples

        Returns:
            True if successful
        """
        query = """
            UPDATE courses.lessons
            SET order_index = %s, updated_at = NOW()
            WHERE lesson_id = %s AND chapter_id = %s
        """

        try:
            for lesson_id, order_index in lesson_order:
                LessonRepository.execute(query, (order_index, lesson_id, chapter_id))
            return True
        except Exception:
            return False

    @staticmethod
    def get_next_order_index(chapter_id: str) -> int:
        """
        Get next available order index for a chapter.

        Args:
            chapter_id: Chapter UUID

        Returns:
            Next order index (max + 1, or 1 if no lessons)
        """
        query = """
            SELECT COALESCE(MAX(order_index), 0) + 1 as next_index
            FROM courses.lessons
            WHERE chapter_id = %s
        """
        row = LessonRepository.fetch_one(query, (chapter_id,))
        return row['next_index'] if row else 1

    @staticmethod
    def get_available_lesson_types() -> List[str]:
        """
        Get available lesson types from database constraint.

        Returns:
            List of valid lesson types from DB
        """
        # Query PostgreSQL constraint to get valid lesson types
        query = """
            SELECT
                UNNEST(
                    STRING_TO_ARRAY(
                        SUBSTRING(
                            pg_get_constraintdef(c.oid)
                            FROM '\\(lesson_type\\)::\\w+\\s*=\\s*ANY\\s*\\(ARRAY\\[(.*)\\]'
                        ),
                        ','
                    )
                ) AS lesson_type
            FROM pg_constraint c
            JOIN pg_class t ON c.conrelid = t.oid
            JOIN pg_namespace n ON t.relnamespace = n.oid
            WHERE c.conname = 'chk_lesson_type'
            AND n.nspname = 'courses'
            AND t.relname = 'lessons'
        """

        rows = LessonRepository.fetch_all(query, ())

        if rows:
            # Clean up the values (remove quotes and whitespace)
            return [row['lesson_type'].strip().strip("'\"") for row in rows]

        # Fallback: query actual distinct values in table
        fallback_query = """
            SELECT DISTINCT lesson_type
            FROM courses.lessons
            ORDER BY lesson_type
        """
        fallback_rows = LessonRepository.fetch_all(fallback_query, ())
        return [row['lesson_type'] for row in fallback_rows]
