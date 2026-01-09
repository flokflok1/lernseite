"""
LernsystemX Chapter Theory Factory

DDD Factory Pattern for creating chapter theory instances.

Factory Methods:
    - create_theory: Create theory with validation
    - generate_from_lesson: Generate theory from lesson context (future)

DDD Pattern: 2026-01-08
Per Developer-Guide-KI Section Development Priority Rules
"""

from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TheoryFactory:
    """
    Factory for creating Chapter Theory instances.
    Implements Domain-Driven Design (DDD) Factory Pattern.
    """

    @staticmethod
    def create_theory(
        chapter_id: str,
        style: str,
        theory_data: dict,
        title: Optional[str] = None,
        audio_url: Optional[str] = None,
        audio_duration: Optional[int] = None,
        tokens_used: int = 0,
        model_used: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> dict:
        """
        Create a chapter theory with validation and defaults.

        Args:
            chapter_id: UUID of the chapter
            style: Theory style (adhs, detailed, short, exam_focus, standard)
            theory_data: JSON-serializable theory content
            title: Optional title (auto-generated if not provided)
            audio_url: Optional URL to TTS audio
            audio_duration: Optional audio duration in seconds
            tokens_used: Number of tokens used for generation
            model_used: AI model identifier
            user_id: UUID of user who generated the theory

        Returns:
            Dict ready for database insertion

        Raises:
            ValueError: If validation fails
        """
        # Validate style
        valid_styles = ['adhs', 'detailed', 'short', 'exam_focus', 'standard']
        if style not in valid_styles:
            raise ValueError(f"Invalid style: {style}. Must be one of {valid_styles}")

        # Validate theory_data
        if not isinstance(theory_data, dict):
            raise ValueError("theory_data must be a dictionary")

        # Generate title if not provided
        if not title:
            timestamp = datetime.now().strftime('%d.%m.%Y %H:%M')
            style_names = {
                'adhs': 'ADHS-freundlich',
                'detailed': 'Ausfuehrlich',
                'short': 'Kurz & Kompakt',
                'exam_focus': 'Pruefungsfokus',
                'standard': 'Standard'
            }
            style_name = style_names.get(style, style)
            title = f"{style_name} ({timestamp})"

        # Validate audio_duration if provided
        if audio_duration is not None and audio_duration < 0:
            raise ValueError("audio_duration must be positive")

        # Validate tokens_used
        if tokens_used < 0:
            raise ValueError("tokens_used must be non-negative")

        theory_instance = {
            'chapter_id': chapter_id,
            'style': style,
            'title': title,
            'theory_data': theory_data,
            'audio_url': audio_url,
            'audio_duration_seconds': audio_duration,
            'tokens_used': tokens_used,
            'model_used': model_used,
            'generated_by': user_id,
        }

        logger.info(f"TheoryFactory created theory: style={style}, tokens={tokens_used}")

        return theory_instance

    @staticmethod
    def create_with_defaults(chapter_id: str, style: str = 'standard') -> dict:
        """
        Create a minimal theory with sensible defaults.

        Args:
            chapter_id: UUID of the chapter
            style: Theory style (default: 'standard')

        Returns:
            Dict ready for database insertion
        """
        return TheoryFactory.create_theory(
            chapter_id=chapter_id,
            style=style,
            theory_data={
                'overview': 'Placeholder theory content',
                'learningGoals': [],
                'concepts': [],
                'terms': [],
                'examRelevance': 'To be determined'
            },
            tokens_used=0,
            model_used='placeholder'
        )

    @staticmethod
    def generate_from_lesson(
        chapter_id: str,
        lesson_titles: list,
        style: str = 'standard'
    ) -> dict:
        """
        Generate theory metadata from lesson context.
        (Future implementation: integrate with AI generation)

        Args:
            chapter_id: UUID of the chapter
            lesson_titles: List of lesson titles in the chapter
            style: Theory style

        Returns:
            Dict with metadata for theory generation
        """
        context = {
            'chapter_id': chapter_id,
            'style': style,
            'lesson_count': len(lesson_titles),
            'lesson_titles': ', '.join(lesson_titles[:10]),  # Max 10 for brevity
            'requires_generation': True
        }

        logger.info(f"TheoryFactory prepared generation context: {lesson_titles[:3]}...")

        return context
