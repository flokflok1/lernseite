"""
Tutor Services (DDD)

Domain Services for tutor business logic.
"""

from typing import Dict, Any, Optional, List
import logging

from app.services.tutor_knowledge_service import TutorKnowledgeService as BaseTutorKnowledgeService
from .value_objects import TutorContext, GenerationStyle

logger = logging.getLogger(__name__)


class TutorKnowledgeService:
    """
    Service for loading and building tutor knowledge context.

    Domain Service: Orchestrates knowledge loading from various sources.
    """

    @staticmethod
    def build_context_for_chat(
        context: TutorContext,
        include_files: bool = True,
        include_progress: bool = True
    ) -> str:
        """
        Build knowledge context for tutor chat.

        Args:
            context: Tutor context with IDs
            include_files: Include course files
            include_progress: Include user progress

        Returns:
            Context string for AI prompt

        Business Logic:
        - Loads course/chapter/lesson content if IDs provided
        - Includes user progress if requested
        - Formats context for AI consumption
        """
        if not context.has_course_context():
            return "Kein spezifischer Kurs-Kontext verfügbar."

        try:
            knowledge_context = BaseTutorKnowledgeService.build_tutor_context_prompt(
                course_id=context.course_id,
                chapter_id=context.chapter_id,
                lesson_id=context.lesson_id,
                method_id=context.method_id,
                user_id=context.user_id,
                include_files=include_files,
                include_progress=include_progress
            )
            return knowledge_context
        except Exception as e:
            logger.warning(f"Could not load tutor knowledge context: {e}")
            return "Kein spezifischer Kurs-Kontext verfügbar."

    @staticmethod
    def build_context_for_generation(
        course_title: str,
        chapter_title: str,
        chapter_description: Optional[str] = None,
        lesson_titles: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Build context for content generation (theory, explanations).

        Args:
            course_title: Course title
            chapter_title: Chapter title
            chapter_description: Optional chapter description
            lesson_titles: Optional list of lesson titles

        Returns:
            Context dict for prompt templates
        """
        return {
            'course_title': course_title,
            'chapter_title': chapter_title,
            'chapter_description': chapter_description or '',
            'lesson_titles': ', '.join(lesson_titles) if lesson_titles else 'Keine spezifischen Lektionen',
            'target_audience': 'Fachinformatiker Systemintegration (FISI) in Prüfungsvorbereitung'
        }


class TutorResponseService:
    """
    Service for processing and formatting tutor responses.

    Domain Service: Handles response formatting and validation.
    """

    @staticmethod
    def format_chat_response(
        ai_response: str,
        tokens_used: int,
        context_used: bool,
        cost_eur: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Format tutor chat response.

        Args:
            ai_response: AI-generated response
            tokens_used: Total tokens used
            context_used: Whether course context was used
            cost_eur: Optional cost in EUR

        Returns:
            Formatted response dict
        """
        response = {
            'message': ai_response,
            'tokens_used': tokens_used,
            'context_used': context_used
        }

        if cost_eur is not None:
            response['cost_eur'] = float(cost_eur)

        return response

    @staticmethod
    def validate_theory_data(theory_data: dict) -> bool:
        """
        Validate theory data structure.

        Args:
            theory_data: Theory data dict

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails

        Business Rules:
        - Must have: title, introduction, sections, summary, key_points
        - Sections must be list
        - Key points must be list
        """
        required_fields = ['title', 'introduction', 'sections', 'summary', 'key_points']

        for field in required_fields:
            if field not in theory_data:
                raise ValueError(f"Missing required field: {field}")

        if not isinstance(theory_data['sections'], list):
            raise ValueError("Sections must be a list")

        if not isinstance(theory_data['key_points'], list):
            raise ValueError("Key points must be a list")

        return True

    @staticmethod
    def parse_json_response(output_text: str, fallback_title: str = "Theorie") -> dict:
        """
        Parse JSON response from AI.

        Args:
            output_text: AI output text (should be JSON)
            fallback_title: Fallback title if parsing fails

        Returns:
            Parsed theory data dict

        Business Logic:
        - Attempts to parse JSON
        - Falls back to structured text if parsing fails
        - Always returns valid structure
        """
        import json

        try:
            # Try to parse as JSON
            data = json.loads(output_text)

            # Validate structure
            if isinstance(data, dict) and 'title' in data:
                return data

        except json.JSONDecodeError:
            pass

        # Fallback: Create basic structure from text
        return {
            'title': fallback_title,
            'introduction': output_text[:500] if len(output_text) > 500 else output_text,
            'sections': [{
                'title': 'Inhalt',
                'content': output_text,
                'subsections': []
            }],
            'summary': 'Siehe Inhalt oben.',
            'key_points': [],
            'parse_error': True
        }


class TutorStyleService:
    """
    Service for style-specific configurations.

    Domain Service: Manages generation styles and their settings.
    """

    @staticmethod
    def get_style_instructions(style: GenerationStyle) -> Dict[str, Any]:
        """
        Get generation instructions for a style.

        Args:
            style: Generation style

        Returns:
            Dict with instructions, temperature, max_tokens, etc.
        """
        style_configs = {
            GenerationStyle.ADHS: {
                'instructions': [
                    'Nutze kurze, prägnante Sätze (max 15 Wörter)',
                    'Strukturiere mit Überschriften, Listen und Emojis',
                    'Hebe wichtige Punkte visuell hervor',
                    'Verwende Bullet Points statt langer Absätze',
                    'Füge Beispiele und visuelle Ankerpunkte hinzu'
                ],
                'temperature': 0.7,
                'max_tokens': 3000,
                'emoji': True
            },
            GenerationStyle.DETAILED: {
                'instructions': [
                    'Erkläre Konzepte ausführlich und detailliert',
                    'Gehe auf Zusammenhänge und Hintergründe ein',
                    'Nutze Beispiele und Analogien',
                    'Strukturiere logisch mit Überschriften',
                    'Biete tiefgehende Erklärungen'
                ],
                'temperature': 0.6,
                'max_tokens': 4000,
                'emoji': False
            },
            GenerationStyle.SHORT: {
                'instructions': [
                    'Fasse die wichtigsten Punkte zusammen',
                    'Nutze kompakte Stichpunkte',
                    'Fokussiere auf das Wesentliche',
                    'Keine langen Erklärungen',
                    'Maximal 3-5 Hauptpunkte'
                ],
                'temperature': 0.5,
                'max_tokens': 1500,
                'emoji': False
            },
            GenerationStyle.EXAM_FOCUS: {
                'instructions': [
                    'Fokussiere auf prüfungsrelevante Inhalte',
                    'Betone wichtige Definitionen und Fakten',
                    'Füge typische Prüfungsfragen hinzu',
                    'Strukturiere nach Relevanz für die Prüfung',
                    'Markiere besonders wichtige Punkte'
                ],
                'temperature': 0.6,
                'max_tokens': 3500,
                'emoji': False
            }
        }

        return style_configs.get(style, style_configs[GenerationStyle.ADHS])

    @staticmethod
    def get_available_styles() -> List[Dict[str, str]]:
        """
        Get list of available generation styles.

        Returns:
            List of dicts with value, name, description
        """
        return [
            {
                'value': style.value,
                'name': style.display_name,
                'description': style.description
            }
            for style in GenerationStyle
        ]
