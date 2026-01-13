"""
Admin Course Management Operations

Admin-only course operations:
- List all courses with advanced filtering
- Get detailed course information (bypass cache)
- Create courses on behalf of creators (academy courses)
- Update course metadata with audit trail

Requires admin role for all operations.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime

from app.database.connection import fetch_one, fetch_all, update_returning
from app.repositories.base_repository import BaseRepository
from app.services.cache_service import CacheService


class CourseRepositoryAdmin(BaseRepository):
    """
    Admin-specific course management operations

    Provides methods for system administrators to manage all courses,
    including advanced filtering, listing, and creation workflows.
    """

    table_name = 'courses.courses'

    @classmethod
    def admin_list_courses(
        cls,
        page: int = 1,
        per_page: int = 50,
        status: str = 'all',
        search: Optional[str] = None,
        creator_id: Optional[int] = None,
        organization_id: Optional[int] = None,
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
            organization_id: Filter by organisation
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

        # Status filter (virtual status based on is_published and archived_at)
        if status == 'draft':
            conditions.append("c.published = FALSE AND c.status != 'archived'")
        elif status == 'published':
            conditions.append("c.published = TRUE AND c.status != 'archived'")
        elif status == 'archived':
            conditions.append("c.status = 'archived'")
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
        if organization_id:
            conditions.append("c.organization_id = %s")
            params.append(organization_id)

        # Category filter (by name)
        if category:
            conditions.append("cat.name = %s")
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
            conditions.append("c.language_default = %s")
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
            FROM courses.courses c
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
                c.organization_id,
                o.name AS organisation_name,
                c.category_id,
                cat.name AS category_name,
                c.level,
                c.language_default,
                c.price,
                c.published,
                c.thumbnail_url,
                c.tags,
                c.created_at,
                c.updated_at,
                c.published_at,
                (SELECT COUNT(*) FROM courses.chapters WHERE course_id = c.course_id) AS chapter_count,
                (SELECT COUNT(*) FROM courses.course_enrollments WHERE course_id = c.course_id) AS enrollment_count,
                c.status
            FROM courses.courses c
            LEFT JOIN core.users u ON c.creator_user_id = u.user_id
            LEFT JOIN organisations.organizations o ON c.organization_id = o.organization_id
            LEFT JOIN courses.course_categories cat ON c.category_id = cat.category_id
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
                (SELECT COUNT(*) FROM courses.chapters WHERE course_id = c.course_id) AS chapter_count,
                (SELECT COUNT(*) FROM courses.course_enrollments WHERE course_id = c.course_id) AS enrollment_count
            FROM courses.courses c
            LEFT JOIN core.users u ON c.creator_user_id = u.user_id
            LEFT JOIN organisations.organizations o ON c.organization_id = o.organization_id
            LEFT JOIN courses.course_categories cc ON c.category_id = cc.category_id
            WHERE c.course_id = %s
        """

        return fetch_one(query, (course_id,))

    @classmethod
    def admin_create_course(
        cls,
        course_data: Dict[str, Any],
        created_by_admin: int
    ) -> Optional[Dict[str, Any]]:
        """
        Admin: Create a course on behalf of a creator

        Args:
            course_data: Course data including creator_id
            created_by_admin: Admin user ID who created this

        Returns:
            Created course dict or None
        """
        query = """
            INSERT INTO courses.courses (
                title, description, creator_user_id, organization_id, course_type,
                category_id, level, language_default, price,
                published, thumbnail_url, video_preview_url,
                tags, status, created_at, updated_at
            ) VALUES (
                %(title)s, %(description)s, %(creator_user_id)s, %(organization_id)s, 'academy',
                %(category_id)s, %(level)s, %(language_default)s, %(price)s,
                FALSE, %(thumbnail_url)s, %(video_preview_url)s,
                %(tags)s, 'draft', NOW(), NOW()
            )
            RETURNING
                course_id, title, description, creator_user_id AS creator_id, organization_id,
                category_id, level, language_default, price, published,
                thumbnail_url, video_preview_url, tags,
                created_at, updated_at, published_at, status
        """

        # Set defaults
        defaults = {
            'description': None,
            'organization_id': None,
            'category_id': None,
            'level': 'beginner',
            'language_default': 'de',
            'price': 0.00,
            'thumbnail_url': None,
            'video_preview_url': None,
            'tags': []
        }

        params = {**defaults, **course_data}

        # Rename creator_id to creator_user_id for query
        if 'creator_id' in params:
            params['creator_user_id'] = params.pop('creator_id')

        return fetch_one(query, params)

    @classmethod
    def admin_update_course(
        cls,
        course_id: str,
        update_data: Dict[str, Any],
        updated_by_admin: int
    ) -> Optional[Dict[str, Any]]:
        """
        Admin: Update course metadata

        Args:
            course_id: Course ID (UUID string)
            update_data: Fields to update
            updated_by_admin: Admin user ID who updated this

        Returns:
            Updated course or None
        """
        # Don't allow updating these fields
        restricted_fields = ['course_id', 'creator_id', 'creator_user_id', 'created_at', 'published_at', 'archived_at']
        update_data = {k: v for k, v in update_data.items() if k not in restricted_fields}

        if not update_data:
            return cls.admin_get_course_by_id(course_id)

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
