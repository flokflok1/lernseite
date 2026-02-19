"""
File Loader - Kurs-Dateien (Skripte, Materialien) fuer den Tutor
"""

from typing import Dict, Any, Optional, List
import logging

from app.infrastructure.persistence.repositories.tutor_knowledge import (
    TutorKnowledgeRepository
)

logger = logging.getLogger(__name__)


def get_course_files(
    course_id: str,
    category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Laedt Kurs-Dateien (PDFs, Skripte, Materialien).

    Args:
        course_id: UUID des Kurses
        category: Optional: 'script', 'material', 'exercise', etc.

    Returns:
        Liste der Dateien mit Metadaten
    """
    try:
        files = TutorKnowledgeRepository.get_course_files(course_id, category)

        return [
            {
                'id': str(f['course_file_id']),
                'name': f.get('display_name') or f['file_name'],
                'description': f.get('description'),
                'category': f['file_category'],
                'type': f['file_type'],
                'url': f.get('cdn_url') or f.get('public_url'),
                'ai_summary': f.get('ai_summary'),
                'ai_keywords': f.get('ai_keywords'),
                'ai_processed': f.get('ai_processed', False)
            }
            for f in (files or [])
        ]

    except Exception as e:
        logger.error(f"Error loading course files: {e}")
        return []
