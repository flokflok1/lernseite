"""
Tutor Knowledge Repository.

Database queries for loading course context, chapter context,
lesson content, course files, learning method data, and user progress
for the NPC tutor system.
"""

from typing import Any, Dict, List, Optional

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all


class TutorKnowledgeRepository:
    """Repository for tutor knowledge base queries."""

    # ─── Course Context ────────────────────────────────────────

    @staticmethod
    def get_course_chapters(course_id: str) -> List[Dict]:
        """Get chapters with lesson/method counts for a course."""
        return fetch_all("""
            SELECT
                ch.chapter_id,
                ch.title,
                ch.description,
                ch.order_index,
                (SELECT COUNT(*) FROM lessons l WHERE l.chapter_id = ch.chapter_id) as lesson_count,
                (SELECT COUNT(*) FROM learning_methods lm WHERE lm.chapter_id = ch.chapter_id) as method_count
            FROM chapters ch
            WHERE ch.course_id = %s
            ORDER BY ch.order_index
        """, (course_id,)) or []

    @staticmethod
    def get_category_name(category_id: str) -> Optional[Dict]:
        """Get category name by ID."""
        return fetch_one("""
            SELECT name FROM course_categories WHERE category_id = %s
        """, (category_id,))

    # ─── Chapter Context ──────────────────────────────────────

    @staticmethod
    def get_chapter(chapter_id: str) -> Optional[Dict]:
        """Get chapter with course title."""
        return fetch_one("""
            SELECT
                ch.chapter_id,
                ch.course_id,
                ch.title,
                ch.description,
                ch.order_index,
                c.title as course_title
            FROM chapters ch
            LEFT JOIN courses c ON ch.course_id = c.course_id
            WHERE ch.chapter_id = %s
        """, (chapter_id,))

    @staticmethod
    def get_chapter_lessons(chapter_id: str) -> List[Dict]:
        """Get lessons for a chapter."""
        return fetch_all("""
            SELECT
                lesson_id,
                title,
                lesson_type,
                content,
                order_index,
                duration_minutes
            FROM lessons
            WHERE chapter_id = %s
            ORDER BY order_index
        """, (chapter_id,)) or []

    @staticmethod
    def get_chapter_methods(chapter_id: str) -> List[Dict]:
        """Get published learning methods for a chapter."""
        return fetch_all("""
            SELECT
                method_id,
                method_type,
                title,
                instructions,
                data,
                difficulty,
                order_index
            FROM learning_methods
            WHERE chapter_id = %s AND published = TRUE
            ORDER BY order_index
        """, (chapter_id,)) or []

    # ─── Lesson Content ───────────────────────────────────────

    @staticmethod
    def get_lesson(lesson_id: int) -> Optional[Dict]:
        """Get full lesson with chapter and course info."""
        return fetch_one("""
            SELECT
                l.*,
                ch.title as chapter_title,
                ch.course_id,
                c.title as course_title
            FROM lessons l
            LEFT JOIN chapters ch ON l.chapter_id = ch.chapter_id
            LEFT JOIN courses c ON ch.course_id = c.course_id
            WHERE l.lesson_id = %s
        """, (lesson_id,))

    # ─── Course Files ─────────────────────────────────────────

    @staticmethod
    def get_course_files(
        course_id: str,
        category: Optional[str] = None
    ) -> List[Dict]:
        """Get course files with optional category filter."""
        query = """
            SELECT
                cf.course_file_id,
                cf.file_name,
                cf.display_name,
                cf.description,
                cf.file_category,
                cf.file_type,
                cf.ai_summary,
                cf.ai_keywords,
                cf.ai_processed,
                mf.public_url,
                mf.cdn_url
            FROM course_files cf
            LEFT JOIN media_files mf ON cf.file_id = mf.file_id
            WHERE cf.course_id = %s
        """
        params: List[Any] = [course_id]

        if category:
            query += " AND cf.file_category = %s"
            params.append(category)

        query += " ORDER BY cf.order_index"

        return fetch_all(query, tuple(params)) or []

    # ─── Learning Method Data ─────────────────────────────────

    @staticmethod
    def get_learning_method(method_id: str) -> Optional[Dict]:
        """Get full learning method with chapter and course info."""
        return fetch_one("""
            SELECT
                lm.*,
                ch.title as chapter_title,
                ch.course_id,
                c.title as course_title
            FROM learning_methods lm
            LEFT JOIN chapters ch ON lm.chapter_id = ch.chapter_id
            LEFT JOIN courses c ON ch.course_id = c.course_id
            WHERE lm.method_id = %s
        """, (method_id,))

    # ─── User Progress ────────────────────────────────────────

    @staticmethod
    def get_enrollment(user_id: str, course_id: str) -> Optional[Dict]:
        """Get enrollment status for user in course."""
        return fetch_one("""
            SELECT
                enrollment_id,
                enrollment_type,
                progress_percentage,
                last_accessed_at,
                completed_at
            FROM enrollments
            WHERE user_id = %s AND course_id = %s
        """, (user_id, course_id))

    @staticmethod
    def get_completed_lessons(
        user_id: str, course_id: str
    ) -> List[Dict]:
        """Get completed lessons for user in course."""
        return fetch_all("""
            SELECT
                lp.lesson_id,
                l.title,
                lp.completed_at
            FROM lesson_progress lp
            JOIN lessons l ON lp.lesson_id = l.lesson_id
            JOIN chapters ch ON l.chapter_id = ch.chapter_id
            WHERE lp.user_id = %s AND ch.course_id = %s AND lp.completed = TRUE
            ORDER BY lp.completed_at DESC
        """, (user_id, course_id)) or []

    @staticmethod
    def get_method_progress(
        user_id: str, course_id: str
    ) -> List[Dict]:
        """Get learning method progress for user in course."""
        return fetch_all("""
            SELECT
                lmp.method_id,
                lm.title,
                lm.method_type,
                lmp.attempts,
                lmp.best_score,
                lmp.completed
            FROM learning_method_progress lmp
            JOIN learning_methods lm ON lmp.method_id = lm.method_id
            JOIN chapters ch ON lm.chapter_id = ch.chapter_id
            WHERE lmp.user_id = %s AND ch.course_id = %s
            ORDER BY lmp.updated_at DESC
        """, (user_id, course_id)) or []
