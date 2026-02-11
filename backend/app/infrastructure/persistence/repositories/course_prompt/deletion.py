"""
DELETE and BULK Operations for Course Prompts

Provides hard delete, soft delete, and bulk deletion operations
for course prompts.

Part of: repositories/course_prompt package
"""

from typing import Optional, List
from app.infrastructure.persistence.repositories.core.base import BaseRepository


class CoursePromptDeletionRepository(BaseRepository):
    """
    Repository for course_prompts deletion operations.

    Provides single deletion, soft deletion, and bulk deletion methods.
    """

    # ========================================================================
    # DELETE Operations
    # ========================================================================

    @staticmethod
    def delete(course_prompt_id: str) -> bool:
        """
        Hard delete a course prompt.

        Args:
            course_prompt_id: UUID of the course prompt

        Returns:
            True if deleted, False if not found
        """
        query = "DELETE FROM courses.course_prompts WHERE course_prompt_id = %s"
        result = CoursePromptDeletionRepository.execute(query, (course_prompt_id,))
        return result is not None

    @staticmethod
    def soft_delete(course_prompt_id: str) -> bool:
        """
        Soft delete a course prompt (set is_active = FALSE).

        Args:
            course_prompt_id: UUID of the course prompt

        Returns:
            True if deactivated, False if not found
        """
        query = """
            UPDATE courses.course_prompts
            SET is_active = FALSE
            WHERE course_prompt_id = %s
        """
        result = CoursePromptDeletionRepository.execute(query, (course_prompt_id,))
        return result is not None

    @staticmethod
    def delete_by_course_and_scope(
        course_id: str,
        scope: str,
        language: Optional[str] = None
    ) -> bool:
        """
        Delete a course prompt by course, scope, and language.

        Used for "reset to default" functionality.

        Args:
            course_id: UUID of the course
            scope: Scope of the prompt
            language: Optional language code

        Returns:
            True if deleted, False if not found
        """
        if language is None:
            query = """
                DELETE FROM courses.course_prompts
                WHERE course_id = %s AND scope = %s AND language IS NULL
            """
            params = (course_id, scope)
        else:
            query = """
                DELETE FROM courses.course_prompts
                WHERE course_id = %s AND scope = %s AND language = %s
            """
            params = (course_id, scope, language)

        result = CoursePromptDeletionRepository.execute(query, params)
        return result is not None

    @staticmethod
    def delete_by_course(course_id: str) -> int:
        """
        Delete all prompts for a specific course.

        Args:
            course_id: UUID of the course

        Returns:
            Number of prompts deleted (1 if successful, 0 if failed)
        """
        query = "DELETE FROM courses.course_prompts WHERE course_id = %s"
        result = CoursePromptDeletionRepository.execute(query, (course_id,))
        # Note: execute() doesn't return rowcount, so we return 1 if successful
        return 1 if result is not None else 0

    # ========================================================================
    # BULK Operations
    # ========================================================================

    @staticmethod
    def bulk_reset_by_course(
        course_id: str,
        scopes: Optional[List[str]] = None
    ) -> int:
        """
        Reset course prompts to global defaults (bulk delete).

        Args:
            course_id: UUID of the course
            scopes: Optional list of scopes to reset. If None, resets all scopes.

        Returns:
            Number of prompts deleted (1 if successful, 0 if failed)
        """
        if scopes is None or len(scopes) == 0:
            # Reset all scopes
            query = "DELETE FROM courses.course_prompts WHERE course_id = %s"
            params = (course_id,)
        else:
            # Reset specific scopes
            placeholders = ', '.join(['%s'] * len(scopes))
            query = f"""
                DELETE FROM courses.course_prompts
                WHERE course_id = %s AND scope IN ({placeholders})
            """
            params = (course_id, *scopes)

        result = CoursePromptDeletionRepository.execute(query, params)
        return 1 if result is not None else 0
