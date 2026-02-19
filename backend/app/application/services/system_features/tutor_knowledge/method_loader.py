"""
Method Loader - Lernmethoden-Daten fuer den Tutor
"""

from typing import Dict, Any, Optional
import logging

from app.infrastructure.persistence.repositories.tutor_knowledge import (
    TutorKnowledgeRepository
)

logger = logging.getLogger(__name__)


def get_learning_method_data(method_id: str) -> Optional[Dict[str, Any]]:
    """
    Laedt die vollstaendigen Daten einer Lernmethode.

    Args:
        method_id: UUID der Lernmethode

    Returns:
        Dict mit Lernmethoden-Daten inkl. JSONB-Content
    """
    try:
        method = TutorKnowledgeRepository.get_learning_method(method_id)

        if not method:
            return None

        return {
            'method': {
                'id': str(method['method_id']),
                'type': method['method_type'],
                'title': method['title'],
                'instructions': method.get('instructions'),
                'data': method.get('data', {}),
                'solution': method.get('solution'),
                'difficulty': method.get('difficulty'),
                'tier': method.get('tier')
            },
            'chapter': {
                'id': str(method['chapter_id']),
                'title': method['chapter_title']
            },
            'course': {
                'id': str(method['course_id']),
                'title': method['course_title']
            }
        }

    except Exception as e:
        logger.error(f"Error loading learning method data: {e}")
        return None
