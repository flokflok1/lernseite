"""
Question Generator Service

AI-powered generation of IHK-style exam questions for curriculum positions.
"""

import json
import logging
from typing import Dict, Any, List

from app.application.services.exams.curriculum_mapping_helpers import extract_json_object

logger = logging.getLogger(__name__)


class QuestionGeneratorService:
    """Generates IHK-style exam questions for curriculum positions."""

    @staticmethod
    def generate_for_position(
        position_id: int,
        count: int = 3,
        difficulty: str = 'mittel',
        style: str = 'multiple_choice',
        provider: str = None,
        model: str = None,
    ) -> List[Dict[str, Any]]:
        """Generate exam questions for a curriculum position.

        Args:
            position_id: Curriculum position ID.
            count: Number of questions to generate (1-10).
            difficulty: leicht/mittel/schwer.
            style: Question style (multiple_choice, assignment, etc.).
            provider: Optional AI provider.
            model: Optional AI model.

        Returns:
            List of generated question dicts.
        """
        from app.infrastructure.ai.adapter import AIAdapter
        from app.infrastructure.persistence.repositories.exams.curriculum import (
            CurriculumFrameworkRepository,
        )
        from app.domain.services.exam_question_style import build_generation_context

        count = min(max(count, 1), 10)

        # Load position objectives
        # Returns: objective_id, code, description_text, bloom_level, position_id, order_index
        objectives = CurriculumFrameworkRepository.find_objectives_by_position(
            position_id,
        )
        if not objectives:
            raise ValueError(f"No objectives found for position {position_id}")

        # Load example questions for style reference (up to 3)
        first_objective_id = objectives[0]['objective_id']
        example_questions = CurriculumFrameworkRepository.find_questions_by_objective(
            first_objective_id,
        )[:3]

        context = build_generation_context(style, difficulty)

        prompt = QuestionGeneratorService._build_prompt(
            objectives, example_questions, context, count,
        )

        ai_opts = {
            k: v for k, v in {'provider': provider, 'model': model}.items() if v
        }
        adapter = AIAdapter(**ai_opts)
        response = adapter.send_request(
            prompt=prompt,
            temperature=0.7,
            max_tokens=16000,
        )

        raw = extract_json_object(response.get('output_text', ''))
        try:
            questions = json.loads(raw)
        except json.JSONDecodeError:
            logger.exception("Failed to parse AI question generation response")
            raise ValueError("AI response is not valid JSON")

        if not isinstance(questions, list):
            raise ValueError("AI response is not a JSON array")

        # Tag generated questions with metadata
        for q in questions:
            q['source'] = 'ai_generated'
            q['generated_from_position'] = position_id
            q['difficulty'] = difficulty

        logger.info(
            "Generated %d questions for position %d (%s, %s)",
            len(questions), position_id, difficulty, style,
        )
        return questions

    @staticmethod
    def _build_prompt(
        objectives: List[Dict],
        examples: List[Dict],
        context: Dict,
        count: int,
    ) -> str:
        """Build AI prompt for question generation."""
        obj_text = "\n".join(
            f"- {o.get('code', '?')}: {_extract_description(o)[:150]}"
            for o in objectives
        )

        example_text = ""
        if examples:
            example_text = "\n\nBeispiel-Fragen als Stil-Referenz:\n" + "\n".join(
                f"- Q{e.get('question_number', '?')}: "
                f"{(e.get('question_text') or '')[:200]}"
                for e in examples[:3]
            )

        return (
            "Du bist ein Experte für IHK-Prüfungsaufgaben im IT-Bereich.\n\n"
            f"Erstelle {count} Prüfungsfrage(n) im Stil '{context['style_name']}' "
            f"mit Schwierigkeitsgrad '{context['difficulty_label']}' "
            f"({context['difficulty_description']}).\n\n"
            f"Lernziele der Position:\n{obj_text}\n"
            f"{example_text}\n\n"
            f"Antwortformat: {context['answer_format']}\n"
            f"Punktebereich: {context['points_range']}\n"
            f"Kompetenzstufe: {context['competency_level']}\n\n"
            "Antworte NUR mit einem JSON-Array:\n"
            '[{"question_text": "...", "answer_options": [...], '
            '"correct_answer": "...", "explanation": "...", '
            f'"points": N, "question_type": "{context["answer_format"]}"}}]\n\n'
            "Regeln:\n"
            "- Fragen MÜSSEN sich auf die genannten Lernziele beziehen\n"
            "- IHK-typischer Stil: präzise, fachlich, praxisnah\n"
            "- Schwierigkeitsgrad beachten\n"
            "- Deutsche Sprache\n"
            "- Jede Frage braucht: question_text, points, question_type"
        )


def _extract_description(objective: Dict) -> str:
    """Extract plain text description from objective dict.

    Handles both raw string and JSONB dict values stored in description_text.
    """
    desc = objective.get('description_text', '')
    if isinstance(desc, dict):
        return desc.get('de', '') or next(iter(desc.values()), '')
    return str(desc) if desc else ''
