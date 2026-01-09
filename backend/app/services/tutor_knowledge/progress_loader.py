"""
Progress Loader - Lernfortschritt für den Tutor
"""

from typing import Dict, Any, Optional
import logging

from app.database.connection import fetch_one, fetch_all

logger = logging.getLogger(__name__)


def get_user_progress(
    user_id: str,
    course_id: str
) -> Optional[Dict[str, Any]]:
    """
    Lädt den Lernfortschritt eines Users in einem Kurs.

    Args:
        user_id: UUID des Users
        course_id: UUID des Kurses

    Returns:
        Dict mit Fortschrittsdaten
    """
    try:
        # Enrollment-Status
        enrollment = fetch_one("""
            SELECT
                enrollment_id,
                enrollment_type,
                progress_percentage,
                last_accessed_at,
                completed_at
            FROM enrollments
            WHERE user_id = %s AND course_id = %s
        """, (user_id, course_id))

        if not enrollment:
            return None

        # Abgeschlossene Lektionen
        completed_lessons = fetch_all("""
            SELECT
                lp.lesson_id,
                l.title,
                lp.completed_at
            FROM lesson_progress lp
            JOIN lessons l ON lp.lesson_id = l.lesson_id
            JOIN chapters ch ON l.chapter_id = ch.chapter_id
            WHERE lp.user_id = %s AND ch.course_id = %s AND lp.completed = TRUE
            ORDER BY lp.completed_at DESC
        """, (user_id, course_id))

        # Lernmethoden-Fortschritt
        method_progress = fetch_all("""
            SELECT
                lmp.method_id,
                lm.title,
                lm.method_type,
                lmp.attempts,
                lmp.best_score,
                lmp.completed
            FROM learning_method_progress lmp
            JOIN learning_methods lm ON lmp.method_id = lm.method_id
            JOIN chapters ch ON lm.chapter_id = ch.chapter_id
            WHERE lmp.user_id = %s AND ch.course_id = %s
            ORDER BY lmp.updated_at DESC
        """, (user_id, course_id))

        return {
            'enrollment': {
                'type': enrollment['enrollment_type'],
                'progress': enrollment.get('progress_percentage', 0),
                'last_accessed': enrollment.get('last_accessed_at'),
                'completed': enrollment.get('completed_at') is not None
            },
            'completed_lessons': [
                {
                    'id': l['lesson_id'],
                    'title': l['title'],
                    'completed_at': l['completed_at']
                }
                for l in (completed_lessons or [])
            ],
            'method_progress': [
                {
                    'id': str(m['method_id']),
                    'title': m['title'],
                    'type': m['method_type'],
                    'attempts': m.get('attempts', 0),
                    'best_score': m.get('best_score'),
                    'completed': m.get('completed', False)
                }
                for m in (method_progress or [])
            ]
        }

    except Exception as e:
        logger.error(f"Error loading user progress: {e}")
        return None
