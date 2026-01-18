"""
Course Search and Filtering Operations

Handles public course discovery:
- Search public published courses
- Apply multiple filters (category, level, language, price, tags)
- Pagination support
- Aggregation of course metadata (chapters, enrollments)

Used by learners and course browsers (non-admin).
"""

from typing import Optional, Dict, List, Any

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all
from app.infrastructure.persistence.repositories.base_repository import BaseRepository


class CourseRepositorySearch(BaseRepository):
    """
    Search and filtering operations for courses

    Provides methods for discovering and filtering public courses
    with various filters and pagination.
    """

    table_name = 'courses.courses'

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
        conditions = ["c.status != 'archived'"]
        params = []

        # For non-admin requests, only show public published courses
        if not include_drafts:
            conditions.append("c.published = TRUE")
            conditions.append("c.published = TRUE")

        # Filter by course type
        if course_type:
            conditions.append("c.course_type = %s")
            params.append(course_type)

        if search_term:
            conditions.append("(c.title ILIKE %s OR c.description ILIKE %s)")
            params.append(f'%{search_term}%')
            params.append(f'%{search_term}%')

        if category:
            conditions.append("cat.name = %s")
            params.append(category)

        if level:
            conditions.append("c.level = %s")
            params.append(level)

        if language:
            conditions.append("c.language_default = %s")
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
            FROM courses.courses c
            WHERE {where_clause}
        """

        # Data query
        data_query = f"""
            SELECT
                c.*,
                u.firstname || ' ' || u.lastname AS creator_name,
                (SELECT COUNT(*) FROM courses.chapters WHERE course_id = c.course_id) AS chapter_count,
                (SELECT COUNT(*) FROM courses.course_enrollments WHERE course_id = c.course_id) AS enrollment_count
            FROM courses.courses c
            LEFT JOIN core.users u ON c.creator_user_id = u.user_id
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
