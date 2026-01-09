"""
Course Repository (DB-First Architecture)

All course data loaded dynamically from database.
NO hardcoded values or configurations.

Uses Repository Pattern with direct SQL (NO ORM).
"""

from typing import List, Optional, Dict, Any
from src.infrastructure.database.base_repository import BaseRepository
from src.api.content.courses.core.domain.entities.course import Course


class CourseRepository(BaseRepository):
    """
    Course repository for database access.

    ALL data loaded from database dynamically.
    NO hardcoded course lists or configurations.
    """

    @staticmethod
    def find_by_id(course_id: str) -> Optional[Course]:
        """
        Find course by ID.

        Args:
            course_id: Course UUID

        Returns:
            Course entity or None
        """
        query = """
            SELECT
                course_id, title, description, creator_id, category_id,
                difficulty_level, status, visibility, is_published,
                is_drm_protected, organisation_id, price,
                created_at, updated_at, published_at
            FROM courses
            WHERE course_id = %s
        """
        row = CourseRepository.fetch_one(query, (course_id,))

        if row:
            return Course(**row)
        return None

    @staticmethod
    def find_all(
        status: Optional[str] = None,
        visibility: Optional[str] = None,
        creator_id: Optional[str] = None,
        category_id: Optional[str] = None,
        organisation_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Course]:
        """
        Find courses with dynamic filters.

        ALL filter values come from database or parameters.
        NO hardcoded filter lists.

        Args:
            status: Filter by status (from DB enum)
            visibility: Filter by visibility (from DB enum)
            creator_id: Filter by creator
            category_id: Filter by category (from DB)
            organisation_id: Filter by organisation
            limit: Result limit
            offset: Result offset

        Returns:
            List of course entities
        """
        query = """
            SELECT
                course_id, title, description, creator_id, category_id,
                difficulty_level, status, visibility, is_published,
                is_drm_protected, organisation_id, price,
                created_at, updated_at, published_at
            FROM courses
            WHERE 1=1
        """
        params = []

        # Dynamic filters - NO hardcoded values
        if status:
            query += " AND status = %s"
            params.append(status)

        if visibility:
            query += " AND visibility = %s"
            params.append(visibility)

        if creator_id:
            query += " AND creator_id = %s"
            params.append(creator_id)

        if category_id:
            query += " AND category_id = %s"
            params.append(category_id)

        if organisation_id:
            query += " AND organisation_id = %s"
            params.append(organisation_id)

        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        rows = CourseRepository.fetch_all(query, tuple(params))
        return [Course(**row) for row in rows]

    @staticmethod
    def find_published(
        category_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Course]:
        """
        Find published public courses.

        Args:
            category_id: Optional category filter (from DB)
            limit: Result limit
            offset: Result offset

        Returns:
            List of published courses
        """
        query = """
            SELECT
                course_id, title, description, creator_id, category_id,
                difficulty_level, status, visibility, is_published,
                is_drm_protected, organisation_id, price,
                created_at, updated_at, published_at
            FROM courses
            WHERE is_published = TRUE AND visibility = 'public'
        """
        params = []

        if category_id:
            query += " AND category_id = %s"
            params.append(category_id)

        query += " ORDER BY published_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        rows = CourseRepository.fetch_all(query, tuple(params))
        return [Course(**row) for row in rows]

    @staticmethod
    def create(course: Course) -> Course:
        """
        Create new course.

        Args:
            course: Course entity to create

        Returns:
            Created course with DB-generated fields
        """
        query = """
            INSERT INTO courses (
                course_id, title, description, creator_id, category_id,
                difficulty_level, status, visibility, is_published,
                is_drm_protected, organisation_id, price,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
            )
            RETURNING
                course_id, title, description, creator_id, category_id,
                difficulty_level, status, visibility, is_published,
                is_drm_protected, organisation_id, price,
                created_at, updated_at, published_at
        """
        params = (
            course.course_id,
            course.title,
            course.description,
            course.creator_id,
            course.category_id,
            course.difficulty_level,
            course.status,
            course.visibility,
            course.is_published,
            course.is_drm_protected,
            course.organisation_id,
            course.price,
        )

        row = CourseRepository.execute_returning(query, params)
        return Course(**row) if row else course

    @staticmethod
    def update(course: Course) -> Course:
        """
        Update existing course.

        Args:
            course: Course entity with updates

        Returns:
            Updated course
        """
        query = """
            UPDATE courses SET
                title = %s,
                description = %s,
                category_id = %s,
                difficulty_level = %s,
                status = %s,
                visibility = %s,
                is_published = %s,
                is_drm_protected = %s,
                price = %s,
                updated_at = NOW(),
                published_at = %s
            WHERE course_id = %s
            RETURNING
                course_id, title, description, creator_id, category_id,
                difficulty_level, status, visibility, is_published,
                is_drm_protected, organisation_id, price,
                created_at, updated_at, published_at
        """
        params = (
            course.title,
            course.description,
            course.category_id,
            course.difficulty_level,
            course.status,
            course.visibility,
            course.is_published,
            course.is_drm_protected,
            course.price,
            course.published_at,
            course.course_id,
        )

        row = CourseRepository.execute_returning(query, params)
        return Course(**row) if row else course

    @staticmethod
    def delete(course_id: str) -> bool:
        """
        Delete course (soft delete - archive instead).

        Args:
            course_id: Course UUID

        Returns:
            True if deleted
        """
        query = """
            UPDATE courses SET
                status = 'archived',
                is_published = FALSE,
                updated_at = NOW()
            WHERE course_id = %s
        """
        affected = CourseRepository.execute(query, (course_id,))
        return affected > 0

    @staticmethod
    def count(
        status: Optional[str] = None,
        creator_id: Optional[str] = None,
        category_id: Optional[str] = None
    ) -> int:
        """
        Count courses with dynamic filters.

        Args:
            status: Filter by status
            creator_id: Filter by creator
            category_id: Filter by category

        Returns:
            Course count
        """
        query = "SELECT COUNT(*) as count FROM courses WHERE 1=1"
        params = []

        if status:
            query += " AND status = %s"
            params.append(status)

        if creator_id:
            query += " AND creator_id = %s"
            params.append(creator_id)

        if category_id:
            query += " AND category_id = %s"
            params.append(category_id)

        row = CourseRepository.fetch_one(query, tuple(params))
        return row['count'] if row else 0
