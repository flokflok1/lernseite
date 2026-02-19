"""
Agent Prompts - Prompt building and question normalization

Handles:
- Question normalization for consistent hashing
- System prompt generation from config
- User prompt enrichment with context
- Persona and terminology mapping
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    Builds and normalizes prompts for AI requests.
    """

    @staticmethod
    def normalize_question(question: str) -> str:
        """
        Normalize question for consistent hashing.

        - Lowercase
        - Remove extra whitespace
        - Remove common filler words

        Args:
            question: Raw question text

        Returns:
            Normalized question
        """
        normalized = question.lower().strip()
        normalized = ' '.join(normalized.split())
        return normalized

    @staticmethod
    def build_system_prompt(
        config: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build system prompt from agent config.

        Args:
            config: Agent configuration dict
            context: Optional context

        Returns:
            System prompt string
        """
        persona = config.get('persona', 'friendly')
        language = config.get('language', 'de')
        blocked_topics = config.get('blocked_topics', [])
        terminology = config.get('custom_terminology', {})
        additional_context = config.get('additional_context', '')

        persona_map = {
            'friendly': 'Du bist ein freundlicher und geduldiger KI-Tutor.',
            'professional': 'Du bist ein professioneller und sachlicher KI-Tutor.',
            'encouraging': 'Du bist ein ermutigender und motivierender KI-Tutor.',
            'socratic': 'Du bist ein sokratischer Tutor, der durch Fragen zum Denken anregt.'
        }

        prompt = persona_map.get(persona, persona_map['friendly'])
        prompt += f"\nAntworte immer auf {language.upper()}."
        prompt += "\nGib klare, verstaendliche Erklaerungen."
        prompt += "\nVerwende Beispiele wo sinnvoll."

        if blocked_topics:
            prompt += f"\nVermeide folgende Themen: {', '.join(blocked_topics)}"

        if terminology:
            terms = [f"{k} = {v}" for k, v in terminology.items()]
            prompt += f"\nVerwende diese Terminologie: {'; '.join(terms)}"

        if additional_context:
            prompt += f"\n{additional_context}"

        return prompt

    @staticmethod
    def build_user_prompt(
        question: str,
        context: Optional[Dict[str, Any]] = None,
        language: str = 'de'
    ) -> str:
        """
        Build user prompt with context enrichment.

        Args:
            question: User's question
            context: Optional context dict
            language: Response language

        Returns:
            User prompt with context
        """
        prompt = question

        if context:
            if context.get('lesson_title'):
                prompt = f"Lektion: {context['lesson_title']}\n\nFrage: {question}"
            elif context.get('chapter_title'):
                prompt = f"Kapitel: {context['chapter_title']}\n\nFrage: {question}"
            elif context.get('course_title'):
                prompt = f"Kurs: {context['course_title']}\n\nFrage: {question}"

        return prompt
