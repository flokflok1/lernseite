"""
Course CRUD Operations (Create, Read, Update)

Handles basic course data access operations:
- Course creation
- Retrieving course details by ID
- Fetching courses by creator or organization
- Updating course metadata
- Cache invalidation

Inherits from BaseRepository for connection pooling and standard operations.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime

from app.database.connection import fetch_one, fetch_all, insert_returning
from app.repositories.base_repository import BaseRepository
from app.services.cache_service import CacheService
from flask import current_app


class CourseRepositoryCRUD(BaseRepository):
    """
    CRUD operations for Course entity

    Handles all basic database operations for courses including:
    - Course creation
    - Finding courses by ID, creator, or organization
    - Updating course metadata
    - Cache management
    """

    table_name = 'courses.courses'

    @classmethod
    def create(cls, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new course

        Args:
            course_data: Course data including:
                - title: str (required)
                - description: str
                - creator_id: int (required)
                - organization_id: int (optional, for org courses)
                - category: str
                - level: str (beginner, intermediate, advanced, expert)
                - language: str (default: 'de')
                - price: Decimal
                - is_public: bool (default: False)
                - is_published: bool (default: False)
                - thumbnail_url: str
                - video_preview_url: str
                - tags: list of str

        Returns:
            Created course with course_id

        Example:
            >>> course = CourseRepository.create({
            ...     'title': 'Python Grundlagen',
            ...     'creator_id': 1,
            ...     'level': 'beginner',
            ...     'language_default': 'de'
            ... })
        """
        query = """
            INSERT INTO courses.courses (
                title, description, creator_user_id, organization_id, course_type,
                category_id, level, language_default, price,
                published, thumbnail_url, video_preview_url,
                tags, status, created_at, updated_at
            ) VALUES (
                %(title)s, %(description)s, %(creator_user_id)s, %(organization_id)s, 'standard',
                %(category_id)s, %(level)s, %(language_default)s, %(price)s,
                %(published)s, %(thumbnail_url)s, %(video_preview_url)s,
                %(tags)s, 'draft', NOW(), NOW()
            )
            RETURNING
                course_id, title, description, creator_user_id AS creator_id, organization_id,
                category_id, level, language_default, price, published,
                thumbnail_url, video_preview_url, tags,
                created_at, updated_at, published_at, status
        """

        # Map creator_id to creator_user_id
        if 'creator_id' in course_data:
            course_data['creator_user_id'] = course_data.pop('creator_id')

        # Set defaults
        defaults = {
            'description': None,
            'organization_id': None,
            'category_id': None,
            'level': 'beginner',
            'language_default': 'de',
            'price': 0.00,
            'published': False,
            'thumbnail_url': None,
            'video_preview_url': None,
            'tags': []
        }

        params = {**defaults, **course_data}

        return insert_returning(query, params)

    @classmethod
    def find_by_id(cls, course_id: int, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Find course by ID with creator and organisation info

        Args:
            course_id: Course ID
            use_cache: Use cache (default: True)

        Returns:
            Course dict with creator name or None
        """
        # Try cache first
        if use_cache:
            cache_key = CacheService.make_key('COURSE', str(course_id), 'detail')
            ttl = current_app.config.get('CACHE_COURSE_TTL', 3600)

            def load_course():
                query = """
                    SELECT
                        c.*,
                        u.firstname || ' ' || u.lastname AS creator_name,
                        u.email AS creator_email,
                        o.name AS organisation_name,
                        (SELECT COUNT(*) FROM courses.chapters WHERE course_id = c.course_id) AS chapter_count,
                        (SELECT COUNT(*) FROM courses.course_enrollments WHERE course_id = c.course_id) AS enrollment_count
                    FROM courses.courses c
                    LEFT JOIN core.users u ON c.creator_user_id = u.user_id
                    LEFT JOIN organisations.organisations o ON c.organization_id = o.organization_id
                    WHERE c.course_id = %s
                """
                return fetch_one(query, (course_id,))

            return CacheService.cache_get_or_set(cache_key, ttl, load_course)

        # Bypass cache
        query = """
            SELECT
                c.*,
                u.firstname || ' ' || u.lastname AS creator_name,
                u.email AS creator_email,
                o.name AS organisation_name,
                (SELECT COUNT(*) FROM courses.chapters WHERE course_id = c.course_id) AS chapter_count,
                (SELECT COUNT(*) FROM courses.course_enrollments WHERE course_id = c.course_id) AS enrollment_count
            FROM courses.courses c
            LEFT JOIN core.users u ON c.creator_user_id = u.user_id
            LEFT JOIN organisations.organisations o ON c.organization_id = o.organization_id
            WHERE c.course_id = %s
        """

        return fetch_one(query, (course_id,))

    @classmethod
    def find_by_creator(
        cls,
        creator_id: int,
        include_archived: bool = False,
        course_type: str = 'creator'
    ) -> List[Dict[str, Any]]:
        """
        Find all courses by creator

        Args:
            creator_id: Creator user ID
            include_archived: Include archived courses
            course_type: Filter by course type ('creator', 'academy', or None for all)

        Returns:
            List of courses
        """
        query = """
            SELECT
                c.*,
                (SELECT COUNT(*) FROM courses.chapters WHERE course_id = c.course_id) AS chapter_count,
                (SELECT COUNT(*) FROM courses.course_enrollments WHERE course_id = c.course_id) AS enrollment_count
            FROM courses.courses c
            WHERE c.creator_user_id = %s
        """
        params = [creator_id]

        # Filter by course_type - by default only show 'creator' courses (user-created)
        # Academy courses created by admins should not appear in "Meine Kurse"
        if course_type:
            query += " AND c.course_type = %s"
            params.append(course_type)

        if not include_archived:
            query += " AND c.status != 'archived'"

        query += " ORDER BY c.created_at DESC"

        return fetch_all(query, tuple(params))

    @classmethod
    def find_by_organisation(
        cls,
        organization_id: int,
        include_archived: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Find all courses by organisation

        Args:
            organization_id: Organisation ID
            include_archived: Include archived courses

        Returns:
            List of courses
        """
        query = """
            SELECT
                c.*,
                u.firstname || ' ' || u.lastname AS creator_name,
                (SELECT COUNT(*) FROM courses.chapters WHERE course_id = c.course_id) AS chapter_count,
                (SELECT COUNT(*) FROM courses.course_enrollments WHERE course_id = c.course_id) AS enrollment_count
            FROM courses.courses c
            LEFT JOIN core.users u ON c.creator_user_id = u.user_id
            WHERE c.organization_id = %s
        """

        if not include_archived:
            query += " AND c.status != 'archived'"

        query += " ORDER BY c.created_at DESC"

        return fetch_all(query, (organization_id,))

    @classmethod
    def update(cls, course_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update course

        Args:
            course_id: Course ID
            update_data: Fields to update

        Returns:
            Updated course or None
        """
        # Don't allow updating these fields directly
        restricted_fields = ['course_id', 'creator_id', 'created_at', 'published_at', 'archived_at']
        update_data = {k: v for k, v in update_data.items() if k not in restricted_fields}

        if not update_data:
            return cls.find_by_id(course_id)

        # Always update updated_at
        update_data['updated_at'] = datetime.utcnow()

        # Build SET clause
        set_parts = [f"{key} = %({key})s" for key in update_data.keys()]
        set_clause = ", ".join(set_parts)

        query = f"""
            UPDATE courses.courses
            SET {set_clause}
            WHERE course_id = %(course_id)s
            RETURNING *
        """

        params = {**update_data, 'course_id': course_id}

        result = insert_returning(query, params)

        # Invalidate course cache after update
        if result:
            CacheService.invalidate_course_cache(course_id)

        return result
