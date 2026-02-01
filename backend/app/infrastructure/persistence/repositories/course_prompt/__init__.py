"""
Course Prompt Repository Package

Provides database operations for course-specific AI prompt overrides.
Follows the repository pattern with direct SQL (no ORM).

Phase: C1.4 - Prompt-System für Kurs/Modul/Prüfung
Date: 2025-01-23

Modules:
- queries: Shared query constants and helpers
- crud: CREATE, READ, UPDATE operations
- deletion: DELETE and BULK delete operations
- statistics: Counting and aggregation operations

Example:
    from app.infrastructure.persistence.repositories.course_prompt import CoursePromptRepository

    # Find prompt
    prompt = CoursePromptRepository.find_by_id("prompt-uuid")

    # Create prompt
    prompt = CoursePromptRepository.create(
        course_id="course-uuid",
        scope="module_generation",
        created_by="user-uuid"
    )

    # Update prompt
    updated = CoursePromptRepository.update(
        course_prompt_id="prompt-uuid",
        prompt_system="New system prompt"
    )

    # Delete prompt
    CoursePromptRepository.delete("prompt-uuid")

    # Count prompts
    count = CoursePromptRepository.count_by_course("course-uuid")
"""

from .crud import CoursePromptCrudRepository
from .deletion import CoursePromptDeletionRepository
from .statistics import CoursePromptStatisticsRepository


class CoursePromptRepository(
    CoursePromptCrudRepository,
    CoursePromptDeletionRepository,
    CoursePromptStatisticsRepository
):
    """
    Unified Repository for course_prompts table operations.

    Combines CRUD, deletion, and statistics operations.
    Inherits from multiple repositories for better code organisation.

    Example:
        prompt = CoursePromptRepository.find_by_id("prompt-uuid")
        CoursePromptRepository.delete("prompt-uuid")
        count = CoursePromptRepository.count_by_course("course-uuid")
    """
    pass


__all__ = [
    "CoursePromptRepository",
    "CoursePromptCrudRepository",
    "CoursePromptDeletionRepository",
    "CoursePromptStatisticsRepository",
]
