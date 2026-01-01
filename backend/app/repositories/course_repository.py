"""
LernsystemX Course Repository

Data access layer for course management:
- CRUD operations for courses
- Course search and filtering
- Course publishing and archiving
- Multi-tenancy support (LSX Academy, Schools, Companies)
- Creator and organisation-based access control

ISO 27001:2013 compliant - Secure course data management
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
from psycopg.rows import dict_row

from app.database.connection import get_connection, fetch_one, fetch_all, execute_query, insert_returning
from app.repositories.base_repository import BaseRepository
from app.services.cache_service import CacheService
from flask import current_app


class CourseRepository(BaseRepository):
    """
    Repository for Course entity

    Handles all database operations for courses including:
    - Course creation and management
    - Search and filtering
    - Publishing workflow
    - Organisation and creator-based access control
    """

    table_name = 'courses'

    @classmethod
    def create(cls, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new course

        Args:
            course_data: Course data including:
                - title: str (required)
                - description: str
                - creator_id: int (required)
                - organisation_id: int (optional, for org courses)
                - category: str
                - level: str (beginner, intermediate, advanced, expert)
                - language: str (default: 'de')
                - price: Decimal
                - is_public: bool (default: False)
                - is_published: bool (default: False)
                - thumbnail_url: str
                - preview_video_url: str
                - tags: list of str

        Returns:
            Created course with course_id

        Example:
            >>> course = CourseRepository.create({
            ...     'title': 'Python Grundlagen',
            ...     'creator_id': 1,
            ...     'level': 'beginner',
            ...     'language': 'de'
            ... })
        """
        query = """
            INSERT INTO courses (
                title, description, creator_user_id, organisation_id, course_type,
                category, level, language, price,
                is_public, is_published, thumbnail_url, preview_video_url,
                tags, created_at, updated_at
            ) VALUES (
                %(title)s, %(description)s, %(creator_user_id)s, %(organisation_id)s, 'standard',
                %(category)s, %(level)s, %(language)s, %(price)s,
                %(is_public)s, %(is_published)s, %(thumbnail_url)s, %(preview_video_url)s,
                %(tags)s, NOW(), NOW()
            )
            RETURNING
                course_id, title, description, creator_user_id AS creator_id, organisation_id,
                category, level, language, price, is_public, is_published,
                thumbnail_url, preview_video_url, tags,
                created_at, updated_at, published_at, archived_at
        """

        # Map creator_id to creator_user_id
        if 'creator_id' in course_data:
            course_data['creator_user_id'] = course_data.pop('creator_id')

        # Set defaults
        defaults = {
            'description': None,
            'organisation_id': None,
            'category': None,
            'level': 'beginner',
            'language': 'de',
            'price': 0.00,
            'is_public': False,
            'is_published': False,
            'thumbnail_url': None,
            'preview_video_url': None,
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
                        (SELECT COUNT(*) FROM chapters WHERE course_id = c.course_id) AS chapter_count,
                        (SELECT COUNT(*) FROM course_enrollments WHERE course_id = c.course_id) AS enrollment_count
                    FROM courses c
                    LEFT JOIN users u ON c.creator_user_id = u.user_id
                    LEFT JOIN organisations o ON c.organisation_id = o.organisation_id
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
                (SELECT COUNT(*) FROM chapters WHERE course_id = c.course_id) AS chapter_count,
                (SELECT COUNT(*) FROM course_enrollments WHERE course_id = c.course_id) AS enrollment_count
            FROM courses c
            LEFT JOIN users u ON c.creator_user_id = u.user_id
            LEFT JOIN organisations o ON c.organisation_id = o.organisation_id
            WHERE c.course_id = %s
        """

        return fetch_one(query, (course_id,))

    @classmethod
    def find_by_creator(cls, creator_id: int, include_archived: bool = False, course_type: str = 'creator') -> List[Dict[str, Any]]:
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
                (SELECT COUNT(*) FROM chapters WHERE course_id = c.course_id) AS chapter_count,
                (SELECT COUNT(*) FROM course_enrollments WHERE course_id = c.course_id) AS enrollment_count
            FROM courses c
            WHERE c.creator_user_id = %s
        """
        params = [creator_id]

        # Filter by course_type - by default only show 'creator' courses (user-created)
        # Academy courses created by admins should not appear in "Meine Kurse"
        if course_type:
            query += " AND c.course_type = %s"
            params.append(course_type)

        if not include_archived:
            query += " AND c.archived_at IS NULL"

        query += " ORDER BY c.created_at DESC"

        return fetch_all(query, tuple(params))

    @classmethod
    def find_by_organisation(cls, organisation_id: int, include_archived: bool = False) -> List[Dict[str, Any]]:
        """
        Find all courses by organisation

        Args:
            organisation_id: Organisation ID
            include_archived: Include archived courses

        Returns:
            List of courses
        """
        query = """
            SELECT
                c.*,
                u.firstname || ' ' || u.lastname AS creator_name,
                (SELECT COUNT(*) FROM chapters WHERE course_id = c.course_id) AS chapter_count,
                (SELECT COUNT(*) FROM course_enrollments WHERE course_id = c.course_id) AS enrollment_count
            FROM courses c
            LEFT JOIN users u ON c.creator_user_id = u.user_id
            WHERE c.organisation_id = %s
        """

        if not include_archived:
            query += " AND c.archived_at IS NULL"

        query += " ORDER BY c.created_at DESC"

        return fetch_all(query, (organisation_id,))

    @classmethod
    def search_public_courses(
        cls,
        search_term: Optional[str] = None,
        category: Optional[str] = None,
        level: Optional[str] = None,
        language: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        tags: Optional[List[str]] = None,
        course_type: Optional[str] = None,
        include_drafts: bool = False,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search public published courses with filters

        Args:
            search_term: Search in title and description
            category: Filter by category
            level: Filter by level
            language: Filter by language
            min_price: Minimum price
            max_price: Maximum price
            tags: Filter by tags (any match)
            course_type: Filter by course type (academy, creator)
            include_drafts: If True, include draft courses (for admins)
            limit: Results per page
            offset: Page offset

        Returns:
            Dict with 'items' and 'total' count
        """
        conditions = ["c.archived_at IS NULL"]
        params = []

        # For non-admin requests, only show public published courses
        if not include_drafts:
            conditions.append("c.is_public = TRUE")
            conditions.append("c.is_published = TRUE")

        # Filter by course type
        if course_type:
            conditions.append("c.course_type = %s")
            params.append(course_type)

        if search_term:
            conditions.append("(c.title ILIKE %s OR c.description ILIKE %s)")
            params.append(f'%{search_term}%')
            params.append(f'%{search_term}%')

        if category:
            conditions.append("c.category = %s")
            params.append(category)

        if level:
            conditions.append("c.level = %s")
            params.append(level)

        if language:
            conditions.append("c.language = %s")
            params.append(language)

        if min_price is not None:
            conditions.append("c.price >= %s")
            params.append(min_price)

        if max_price is not None:
            conditions.append("c.price <= %s")
            params.append(max_price)

        if tags:
            conditions.append("c.tags && %s")
            params.append(tags)

        where_clause = " AND ".join(conditions)

        # Count query - use same params without limit/offset
        count_query = f"""
            SELECT COUNT(*) as total
            FROM courses c
            WHERE {where_clause}
        """

        # Data query
        data_query = f"""
            SELECT
                c.*,
                u.firstname || ' ' || u.lastname AS creator_name,
                (SELECT COUNT(*) FROM chapters WHERE course_id = c.course_id) AS chapter_count,
                (SELECT COUNT(*) FROM course_enrollments WHERE course_id = c.course_id) AS enrollment_count
            FROM courses c
            LEFT JOIN users u ON c.creator_user_id = u.user_id
            WHERE {where_clause}
            ORDER BY c.created_at DESC
            LIMIT %s OFFSET %s
        """

        # Execute count query with filter params only
        total_result = fetch_one(count_query, tuple(params))
        total = total_result['total'] if total_result else 0

        # Execute data query with filter params + limit/offset
        data_params = params + [limit, offset]
        items = fetch_all(data_query, tuple(data_params))

        return {
            'items': items,
            'total': total,
            'limit': limit,
            'offset': offset
        }

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
            UPDATE courses
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
            UPDATE courses
            SET
                is_published = TRUE,
                status = 'published',
                published_at = NOW(),
                updated_at = NOW()
            WHERE course_id = %s AND is_published = FALSE
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
            UPDATE courses
            SET
                is_published = FALSE,
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
            UPDATE courses
            SET
                archived_at = NOW(),
                is_published = FALSE,
                status = 'archived',
                updated_at = NOW()
            WHERE course_id = %s AND archived_at IS NULL
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
            UPDATE courses
            SET
                archived_at = NULL,
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
        query = "DELETE FROM courses WHERE course_id = %s RETURNING course_id"
        result = fetch_one(query, (course_id,))

        # Invalidate course cache after deletion
        if result:
            CacheService.invalidate_course_cache(course_id)
            return True

        return False

    @classmethod
    def get_statistics(cls, course_id: int) -> Dict[str, Any]:
        """
        Get course statistics

        Args:
            course_id: Course ID

        Returns:
            Statistics dict with counts and averages
        """
        query = """
            SELECT
                c.course_id,
                c.title,
                COUNT(DISTINCT ch.chapter_id) AS chapter_count,
                COUNT(DISTINCT l.lesson_id) AS lesson_count,
                COUNT(DISTINCT e.enrollment_id) AS enrollment_count,
                COUNT(DISTINCT CASE WHEN e.status = 'completed' THEN e.enrollment_id END) AS completed_count,
                AVG(e.progress_percentage) AS avg_progress,
                SUM(CASE WHEN e.status = 'active' THEN 1 ELSE 0 END) AS active_students
            FROM courses c
            LEFT JOIN chapters ch ON c.course_id = ch.course_id
            LEFT JOIN lessons l ON ch.chapter_id = l.chapter_id
            LEFT JOIN course_enrollments e ON c.course_id = e.course_id
            WHERE c.course_id = %s
            GROUP BY c.course_id, c.title
        """

        result = fetch_one(query, (course_id,))

        if not result:
            return {}

        return {
            'course_id': result['course_id'],
            'title': result['title'],
            'chapter_count': result['chapter_count'] or 0,
            'lesson_count': result['lesson_count'] or 0,
            'enrollment_count': result['enrollment_count'] or 0,
            'completed_count': result['completed_count'] or 0,
            'avg_progress': float(result['avg_progress']) if result['avg_progress'] else 0.0,
            'active_students': result['active_students'] or 0
        }

    # ==========================================
    # ADMIN METHODS (Phase B24-02)
    # ==========================================

    @classmethod
    def admin_list_courses(
        cls,
        page: int = 1,
        per_page: int = 50,
        status: str = 'all',
        search: Optional[str] = None,
        creator_id: Optional[int] = None,
        organisation_id: Optional[int] = None,
        category: Optional[str] = None,
        category_id: Optional[int] = None,
        level: Optional[str] = None,
        language: Optional[str] = None,
        sort: str = 'created_at',
        order: str = 'desc'
    ) -> Dict[str, Any]:
        """
        Admin: List all courses with advanced filtering and pagination

        Args:
            page: Page number (1-indexed)
            per_page: Items per page (max 100)
            status: Filter by status (all, draft, published, archived)
            search: Search in title and description
            creator_id: Filter by creator
            organisation_id: Filter by organisation
            category: Filter by category
            level: Filter by level
            language: Filter by language
            sort: Sort field (created_at, updated_at, title, enrollment_count)
            order: Sort order (asc, desc)

        Returns:
            Dict with 'courses' list and 'pagination' info
        """
        conditions = []
        params = []
        param_idx = 1

        # Status filter (virtual status based on is_published and archived_at)
        if status == 'draft':
            conditions.append("c.is_published = FALSE AND c.archived_at IS NULL")
        elif status == 'published':
            conditions.append("c.is_published = TRUE AND c.archived_at IS NULL")
        elif status == 'archived':
            conditions.append("c.archived_at IS NOT NULL")
        # 'all' = no status filter

        # Search filter
        if search:
            conditions.append("(c.title ILIKE %s OR c.description ILIKE %s)")
            params.append(f'%{search}%')
            params.append(f'%{search}%')

        # Creator filter
        if creator_id:
            conditions.append("c.creator_user_id = %s")
            params.append(creator_id)

        # Organisation filter
        if organisation_id:
            conditions.append("c.organisation_id = %s")
            params.append(organisation_id)

        # Category filter (by name)
        if category:
            conditions.append("c.category = %s")
            params.append(category)

        # Category filter (by ID)
        if category_id:
            conditions.append("c.category_id = %s")
            params.append(category_id)

        # Level filter
        if level:
            conditions.append("c.level = %s")
            params.append(level)

        # Language filter
        if language:
            conditions.append("c.language = %s")
            params.append(language)

        where_clause = " AND ".join(conditions) if conditions else "TRUE"

        # Validate sort field
        valid_sorts = {'created_at', 'updated_at', 'title', 'enrollment_count'}
        if sort not in valid_sorts:
            sort = 'created_at'

        # Validate order
        order = 'DESC' if order.lower() == 'desc' else 'ASC'

        # Count query
        count_query = f"""
            SELECT COUNT(*) as total
            FROM courses c
            WHERE {where_clause}
        """

        # Data query with sort
        data_query = f"""
            SELECT
                c.course_id,
                c.title,
                c.description,
                c.creator_user_id,
                u.firstname || ' ' || u.lastname AS creator_name,
                c.organisation_id,
                o.name AS organisation_name,
                c.category,
                c.category_id,
                cat.name AS category_name,
                c.level,
                c.language,
                c.price,
                c.is_public,
                c.is_published,
                c.thumbnail_url,
                c.tags,
                c.created_at,
                c.updated_at,
                c.published_at,
                c.archived_at,
                (SELECT COUNT(*) FROM chapters WHERE course_id = c.course_id) AS chapter_count,
                (SELECT COUNT(*) FROM course_enrollments WHERE course_id = c.course_id) AS enrollment_count,
                CASE
                    WHEN c.archived_at IS NOT NULL THEN 'archived'
                    WHEN c.is_published = TRUE THEN 'published'
                    ELSE 'draft'
                END AS status
            FROM courses c
            LEFT JOIN users u ON c.creator_user_id = u.user_id
            LEFT JOIN organisations o ON c.organisation_id = o.organisation_id
            LEFT JOIN course_categories cat ON c.category_id = cat.category_id
            WHERE {where_clause}
            ORDER BY {sort} {order}
            LIMIT %s OFFSET %s
        """

        # Calculate offset
        offset = (page - 1) * per_page
        params.extend([per_page, offset])

        # Execute queries
        total_result = fetch_one(count_query, tuple(params[:-2]))
        total = total_result['total'] if total_result else 0

        courses = fetch_all(data_query, tuple(params))

        # Calculate pagination
        total_pages = (total + per_page - 1) // per_page

        return {
            'courses': courses,
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            }
        }

    @classmethod
    def admin_get_course_by_id(cls, course_id: int) -> Optional[Dict[str, Any]]:
        """
        Admin: Get detailed course information (bypass cache)

        Args:
            course_id: Course ID

        Returns:
            Course dict with all details, or None
        """
        query = """
            SELECT
                c.*,
                u.firstname || ' ' || u.lastname AS creator_name,
                u.email AS creator_email,
                o.name AS organisation_name,
                cc.name AS category_name,
                (SELECT COUNT(*) FROM chapters WHERE course_id = c.course_id) AS chapter_count,
                (SELECT COUNT(*) FROM course_enrollments WHERE course_id = c.course_id) AS enrollment_count,
                CASE
                    WHEN c.archived_at IS NOT NULL THEN 'archived'
                    WHEN c.is_published = TRUE THEN 'published'
                    ELSE 'draft'
                END AS status
            FROM courses c
            LEFT JOIN users u ON c.creator_user_id = u.user_id
            LEFT JOIN organisations o ON c.organisation_id = o.organisation_id
            LEFT JOIN course_categories cc ON c.category_id = cc.category_id
            WHERE c.course_id = %s
        """

        return fetch_one(query, (course_id,))

    @classmethod
    def admin_create_course(cls, course_data: Dict[str, Any], created_by_admin: int) -> Optional[Dict[str, Any]]:
        """
        Admin: Create a course on behalf of a creator

        Args:
            course_data: Course data including creator_id
            created_by_admin: Admin user ID who created this

        Returns:
            Created course dict or None
        """
        query = """
            INSERT INTO courses (
                title, description, creator_user_id, organisation_id, course_type,
                category, level, language, price,
                is_public, is_published, thumbnail_url, preview_video_url,
                tags, created_at, updated_at
            ) VALUES (
                %(title)s, %(description)s, %(creator_user_id)s, %(organisation_id)s, 'academy',
                %(category)s, %(level)s, %(language)s, %(price)s,
                %(is_public)s, FALSE, %(thumbnail_url)s, %(preview_video_url)s,
                %(tags)s, NOW(), NOW()
            )
            RETURNING
                course_id, title, description, creator_user_id AS creator_id, organisation_id,
                category, level, language, price, is_public, is_published,
                thumbnail_url, preview_video_url, tags,
                created_at, updated_at, published_at, archived_at
        """

        # Set defaults
        defaults = {
            'description': None,
            'organisation_id': None,
            'category': None,
            'level': 'beginner',
            'language': 'de',
            'price': 0.00,
            'is_public': False,
            'thumbnail_url': None,
            'preview_video_url': None,
            'tags': []
        }

        params = {**defaults, **course_data}

        # Rename creator_id to creator_user_id for query
        if 'creator_id' in params:
            params['creator_user_id'] = params.pop('creator_id')

        # Convert category_id to category if present
        if 'category_id' in params and params['category_id']:
            # TODO: Lookup category name from ID - for now just remove it
            params.pop('category_id')

        return fetch_one(query, params)

    @classmethod
    def admin_update_course(cls, course_id: str, update_data: Dict[str, Any], updated_by_admin: int) -> Optional[Dict[str, Any]]:
        """
        Admin: Update course metadata

        Args:
            course_id: Course ID (UUID string)
            update_data: Fields to update
            updated_by_admin: Admin user ID who updated this

        Returns:
            Updated course or None
        """
        from app.database.connection import update_returning

        # Don't allow updating these fields
        restricted_fields = ['course_id', 'creator_id', 'creator_user_id', 'created_at', 'published_at', 'archived_at']
        update_data = {k: v for k, v in update_data.items() if k not in restricted_fields}

        if not update_data:
            return cls.find_by_id(course_id, use_cache=False)

        # Always update updated_at
        update_data['updated_at'] = datetime.utcnow()

        # Use update_returning helper function
        result = update_returning(
            table='courses',
            data=update_data,
            where='course_id = %s',
            where_params=(course_id,),
            returning='*'
        )

        # Invalidate cache
        if result:
            CacheService.invalidate_course_cache(course_id)

        return result
