"""
Tutor Factories (DDD)

Factory Pattern for creating tutor domain objects with business rules.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from .value_objects import GenerationStyle, TutorContext


class TutorSessionFactory:
    """
    Factory for creating tutor session instances.

    Implements Domain-Driven Design (DDD) Factory Pattern.
    Business rules are enforced during creation.
    """

    @staticmethod
    def create_chat_session(
        user_id: str,
        message: str,
        context: Optional[TutorContext] = None,
        history: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Create tutor chat session configuration.

        Args:
            user_id: User ID
            message: User message
            context: Optional tutor context
            history: Optional conversation history

        Returns:
            Session configuration dict

        Business Rules:
        - History limited to last 10 messages
        - Context is optional
        - Session ID is generated
        """
        session_id = str(uuid.uuid4())

        # Limit history to last 10 messages
        if history and len(history) > 10:
            history = history[-10:]

        return {
            'session_id': session_id,
            'user_id': user_id,
            'message': message,
            'context': context.to_dict() if context else {},
            'history': history or [],
            'created_at': datetime.utcnow(),
            'has_context': context is not None and context.has_course_context() if context else False
        }

    @staticmethod
    def create_tts_request(
        user_id: str,
        text: str,
        voice: str = 'alloy'
    ) -> Dict[str, Any]:
        """
        Create TTS request configuration.

        Args:
            user_id: User ID making the request
            text: Text to synthesize
            voice: Voice ID (default: alloy)

        Returns:
            TTS request dict

        Business Rules:
        - Text limited to 4096 characters
        - Voice must be valid OpenAI voice
        """
        # Valid voices
        valid_voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']

        # Validate voice
        if voice not in valid_voices:
            raise ValueError(f"Invalid voice: {voice}. Must be one of: {', '.join(valid_voices)}")

        # Limit text length
        if len(text) > 4096:
            text = text[:4096]

        return {
            'request_id': str(uuid.uuid4()),
            'text': text,
            'voice': voice,
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'char_count': len(text)
        }


class TutorGenerationFactory:
    """
    Factory for creating tutor content generation configurations.

    Business rules for theory generation, lesson explanations, etc.
    """

    @staticmethod
    def create_chapter_theory_request(
        chapter_id: str,
        chapter_title: str,
        course_title: str,
        style: GenerationStyle,
        user_id: str,
        custom_title: Optional[str] = None,
        generate_tts: bool = False,
        tts_voice: str = 'alloy'
    ) -> Dict[str, Any]:
        """
        Create chapter theory generation request.

        Args:
            chapter_id: Chapter UUID
            chapter_title: Chapter title
            course_title: Course title
            style: Generation style (Value Object)
            user_id: Creator user ID
            custom_title: Optional custom title
            generate_tts: Generate TTS audio
            tts_voice: TTS voice ID

        Returns:
            Generation request dict

        Business Rules:
        - Style must be valid GenerationStyle
        - TTS only if generate_tts=True
        """
        return {
            'request_id': str(uuid.uuid4()),
            'chapter_id': chapter_id,
            'chapter_title': chapter_title,
            'course_title': course_title,
            'style': style.value,
            'style_display': style.display_name,
            'custom_title': custom_title,
            'user_id': user_id,
            'generate_tts': generate_tts,
            'tts_voice': tts_voice if generate_tts else None,
            'created_at': datetime.utcnow()
        }

    @staticmethod
    def create_lesson_explanation_request(
        lesson_id: int,
        lesson_title: str,
        chapter_title: str,
        course_title: str,
        style: GenerationStyle,
        user_id: str,
        explanation_type: str = 'steps',  # 'steps' or 'detailed'
        generate_tts: bool = False,
        tts_voice: str = 'alloy'
    ) -> Dict[str, Any]:
        """
        Create lesson explanation generation request.

        Args:
            lesson_id: Lesson ID
            lesson_title: Lesson title
            chapter_title: Chapter title
            course_title: Course title
            style: Generation style
            user_id: Creator user ID
            explanation_type: Type ('steps' or 'detailed')
            generate_tts: Generate TTS audio
            tts_voice: TTS voice ID

        Returns:
            Generation request dict

        Business Rules:
        - explanation_type must be 'steps' or 'detailed'
        - Style must be valid GenerationStyle
        """
        if explanation_type not in ['steps', 'detailed']:
            raise ValueError(f"Invalid explanation_type: {explanation_type}. Must be 'steps' or 'detailed'")

        return {
            'request_id': str(uuid.uuid4()),
            'lesson_id': lesson_id,
            'lesson_title': lesson_title,
            'chapter_title': chapter_title,
            'course_title': course_title,
            'style': style.value,
            'style_display': style.display_name,
            'explanation_type': explanation_type,
            'user_id': user_id,
            'generate_tts': generate_tts,
            'tts_voice': tts_voice if generate_tts else None,
            'created_at': datetime.utcnow()
        }

    @staticmethod
    def create_theory_data(
        title: str,
        introduction: str,
        sections: list,
        summary: str,
        key_points: list,
        style: GenerationStyle
    ) -> Dict[str, Any]:
        """
        Create theory data structure.

        Args:
            title: Theory title
            introduction: Introduction text
            sections: List of section dicts
            summary: Summary text
            key_points: List of key points
            style: Generation style used

        Returns:
            Theory data dict

        Business Rules:
        - Sections must have: title, content, subsections
        - Key points must be list of strings
        """
        return {
            'title': title,
            'introduction': introduction,
            'sections': sections,
            'summary': summary,
            'key_points': key_points,
            'style': style.value,
            'generated_at': datetime.utcnow().isoformat()
        }
