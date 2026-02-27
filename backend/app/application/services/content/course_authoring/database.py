"""
Database operations for course authoring service.
"""

import json
import logging
from typing import Dict, Optional, List, Any
from datetime import datetime

from psycopg.rows import dict_row

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
        user_id: str,
        conn=None
    ) -> str:
        """
        Erstellt oder aktualisiert Kapitel.

        Args:
            course_id: Course UUID
            chapter_draft: Chapter draft data
            user_id: User UUID
            conn: Optional shared DB connection for atomic transactions

        Returns:
            Chapter ID
        """
        existing_id = chapter_draft.get('existing_id')

        if conn:
            # Use shared connection for atomic transaction
            with conn.cursor(row_factory=dict_row) as cur:
                if existing_id:
                    cur.execute("""
                        UPDATE courses.chapters
                        SET title = %s, description = %s, updated_at = %s
                        WHERE chapter_id = %s
                        RETURNING chapter_id
                    """, (
                        chapter_draft.get('title'),
                        chapter_draft.get('description'),
                        datetime.utcnow(),
                        existing_id
                    ))
                    if cur.fetchone() is None:
                        raise CourseAuthoringError(
                            f"Chapter {existing_id} not found during finalize"
                        )
                    return existing_id
                else:
                    cur.execute("""
                        SELECT COALESCE(MAX(order_index), 0) + 1 AS next_order
                        FROM courses.chapters WHERE course_id = %s
                    """, (course_id,))
                    order_row = cur.fetchone()
                    order_index = order_row['next_order'] if order_row else 1

                    cur.execute("""
                        INSERT INTO courses.chapters (
                            course_id, title, description, order_index,
                            duration_minutes, has_video, has_quiz, has_exam,
                            created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, 0, FALSE, FALSE, FALSE, NOW(), NOW())
                        RETURNING chapter_id
                    """, (
                        course_id,
                        chapter_draft.get('title', 'Neues Kapitel'),
                        chapter_draft.get('description', ''),
                        order_index
                    ))
                    result = cur.fetchone()
                    return str(result['chapter_id'])
        else:
            # Standalone mode (each call gets its own connection)
            if existing_id:
                ChapterRepository.update(existing_id, {
                    'title': chapter_draft.get('title'),
                    'description': chapter_draft.get('description')
                })
                return existing_id
            else:
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
        user_id: str,
        conn=None
    ) -> str:
        """
        Erstellt oder aktualisiert Lektion.

        Args:
            chapter_id: Chapter UUID
            lesson_draft: Lesson draft data
            user_id: User UUID
            conn: Optional shared DB connection for atomic transactions

        Returns:
            Lesson ID
        """
        existing_id = lesson_draft.get('existing_id')

        # Extract content from draft (AI-generated lesson content)
        content_data = lesson_draft.get('content')
        content_json = json.dumps(content_data) if content_data else None

        if conn:
            with conn.cursor(row_factory=dict_row) as cur:
                if existing_id:
                    # Update title, type, and content if provided
                    if content_json:
                        cur.execute("""
                            UPDATE courses.lessons
                            SET title = %s, lesson_type = %s, content = %s::jsonb, updated_at = %s
                            WHERE lesson_id = %s
                            RETURNING lesson_id
                        """, (
                            lesson_draft.get('title'),
                            lesson_draft.get('type', 'text'),
                            content_json,
                            datetime.utcnow(),
                            existing_id
                        ))
                    else:
                        cur.execute("""
                            UPDATE courses.lessons
                            SET title = %s, lesson_type = %s, updated_at = %s
                            WHERE lesson_id = %s
                            RETURNING lesson_id
                        """, (
                            lesson_draft.get('title'),
                            lesson_draft.get('type', 'text'),
                            datetime.utcnow(),
                            existing_id
                        ))
                    if cur.fetchone() is None:
                        raise CourseAuthoringError(
                            f"Lesson {existing_id} not found during finalize"
                        )
                    return existing_id
                else:
                    cur.execute("""
                        SELECT COALESCE(MAX(order_index), 0) + 1 AS next_order
                        FROM courses.lessons WHERE chapter_id = %s
                    """, (chapter_id,))
                    order_row = cur.fetchone()
                    order_index = order_row['next_order'] if order_row else 1

                    cur.execute("""
                        INSERT INTO courses.lessons (
                            chapter_id, title, lesson_type, content,
                            order_index, duration_minutes, published, free_preview,
                            created_at, updated_at
                        ) VALUES (%s, %s, %s, %s::jsonb, %s, 0, FALSE, FALSE, NOW(), NOW())
                        RETURNING lesson_id
                    """, (
                        chapter_id,
                        lesson_draft.get('title', 'Neue Lektion'),
                        lesson_draft.get('type', 'text'),
                        content_json,
                        order_index
                    ))
                    result = cur.fetchone()
                    return str(result['lesson_id'])
        else:
            if existing_id:
                update_data = {
                    'title': lesson_draft.get('title'),
                    'lesson_type': lesson_draft.get('type', 'text')
                }
                if content_json:
                    update_data['content'] = content_json
                LessonRepository.update(existing_id, update_data)
                return existing_id
            else:
                create_data = {
                    'chapter_id': chapter_id,
                    'title': lesson_draft.get('title', 'Neue Lektion'),
                    'lesson_type': lesson_draft.get('type', 'text'),
                    'lm_type': lesson_draft.get('lm_type', 'LM00')
                }
                if content_json:
                    create_data['content'] = content_json
                result = LessonRepository.create(create_data)
                return str(result['lesson_id'])

    @staticmethod
    def create_method(
        lesson_id: str,
        chapter_id: str,
        method_draft: Dict,
        user_id: str,
        conn=None
    ) -> Optional[str]:
        """
        Erstellt Lernmethode.

        Args:
            lesson_id: Lesson UUID
            chapter_id: Chapter UUID
            method_draft: Method draft data
            user_id: User UUID
            conn: Optional shared DB connection for atomic transactions

        Returns:
            Method ID or None
        """
        method_type = method_draft.get('type', 'theory')
        content = method_draft.get('content', {})

        # Map string type to numeric LM type (IDs 0-11, see architecture.md)
        type_mapping = {
            'theory': 0,               # deep_explanation
            'step_by_step': 1,         # step_by_step
            'calculator_tutorial': 1,  # step_by_step variant
            'interactive': 2,          # interactive_theory
            'quiz': 2,                 # interactive_theory (multiple choice)
            'flashcards': 6,           # flashcards
            'exercise': 8,             # cloze_test
            'tool_tutorial': 9,        # free_text_long_answer (code/config)
            'exam': 10,                # ihk_style_tasks
        }

        lm_type = type_mapping.get(method_type, 0)
        title = method_draft.get('title', 'Lernmethode')
        instructions = content.get('instructions', '')
        data_json = json.dumps(content)
        difficulty = content.get('difficulty', 'medium')
        tier = content.get('tier', 'basic')

        if conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    INSERT INTO learning_methods.learning_method_instances (
                        lesson_id, chapter_id, method_type, title,
                        instructions, data, difficulty, tier
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING method_id
                """, (
                    lesson_id, chapter_id, lm_type, title,
                    instructions, data_json, difficulty, tier
                ))
                result = cur.fetchone()
                return str(result['method_id']) if result else None
        else:
            result = CourseAuthoringSessionRepository.create_learning_method_instance(
                lesson_id=lesson_id,
                chapter_id=chapter_id,
                lm_type=lm_type,
                title=title,
                instructions=instructions,
                data_json=data_json,
                difficulty=difficulty,
                tier=tier
            )
            return str(result['method_id']) if result else None

    @staticmethod
    def sync_methods_for_lesson(
        lesson_id: str,
        draft_methods: List[Dict],
        conn=None
    ) -> List[str]:
        """
        Synchronisiert Methoden einer Lektion: löscht Methoden aus der DB
        die nicht mehr in der draft_structure stehen.

        Die KI kann delete_method Operationen durchführen, die nur aus dem
        Draft entfernen. Beim Finalize muss die echte DB abgeglichen werden.

        Args:
            lesson_id: Echte Lesson UUID (existing_id)
            draft_methods: Methoden-Liste aus der draft_structure
            conn: DB connection (Teil der Finalize-Transaktion)

        Returns:
            Liste der gelöschten method_ids
        """
        if not conn:
            return []

        # IDs der Methoden die im Draft stehen und eine existing_id haben
        # (= sie existierten schon in der DB und wurden NICHT gelöscht)
        keep_ids = set()
        for m in draft_methods:
            existing = m.get('existing_id')
            if existing:
                keep_ids.add(str(existing))

        # Alle aktuellen Methoden dieser Lektion aus der echten DB holen
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT method_id
                FROM learning_methods.learning_method_instances
                WHERE lesson_id = %s
            """, (lesson_id,))
            db_methods = cur.fetchall()

        # Differenz berechnen: DB-Methoden die NICHT im Draft sind → löschen
        db_ids = {str(row['method_id']) for row in db_methods}
        to_delete = db_ids - keep_ids

        if to_delete:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM learning_methods.learning_method_instances
                    WHERE method_id = ANY(%s)
                """, (list(to_delete),))
            logger.info(
                f"Deleted {len(to_delete)} orphaned methods for lesson {lesson_id}: "
                f"{to_delete}"
            )

        return list(to_delete)
