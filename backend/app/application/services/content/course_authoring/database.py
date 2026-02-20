"""
Database operations for course authoring service.
"""

import json
import logging
from typing import Dict, Optional, List, Any

from app.infrastructure.persistence.repositories.authoring.sessions import CourseAuthoringSessionRepository
from app.infrastructure.persistence.repositories.courses.crud import CourseRepositoryCRUD
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
        return CourseRepositoryCRUD.get_by_id_simple(course_id)

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
        if CourseAuthoringSessionRepository.check_user_has_write_permission(user_id):
            return True

        # Oder Kurs-Owner
        creator_id = CourseAuthoringSessionRepository.get_course_creator(course_id)
        return creator_id is not None and creator_id == user_id

    @staticmethod
    def get_course_info(course_id: str) -> Dict:
        """
        Lädt Kurs-Info für Prompt.

        Args:
            course_id: Course UUID

        Returns:
            Course information dict
        """
        result = CourseAuthoringSessionRepository.get_course_info(course_id)
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
        chapters = CourseAuthoringSessionRepository.get_chapters_for_course(course_id)

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
            lessons = CourseAuthoringSessionRepository.get_lessons_for_chapter(chapter_id)

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
        CourseAuthoringSessionRepository.update_session(
            session_id,
            draft_structure=draft_structure,
            chat_history=chat_history,
            file_context=file_context,
            tokens_delta=tokens_delta,
            operations_delta=operations_delta
        )

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

        result = CourseAuthoringSessionRepository.create_learning_method_instance(
            lesson_id=lesson_id,
            chapter_id=chapter_id,
            lm_type=lm_type,
            title=method_draft.get('title', 'Lernmethode'),
            instructions=content.get('instructions', ''),
            data_json=json.dumps(content),
            difficulty=content.get('difficulty', 'medium'),
            tier=content.get('tier', 'basic')
        )

        return str(result['method_id']) if result else None
