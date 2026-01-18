"""
Content Saving for Authoring Service

Handles:
- Saving chapters
- Saving lessons
- Saving tasks
- Saving learning methods
"""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ContentSaver:
    """Save generated content to database."""

    @staticmethod
    def save(
        content_type: str,
        content_id: str,
        content_data: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Save generated content to database.

        Args:
            content_type: Type of content
            content_id: Existing content ID (not used, kept for compatibility)
            content_data: Content to save
            user_id: User ID

        Returns:
            Dict with saved content info
        """
        if content_type == 'chapter':
            return ContentSaver._save_chapter(content_data, user_id)
        elif content_type == 'chapter_theory':
            return ContentSaver._save_chapter_theory(content_data, user_id)
        elif content_type == 'lesson':
            return ContentSaver._save_lesson(content_data, user_id)
        elif content_type == 'lesson_explanation':
            return ContentSaver._save_lesson_explanation(content_data, user_id)
        elif content_type == 'task':
            return ContentSaver._save_task(content_data, user_id)
        elif content_type == 'learning_method':
            return ContentSaver._save_learning_method(content_data, user_id)
        else:
            raise ValueError(f"Unknown content type: {content_type}")

    @staticmethod
    def _save_chapter(data: Dict, user_id: str) -> Dict[str, Any]:
        """Save new chapter."""
        from app.infrastructure.persistence.repositories.courses.chapters import ChapterRepository

        chapter_data = {
            'course_id': data.get('course_id'),
            'title': data.get('title'),
            'description': data.get('description'),
            'duration_minutes': data.get('duration_minutes', 0)
        }

        chapter = ChapterRepository.create(chapter_data)
        logger.info(f"Created chapter: {chapter.get('chapter_id')}")

        return {
            'success': True,
            'content_type': 'chapter',
            'chapter_id': str(chapter.get('chapter_id')),
            'title': chapter.get('title')
        }

    @staticmethod
    def _save_chapter_theory(data: Dict, user_id: str) -> Dict[str, Any]:
        """Save chapter theory."""
        from app.infrastructure.persistence.database.connection import fetch_one

        query = """
            INSERT INTO chapter_theory (
                chapter_id, style, title, theory_data,
                tokens_used, model_used, generated_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING theory_id, chapter_id, title, created_at
        """

        result = fetch_one(query, (
            data.get('chapter_id'),
            data.get('style', 'standard'),
            data.get('title', 'Generierte Theorie'),
            json.dumps(data.get('theory_data', {})),
            data.get('tokens_used', 0),
            data.get('model_used', 'unknown'),
            user_id
        ))

        logger.info(f"Created chapter theory: {result.get('theory_id')}")

        return {
            'success': True,
            'content_type': 'chapter_theory',
            'theory_id': str(result.get('theory_id')),
            'chapter_id': str(result.get('chapter_id'))
        }

    @staticmethod
    def _save_lesson(data: Dict, user_id: str) -> Dict[str, Any]:
        """Save new lesson."""
        from app.infrastructure.persistence.repositories.courses.lessons import LessonRepository

        lesson_data = {
            'chapter_id': data.get('chapter_id'),
            'title': data.get('title'),
            'lesson_type': data.get('lesson_type', 'text'),
            'content': json.dumps(data.get('content', {})),
            'duration_minutes': data.get('duration_minutes', 10)
        }

        lesson = LessonRepository.create(lesson_data)
        logger.info(f"Created lesson: {lesson.get('lesson_id')}")

        return {
            'success': True,
            'content_type': 'lesson',
            'lesson_id': str(lesson.get('lesson_id')),
            'title': lesson.get('title')
        }

    @staticmethod
    def _save_lesson_explanation(data: Dict, user_id: str) -> Dict[str, Any]:
        """Save lesson explanation."""
        from app.infrastructure.persistence.database.connection import fetch_one

        query = """
            INSERT INTO lesson_explanations (
                lesson_id, style, title, explanation_data,
                tokens_used, model_used, generated_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING explanation_id, lesson_id, title, created_at
        """

        result = fetch_one(query, (
            data.get('lesson_id'),
            data.get('style', 'standard'),
            data.get('title', 'Generierte Erklärung'),
            json.dumps(data.get('explanation_data', {})),
            data.get('tokens_used', 0),
            data.get('model_used', 'unknown'),
            user_id
        ))

        logger.info(f"Created lesson explanation: {result.get('explanation_id')}")

        return {
            'success': True,
            'content_type': 'lesson_explanation',
            'explanation_id': str(result.get('explanation_id')),
            'lesson_id': str(result.get('lesson_id'))
        }

    @staticmethod
    def _save_task(data: Dict, user_id: str) -> Dict[str, Any]:
        """Save new task/exercise."""
        # Tasks are typically stored as learning method instances
        return ContentSaver._save_learning_method({
            **data,
            'method_type': data.get('method_type', 8)  # LM08 = Whiteboard Tasks
        }, user_id)

    @staticmethod
    def _save_learning_method(data: Dict, user_id: str) -> Dict[str, Any]:
        """Save learning method instance."""
        from app.infrastructure.persistence.repositories.learning_method.instances import (
            LearningMethodInstanceRepository
        )

        method_data = {
            'chapter_id': data.get('chapter_id'),
            'lesson_id': data.get('lesson_id'),
            'method_type': data.get('method_type', 0),
            'title': data.get('title'),
            'instructions': data.get('instructions'),
            'data': data.get('data', {}),
            'solution': data.get('solution'),
            'difficulty': data.get('difficulty', 'medium'),
            'tier': data.get('tier', 'basic')
        }

        method = LearningMethodInstanceRepository.create(method_data)
        logger.info(f"Created learning method: {method.get('method_id')}")

        return {
            'success': True,
            'content_type': 'learning_method',
            'method_id': str(method.get('method_id')),
            'method_type': method.get('method_type')
        }
