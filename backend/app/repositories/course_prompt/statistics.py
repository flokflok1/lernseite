"""
Statistics and Analytics for Course Prompts

Provides counting and aggregation operations for course prompts.

Part of: repositories/course_prompt package
"""

from app.repositories.base_repository import BaseRepository
from . import queries


class CoursePromptStatisticsRepository(BaseRepository):
    """
    Repository for course_prompts statistics operations.

    Provides aggregation and counting methods for analytics.
    """

    @staticmethod
    def count_by_course(course_id: str) -> int:
        """
        Count the number of active prompts for a course.

        Args:
            course_id: UUID of the course

        Returns:
            Number of active prompts
        """
        result = CoursePromptStatisticsRepository.fetch_one(
            queries.COUNT_BY_COURSE_QUERY,
            (course_id,)
        )
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
        result = CoursePromptStatisticsRepository.fetch_one(
            queries.COUNT_BY_SCOPE_QUERY,
            (scope,)
        )
        return result['count'] if result else 0
