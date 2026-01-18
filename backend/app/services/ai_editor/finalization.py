"""
AI Editor Finalization Module

Handles session finalization and creation of course content.
Creates chapters, lessons, and learning method instances from generated content.
"""

import json
import logging
from typing import Dict, Any, Optional

from app.infrastructure.persistence.repositories.ai.editor import (
    AIEditorRepository,
    AIEditorAnalyticsRepository
)
from app.infrastructure.persistence.repositories.courses.chapters import ChapterRepository
from app.infrastructure.persistence.repositories.courses.lessons import LessonRepository
from app.infrastructure.persistence.repositories.learning_method.instances import LearningMethodInstanceRepository
from app.services.ai_editor.utils import AiEditorServiceError

logger = logging.getLogger(__name__)


class AiEditorFinalizer:
    """
    Session finalizer for AI Editor.

    Converts generated content into actual database records.
    """

    @staticmethod
    def finalize_session(
        session_id: str,
        create_chapter: bool = True,
        create_lessons: bool = True,
        create_methods: bool = True,
        chapter_title: Optional[str] = None,
        publish_immediately: bool = False,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Finalize session and create actual chapter, lessons, and learning methods.

        This method takes the generated content from an AI Editor session and
        creates the actual database records in courses/chapters/lessons.

        Args:
            session_id: Session UUID
            create_chapter: Create chapter from generated content
            create_lessons: Create lessons
            create_methods: Create learning methods
            chapter_title: Override chapter title (uses generated if None)
            publish_immediately: Publish chapter immediately
            user_id: User ID for analytics

        Returns:
            Result dict with created IDs

        Raises:
            AiEditorServiceError: On finalization errors
        """
        # Get session with all generated content
        session = AIEditorRepository.find_by_id(session_id)
        if not session:
            raise AiEditorServiceError(f"Session not found: {session_id}")

        course_id = session.get('course_id')
        if not course_id:
            raise AiEditorServiceError("Session has no course_id")

        # Parse JSON fields if needed
        generated_theory = session.get('generated_theory')
        generated_lessons = session.get('generated_lessons', [])
        generated_methods = session.get('generated_methods', [])

        if isinstance(generated_theory, str):
            generated_theory = json.loads(generated_theory) if generated_theory else {}
        if isinstance(generated_lessons, str):
            generated_lessons = json.loads(generated_lessons) if generated_lessons else []
        if isinstance(generated_methods, str):
            generated_methods = json.loads(generated_methods) if generated_methods else []

        result = {
            'chapter_id': None,
            'lesson_ids': [],
            'method_ids': [],
            'stats': {
                'chapters_created': 0,
                'lessons_created': 0,
                'methods_created': 0
            }
        }

        created_chapter = None

        # 1. Create Chapter
        if create_chapter:
            created_chapter = AiEditorFinalizer._create_chapter(
                session, course_id, chapter_title, generated_theory, generated_methods, result
            )

        # 2. Create Lessons
        if create_lessons and created_chapter:
            AiEditorFinalizer._create_lessons(
                session_id, created_chapter, generated_lessons, publish_immediately, result
            )

        # 3. Create Learning Methods
        if create_methods and created_chapter:
            AiEditorFinalizer._create_methods(
                session_id, created_chapter, generated_methods, publish_immediately, result
            )

        # 4. Update session status
        AIEditorRepository.update_status(session_id, 'completed')

        # 5. Log analytics
        if user_id:
            AIEditorAnalyticsRepository.log_event({
                'session_id': session_id,
                'user_id': user_id,
                'event_type': 'session_finalized',
                'event_data': {
                    'chapter_id': result['chapter_id'],
                    'lessons_created': result['stats']['lessons_created'],
                    'methods_created': result['stats']['methods_created'],
                    'publish_immediately': publish_immediately
                },
                'step_name': 'finalize'
            })

        logger.info(
            f"Session {session_id} finalized: "
            f"{result['stats']['chapters_created']} chapters, "
            f"{result['stats']['lessons_created']} lessons, "
            f"{result['stats']['methods_created']} methods"
        )

        return result

    @staticmethod
    def _create_chapter(
        session: Dict[str, Any],
        course_id: str,
        chapter_title: Optional[str],
        generated_theory: Dict[str, Any],
        generated_methods: list,
        result: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create chapter from generated content.

        Args:
            session: AI Editor session
            course_id: Course ID
            chapter_title: Optional override title
            generated_theory: Generated theory content
            generated_methods: Generated methods
            result: Result dict to update

        Returns:
            Created chapter dict or None on error
        """
        # Get chapter title from request, generated theory, or session name
        final_chapter_title = (
            chapter_title or
            generated_theory.get('title') or
            generated_theory.get('chapter_title') or
            session.get('session_name') or
            'KI-generiertes Kapitel'
        )

        chapter_description = (
            generated_theory.get('description') or
            generated_theory.get('summary') or
            None
        )

        chapter_data = {
            'course_id': course_id,
            'title': final_chapter_title,
            'description': chapter_description,
            'duration_minutes': generated_theory.get('estimated_duration', 0),
            'has_quiz': any(m.get('method_type') in [13, 22] for m in generated_methods),
            'has_exam': any(m.get('method_type') in [25] for m in generated_methods)
        }

        try:
            created_chapter = ChapterRepository.create(chapter_data)
            result['chapter_id'] = str(created_chapter['chapter_id'])
            result['stats']['chapters_created'] = 1

            # Update session with chapter_id
            session_id = session.get('session_id')
            AIEditorRepository.update_session(session_id, {'chapter_id': created_chapter['chapter_id']})

            logger.info(f"Created chapter: {created_chapter['chapter_id']} - {final_chapter_title}")
            return created_chapter
        except Exception as e:
            logger.error(f"Failed to create chapter: {str(e)}")
            raise AiEditorServiceError(f"Failed to create chapter: {str(e)}")

    @staticmethod
    def _create_lessons(
        session_id: str,
        created_chapter: Dict[str, Any],
        generated_lessons: list,
        publish_immediately: bool,
        result: Dict[str, Any]
    ) -> None:
        """
        Create lessons from generated content.

        Args:
            session_id: Session ID
            created_chapter: Created chapter dict
            generated_lessons: Generated lesson data
            publish_immediately: Publish immediately flag
            result: Result dict to update
        """
        for idx, lesson_data in enumerate(generated_lessons):
            lesson_title = lesson_data.get('title', f'Lektion {idx + 1}')
            lesson_type = lesson_data.get('lesson_type', 'text')

            # Build content from generated data
            lesson_content = {
                'description': lesson_data.get('description'),
                'objectives': lesson_data.get('learning_objectives', []),
                'content_text': lesson_data.get('content_text'),
                'ai_generated': True,
                'source_session_id': session_id
            }

            new_lesson_data = {
                'chapter_id': created_chapter['chapter_id'],
                'title': lesson_title,
                'lesson_type': lesson_type,
                'content': json.dumps(lesson_content),
                'order_index': lesson_data.get('order_index', idx + 1),
                'duration_minutes': lesson_data.get('duration_minutes', 10),
                'published': publish_immediately,
                'free_preview': lesson_data.get('is_preview', False)
            }

            try:
                created_lesson = LessonRepository.create(new_lesson_data)
                result['lesson_ids'].append(str(created_lesson['lesson_id']))
                result['stats']['lessons_created'] += 1
                logger.info(f"Created lesson: {created_lesson['lesson_id']} - {lesson_title}")
            except Exception as e:
                logger.error(f"Failed to create lesson {lesson_title}: {str(e)}")
                # Continue with other lessons

    @staticmethod
    def _create_methods(
        session_id: str,
        created_chapter: Dict[str, Any],
        generated_methods: list,
        publish_immediately: bool,
        result: Dict[str, Any]
    ) -> None:
        """
        Create learning methods from generated content.

        Args:
            session_id: Session ID
            created_chapter: Created chapter dict
            generated_methods: Generated method data
            publish_immediately: Publish immediately flag
            result: Result dict to update
        """
        for idx, method_data in enumerate(generated_methods):
            method_type = method_data.get('method_type', 0)
            method_title = method_data.get('title', f'Lernmethode {idx + 1}')

            # Build data JSONB for the learning method
            method_content = {
                'instructions': method_data.get('instructions'),
                'content': method_data.get('content', {}),
                'ai_generated': True,
                'source_session_id': session_id
            }

            # Merge with any additional data from generation
            if method_data.get('data'):
                method_content.update(method_data['data'])

            new_method_data = {
                'chapter_id': created_chapter['chapter_id'],
                'method_type': method_type,
                'title': method_title,
                'instructions': method_data.get('instructions'),
                'data': method_content,
                'solution': method_data.get('solution'),
                'tier': method_data.get('tier', 'basic'),
                'duration_minutes': method_data.get('duration_minutes'),
                'difficulty': method_data.get('difficulty', 'medium'),
                'order_index': method_data.get('order_index', idx + 1),
                'published': publish_immediately
            }

            try:
                created_method = LearningMethodInstanceRepository.create(new_method_data)
                result['method_ids'].append(str(created_method['method_id']))
                result['stats']['methods_created'] += 1
                logger.info(
                    f"Created method: {created_method['method_id']} - "
                    f"{method_title} (LM{method_type:02d})"
                )
            except Exception as e:
                logger.error(f"Failed to create method {method_title}: {str(e)}")
                # Continue with other methods
