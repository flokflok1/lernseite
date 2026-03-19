"""Solution Analyzer — extracts model answers from solution PDFs.

Converts solution PDF pages to images, sends to Vision AI,
and matches extracted solutions to existing exam questions.
"""
import json
import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Prompt labels per language
_LABELS = {
    'de': {
        'intro': 'Du siehst die Loesungsseiten einer Pruefung als Bilder.',
        'task': 'Extrahiere die Musterloesung fuer JEDE Aufgabe.',
        'rules': [
            'question_number = exakte Nummer (1.1, 2.3, etc.)',
            'solution_text = vollstaendige Musterloesung',
            'Bei Berechnungen: Rechenweg + Ergebnis',
            'Bei SQL: den korrekten SQL-Befehl',
            'Bei Multiple Choice: die korrekte(n) Antwort(en)',
        ],
        'format': 'Antworte NUR mit validem JSON.',
    },
    'en': {
        'intro': 'You see solution pages of an exam as images.',
        'task': 'Extract the model answer for EVERY question.',
        'rules': [
            'question_number = exact number (1.1, 2.3, etc.)',
            'solution_text = complete model answer',
            'For calculations: method + result',
            'For SQL: the correct SQL statement',
            'For multiple choice: the correct answer(s)',
        ],
        'format': 'Reply ONLY with valid JSON.',
    },
}


def analyze_solution_pdf(
    solution_pdf_path: str,
    language: str = 'de',
) -> Optional[List[Dict]]:
    """Analyze a solution PDF and extract answers per question.

    Args:
        solution_pdf_path: Path to the solution PDF file.
        language: Prompt language.

    Returns:
        List of {question_number, solution_text} dicts, or None.
    """
    from app.application.services.exams.archive_service_part2 import (
        convert_pdf_to_images,
    )

    page_images = convert_pdf_to_images(solution_pdf_path, dpi=200)
    if not page_images:
        logger.error("No pages in solution PDF: %s", solution_pdf_path)
        return None

    logger.info(
        "Analyzing solution PDF: %s (%d pages)",
        solution_pdf_path, len(page_images),
    )

    prompt = _build_solution_prompt(language)
    parsed = _call_vision_ai(page_images, prompt, language)

    if not parsed:
        return None

    solutions = parsed.get('solutions', [])
    logger.info("Extracted %d solutions from PDF", len(solutions))
    return solutions


def apply_solutions_to_exam(exam_id: str, solutions: List[Dict]) -> int:
    """Match extracted solutions to exam questions and update DB.

    Args:
        exam_id: The exam UUID.
        solutions: List of {question_number, solution_text}.

    Returns:
        Count of questions updated with solutions.
    """
    from app.infrastructure.persistence.repositories.exams.questions import (
        ExamQuestionRepository,
    )

    count = ExamQuestionRepository.update_solutions_batch(exam_id, solutions)
    logger.info(
        "Applied %d solutions to exam %s (of %d extracted)",
        count, exam_id, len(solutions),
    )
    return count


def _build_solution_prompt(language: str) -> str:
    """Build the Vision AI prompt for solution extraction."""
    lb = _LABELS.get(language, _LABELS['de'])
    rules = '\n'.join(f'- {r}' for r in lb['rules'])
    return (
        f"{lb['intro']}\n{lb['task']}\n\n"
        f"{rules}\n\n"
        f'{lb["format"]}\n'
        '```json\n'
        '{"solutions": [\n'
        '  {"question_number": "1.1", "solution_text": "..."},\n'
        '  {"question_number": "1.2", "solution_text": "..."}\n'
        ']}\n```'
    )


def _call_vision_ai(
    page_images: List[str],
    prompt: str,
    language: str,
) -> Optional[Dict]:
    """Send solution pages to Vision AI and parse response."""
    from app.infrastructure.ai.adapter import AIAdapter
    from app.infrastructure.ai.task_model_resolver import (
        resolve_model_for_task,
    )

    provider, model = resolve_model_for_task('vision')
    adapter = AIAdapter(provider=provider, model=model)

    content = [{"type": "text", "text": prompt}]
    for img_b64 in page_images:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{img_b64}",
                "detail": "high",
            },
        })

    try:
        response = adapter.send_messages(
            messages=[{"role": "user", "content": content}],
            temperature=0.2,
            max_tokens=16000,
        )
        output_text = response.get('output_text', '')
        if not output_text:
            logger.error("Vision AI returned empty response for solutions")
            return None
        return _parse_response(output_text)
    except Exception:
        logger.exception("Vision AI call failed for solution analysis")
        return None


def _parse_response(response: str) -> Optional[Dict]:
    """Parse JSON from Vision AI response."""
    if not response:
        return None
    # Try ```json block
    json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    # Try raw JSON
    try:
        start = response.index('{')
        end = response.rindex('}') + 1
        return json.loads(response[start:end])
    except (ValueError, json.JSONDecodeError):
        logger.error("Failed to parse solution AI response")
        return None
