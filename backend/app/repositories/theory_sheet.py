"""
Theory Sheet Repository

Repository for managing theory sheet records (chapter and lesson level).

Chapter theories:
- One optional summary per chapter (is_summary = TRUE)
- Multiple optional additional theory sheets (is_summary = FALSE)

Lesson theories:
- Multiple theory sheets per lesson
- Ordered by order_index

Phase: AI Studio Implementation - Theory Sheets
"""

from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
import logging

from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class TheorySheetRepository(BaseRepository):
    """Repository for theory sheet operations (chapter and lesson level)."""

    @staticmethod
    def list_by_chapter(
        chapter_id: str,
        include_summary: bool = True
    ) -> List[Dict[str, Any]]:
        """
        List all theory sheets for a chapter.

        Args:
            chapter_id: UUID of the chapter
            include_summary: Include summary sheet in results (default: True)

        Returns:
            List of theory sheet records, ordered by is_summary DESC, then created_at DESC
        """
        query = """
            SELECT
                theory_id, chapter_id as parent_id, 'chapter' as parent_type,
                title, content, NULL as order_index,
                is_summary, created_at, updated_at
            FROM courses.chapter_theory
            WHERE chapter_id = %s
            ORDER BY is_summary DESC, created_at DESC
        """
        return TheorySheetRepository.fetch_all(query, (chapter_id,))

    @staticmethod
    def get_chapter_summary(chapter_id: str) -> Optional[Dict[str, Any]]:
        """
        Get chapter summary (is_summary = TRUE).

        Args:
            chapter_id: UUID of the chapter

        Returns:
            Summary theory sheet record or None
        """
        query = """
            SELECT
                theory_id, chapter_id as parent_id, 'chapter' as parent_type,
                title, content, NULL as order_index,
                is_summary, created_at, updated_at
            FROM courses.chapter_theory
            WHERE chapter_id = %s AND is_summary = TRUE
            LIMIT 1
        """
        return TheorySheetRepository.fetch_one(query, (chapter_id,))

    @staticmethod
    def list_by_lesson(lesson_id: str) -> List[Dict[str, Any]]:
        """
        List all theory sheets for a lesson, ordered.

        Args:
            lesson_id: UUID of the lesson

        Returns:
            List of theory sheet records, ordered by order_index ASC
        """
        query = """
            SELECT
                theory_id, lesson_id as parent_id, 'lesson' as parent_type,
                title, content, order_index,
                NULL as is_summary, created_at, updated_at
            FROM courses.lesson_theory
            WHERE lesson_id = %s
            ORDER BY order_index ASC, created_at ASC
        """
        return TheorySheetRepository.fetch_all(query, (lesson_id,))

    @staticmethod
    def get_by_id(theory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get theory sheet by ID (chapter or lesson).

        Args:
            theory_id: UUID of the theory record

        Returns:
            Theory sheet record or None if not found

        Note:
            Uses UNION to search both chapter_theory and lesson_theory tables.
        """
        query = """
            (
                SELECT
                    theory_id, chapter_id as parent_id, 'chapter' as parent_type,
                    title, content, NULL as order_index,
                    is_summary, created_at, updated_at
                FROM courses.chapter_theory
                WHERE theory_id = %s
            )
            UNION ALL
            (
                SELECT
                    theory_id, lesson_id as parent_id, 'lesson' as parent_type,
                    title, content, order_index,
                    NULL as is_summary, created_at, updated_at
                FROM courses.lesson_theory
                WHERE theory_id = %s
            )
            LIMIT 1
        """
        return TheorySheetRepository.fetch_one(query, (theory_id, theory_id))

    @staticmethod
    def create_chapter_theory(
        chapter_id: str,
        title: str,
        content: str,
        is_summary: bool = False
    ) -> Dict[str, Any]:
        """
        Create a chapter theory sheet.

        Args:
            chapter_id: UUID of the chapter
            title: Theory sheet title
            content: Theory sheet content (markdown/rich text)
            is_summary: Is this the chapter summary? (default: False)

        Returns:
            Created theory sheet record

        Raises:
            Exception: If duplicate summary (is_summary=TRUE and summary exists)
        """
        query = """
            INSERT INTO courses.chapter_theory
            (chapter_id, title, content, is_summary, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            RETURNING
                theory_id, chapter_id as parent_id, 'chapter' as parent_type,
                title, content, NULL as order_index,
                is_summary, created_at, updated_at
        """
        return TheorySheetRepository.fetch_one(
            query,
            (chapter_id, title, content, is_summary)
        )

    @staticmethod
    def create_lesson_theory(
        lesson_id: str,
        title: str,
        content: str,
        order_index: int = 0
    ) -> Dict[str, Any]:
        """
        Create a lesson theory sheet.

        Args:
            lesson_id: UUID of the lesson
            title: Theory sheet title
            content: Theory sheet content
            order_index: Display order (default: 0)

        Returns:
            Created theory sheet record
        """
        query = """
            INSERT INTO courses.lesson_theory
            (lesson_id, title, content, order_index, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            RETURNING
                theory_id, lesson_id as parent_id, 'lesson' as parent_type,
                title, content, order_index,
                NULL as is_summary, created_at, updated_at
        """
        return TheorySheetRepository.fetch_one(
            query,
            (lesson_id, title, content, order_index)
        )

    @staticmethod
    def update_theory(
        theory_id: str,
        parent_type: Literal["chapter", "lesson"],
        title: Optional[str] = None,
        content: Optional[str] = None,
        order_index: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update theory sheet.

        Args:
            theory_id: UUID of the theory sheet
            parent_type: Type of parent ('chapter' or 'lesson')
            title: New title (optional)
            content: New content (optional)
            order_index: New order (only for lesson theories, optional)

        Returns:
            Updated theory sheet record or None if not found
        """
        if parent_type == "chapter":
            # Build dynamic UPDATE for chapter_theory
            updates = []
            params = []

            if title is not None:
                updates.append("title = %s")
                params.append(title)
            if content is not None:
                updates.append("content = %s")
                params.append(content)

            if not updates:
                # No changes, just fetch current record
                return TheorySheetRepository.get_by_id(theory_id)

            updates.append("updated_at = NOW()")
            set_clause = ", ".join(updates)
            params.append(theory_id)

            query = f"""
                UPDATE courses.chapter_theory
                SET {set_clause}
                WHERE theory_id = %s
                RETURNING
                    theory_id, chapter_id as parent_id, 'chapter' as parent_type,
                    title, content, NULL as order_index,
                    is_summary, created_at, updated_at
            """
        else:  # lesson
            updates = []
            params = []

            if title is not None:
                updates.append("title = %s")
                params.append(title)
            if content is not None:
                updates.append("content = %s")
                params.append(content)
            if order_index is not None:
                updates.append("order_index = %s")
                params.append(order_index)

            if not updates:
                return TheorySheetRepository.get_by_id(theory_id)

            updates.append("updated_at = NOW()")
            set_clause = ", ".join(updates)
            params.append(theory_id)

            query = f"""
                UPDATE courses.lesson_theory
                SET {set_clause}
                WHERE theory_id = %s
                RETURNING
                    theory_id, lesson_id as parent_id, 'lesson' as parent_type,
                    title, content, order_index,
                    NULL as is_summary, created_at, updated_at
            """

        return TheorySheetRepository.fetch_one(query, tuple(params))

    @staticmethod
    def delete_by_id(theory_id: str, parent_type: Literal["chapter", "lesson"]) -> bool:
        """
        Delete theory sheet by ID.

        Args:
            theory_id: UUID of the theory sheet
            parent_type: Type of parent ('chapter' or 'lesson')

        Returns:
            True if deleted, False if not found
        """
        table = "courses.chapter_theory" if parent_type == "chapter" else "courses.lesson_theory"
        query = f"DELETE FROM {table} WHERE theory_id = %s"
        result = TheorySheetRepository.execute(query, (theory_id,))
        return result.rowcount > 0 if result else False

    @staticmethod
    def delete_by_chapter(chapter_id: str) -> int:
        """
        Delete all theory sheets for a chapter.

        Args:
            chapter_id: UUID of the chapter

        Returns:
            Number of records deleted
        """
        query = "DELETE FROM courses.chapter_theory WHERE chapter_id = %s"
        result = TheorySheetRepository.execute(query, (chapter_id,))
        return result.rowcount if result else 0

    @staticmethod
    def delete_by_lesson(lesson_id: str) -> int:
        """
        Delete all theory sheets for a lesson.

        Args:
            lesson_id: UUID of the lesson

        Returns:
            Number of records deleted
        """
        query = "DELETE FROM courses.lesson_theory WHERE lesson_id = %s"
        result = TheorySheetRepository.execute(query, (lesson_id,))
        return result.rowcount if result else 0

    @staticmethod
    def count_by_chapter(chapter_id: str) -> int:
        """
        Count theory sheets for a chapter.

        Args:
            chapter_id: UUID of the chapter

        Returns:
            Number of theory sheets
        """
        query = "SELECT COUNT(*) as count FROM courses.chapter_theory WHERE chapter_id = %s"
        result = TheorySheetRepository.fetch_one(query, (chapter_id,))
        return result['count'] if result else 0

    @staticmethod
    def count_by_lesson(lesson_id: str) -> int:
        """
        Count theory sheets for a lesson.

        Args:
            lesson_id: UUID of the lesson

        Returns:
            Number of theory sheets
        """
        query = "SELECT COUNT(*) as count FROM courses.lesson_theory WHERE lesson_id = %s"
        result = TheorySheetRepository.fetch_one(query, (lesson_id,))
        return result['count'] if result else 0
