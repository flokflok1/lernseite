"""
Theory Sheet Repository

Repository for managing theory sheet records (chapter and lesson level).

Chapter theories (courses.chapter_theory):
- Uses theory_data JSONB for title+content
- style='manual' for manual editor sheets
- Multiple sheets per chapter

Lesson theories (courses.lesson_theory):
- Simple title+content columns
- Ordered by order_index

Phase: Manual Editor - Theory Sheets
"""

from typing import Optional, List, Dict, Any, Literal
import json
import logging

from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all

logger = logging.getLogger(__name__)

# Manual editor sheets use this style value
MANUAL_STYLE = 'manual'


class TheorySheetRepository(BaseRepository):
    """Repository for theory sheet operations (chapter and lesson level)."""

    # =========================================================================
    # Chapter Theory (uses theory_data JSONB)
    # =========================================================================

    @staticmethod
    def list_by_chapter(chapter_id: str) -> List[Dict[str, Any]]:
        """List manual theory sheets for a chapter."""
        query = """
            SELECT
                theory_id, chapter_id as parent_id, 'chapter' as parent_type,
                theory_data->>'title' as title,
                theory_data->>'content' as content,
                NULL::int as order_index,
                false as is_summary,
                created_at, updated_at
            FROM courses.chapter_theory
            WHERE chapter_id = %s AND style LIKE 'manual%%'
            ORDER BY created_at ASC
        """
        return fetch_all(query, (chapter_id,))

    @staticmethod
    def count_by_chapter(chapter_id: str) -> int:
        """Count manual theory sheets for a chapter."""
        query = """
            SELECT COUNT(*) as count FROM courses.chapter_theory
            WHERE chapter_id = %s AND style LIKE 'manual%%'
        """
        result = fetch_one(query, (chapter_id,))
        return result['count'] if result else 0

    @staticmethod
    def create_chapter_theory(
        chapter_id: str,
        title: str,
        content: str,
        is_summary: bool = False
    ) -> Dict[str, Any]:
        """Create a manual chapter theory sheet.

        Uses style='manual_N' to satisfy UNIQUE(chapter_id, style) constraint.
        """
        # Get next manual index for this chapter
        count_result = fetch_one(
            "SELECT COUNT(*) as count FROM courses.chapter_theory WHERE chapter_id = %s AND style LIKE 'manual%%'",
            (chapter_id,)
        )
        next_idx = count_result['count'] if count_result else 0
        style = f"manual_{next_idx}"

        theory_data = json.dumps({'title': title, 'content': content})
        query = """
            INSERT INTO courses.chapter_theory
            (chapter_id, style, theory_data, created_at, updated_at)
            VALUES (%s, %s, %s::jsonb, NOW(), NOW())
            RETURNING
                theory_id, chapter_id as parent_id, 'chapter' as parent_type,
                theory_data->>'title' as title,
                theory_data->>'content' as content,
                NULL::int as order_index,
                false as is_summary,
                created_at, updated_at
        """
        return fetch_one(query, (chapter_id, style, theory_data))

    # =========================================================================
    # Lesson Theory (simple title+content columns)
    # =========================================================================

    @staticmethod
    def list_by_lesson(lesson_id: str) -> List[Dict[str, Any]]:
        """List all theory sheets for a lesson, ordered."""
        query = """
            SELECT
                theory_id, lesson_id as parent_id, 'lesson' as parent_type,
                title, content, order_index,
                NULL::bool as is_summary, created_at, updated_at
            FROM courses.lesson_theory
            WHERE lesson_id = %s
            ORDER BY order_index ASC, created_at ASC
        """
        return fetch_all(query, (lesson_id,))

    @staticmethod
    def count_by_lesson(lesson_id: str) -> int:
        """Count theory sheets for a lesson."""
        query = "SELECT COUNT(*) as count FROM courses.lesson_theory WHERE lesson_id = %s"
        result = fetch_one(query, (lesson_id,))
        return result['count'] if result else 0

    @staticmethod
    def create_lesson_theory(
        lesson_id: str,
        title: str,
        content: str,
        order_index: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a lesson theory sheet.

        Auto-calculates order_index if not provided to avoid
        UNIQUE(lesson_id, order_index) constraint violations.
        """
        if order_index is None:
            max_result = fetch_one(
                "SELECT COALESCE(MAX(order_index), -1) + 1 as next_idx FROM courses.lesson_theory WHERE lesson_id = %s",
                (lesson_id,)
            )
            order_index = max_result['next_idx'] if max_result else 0

        query = """
            INSERT INTO courses.lesson_theory
            (lesson_id, title, content, order_index, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            RETURNING
                theory_id, lesson_id as parent_id, 'lesson' as parent_type,
                title, content, order_index,
                NULL::bool as is_summary, created_at, updated_at
        """
        return fetch_one(query, (lesson_id, title, content, order_index))

    # =========================================================================
    # Shared Operations (by theory_id)
    # =========================================================================

    @staticmethod
    def get_by_id(theory_id: str) -> Optional[Dict[str, Any]]:
        """Get theory sheet by ID (chapter or lesson)."""
        query = """
            (
                SELECT
                    theory_id, chapter_id as parent_id, 'chapter' as parent_type,
                    theory_data->>'title' as title,
                    theory_data->>'content' as content,
                    NULL::int as order_index,
                    false as is_summary, created_at, updated_at
                FROM courses.chapter_theory
                WHERE theory_id = %s
            )
            UNION ALL
            (
                SELECT
                    theory_id, lesson_id as parent_id, 'lesson' as parent_type,
                    title, content, order_index,
                    NULL::bool as is_summary, created_at, updated_at
                FROM courses.lesson_theory
                WHERE theory_id = %s
            )
            LIMIT 1
        """
        return fetch_one(query, (theory_id, theory_id))

    @staticmethod
    def update_theory(
        theory_id: str,
        parent_type: Literal["chapter", "lesson"],
        title: Optional[str] = None,
        content: Optional[str] = None,
        order_index: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Update theory sheet."""
        if parent_type == "chapter":
            # Chapter: update JSONB fields in theory_data via chained jsonb_set
            params = []
            expr = "theory_data"

            if title is not None:
                expr = f"jsonb_set({expr}, '{{title}}', %s::jsonb)"
                params.append(json.dumps(title))
            if content is not None:
                expr = f"jsonb_set({expr}, '{{content}}', %s::jsonb)"
                params.append(json.dumps(content))

            if not params:
                return TheorySheetRepository.get_by_id(theory_id)

            params.append(theory_id)

            query = f"""
                UPDATE courses.chapter_theory
                SET theory_data = {expr}, updated_at = NOW()
                WHERE theory_id = %s
                RETURNING
                    theory_id, chapter_id as parent_id, 'chapter' as parent_type,
                    theory_data->>'title' as title,
                    theory_data->>'content' as content,
                    NULL::int as order_index,
                    false as is_summary, created_at, updated_at
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
                    NULL::bool as is_summary, created_at, updated_at
            """

        return fetch_one(query, tuple(params))

    @staticmethod
    def delete_by_id(theory_id: str, parent_type: Literal["chapter", "lesson"]) -> bool:
        """Delete theory sheet by ID."""
        table = "courses.chapter_theory" if parent_type == "chapter" else "courses.lesson_theory"
        query = f"DELETE FROM {table} WHERE theory_id = %s RETURNING theory_id"
        result = fetch_one(query, (theory_id,))
        return result is not None

    @staticmethod
    def delete_by_chapter(chapter_id: str) -> int:
        """Delete all manual theory sheets for a chapter."""
        query = "DELETE FROM courses.chapter_theory WHERE chapter_id = %s AND style LIKE 'manual%%' RETURNING theory_id"
        result = fetch_all(query, (chapter_id,))
        return len(result) if result else 0

    @staticmethod
    def delete_by_lesson(lesson_id: str) -> int:
        """Delete all theory sheets for a lesson."""
        query = "DELETE FROM courses.lesson_theory WHERE lesson_id = %s RETURNING theory_id"
        result = fetch_all(query, (lesson_id,))
        return len(result) if result else 0
