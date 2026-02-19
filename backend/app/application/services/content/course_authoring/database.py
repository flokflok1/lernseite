"""
Database operations for course authoring service.
"""

import json
import logging
from typing import Dict, Optional, List, Any

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query
from app.infrastructure.persistence.repositories.courses.chapters import ChapterRepository
from app.infrastructure.persistence.repositories.courses.lessons import LessonRepository
from app.application.services.content.course_authoring.exceptions import CourseAuthoringError

logger = logging.getLogger(__name__)


class DatabaseOperations:
    """Handles database operations for course authoring."""

    @staticmethod
    def get_course(course_id: str) -> Optional[Dict]:
        """
        Lädt Kurs aus DB.

        Args:
            course_id: Course UUID

        Returns:
            Course data or None
        """
        query = "SELECT * FROM courses WHERE course_id = %s"
        return fetch_one(query, (course_id,))

    @staticmethod
    def check_user_access(user_id: str, course_id: str) -> bool:
        """
        Prüft ob User Zugriff auf Kurs hat (GBA).

        Nutzt GBA-Permissions: Gruppen mit 'content.*:write' oder 'admin.*' Berechtigungen
        haben Zugriff auf Kurs-Authoring.

        Args:
            user_id: User UUID
            course_id: Course UUID

        Returns:
            True if user has access, False otherwise
        """
        # Check via GBA: Benutzer mit write-Permissionen für Inhalte
        query = """
            SELECT 1
            FROM core.users_groups ug
            JOIN core.groups g ON ug.group_id = g.id
            JOIN core.group_permissions gp ON g.id = gp.group_id
            JOIN core.permissions p ON gp.permission_id = p.id
            WHERE ug.user_id = %s
                AND ug.is_active = TRUE
                AND ug.left_at IS NULL
                AND (
                    p.permission_code LIKE 'content.%:write'
                    OR p.permission_code LIKE 'admin.%:write'
                )
            LIMIT 1
        """
        result = fetch_one(query, (user_id,))
        if result:
            return True

        # Oder Kurs-Owner
        query = "SELECT created_by FROM courses WHERE course_id = %s"
        course = fetch_one(query, (course_id,))
        return course and str(course['created_by']) == user_id

    @staticmethod
    def get_course_info(course_id: str) -> Dict:
        """
        Lädt Kurs-Info für Prompt.

        Args:
            course_id: Course UUID

        Returns:
            Course information dict
        """
        query = """
            SELECT c.*, cat.name as category_name
            FROM courses c
            LEFT JOIN course_categories cat ON cat.category_id = c.category_id
            WHERE c.course_id = %s
        """
        result = fetch_one(query, (course_id,))
        if result:
            return {
                'title': result.get('title', ''),
                'description': result.get('description', ''),
                'category': result.get('category_name', ''),
                'target_audience': result.get('target_audience', ''),
                'difficulty': result.get('difficulty_level', 'intermediate')
            }
        return {}

    @staticmethod
    def load_existing_structure(course_id: str, course: Dict) -> Dict:
        """
        Lädt bestehende Kursstruktur in draft_structure Format.

        Args:
            course_id: Course UUID
            course: Course data

        Returns:
            Draft structure dict
        """
        structure = {
            'course_id': course_id,
            'course_title': course.get('title', ''),
            'course_description': course.get('description', ''),
            'chapters': [],
            'meta': {
                'version': 1,
                'source': 'existing',
                'last_operation': None
            }
        }

        # Kapitel laden
        chapters_query = """
            SELECT * FROM chapters
            WHERE course_id = %s
            ORDER BY sort_order, created_at
        """
        chapters = fetch_all(chapters_query, (course_id,))

        for chapter in chapters:
            chapter_id = str(chapter['chapter_id'])
            chapter_draft = {
                'id': chapter_id,
                'existing_id': chapter_id,
                'title': chapter.get('title', ''),
                'description': chapter.get('description', ''),
                'lessons': []
            }

            # Lektionen laden
            lessons_query = """
                SELECT * FROM lessons
                WHERE chapter_id = %s
                ORDER BY sort_order, created_at
            """
            lessons = fetch_all(lessons_query, (chapter_id,))

            for lesson in lessons:
                lesson_id = str(lesson['lesson_id'])
                lesson_draft = {
                    'id': lesson_id,
                    'existing_id': lesson_id,
                    'title': lesson.get('title', ''),
                    'type': lesson.get('lesson_type', 'text'),
                    'lm_type': lesson.get('lm_type', 'LM00'),
                    'methods': []
                }
                chapter_draft['lessons'].append(lesson_draft)

            structure['chapters'].append(chapter_draft)

        return structure

    @staticmethod
    def update_session(
        session_id: str,
        draft_structure: Dict,
        chat_history: List,
        file_context: List,
        tokens_delta: int = 0,
        operations_delta: int = 0
    ) -> None:
        """
        Aktualisiert Session in DB.

        Args:
            session_id: Session UUID
            draft_structure: Updated draft structure
            chat_history: Updated chat history
            file_context: File context list
            tokens_delta: Token count delta
            operations_delta: Operations count delta
        """
        query = """
            UPDATE course_authoring_sessions
            SET draft_structure = %s,
                chat_history = %s,
                file_context = %s,
                total_tokens_used = total_tokens_used + %s,
                total_operations = total_operations + %s
            WHERE session_id = %s
        """
        execute_query(query, (
            json.dumps(draft_structure),
            json.dumps(chat_history),
            json.dumps(file_context),
            tokens_delta,
            operations_delta,
            session_id
        ))

    @staticmethod
    def create_or_update_chapter(
        course_id: str,
        chapter_draft: Dict,
        user_id: str
    ) -> str:
        """
        Erstellt oder aktualisiert Kapitel.

        Args:
            course_id: Course UUID
            chapter_draft: Chapter draft data
            user_id: User UUID

        Returns:
            Chapter ID
        """
        existing_id = chapter_draft.get('existing_id')

        if existing_id:
            # Update
            ChapterRepository.update(existing_id, {
                'title': chapter_draft.get('title'),
                'description': chapter_draft.get('description')
            })
            return existing_id
        else:
            # Create
            result = ChapterRepository.create({
                'course_id': course_id,
                'title': chapter_draft.get('title', 'Neues Kapitel'),
                'description': chapter_draft.get('description', '')
            })
            return str(result['chapter_id'])

    @staticmethod
    def create_or_update_lesson(
        chapter_id: str,
        lesson_draft: Dict,
        user_id: str
    ) -> str:
        """
        Erstellt oder aktualisiert Lektion.

        Args:
            chapter_id: Chapter UUID
            lesson_draft: Lesson draft data
            user_id: User UUID

        Returns:
            Lesson ID
        """
        existing_id = lesson_draft.get('existing_id')

        if existing_id:
            # Update
            LessonRepository.update(existing_id, {
                'title': lesson_draft.get('title'),
                'lesson_type': lesson_draft.get('type', 'text')
            })
            return existing_id
        else:
            # Create
            result = LessonRepository.create({
                'chapter_id': chapter_id,
                'title': lesson_draft.get('title', 'Neue Lektion'),
                'lesson_type': lesson_draft.get('type', 'text'),
                'lm_type': lesson_draft.get('lm_type', 'LM00')
            })
            return str(result['lesson_id'])

    @staticmethod
    def create_method(
        lesson_id: str,
        chapter_id: str,
        method_draft: Dict,
        user_id: str
    ) -> Optional[str]:
        """
        Erstellt Lernmethode.

        Args:
            lesson_id: Lesson UUID
            chapter_id: Chapter UUID
            method_draft: Method draft data
            user_id: User UUID

        Returns:
            Method ID or None
        """
        method_type = method_draft.get('type', 'theory')
        content = method_draft.get('content', {})

        # Map string type to numeric LM type
        type_mapping = {
            'theory': 0,           # LM00
            'step_by_step': 1,     # LM01
            'calculator_tutorial': 1,  # LM01 (Step-by-Step variant)
            'tool_tutorial': 9,    # LM09 (Code/Config)
            'quiz': 22,            # LM22
            'flashcards': 13,      # LM13
            'exercise': 8,         # LM08
            'exam': 19,            # LM19 (IHK-Stil)
            'interactive': 2       # LM02
        }

        lm_type = type_mapping.get(method_type, 0)

        query = """
            INSERT INTO learning_method_instances (
                lesson_id, chapter_id, method_type, title,
                instructions, data, difficulty, tier
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING method_id
        """

        result = fetch_one(query, (
            lesson_id,
            chapter_id,
            lm_type,
            method_draft.get('title', 'Lernmethode'),
            content.get('instructions', ''),
            json.dumps(content),
            content.get('difficulty', 'medium'),
            content.get('tier', 'basic')
        ))

        return str(result['method_id']) if result else None
