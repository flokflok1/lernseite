"""
File Loader - Kurs-Dateien (Skripte, Materialien) für den Tutor
"""

from typing import Dict, Any, Optional, List
import logging

from app.infrastructure.persistence.database.connection import fetch_all

logger = logging.getLogger(__name__)


def get_course_files(
    course_id: str,
    category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Lädt Kurs-Dateien (PDFs, Skripte, Materialien).

    Args:
        course_id: UUID des Kurses
        category: Optional: 'script', 'material', 'exercise', etc.

    Returns:
        Liste der Dateien mit Metadaten
    """
    try:
        query = """
            SELECT
                cf.course_file_id,
                cf.file_name,
                cf.display_name,
                cf.description,
                cf.file_category,
                cf.file_type,
                cf.ai_summary,
                cf.ai_keywords,
                cf.ai_processed,
                mf.public_url,
                mf.cdn_url
            FROM course_files cf
            LEFT JOIN media_files mf ON cf.file_id = mf.file_id
            WHERE cf.course_id = %s
        """
        params: List[Any] = [course_id]

        if category:
            query += " AND cf.file_category = %s"
            params.append(category)

        query += " ORDER BY cf.order_index"

        files = fetch_all(query, tuple(params))

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
