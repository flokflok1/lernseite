"""
CRUD Operations for Course Prompts

Provides CREATE, READ, and UPDATE operations for course-specific
AI prompt overrides following the Repository Pattern.

Part of: repositories/course_prompt package
"""

from typing import Optional, List, Dict, Any
from app.infrastructure.persistence.repositories.core.base import BaseRepository
from . import queries


class CoursePromptCrudRepository(BaseRepository):
    """
    Repository for course_prompts CRUD operations.

    Provides standard Create, Read, Update operations for course prompts.
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
        return CoursePromptCrudRepository.fetch_one(
            queries.FIND_BY_ID_QUERY,
            (course_prompt_id,)
        )

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
        query = (
            queries.FIND_BY_COURSE_ALL_QUERY
            if include_inactive
            else queries.FIND_BY_COURSE_ACTIVE_QUERY
        )
        return CoursePromptCrudRepository.fetch_all(query, (course_id,))

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
            return CoursePromptCrudRepository.fetch_one(
                queries.FIND_BY_COURSE_AND_SCOPE_QUERY_NO_LANG,
                (course_id, scope)
            )
        else:
            return CoursePromptCrudRepository.fetch_one(
                queries.FIND_BY_COURSE_AND_SCOPE_QUERY_WITH_LANG,
                (course_id, scope, language)
            )

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
        query = (
            queries.FIND_BY_SCOPE_ALL_QUERY
            if include_inactive
            else queries.FIND_BY_SCOPE_ACTIVE_QUERY
        )
        return CoursePromptCrudRepository.fetch_all(query, (scope,))

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
        query = queries.get_insert_returning()
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
        return CoursePromptCrudRepository.fetch_one(query, params)

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
        # Check if there are any fields to update
        if all(v is None for v in [language, prompt_system, prompt_user_template, metadata, is_active]):
            # No fields to update, just return current state
            return CoursePromptCrudRepository.find_by_id(course_prompt_id)

        # Build dynamic update query based on provided fields
        query = queries.build_update_query(
            language=language is not None,
            prompt_system=prompt_system is not None,
            prompt_user_template=prompt_user_template is not None,
            metadata=metadata is not None,
            is_active=is_active is not None
        )

        # Build params in the same order as the update fields
        params = []
        if language is not None:
            params.append(language)
        if prompt_system is not None:
            params.append(prompt_system)
        if prompt_user_template is not None:
            params.append(prompt_user_template)
        if metadata is not None:
            params.append(metadata)
        if is_active is not None:
            params.append(is_active)

        # Add course_prompt_id to params
        params.append(course_prompt_id)

        return CoursePromptCrudRepository.fetch_one(query, tuple(params))

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
        query = queries.get_upsert_returning()
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
        return CoursePromptCrudRepository.fetch_one(query, params)
