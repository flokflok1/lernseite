"""
Repository for Course-Specific Prompts (Phase C1.4)

Provides database operations for course-specific AI prompt overrides.
Follows the repository pattern with direct SQL (no ORM).

Phase: C1.4 - Prompt-System für Kurs/Modul/Prüfung
Date: 2025-01-23
"""

from typing import Optional, List, Dict, Any
from app.repositories.base_repository import BaseRepository


class CoursePromptRepository(BaseRepository):
    """
    Repository for course_prompts table operations.

    Provides CRUD operations and specialized queries for course-specific prompts.
    """

    # ========================================================================
    # READ Operations
    # ========================================================================

    @staticmethod
    def find_by_id(course_prompt_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a course prompt by ID.

        Args:
            course_prompt_id: UUID of the course prompt

        Returns:
            Dict with course prompt data, or None if not found
        """
        query = """
            SELECT
                course_prompt_id::text,
                course_id::text,
                scope,
                language,
                prompt_system,
                prompt_user_template,
                metadata,
                is_active,
                created_by::text,
                created_at,
                updated_at
            FROM course_prompts
            WHERE course_prompt_id = %s
        """
        return CoursePromptRepository.fetch_one(query, (course_prompt_id,))

    @staticmethod
    def find_by_course(
        course_id: str,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Find all prompts for a specific course.

        Args:
            course_id: UUID of the course
            include_inactive: If True, includes inactive prompts

        Returns:
            List of course prompts (empty list if none found)
        """
        if include_inactive:
            query = """
                SELECT
                    course_prompt_id::text,
                    course_id::text,
                    scope,
                    language,
                    prompt_system,
                    prompt_user_template,
                    metadata,
                    is_active,
                    created_by::text,
                    created_at,
                    updated_at
                FROM course_prompts
                WHERE course_id = %s
                ORDER BY scope, language NULLS FIRST
            """
            params = (course_id,)
        else:
            query = """
                SELECT
                    course_prompt_id::text,
                    course_id::text,
                    scope,
                    language,
                    prompt_system,
                    prompt_user_template,
                    metadata,
                    is_active,
                    created_by::text,
                    created_at,
                    updated_at
                FROM course_prompts
                WHERE course_id = %s AND is_active = TRUE
                ORDER BY scope, language NULLS FIRST
            """
            params = (course_id,)

        return CoursePromptRepository.fetch_all(query, params)

    @staticmethod
    def find_by_course_and_scope(
        course_id: str,
        scope: str,
        language: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find a specific prompt by course, scope, and optional language.

        This is the primary lookup method used by the Prompt-Resolver.

        Args:
            course_id: UUID of the course
            scope: Scope of the prompt (e.g., 'module_generation')
            language: Optional language code (e.g., 'de'). If None, matches NULL language.

        Returns:
            Dict with course prompt data, or None if not found
        """
        if language is None:
            query = """
                SELECT
                    course_prompt_id::text,
                    course_id::text,
                    scope,
                    language,
                    prompt_system,
                    prompt_user_template,
                    metadata,
                    is_active,
                    created_by::text,
                    created_at,
                    updated_at
                FROM course_prompts
                WHERE course_id = %s
                  AND scope = %s
                  AND language IS NULL
                  AND is_active = TRUE
            """
            params = (course_id, scope)
        else:
            query = """
                SELECT
                    course_prompt_id::text,
                    course_id::text,
                    scope,
                    language,
                    prompt_system,
                    prompt_user_template,
                    metadata,
                    is_active,
                    created_by::text,
                    created_at,
                    updated_at
                FROM course_prompts
                WHERE course_id = %s
                  AND scope = %s
                  AND language = %s
                  AND is_active = TRUE
            """
            params = (course_id, scope, language)

        return CoursePromptRepository.fetch_one(query, params)

    @staticmethod
    def find_by_scope(
        scope: str,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Find all prompts for a specific scope (across all courses).

        Useful for analytics: "Which courses have custom module_generation prompts?"

        Args:
            scope: Scope to filter by
            include_inactive: If True, includes inactive prompts

        Returns:
            List of course prompts
        """
        if include_inactive:
            query = """
                SELECT
                    course_prompt_id::text,
                    course_id::text,
                    scope,
                    language,
                    prompt_system,
                    prompt_user_template,
                    metadata,
                    is_active,
                    created_by::text,
                    created_at,
                    updated_at
                FROM course_prompts
                WHERE scope = %s
                ORDER BY created_at DESC
            """
        else:
            query = """
                SELECT
                    course_prompt_id::text,
                    course_id::text,
                    scope,
                    language,
                    prompt_system,
                    prompt_user_template,
                    metadata,
                    is_active,
                    created_by::text,
                    created_at,
                    updated_at
                FROM course_prompts
                WHERE scope = %s AND is_active = TRUE
                ORDER BY created_at DESC
            """

        return CoursePromptRepository.fetch_all(query, (scope,))

    # ========================================================================
    # CREATE Operations
    # ========================================================================

    @staticmethod
    def create(
        course_id: str,
        scope: str,
        created_by: str,
        language: Optional[str] = None,
        prompt_system: Optional[str] = None,
        prompt_user_template: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_active: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new course prompt.

        Args:
            course_id: UUID of the course
            scope: Scope of the prompt
            created_by: UUID of user creating the prompt
            language: Optional language code
            prompt_system: System prompt text
            prompt_user_template: User prompt template text
            metadata: Additional metadata (JSONB)
            is_active: Active flag

        Returns:
            Dict with created course prompt data, or None on failure
        """
        query = """
            INSERT INTO course_prompts (
                course_id,
                scope,
                language,
                prompt_system,
                prompt_user_template,
                metadata,
                is_active,
                created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING
                course_prompt_id::text,
                course_id::text,
                scope,
                language,
                prompt_system,
                prompt_user_template,
                metadata,
                is_active,
                created_by::text,
                created_at,
                updated_at
        """
        params = (
            course_id,
            scope,
            language,
            prompt_system,
            prompt_user_template,
            metadata or {},
            is_active,
            created_by
        )

        return CoursePromptRepository.fetch_one(query, params)

    # ========================================================================
    # UPDATE Operations
    # ========================================================================

    @staticmethod
    def update(
        course_prompt_id: str,
        language: Optional[str] = None,
        prompt_system: Optional[str] = None,
        prompt_user_template: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing course prompt (partial update).

        Only provided fields are updated. None values are ignored.

        Args:
            course_prompt_id: UUID of the course prompt
            language: Optional new language code
            prompt_system: Optional new system prompt
            prompt_user_template: Optional new user prompt template
            metadata: Optional new metadata
            is_active: Optional new active flag

        Returns:
            Dict with updated course prompt data, or None if not found
        """
        # Build dynamic update query
        update_fields = []
        params = []

        if language is not None:
            update_fields.append("language = %s")
            params.append(language)

        if prompt_system is not None:
            update_fields.append("prompt_system = %s")
            params.append(prompt_system)

        if prompt_user_template is not None:
            update_fields.append("prompt_user_template = %s")
            params.append(prompt_user_template)

        if metadata is not None:
            update_fields.append("metadata = %s")
            params.append(metadata)

        if is_active is not None:
            update_fields.append("is_active = %s")
            params.append(is_active)

        if not update_fields:
            # No fields to update, just return current state
            return CoursePromptRepository.find_by_id(course_prompt_id)

        # Add course_prompt_id to params
        params.append(course_prompt_id)

        query = f"""
            UPDATE course_prompts
            SET {', '.join(update_fields)}
            WHERE course_prompt_id = %s
            RETURNING
                course_prompt_id::text,
                course_id::text,
                scope,
                language,
                prompt_system,
                prompt_user_template,
                metadata,
                is_active,
                created_by::text,
                created_at,
                updated_at
        """

        return CoursePromptRepository.fetch_one(query, tuple(params))

    @staticmethod
    def upsert(
        course_id: str,
        scope: str,
        language: Optional[str],
        created_by: str,
        prompt_system: Optional[str] = None,
        prompt_user_template: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_active: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Insert or update a course prompt (UPSERT).

        If a prompt with the same (course_id, scope, language) exists, update it.
        Otherwise, create a new one.

        Args:
            course_id: UUID of the course
            scope: Scope of the prompt
            language: Optional language code
            created_by: UUID of user creating/updating the prompt
            prompt_system: System prompt text
            prompt_user_template: User prompt template text
            metadata: Additional metadata
            is_active: Active flag

        Returns:
            Dict with created/updated course prompt data, or None on failure
        """
        query = """
            INSERT INTO course_prompts (
                course_id,
                scope,
                language,
                prompt_system,
                prompt_user_template,
                metadata,
                is_active,
                created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (course_id, scope, language)
            DO UPDATE SET
                prompt_system = EXCLUDED.prompt_system,
                prompt_user_template = EXCLUDED.prompt_user_template,
                metadata = EXCLUDED.metadata,
                is_active = EXCLUDED.is_active
            RETURNING
                course_prompt_id::text,
                course_id::text,
                scope,
                language,
                prompt_system,
                prompt_user_template,
                metadata,
                is_active,
                created_by::text,
                created_at,
                updated_at
        """
        params = (
            course_id,
            scope,
            language,
            prompt_system,
            prompt_user_template,
            metadata or {},
            is_active,
            created_by
        )

        return CoursePromptRepository.fetch_one(query, params)

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
        query = "DELETE FROM course_prompts WHERE course_prompt_id = %s"
        result = CoursePromptRepository.execute(query, (course_prompt_id,))
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
            UPDATE course_prompts
            SET is_active = FALSE
            WHERE course_prompt_id = %s
        """
        result = CoursePromptRepository.execute(query, (course_prompt_id,))
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
                DELETE FROM course_prompts
                WHERE course_id = %s AND scope = %s AND language IS NULL
            """
            params = (course_id, scope)
        else:
            query = """
                DELETE FROM course_prompts
                WHERE course_id = %s AND scope = %s AND language = %s
            """
            params = (course_id, scope, language)

        result = CoursePromptRepository.execute(query, params)
        return result is not None

    @staticmethod
    def delete_by_course(course_id: str) -> int:
        """
        Delete all prompts for a specific course.

        Args:
            course_id: UUID of the course

        Returns:
            Number of prompts deleted
        """
        query = "DELETE FROM course_prompts WHERE course_id = %s"
        result = CoursePromptRepository.execute(query, (course_id,))
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
            Number of prompts deleted
        """
        if scopes is None or len(scopes) == 0:
            # Reset all scopes
            query = "DELETE FROM course_prompts WHERE course_id = %s"
            params = (course_id,)
        else:
            # Reset specific scopes
            placeholders = ', '.join(['%s'] * len(scopes))
            query = f"""
                DELETE FROM course_prompts
                WHERE course_id = %s AND scope IN ({placeholders})
            """
            params = (course_id, *scopes)

        result = CoursePromptRepository.execute(query, params)
        return 1 if result is not None else 0

    # ========================================================================
    # STATISTICS
    # ========================================================================

    @staticmethod
    def count_by_course(course_id: str) -> int:
        """
        Count the number of active prompts for a course.

        Args:
            course_id: UUID of the course

        Returns:
            Number of active prompts
        """
        query = """
            SELECT COUNT(*)
            FROM course_prompts
            WHERE course_id = %s AND is_active = TRUE
        """
        result = CoursePromptRepository.fetch_one(query, (course_id,))
        return result['count'] if result else 0

    @staticmethod
    def count_by_scope(scope: str) -> int:
        """
        Count the number of courses with custom prompts for a specific scope.

        Args:
            scope: Scope to count

        Returns:
            Number of courses with custom prompts for this scope
        """
        query = """
            SELECT COUNT(DISTINCT course_id)
            FROM course_prompts
            WHERE scope = %s AND is_active = TRUE
        """
        result = CoursePromptRepository.fetch_one(query, (scope,))
        return result['count'] if result else 0
