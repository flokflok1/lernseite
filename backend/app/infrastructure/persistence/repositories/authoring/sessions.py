"""
Course Authoring Session Repository

Database access for course authoring sessions:
- Session CRUD (create, get, update, finalize)
- Course access checks for authoring
- Course info loading for AI prompts
- Existing structure loading (chapters/lessons)
- Learning method instance creation
"""

import json
from typing import Dict, Optional, List, Any

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query
)


class CourseAuthoringSessionRepository:
    """Repository for course_authoring_sessions and related authoring queries."""

    @staticmethod
    def get_course(course_id: str) -> Optional[Dict]:
        """
        Load course by ID.

        Args:
            course_id: Course UUID

        Returns:
            Course data or None
        """
        query = "SELECT * FROM courses WHERE course_id = %s"
        return fetch_one(query, (course_id,))

    @staticmethod
    def check_user_has_write_permission(user_id: str) -> bool:
        """
        Check if user has content write or admin write permissions via GBA.

        Args:
            user_id: User UUID

        Returns:
            True if user has write permissions
        """
        query = """
            SELECT 1
            FROM core.users_groups ug
            JOIN core.groups g ON ug.group_id = g.id
            JOIN core.group_permissions gp ON g.id = gp.group_id
            JOIN core.permissions p ON gp.permission_id = p.id
            WHERE ug.user_id = %s
                AND ug.is_active = TRUE
                AND ug.left_at IS NULL
                AND (
                    p.permission_code LIKE 'content.%%:write'
                    OR p.permission_code LIKE 'admin.%%:write'
                )
            LIMIT 1
        """
        result = fetch_one(query, (user_id,))
        return result is not None

    @staticmethod
    def get_course_creator(course_id: str) -> Optional[str]:
        """
        Get the created_by user ID for a course.

        Args:
            course_id: Course UUID

        Returns:
            Creator user ID as string or None
        """
        query = "SELECT created_by FROM courses WHERE course_id = %s"
        course = fetch_one(query, (course_id,))
        return str(course['created_by']) if course else None

    @staticmethod
    def get_course_info(course_id: str) -> Optional[Dict]:
        """
        Load course info with category name for AI prompts.

        Args:
            course_id: Course UUID

        Returns:
            Course row with category_name or None
        """
        query = """
            SELECT c.*, cat.name as category_name
            FROM courses c
            LEFT JOIN course_categories cat ON cat.category_id = c.category_id
            WHERE c.course_id = %s
        """
        return fetch_one(query, (course_id,))

    @staticmethod
    def get_chapters_for_course(course_id: str) -> List[Dict]:
        """
        Load all chapters for a course ordered by sort_order.

        Args:
            course_id: Course UUID

        Returns:
            List of chapter rows
        """
        query = """
            SELECT * FROM chapters
            WHERE course_id = %s
            ORDER BY sort_order, created_at
        """
        return fetch_all(query, (course_id,))

    @staticmethod
    def get_lessons_for_chapter(chapter_id: str) -> List[Dict]:
        """
        Load all lessons for a chapter ordered by sort_order.

        Args:
            chapter_id: Chapter UUID

        Returns:
            List of lesson rows
        """
        query = """
            SELECT * FROM lessons
            WHERE chapter_id = %s
            ORDER BY sort_order, created_at
        """
        return fetch_all(query, (chapter_id,))

    @staticmethod
    def update_session(
        session_id: str,
        draft_structure: Dict,
        chat_history: List,
        file_context: List,
        tokens_delta: int = 0,
        operations_delta: int = 0
    ) -> None:
        """
        Update session draft_structure, chat_history, file_context and counters.

        Args:
            session_id: Session UUID
            draft_structure: Updated draft structure
            chat_history: Updated chat history
            file_context: File context list
            tokens_delta: Token count delta
            operations_delta: Operations count delta
        """
        query = """
            UPDATE course_authoring_sessions
            SET draft_structure = %s,
                chat_history = %s,
                file_context = %s,
                total_tokens_used = total_tokens_used + %s,
                total_operations = total_operations + %s
            WHERE session_id = %s
        """
        execute_query(query, (
            json.dumps(draft_structure),
            json.dumps(chat_history),
            json.dumps(file_context),
            tokens_delta,
            operations_delta,
            session_id
        ))

    @staticmethod
    def create_learning_method_instance(
        lesson_id: str,
        chapter_id: str,
        lm_type: int,
        title: str,
        instructions: str,
        data_json: str,
        difficulty: str,
        tier: str
    ) -> Optional[Dict]:
        """
        Insert a new learning method instance.

        Args:
            lesson_id: Lesson UUID
            chapter_id: Chapter UUID
            lm_type: Numeric learning method type
            title: Method title
            instructions: Method instructions
            data_json: JSON string of method data
            difficulty: Difficulty level
            tier: Content tier

        Returns:
            Row with method_id or None
        """
        query = """
            INSERT INTO learning_method_instances (
                lesson_id, chapter_id, method_type, title,
                instructions, data, difficulty, tier
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING method_id
        """
        return fetch_one(query, (
            lesson_id, chapter_id, lm_type, title,
            instructions, data_json, difficulty, tier
        ))

    @staticmethod
    def create_session(
        session_id: str,
        course_id: str,
        user_id: str,
        model_profile: str,
        draft_structure_json: str,
        chat_history_json: str
    ) -> Optional[Dict]:
        """
        Insert a new course authoring session.

        Args:
            session_id: Session UUID
            course_id: Course UUID
            user_id: Creator user UUID
            model_profile: AI model profile string
            draft_structure_json: JSON string of draft structure
            chat_history_json: JSON string of chat history

        Returns:
            Created session row or None
        """
        query = """
            INSERT INTO course_authoring_sessions (
                session_id, course_id, created_by, model_profile,
                draft_structure, chat_history, status
            ) VALUES (%s, %s, %s, %s, %s, %s, 'active')
            RETURNING session_id, course_id, created_by, draft_structure,
                      status, created_at
        """
        return fetch_one(query, (
            session_id, course_id, user_id, model_profile,
            draft_structure_json, chat_history_json
        ))

    @staticmethod
    def get_session_with_course(session_id: str) -> Optional[Dict]:
        """
        Load session joined with course title.

        Args:
            session_id: Session UUID

        Returns:
            Session row with course_title or None
        """
        query = """
            SELECT s.*, c.title as course_title
            FROM course_authoring_sessions s
            JOIN courses c ON c.course_id = s.course_id
            WHERE s.session_id = %s
        """
        return fetch_one(query, (session_id,))

    @staticmethod
    def finalize_session(session_id: str) -> None:
        """
        Mark session as finalized with current timestamp.

        Args:
            session_id: Session UUID
        """
        query = """
            UPDATE course_authoring_sessions
            SET status = 'finalized', finalized_at = NOW()
            WHERE session_id = %s
        """
        execute_query(query, (session_id,))
