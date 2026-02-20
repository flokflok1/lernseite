"""
Context Loader - Kurs-, Kapitel-, und Lektions-Kontext fuer den Tutor
"""

from typing import Dict, Any, Optional
import logging

from app.infrastructure.persistence.repositories.tutor_knowledge import (
    TutorKnowledgeRepository
)
from app.infrastructure.persistence.repositories.courses.crud import CourseRepositoryCRUD

logger = logging.getLogger(__name__)


def get_course_context(course_id: str) -> Optional[Dict[str, Any]]:
    """
    Laedt den vollstaendigen Kurs-Kontext fuer den Tutor.

    Args:
        course_id: UUID des Kurses

    Returns:
        Dict mit Kurs-Informationen fuer den Tutor:
        {
            'course': {...},
            'chapters': [...],
            'total_lessons': int,
            'learning_objectives': [...]
        }
    """
    try:
        # Kurs-Grunddaten
        course = CourseRepositoryCRUD.get_by_id_simple(course_id)

        if not course:
            return None

        # Kapitel mit Lektionen
        chapters = TutorKnowledgeRepository.get_course_chapters(course_id)

        # Kategorie-Name (falls vorhanden)
        category_name = None
        if course.get('category_id'):
            cat = TutorKnowledgeRepository.get_category_name(
                course['category_id']
            )
            if cat:
                category_name = cat['name']

        return {
            'course': {
                'id': str(course['course_id']),
                'title': course['title'],
                'subtitle': course.get('subtitle'),
                'description': course.get('description'),
                'learning_objectives': course.get('learning_objectives', []),
                'target_audience': course.get('target_audience'),
                'prerequisites': course.get('prerequisites'),
                'difficulty': course.get('difficulty_level', 'beginner'),
                'language': course.get('language', 'de'),
                'duration_hours': course.get('duration_hours'),
                'category': category_name
            },
            'chapters': [
                {
                    'id': str(ch['chapter_id']),
                    'title': ch['title'],
                    'description': ch.get('description'),
                    'order': ch['order_index'],
                    'lesson_count': ch['lesson_count'],
                    'method_count': ch['method_count']
                }
                for ch in (chapters or [])
            ],
            'total_chapters': len(chapters or []),
            'total_lessons': sum(ch['lesson_count'] for ch in (chapters or []))
        }

    except Exception as e:
        logger.error(f"Error loading course context: {e}")
        return None


def get_chapter_context(chapter_id: str) -> Optional[Dict[str, Any]]:
    """
    Laedt den Kapitel-Kontext mit allen Lektionen und Lernmethoden.

    Args:
        chapter_id: UUID des Kapitels

    Returns:
        Dict mit Kapitel-Details fuer den Tutor
    """
    try:
        # Kapitel-Grunddaten
        chapter = TutorKnowledgeRepository.get_chapter(chapter_id)

        if not chapter:
            return None

        # Lektionen des Kapitels
        lessons = TutorKnowledgeRepository.get_chapter_lessons(chapter_id)

        # Lernmethoden des Kapitels
        methods = TutorKnowledgeRepository.get_chapter_methods(chapter_id)

        return {
            'chapter': {
                'id': str(chapter['chapter_id']),
                'title': chapter['title'],
                'description': chapter.get('description'),
                'order': chapter['order_index'],
                'course_id': str(chapter['course_id']),
                'course_title': chapter['course_title']
            },
            'lessons': [
                {
                    'id': str(l['lesson_id']),
                    'title': l['title'],
                    'type': l['lesson_type'],
                    'content_preview': (l.get('content') or '')[:500] if l.get('content') else None,
                    'order': l['order_index'],
                    'duration_minutes': l.get('duration_minutes')
                }
                for l in (lessons or [])
            ],
            'learning_methods': [
                {
                    'id': str(m['method_id']),
                    'type': m['method_type'],
                    'title': m['title'],
                    'instructions': m.get('instructions'),
                    'difficulty': m.get('difficulty'),
                    'order': m['order_index']
                }
                for m in (methods or [])
            ]
        }

    except Exception as e:
        logger.error(f"Error loading chapter context: {e}")
        return None


def get_lesson_content(lesson_id: int) -> Optional[Dict[str, Any]]:
    """
    Laedt den vollstaendigen Inhalt einer Lektion fuer den Tutor.

    Args:
        lesson_id: ID der Lektion

    Returns:
        Dict mit Lektions-Inhalt
    """
    try:
        lesson = TutorKnowledgeRepository.get_lesson(lesson_id)

        if not lesson:
            return None

        return {
            'lesson': {
                'id': lesson['lesson_id'],
                'title': lesson['title'],
                'type': lesson['lesson_type'],
                'content': lesson.get('content'),
                'duration_minutes': lesson.get('duration_minutes')
            },
            'chapter': {
                'id': str(lesson['chapter_id']),
                'title': lesson['chapter_title']
            },
            'course': {
                'id': str(lesson['course_id']),
                'title': lesson['course_title']
            }
        }

    except Exception as e:
        logger.error(f"Error loading lesson content: {e}")
        return None
