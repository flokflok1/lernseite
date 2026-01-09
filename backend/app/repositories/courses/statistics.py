"""
Course Statistics and Analytics

Calculates course metrics:
- Enrollment counts
- Completion rates
- Average progress
- Active student count
- Chapter and lesson counts

Used by dashboards and reporting systems.
"""

from typing import Dict, Any

from app.database.connection import fetch_one
from app.repositories.base_repository import BaseRepository


class CourseRepositoryStatistics(BaseRepository):
    """
    Statistics and analytics operations for courses

    Aggregates course data to provide insights and metrics.
    """

    table_name = 'courses.courses'

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
            FROM courses.courses c
            LEFT JOIN courses.chapters ch ON c.course_id = ch.course_id
            LEFT JOIN courses.lessons l ON ch.chapter_id = l.chapter_id
            LEFT JOIN courses.course_enrollments e ON c.course_id = e.course_id
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
