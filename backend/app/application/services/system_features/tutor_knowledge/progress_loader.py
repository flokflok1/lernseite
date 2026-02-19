"""
Progress Loader - Lernfortschritt fuer den Tutor
"""

from typing import Dict, Any, Optional
import logging

from app.infrastructure.persistence.repositories.tutor_knowledge import (
    TutorKnowledgeRepository
)

logger = logging.getLogger(__name__)


def get_user_progress(
    user_id: str,
    course_id: str
) -> Optional[Dict[str, Any]]:
    """
    Laedt den Lernfortschritt eines Users in einem Kurs.

    Args:
        user_id: UUID des Users
        course_id: UUID des Kurses

    Returns:
        Dict mit Fortschrittsdaten
    """
    try:
        # Enrollment-Status
        enrollment = TutorKnowledgeRepository.get_enrollment(
            user_id, course_id
        )

        if not enrollment:
            return None

        # Abgeschlossene Lektionen
        completed_lessons = TutorKnowledgeRepository.get_completed_lessons(
            user_id, course_id
        )

        # Lernmethoden-Fortschritt
        method_progress = TutorKnowledgeRepository.get_method_progress(
            user_id, course_id
        )

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
