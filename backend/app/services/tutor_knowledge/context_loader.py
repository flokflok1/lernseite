"""
Context Loader - Kurs-, Kapitel-, und Lektions-Kontext für den Tutor
"""

from typing import Dict, Any, Optional, List
import logging

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all

logger = logging.getLogger(__name__)


def get_course_context(course_id: str) -> Optional[Dict[str, Any]]:
    """
    Lädt den vollständigen Kurs-Kontext für den Tutor.

    Args:
        course_id: UUID des Kurses

    Returns:
        Dict mit Kurs-Informationen für den Tutor:
        {
            'course': {...},
            'chapters': [...],
            'total_lessons': int,
            'learning_objectives': [...]
        }
    """
    try:
        # Kurs-Grunddaten
        course = fetch_one("""
            SELECT
                course_id,
                title,
                subtitle,
                description,
                learning_objectives,
                target_audience,
                prerequisites,
                difficulty_level,
                language,
                duration_hours,
                category_id
            FROM courses
            WHERE course_id = %s
        """, (course_id,))

        if not course:
            return None

        # Kapitel mit Lektionen
        chapters = fetch_all("""
            SELECT
                ch.chapter_id,
                ch.title,
                ch.description,
                ch.order_index,
                (SELECT COUNT(*) FROM lessons l WHERE l.chapter_id = ch.chapter_id) as lesson_count,
                (SELECT COUNT(*) FROM learning_methods lm WHERE lm.chapter_id = ch.chapter_id) as method_count
            FROM chapters ch
            WHERE ch.course_id = %s
            ORDER BY ch.order_index
        """, (course_id,))

        # Kategorie-Name (falls vorhanden)
        category_name = None
        if course.get('category_id'):
            cat = fetch_one("""
                SELECT name FROM course_categories WHERE category_id = %s
            """, (course['category_id'],))
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
    Lädt den Kapitel-Kontext mit allen Lektionen und Lernmethoden.

    Args:
        chapter_id: UUID des Kapitels

    Returns:
        Dict mit Kapitel-Details für den Tutor
    """
    try:
        # Kapitel-Grunddaten
        chapter = fetch_one("""
            SELECT
                ch.chapter_id,
                ch.course_id,
                ch.title,
                ch.description,
                ch.order_index,
                c.title as course_title
            FROM chapters ch
            LEFT JOIN courses c ON ch.course_id = c.course_id
            WHERE ch.chapter_id = %s
        """, (chapter_id,))

        if not chapter:
            return None

        # Lektionen des Kapitels
        lessons = fetch_all("""
            SELECT
                lesson_id,
                title,
                lesson_type,
                content,
                order_index,
                duration_minutes
            FROM lessons
            WHERE chapter_id = %s
            ORDER BY order_index
        """, (chapter_id,))

        # Lernmethoden des Kapitels
        methods = fetch_all("""
            SELECT
                method_id,
                method_type,
                title,
                instructions,
                data,
                difficulty,
                order_index
            FROM learning_methods
            WHERE chapter_id = %s AND published = TRUE
            ORDER BY order_index
        """, (chapter_id,))

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
    Lädt den vollständigen Inhalt einer Lektion für den Tutor.

    Args:
        lesson_id: ID der Lektion

    Returns:
        Dict mit Lektions-Inhalt
    """
    try:
        lesson = fetch_one("""
            SELECT
                l.*,
                ch.title as chapter_title,
                ch.course_id,
                c.title as course_title
            FROM lessons l
            LEFT JOIN chapters ch ON l.chapter_id = ch.chapter_id
            LEFT JOIN courses c ON ch.course_id = c.course_id
            WHERE l.lesson_id = %s
        """, (lesson_id,))

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
