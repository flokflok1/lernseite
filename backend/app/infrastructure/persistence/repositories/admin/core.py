"""
LernsystemX Admin Repository

Admin statistics and dashboard data access layer.
Phase 2.1 - Admin Dashboard Implementation

ISO 9001:2015 compliant - Standardized admin data access
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.database.connection import fetch_one


class AdminRepository(BaseRepository):
    """
    Repository for admin statistics and dashboard data

    Provides optimized SQL queries for admin dashboard metrics.
    """

    # No specific table for admin (aggregates from multiple tables)
    table_name = None

    @classmethod
    def get_user_stats(cls) -> Dict[str, int]:
        """
        Get user statistics for admin dashboard

        Returns:
            Dict with:
            - total_users: Total number of users
            - active_users: Active users in last 7 days
            - banned_users: Number of banned users
            - new_users_30d: New users in last 30 days

        Example:
            >>> stats = AdminRepository.get_user_stats()
            >>> print(f"Total users: {stats['total_users']}")
        """
        query = """
            SELECT
                COUNT(*) as total_users,
                COUNT(*) FILTER (
                    WHERE last_login >= NOW() - INTERVAL '7 days'
                ) as active_users,
                COUNT(*) FILTER (
                    WHERE status = 'banned'
                ) as banned_users,
                COUNT(*) FILTER (
                    WHERE created_at >= NOW() - INTERVAL '30 days'
                ) as new_users_30d
            FROM users
        """

        result = fetch_one(query)
        return {
            'total_users': result['total_users'] or 0,
            'active_users': result['active_users'] or 0,
            'banned_users': result['banned_users'] or 0,
            'new_users_30d': result['new_users_30d'] or 0
        }

    @classmethod
    def get_course_stats(cls) -> Dict[str, int]:
        """
        Get course statistics for admin dashboard

        Returns:
            Dict with:
            - total_courses: Total number of courses
            - published: Published courses
            - pending_review: Courses pending review
            - rejected: Rejected courses

        Example:
            >>> stats = AdminRepository.get_course_stats()
            >>> print(f"Published courses: {stats['published']}")
        """
        query = """
            SELECT
                COUNT(*) as total_courses,
                COUNT(*) FILTER (WHERE status = 'published') as published,
                COUNT(*) FILTER (WHERE status = 'pending_review') as pending_review,
                COUNT(*) FILTER (WHERE status = 'rejected') as rejected
            FROM courses
        """

        result = fetch_one(query)
        return {
            'total_courses': result['total_courses'] or 0,
            'published': result['published'] or 0,
            'pending_review': result['pending_review'] or 0,
            'rejected': result['rejected'] or 0
        }

    @classmethod
    def get_system_stats(cls, app_start_time: datetime) -> Dict[str, Any]:
        """
        Get system statistics for admin dashboard

        Args:
            app_start_time: Application start time for uptime calculation

        Returns:
            Dict with:
            - uptime: System uptime in seconds
            - db_latency: Database latency in ms
            - request_count_24h: API requests in last 24 hours
            - error_rate: Error rate percentage (0-100)

        Example:
            >>> from datetime import datetime
            >>> start_time = datetime.utcnow()
            >>> stats = AdminRepository.get_system_stats(start_time)
            >>> print(f"Uptime: {stats['uptime']} seconds")
        """
        # Calculate uptime
        uptime = (datetime.utcnow() - app_start_time).total_seconds()

        # Measure database latency with a simple query
        start = datetime.utcnow()
        fetch_one("SELECT 1")
        db_latency = (datetime.utcnow() - start).total_seconds() * 1000  # Convert to ms

        # Get request count from audit logs (last 24 hours)
        request_query = """
            SELECT COUNT(*) as request_count
            FROM core.audit_logs
            WHERE created_at >= NOW() - INTERVAL '24 hours'
        """
        request_result = fetch_one(request_query)
        request_count_24h = request_result['request_count'] if request_result else 0

        # Calculate error rate from audit logs (last 24 hours)
        error_query = """
            SELECT
                COUNT(*) FILTER (WHERE severity IN ('error', 'critical')) as error_count,
                COUNT(*) as total_count
            FROM core.audit_logs
            WHERE created_at >= NOW() - INTERVAL '24 hours'
        """
        error_result = fetch_one(error_query)

        if error_result and error_result['total_count'] > 0:
            error_rate = (error_result['error_count'] / error_result['total_count']) * 100
        else:
            error_rate = 0.0

        return {
            'uptime': round(uptime, 2),
            'db_latency': round(db_latency, 2),
            'request_count_24h': request_count_24h,
            'error_rate': round(error_rate, 2)
        }
