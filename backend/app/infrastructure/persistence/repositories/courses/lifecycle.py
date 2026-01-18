"""
Course Lifecycle Management

Handles workflow operations:
- Publishing and unpublishing courses
- Archiving and unarchiving courses (soft delete)
- Hard deletion (with cascading)
- Cache invalidation

Used by creators and admins to manage course visibility and status.
"""

from typing import Optional, Dict, Any

from app.infrastructure.persistence.database.connection import fetch_one
from app.infrastructure.persistence.repositories.base_repository import BaseRepository
from app.infrastructure.cache.service import CacheService


class CourseRepositoryLifecycle(BaseRepository):
    """
    Lifecycle and status management for courses

    Handles workflow transitions (draft → published → archived)
    and deletion operations.
    """

    table_name = 'courses.courses'

    @classmethod
    def publish(cls, course_id: str) -> Optional[Dict[str, Any]]:
        """
        Publish a course (make it available for enrollment)

        Args:
            course_id: Course ID (UUID string)

        Returns:
            Updated course or None
        """
        query = """
            UPDATE courses.courses
            SET
                published = TRUE,
                status = 'published',
                published_at = NOW(),
                updated_at = NOW()
            WHERE course_id = %s AND published = FALSE
            RETURNING *
        """

        result = fetch_one(query, (course_id,))

        # Invalidate course cache after publishing
        if result:
            CacheService.invalidate_course_cache(course_id)

        return result

    @classmethod
    def unpublish(cls, course_id: str) -> Optional[Dict[str, Any]]:
        """
        Unpublish a course

        Args:
            course_id: Course ID (UUID string)

        Returns:
            Updated course or None
        """
        query = """
            UPDATE courses.courses
            SET
                published = FALSE,
                status = 'draft',
                updated_at = NOW()
            WHERE course_id = %s
            RETURNING *
        """

        result = fetch_one(query, (course_id,))

        # Invalidate course cache after unpublishing
        if result:
            CacheService.invalidate_course_cache(course_id)

        return result

    @classmethod
    def archive(cls, course_id: str) -> Optional[Dict[str, Any]]:
        """
        Archive a course (soft delete)

        Args:
            course_id: Course ID (UUID string)

        Returns:
            Updated course or None
        """
        query = """
            UPDATE courses.courses
            SET
                status = 'archived',
                published = FALSE,
                status = 'archived',
                updated_at = NOW()
            WHERE course_id = %s AND status != 'archived'
            RETURNING *
        """

        result = fetch_one(query, (course_id,))

        # Invalidate course cache after archiving
        if result:
            CacheService.invalidate_course_cache(course_id)

        return result

    @classmethod
    def unarchive(cls, course_id: str) -> Optional[Dict[str, Any]]:
        """
        Unarchive a course

        Args:
            course_id: Course ID (UUID string)

        Returns:
            Updated course or None
        """
        query = """
            UPDATE courses.courses
            SET
                status = 'draft',
                status = 'draft',
                updated_at = NOW()
            WHERE course_id = %s
            RETURNING *
        """

        result = fetch_one(query, (course_id,))

        # Invalidate course cache after unarchiving
        if result:
            CacheService.invalidate_course_cache(course_id)

        return result

    @classmethod
    def delete(cls, course_id: str) -> bool:
        """
        Hard delete a course (and cascade to modules, lessons, enrollments)

        WARNING: This permanently deletes the course and all related data!
        Use archive() for soft delete instead.

        Args:
            course_id: Course UUID

        Returns:
            True if deleted, False otherwise
        """
        # Use RETURNING to check if a row was actually deleted
        query = "DELETE FROM courses.courses WHERE course_id = %s RETURNING course_id"
        result = fetch_one(query, (course_id,))

        # Invalidate course cache after deletion
        if result:
            CacheService.invalidate_course_cache(course_id)
            return True

        return False
