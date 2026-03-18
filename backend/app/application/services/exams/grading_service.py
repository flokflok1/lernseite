"""AI Grading Service — grades free-text exam answers using AI.

Supports essay, short_answer, and case_study question types.
Uses the default AI provider configured in the system (no hardcoding).
"""
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Grading prompt templates keyed by language
_GRADING_LABELS = {
    'de': {
        'role': 'Du bist ein IHK-Pruefer. Bewerte die folgende Antwort.',
        'task_header': 'AUFGABE',
        'points_label': 'Punkte',
        'type_label': 'Typ',
        'solution_header': 'MUSTERLOESUNG',
        'no_solution': 'Keine Musterloesung vorhanden — bewerte nach Fachwissen.',
        'answer_header': 'ANTWORT DES PRUEFLINGS',
        'rules': [
            'Vergib 0 bis {max_points} Punkte (Teilpunkte erlaubt)',
            'Akzeptiere alternative korrekte Formulierungen',
            'Bei Rechenaufgaben: Rechenweg UND Ergebnis pruefen',
            'Bei SQL: Syntax und Logik pruefen',
        ],
        'rules_header': 'REGELN',
        'json_instruction': 'Antworte NUR als JSON:',
        'no_answer': 'Keine Antwort eingegeben.',
    },
    'en': {
        'role': 'You are an IHK examiner. Grade the following answer.',
        'task_header': 'TASK',
        'points_label': 'Points',
        'type_label': 'Type',
        'solution_header': 'MODEL SOLUTION',
        'no_solution': 'No model solution available — grade based on expertise.',
        'answer_header': 'EXAMINEE ANSWER',
        'rules': [
            'Award 0 to {max_points} points (partial credit allowed)',
            'Accept alternative correct formulations',
            'For calculations: check method AND result',
            'For SQL: check syntax and logic',
        ],
        'rules_header': 'RULES',
        'json_instruction': 'Reply ONLY as JSON:',
        'no_answer': 'No answer provided.',
    },
}


class GradingService:
    """Grades exam answers using AI."""

    @staticmethod
    def grade_free_text(
        question_text: str,
        solution_text: str,
        user_answer: str,
        max_points: float,
        question_type: str = 'essay',
        language: str = 'de',
    ) -> Optional[Dict]:
        """Grade a free-text answer using AI.

        Args:
            question_text: The exam question.
            solution_text: Model solution (may be empty).
            user_answer: The student's answer.
            max_points: Maximum achievable points.
            question_type: Question type (essay, short_answer, etc.).
            language: Language for grading prompt.

        Returns:
            Dict with points_earned, is_correct, explanation — or None.
        """
        lb = _GRADING_LABELS.get(language, _GRADING_LABELS['de'])

        if not user_answer or not user_answer.strip():
            return {
                'points_earned': 0,
                'is_correct': False,
                'explanation': lb['no_answer'],
            }

        prompt = _build_grading_prompt(
            question_text, solution_text, user_answer,
            max_points, question_type, lb,
        )

        try:
            from app.infrastructure.ai.adapter import AIAdapter
            adapter = AIAdapter()
            response = adapter.send_request(
                prompt=prompt, language=language,
                temperature=0.1, max_tokens=500,
            )
            return _parse_grading_response(
                response.get('output_text', ''), max_points,
            )
        except Exception:
            logger.exception("AI grading failed")
            return None


def _build_grading_prompt(
    question_text: str,
    solution_text: str,
    user_answer: str,
    max_points: float,
    question_type: str,
    lb: Dict[str, object],
) -> str:
    """Build the grading prompt from language-specific labels."""
    solution_section = (
        f"{lb['solution_header']}:\n{solution_text[:800]}"
        if solution_text
        else lb['no_solution']
    )
    rules_list = '\n'.join(
        f"- {r.format(max_points=max_points)}"
        for r in lb['rules']
    )
    return (
        f"{lb['role']}\n\n"
        f"{lb['task_header']} ({max_points} {lb['points_label']}, "
        f"{lb['type_label']}: {question_type}):\n"
        f"{question_text[:800]}\n\n"
        f"{solution_section}\n\n"
        f"{lb['answer_header']}:\n{user_answer[:1000]}\n\n"
        f"{lb['rules_header']}:\n{rules_list}\n\n"
        f"{lb['json_instruction']}\n"
        '{"points": <number>, "correct": <bool>, "feedback": "<reason>"}'
    )


def _parse_grading_response(
    response: str, max_points: float,
) -> Optional[Dict]:
    """Parse AI grading JSON response."""
    try:
        if '{' in response:
            start = response.index('{')
            end = response.rindex('}') + 1
            data = json.loads(response[start:end])
            points = min(float(data.get('points', 0)), max_points)
            return {
                'points_earned': max(0, points),
                'is_correct': data.get(
                    'correct', points >= max_points * 0.5,
                ),
                'explanation': data.get('feedback', ''),
            }
    except (json.JSONDecodeError, ValueError):
        pass
    logger.warning("Could not parse grading response: %s", response[:200])
    return None
