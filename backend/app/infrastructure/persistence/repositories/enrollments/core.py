"""
LernsystemX Enrollment Repository

Data access layer for course enrollments:
- Student enrollment in courses
- Enrollment status management (active, completed, cancelled)
- Progress tracking
- Access control and validation

ISO 27001:2013 compliant - Secure enrollment data management
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
from decimal import Decimal

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query, insert_returning
from app.infrastructure.persistence.repositories.core.base import BaseRepository


class EnrollmentRepository(BaseRepository):
    """
    Repository for Enrollment entity

    Handles all database operations for course enrollments including:
    - Enrollment creation and management
    - Progress tracking and updates
    - Status management (active, completed, cancelled)
    - Certificate generation tracking
    """

    table_name = 'courses.course_enrollments'

    @classmethod
    def create(cls, enrollment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new enrollment

        Args:
            enrollment_data: Enrollment data including:
                - user_id: UUID (required)
                - course_id: UUID (required)

        Returns:
            Created enrollment with enrollment_id

        Example:
            >>> enrollment = EnrollmentRepository.create({
            ...     'user_id': 'uuid-string',
            ...     'course_id': 'uuid-string'
            ... })
        """
        # Build params with required fields only
        params = {
            'user_id': enrollment_data['user_id'],
            'course_id': enrollment_data['course_id'],
            'status': 'active',
            'completion_percentage': 0
        }

        return insert_returning(
            'course_enrollments',
            params,
            'enrollment_id, user_id, course_id, status, completion_percentage, enrolled_at, started_at, completed_at, last_accessed_at'
        )

    @classmethod
    def find_by_id(cls, enrollment_id: int) -> Optional[Dict[str, Any]]:
        """
        Find enrollment by ID with user and course info

        Args:
            enrollment_id: Enrollment ID

        Returns:
            Enrollment dict with user and course details or None
        """
        query = """
            SELECT
                e.*,
                u.full_name AS user_name,
                u.email AS user_email,
                c.title AS course_title,
                c.creator_user_id AS course_creator_id,
                c.organisation_id AS course_organisation_id
            FROM courses.course_enrollments e
            LEFT JOIN core.users u ON e.user_id = u.user_id
            LEFT JOIN courses.courses c ON e.course_id = c.course_id
            WHERE e.enrollment_id = %s
        """

        return fetch_one(query, (enrollment_id,))

    @classmethod
    def find_by_user_and_course(cls, user_id: int, course_id: int) -> Optional[Dict[str, Any]]:
        """
        Find enrollment by user and course

        Args:
            user_id: User ID
            course_id: Course ID

        Returns:
            Enrollment dict or None
        """
        query = """
            SELECT e.*
            FROM courses.course_enrollments e
            WHERE e.user_id = %s AND e.course_id = %s
        """

        return fetch_one(query, (user_id, course_id))

    @classmethod
    def is_user_enrolled(cls, user_id: int, course_id: int) -> bool:
        """
        Check if user is enrolled in course

        Args:
            user_id: User ID
            course_id: Course ID

        Returns:
            True if enrolled (active or completed), False otherwise
        """
        query = """
            SELECT COUNT(*) as count
            FROM courses.course_enrollments
            WHERE user_id = %s AND course_id = %s AND status IN ('active', 'completed')
        """

        result = fetch_one(query, (user_id, course_id))
        return result['count'] > 0 if result else False

    @classmethod
    def find_by_user(
        cls,
        user_id: int,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Find all enrollments for a user

        Args:
            user_id: User ID
            status: Filter by status (active, completed, cancelled)
            limit: Results per page
            offset: Page offset

        Returns:
            Dict with 'items' and 'total' count
        """
        conditions = ["e.user_id = %s"]
        params = [user_id]

        if status:
            conditions.append("e.status = %s")
            params.append(status)

        where_clause = " AND ".join(conditions)

        # Count query
        count_query = f"""
            SELECT COUNT(*) as total
            FROM courses.course_enrollments e
            WHERE {where_clause}
        """

        # Data query
        data_query = f"""
            SELECT
                e.*,
                c.title AS course_title,
                c.thumbnail_url AS course_thumbnail,
                c.creator_user_id,
                u.full_name AS creator_name
            FROM courses.course_enrollments e
            LEFT JOIN courses.courses c ON e.course_id = c.course_id
            LEFT JOIN core.users u ON c.creator_user_id = u.user_id
            WHERE {where_clause}
            ORDER BY e.last_accessed_at DESC NULLS LAST, e.enrolled_at DESC
            LIMIT %s OFFSET %s
        """

        params_with_pagination = params + [limit, offset]

        total_result = fetch_one(count_query, tuple(params))
        total = total_result['total'] if total_result else 0

        items = fetch_all(data_query, tuple(params_with_pagination))

        return {
            'items': items,
            'total': total,
            'limit': limit,
            'offset': offset
        }

    @classmethod
    def find_by_course(
        cls,
        course_id: int,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Find all enrollments for a course

        Args:
            course_id: Course ID
            status: Filter by status
            limit: Results per page
            offset: Page offset

        Returns:
            Dict with 'items' and 'total' count
        """
        conditions = ["e.course_id = %s"]
        params = [course_id]

        if status:
            conditions.append("e.status = %s")
            params.append(status)

        where_clause = " AND ".join(conditions)

        # Count query
        count_query = f"""
            SELECT COUNT(*) as total
            FROM courses.course_enrollments e
            WHERE {where_clause}
        """

        # Data query
        data_query = f"""
            SELECT
                e.*,
                u.full_name AS user_name,
                u.email AS user_email
            FROM courses.course_enrollments e
            LEFT JOIN core.users u ON e.user_id = u.user_id
            WHERE {where_clause}
            ORDER BY e.enrolled_at DESC
            LIMIT %s OFFSET %s
        """

        params_with_pagination = params + [limit, offset]

        total_result = fetch_one(count_query, tuple(params))
        total = total_result['total'] if total_result else 0

        items = fetch_all(data_query, tuple(params_with_pagination))

        return {
            'items': items,
            'total': total,
            'limit': limit,
            'offset': offset
        }

    @classmethod
    def update_progress(cls, enrollment_id: int, progress_percentage: float) -> Optional[Dict[str, Any]]:
        """
        Update enrollment progress

        Args:
            enrollment_id: Enrollment ID
            progress_percentage: Progress (0-100)

        Returns:
            Updated enrollment or None
        """
        # Cap progress at 100
        progress_percentage = min(progress_percentage, 100.0)

        query = """
            UPDATE courses.course_enrollments
            SET
                completion_percentage = %s,
                last_accessed_at = NOW()
            WHERE enrollment_id = %s
            RETURNING *
        """

        return fetch_one(query, (progress_percentage, enrollment_id))

    @classmethod
    def mark_completed(cls, enrollment_id: int) -> Optional[Dict[str, Any]]:
        """
        Mark enrollment as completed

        Args:
            enrollment_id: Enrollment ID

        Returns:
            Updated enrollment or None
        """
        query = """
            UPDATE courses.course_enrollments
            SET
                status = 'completed',
                completion_percentage = 100,
                completed_at = NOW()
            WHERE enrollment_id = %s AND status = 'active'
            RETURNING *
        """

        return fetch_one(query, (enrollment_id,))

    @classmethod
    def cancel(cls, enrollment_id: int) -> Optional[Dict[str, Any]]:
        """
        Cancel enrollment

        Args:
            enrollment_id: Enrollment ID

        Returns:
            Updated enrollment or None
        """
        query = """
            UPDATE courses.course_enrollments
            SET
                status = 'dropped'
            WHERE enrollment_id = %s
            RETURNING *
        """

        return fetch_one(query, (enrollment_id,))

    @classmethod
    def reactivate(cls, enrollment_id: int) -> Optional[Dict[str, Any]]:
        """
        Reactivate a cancelled/dropped enrollment

        Args:
            enrollment_id: Enrollment ID

        Returns:
            Updated enrollment or None
        """
        query = """
            UPDATE courses.course_enrollments
            SET
                status = 'active'
            WHERE enrollment_id = %s AND status IN ('dropped', 'paused')
            RETURNING *
        """

        return fetch_one(query, (enrollment_id,))

    @classmethod
    def update_last_access(cls, enrollment_id: int) -> bool:
        """
        Update last_accessed_at timestamp

        Args:
            enrollment_id: Enrollment ID

        Returns:
            True if successful
        """
        query = """
            UPDATE courses.course_enrollments
            SET last_accessed_at = NOW()
            WHERE enrollment_id = %s
        """

        return execute_query(query, (enrollment_id,))

    @classmethod
    def delete(cls, enrollment_id: int) -> bool:
        """
        Hard delete an enrollment

        Args:
            enrollment_id: Enrollment ID

        Returns:
            True if deleted, False otherwise
        """
        query = "DELETE FROM courses.course_enrollments WHERE enrollment_id = %s"
        return execute_query(query, (enrollment_id,))

    @classmethod
    def calculate_progress(cls, user_id: int, course_id: int) -> float:
        """
        Calculate user's progress percentage for a course

        Progress = (completed lessons / total lessons) * 100

        Args:
            user_id: User ID
            course_id: Course ID

        Returns:
            Progress percentage (0-100)
        """
        query = """
            SELECT
                COUNT(l.lesson_id) AS total_lessons,
                COUNT(lp.lesson_id) AS completed_lessons
            FROM courses.lessons l
            INNER JOIN courses.chapters ch ON l.chapter_id = ch.chapter_id
            LEFT JOIN lesson_progress lp ON l.lesson_id = lp.lesson_id AND lp.user_id = %s
            WHERE ch.course_id = %s
        """

        result = fetch_one(query, (user_id, course_id))

        if not result or result['total_lessons'] == 0:
            return 0.0

        progress = (result['completed_lessons'] / result['total_lessons']) * 100
        return round(progress, 2)

    @classmethod
    def get_enrollment_stats(cls, course_id: int) -> Dict[str, Any]:
        """
        Get enrollment statistics for a course

        Args:
            course_id: Course ID

        Returns:
            Statistics dict
        """
        query = """
            SELECT
                COUNT(*) AS total_enrollments,
                COUNT(CASE WHEN status = 'active' THEN 1 END) AS active_enrollments,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) AS completed_enrollments,
                COUNT(CASE WHEN status = 'cancelled' THEN 1 END) AS cancelled_enrollments,
                AVG(progress_percentage) AS avg_progress,
                SUM(price_paid) AS total_revenue
            FROM courses.course_enrollments
            WHERE course_id = %s
        """

        result = fetch_one(query, (course_id,))

        if not result:
            return {}

        return {
            'total_enrollments': result['total_enrollments'] or 0,
            'active_enrollments': result['active_enrollments'] or 0,
            'completed_enrollments': result['completed_enrollments'] or 0,
            'cancelled_enrollments': result['cancelled_enrollments'] or 0,
            'avg_progress': float(result['avg_progress']) if result['avg_progress'] else 0.0,
            'total_revenue': float(result['total_revenue']) if result['total_revenue'] else 0.0
        }

    @classmethod
    def count_by_user(cls, user_id: str, status: Optional[str] = None) -> int:
        """
        Count enrollments for a user

        Args:
            user_id: User UUID
            status: Optional status filter ('active', 'completed', 'cancelled')

        Returns:
            Count of enrollments
        """
        if status:
            query = """
                SELECT COUNT(*) as count
                FROM courses.course_enrollments
                WHERE user_id = %s AND status = %s
            """
            result = fetch_one(query, (user_id, status))
        else:
            query = """
                SELECT COUNT(*) as count
                FROM courses.course_enrollments
                WHERE user_id = %s
            """
            result = fetch_one(query, (user_id,))

        return result['count'] if result else 0
