"""
Course Analytics Repository - SQL for admin course analytics endpoints.

Provides static methods for course-specific analytics:
- Content statistics (chapters, lessons, methods)
- AI usage statistics
- Enrollment statistics
- Learning method distribution
- Recent authoring sessions
"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all


class CourseAnalyticsRepository:
    """SQL queries for course analytics endpoints."""

    @staticmethod
    def get_content_stats(course_id: str) -> Dict:
        """Get content statistics for a course."""
        query = """
            WITH chapter_stats AS (
                SELECT
                    COUNT(*) as chapter_count,
                    SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) as published_chapters
                FROM chapters
                WHERE course_id = %s
            ),
            lesson_stats AS (
                SELECT
                    COUNT(*) as lesson_count,
                    SUM(CASE WHEN l.status = 'published' THEN 1 ELSE 0 END) as published_lessons
                FROM lessons l
                JOIN chapters ch ON ch.chapter_id = l.chapter_id
                WHERE ch.course_id = %s
            ),
            method_stats AS (
                SELECT
                    COUNT(*) as method_count,
                    COUNT(DISTINCT lmi.method_type) as unique_methods
                FROM learning_method_instances lmi
                JOIN lessons l ON l.lesson_id = lmi.lesson_id
                JOIN chapters ch ON ch.chapter_id = l.chapter_id
                WHERE ch.course_id = %s
            )
            SELECT
                cs.chapter_count,
                cs.published_chapters,
                ls.lesson_count,
                ls.published_lessons,
                ms.method_count,
                ms.unique_methods
            FROM chapter_stats cs, lesson_stats ls, method_stats ms
        """
        return fetch_one(query, (course_id, course_id, course_id)) or {
            'chapter_count': 0,
            'published_chapters': 0,
            'lesson_count': 0,
            'published_lessons': 0,
            'method_count': 0,
            'unique_methods': 0
        }

    @staticmethod
    def get_ai_usage_stats(course_id: str, since: datetime) -> Dict:
        """Get AI usage aggregate statistics for a course since a given date."""
        query = """
            SELECT
                COUNT(*) as total_requests,
                COALESCE(SUM(tokens_used), 0) as total_tokens,
                COALESCE(SUM(cost_usd), 0) as total_cost_usd,
                COUNT(DISTINCT request_type) as request_types,
                COUNT(DISTINCT user_id) as unique_users
            FROM ki_requests
            WHERE course_id = %s AND created_at >= %s
        """
        return fetch_one(query, (course_id, since)) or {}

    @staticmethod
    def get_ai_usage_by_type(course_id: str, since: datetime) -> List[Dict]:
        """Get AI usage breakdown by request type."""
        query = """
            SELECT
                request_type,
                COUNT(*) as count,
                COALESCE(SUM(tokens_used), 0) as tokens
            FROM ki_requests
            WHERE course_id = %s AND created_at >= %s
            GROUP BY request_type
            ORDER BY count DESC
        """
        return fetch_all(query, (course_id, since)) or []

    @staticmethod
    def get_enrollment_stats(course_id: str) -> Dict:
        """Get enrollment statistics for a course."""
        query = """
            SELECT
                COUNT(*) as total_enrollments,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_enrollments,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_enrollments,
                COALESCE(AVG(progress_percent), 0) as avg_progress
            FROM enrollments
            WHERE course_id = %s
        """
        return fetch_one(query, (course_id,)) or {
            'total_enrollments': 0,
            'active_enrollments': 0,
            'completed_enrollments': 0,
            'avg_progress': 0
        }

    @staticmethod
    def get_method_distribution(course_id: str) -> List[Dict]:
        """Get learning method distribution for a course."""
        query = """
            SELECT
                lmi.method_type,
                lmt.name as method_name,
                COUNT(*) as count
            FROM learning_method_instances lmi
            JOIN lessons l ON l.lesson_id = lmi.lesson_id
            JOIN chapters ch ON ch.chapter_id = l.chapter_id
            LEFT JOIN learning_method_types lmt ON lmt.method_number = lmi.method_type
            WHERE ch.course_id = %s
            GROUP BY lmi.method_type, lmt.name
            ORDER BY count DESC
        """
        return fetch_all(query, (course_id,)) or []

    @staticmethod
    def get_recent_sessions(course_id: str, limit: int = 10) -> List[Dict]:
        """Get recent authoring sessions for a course."""
        query = """
            SELECT
                session_id,
                status,
                model_profile,
                total_tokens_used,
                total_operations,
                created_at,
                updated_at
            FROM course_authoring_sessions
            WHERE course_id = %s
            ORDER BY updated_at DESC
            LIMIT %s
        """
        return fetch_all(query, (course_id, limit)) or []
