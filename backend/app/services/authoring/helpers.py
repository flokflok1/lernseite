"""
Helper utilities for authoring service

Handles:
- Context information retrieval
- Conversation history formatting
- JSON extraction from AI responses
- Text preprocessing
"""

import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ContextHelper:
    """Retrieve context information for prompts."""

    @staticmethod
    def get_context_info(
        course_id: str,
        context_type: str,
        context_id: Optional[str]
    ) -> Dict[str, Any]:
        """
        Get context information for prompts.

        Args:
            course_id: Course identifier
            context_type: Type of context (chapter, lesson, etc.)
            context_id: ID of the context entity

        Returns:
            Dict with course, chapter, and lesson info
        """
        from app.infrastructure.persistence.repositories.courses import CourseRepository
        from app.infrastructure.persistence.repositories.courses.chapters import ChapterRepository
        from app.infrastructure.persistence.repositories.courses.lessons import LessonRepository

        info = {'course': {}, 'chapter': {}, 'lesson': {}}

        try:
            # Get course info
            course = CourseRepository.find_by_id(course_id)
            if course:
                info['course'] = {
                    'course_id': str(course.get('course_id')),
                    'title': course.get('title', ''),
                    'description': course.get('description', ''),
                    'category': course.get('category', '')
                }

            # Get specific context
            if context_type == 'chapter' and context_id:
                chapter = ChapterRepository.find_by_id(context_id)
                if chapter:
                    info['chapter'] = {
                        'chapter_id': str(chapter.get('chapter_id')),
                        'title': chapter.get('title', ''),
                        'description': chapter.get('description', '')
                    }

            elif context_type == 'lesson' and context_id:
                lesson = LessonRepository.find_by_id(context_id)
                if lesson:
                    info['lesson'] = {
                        'lesson_id': str(lesson.get('lesson_id')),
                        'title': lesson.get('title', ''),
                        'lm_type': lesson.get('lm_type', 'LM00')
                    }
                    # Also get chapter info
                    chapter_id = lesson.get('chapter_id')
                    if chapter_id:
                        chapter = ChapterRepository.find_by_id(chapter_id)
                        if chapter:
                            info['chapter'] = {
                                'chapter_id': str(chapter.get('chapter_id')),
                                'title': chapter.get('title', '')
                            }

        except Exception as e:
            logger.warning(f"Error getting context info: {e}")

        return info


class ConversationHelper:
    """Format conversation history for prompts."""

    @staticmethod
    def format_history(messages: List[Dict]) -> str:
        """
        Format conversation history for prompt.

        Args:
            messages: List of message dicts

        Returns:
            Formatted conversation string
        """
        if not messages:
            return "Keine vorherigen Nachrichten."

        formatted = []
        for msg in messages[-5:]:  # Last 5 messages
            role = "Benutzer" if msg['role'] == 'user' else "Assistent"
            formatted.append(f"{role}: {msg['content'][:200]}...")

        return "\n".join(formatted)


class JSONHelper:
    """Extract and parse JSON from text."""

    @staticmethod
    def extract_json(text: str) -> Optional[Dict]:
        """
        Extract JSON from text response.

        Args:
            text: Text containing JSON

        Returns:
            Parsed JSON dict or None
        """
        # Try to find JSON block
        if '```json' in text:
            start = text.find('```json') + 7
            end = text.find('```', start)
            if end > start:
                try:
                    return json.loads(text[start:end].strip())
                except json.JSONDecodeError:
                    return None

        # Try to parse as JSON directly
        if text.strip().startswith('{'):
            # Find the JSON object
            brace_count = 0
            start = text.find('{')
            for i, char in enumerate(text[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        try:
                            return json.loads(text[start:i+1])
                        except json.JSONDecodeError:
                            return None

        return None

    @staticmethod
    def extract_text_before_json(text: str) -> str:
        """
        Extract text before JSON block.

        Args:
            text: Text with JSON

        Returns:
            Text portion before JSON
        """
        if '```json' in text:
            return text[:text.find('```json')].strip()
        if text.strip().startswith('{'):
            return ""
        return text
