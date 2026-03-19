"""Solution Generator — creates model answers using AI expertise.

For exam questions that have no solution (no PDF or PDF didn't cover them),
generates a fachlich korrekte Musterloesung using the AI grading model.
"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Prompt labels per language
_LABELS = {
    'de': {
        'intro': 'Du bist ein Experte fuer IHK-Pruefungen (Fachinformatiker).',
        'task': 'Erstelle eine vollstaendige Musterloesung fuer folgende Pruefungsfrage.',
        'rules': [
            'Die Loesung muss fachlich korrekt und pruefungsgerecht sein.',
            'Bei Berechnungen: Rechenweg + Ergebnis angeben.',
            'Bei SQL: korrekten SQL-Befehl schreiben.',
            'Bei Multiple Choice: korrekte Antwort(en) mit Begruendung.',
            'Bei Textaufgaben: vollstaendige, strukturierte Antwort.',
            'Punkte beachten: mehr Punkte = ausfuehrlichere Antwort.',
        ],
        'format': 'Antworte NUR mit der Musterloesung, kein JSON, kein Markdown-Fence.',
    },
    'en': {
        'intro': 'You are an expert for IHK exams (Fachinformatiker).',
        'task': 'Create a complete model answer for the following exam question.',
        'rules': [
            'The answer must be technically correct and exam-appropriate.',
            'For calculations: show method + result.',
            'For SQL: write the correct SQL statement.',
            'For multiple choice: correct answer(s) with reasoning.',
            'For text questions: complete, structured answer.',
            'Consider points: more points = more detailed answer.',
        ],
        'format': 'Reply ONLY with the model answer, no JSON, no markdown fence.',
    },
}


def generate_solutions_for_exam(
    exam_id: str, language: str = 'de',
) -> int:
    """Generate AI solutions for all questions without solution_text.

    Args:
        exam_id: Exam UUID.
        language: Prompt language.

    Returns:
        Count of solutions generated.
    """
    from app.infrastructure.persistence.repositories.exams.questions import (
        ExamQuestionRepository,
    )

    questions = ExamQuestionRepository.find_by_exam(exam_id)
    count = 0
    for q in questions:
        sol = q.get('solution_text') or ''
        if sol:
            continue
        text = q.get('question_text') or ''
        if not text:
            continue

        solution = _generate_single_solution(
            question_text=text,
            question_type=q.get('question_type', 'essay'),
            points=q.get('points') or 5,
            scenario_title=q.get('scenario_title') or '',
            topics=q.get('topics') or [],
            language=language,
        )
        if solution:
            ExamQuestionRepository.update_question(
                str(q['question_id']),
                {'solution_text': f'[KI-generiert] {solution}'},
            )
            count += 1
            logger.info(
                "Generated solution for q=%s in exam=%s",
                q.get('question_number'), exam_id,
            )

    logger.info(
        "Generated %d solutions for exam %s", count, exam_id,
    )
    return count


def _generate_single_solution(
    question_text: str,
    question_type: str,
    points: float,
    scenario_title: str,
    topics: list,
    language: str,
) -> Optional[str]:
    """Call AI to generate a single solution."""
    from app.infrastructure.ai.adapter import AIAdapter
    from app.infrastructure.ai.task_model_resolver import (
        resolve_model_for_task,
    )

    prompt = _build_prompt(
        question_text, question_type, points,
        scenario_title, topics, language,
    )

    try:
        provider, model = resolve_model_for_task('grading')
        adapter = AIAdapter(provider=provider, model=model)
        response = adapter.send_messages(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000,
        )
        return (response.get('output_text') or '').strip()
    except Exception:
        logger.exception("Failed to generate solution")
        return None


def _build_prompt(
    question_text: str,
    question_type: str,
    points: float,
    scenario_title: str,
    topics: list,
    language: str,
) -> str:
    """Build the AI prompt for solution generation."""
    lb = _LABELS.get(language, _LABELS['de'])
    rules = '\n'.join(f'- {r}' for r in lb['rules'])

    context_parts = [f"Fragetyp: {question_type}", f"Punkte: {points}"]
    if scenario_title:
        context_parts.append(f"Kontext: {scenario_title}")
    if topics:
        context_parts.append(f"Themen: {', '.join(topics)}")

    context = '\n'.join(context_parts)
    return (
        f"{lb['intro']}\n{lb['task']}\n\n"
        f"{rules}\n\n"
        f"{context}\n\n"
        f"Frage:\n{question_text}\n\n"
        f"{lb['format']}"
    )
