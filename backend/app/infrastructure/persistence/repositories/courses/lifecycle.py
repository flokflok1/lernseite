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

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all
from app.infrastructure.persistence.repositories.core.base import BaseRepository
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
        Archive a course (intentional archive, NOT trash).
        Clears trashed_at to distinguish from trash.

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
                trashed_at = NULL,
                updated_at = NOW()
            WHERE course_id = %s AND (status != 'archived' OR trashed_at IS NOT NULL)
            RETURNING *
        """

        result = fetch_one(query, (course_id,))

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
    def trash(cls, course_id: str) -> Optional[Dict[str, Any]]:
        """
        Move a course to the trash (soft delete with 30-day auto-purge).
        Sets status='archived' and trashed_at=NOW().

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
                trashed_at = NOW(),
                updated_at = NOW()
            WHERE course_id = %s AND trashed_at IS NULL
            RETURNING *
        """

        result = fetch_one(query, (course_id,))

        if result:
            CacheService.invalidate_course_cache(course_id)

        return result

    @classmethod
    def restore_from_trash(cls, course_id: str) -> Optional[Dict[str, Any]]:
        """
        Restore a course from the trash back to draft status.

        Args:
            course_id: Course ID (UUID string)

        Returns:
            Updated course or None
        """
        query = """
            UPDATE courses.courses
            SET
                status = 'draft',
                trashed_at = NULL,
                updated_at = NOW()
            WHERE course_id = %s AND trashed_at IS NOT NULL
            RETURNING *
        """

        result = fetch_one(query, (course_id,))

        if result:
            CacheService.invalidate_course_cache(course_id)

        return result

    @classmethod
    def purge_trash(cls, days: int = 30) -> int:
        """
        Permanently delete all courses that have been in the trash
        longer than the specified number of days.

        Args:
            days: Number of days after which trashed courses are purged

        Returns:
            Number of courses purged
        """
        query = """
            DELETE FROM courses.courses
            WHERE trashed_at IS NOT NULL
              AND trashed_at < NOW() - MAKE_INTERVAL(days => %s)
            RETURNING course_id
        """
        results = fetch_all(query, (days,))
        return len(results) if results else 0

    @classmethod
    def delete(cls, course_id: str) -> bool:
        """
        Hard delete a course (and cascade to modules, lessons, enrollments)

        WARNING: This permanently deletes the course and all related data!
        Use trash() for soft delete instead.

        Args:
            course_id: Course UUID

        Returns:
            True if deleted, False otherwise
        """
        query = "DELETE FROM courses.courses WHERE course_id = %s RETURNING course_id"
        result = fetch_one(query, (course_id,))

        if result:
            CacheService.invalidate_course_cache(course_id)
            return True

        return False
