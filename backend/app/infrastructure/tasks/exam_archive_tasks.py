"""
LernsystemX Exam Archive Analysis Celery Task

Background task for AI-powered analysis of real IHK exam PDFs.
Extracts scenarios and questions from raw PDF text using AI,
then inserts structured question data into the database.
"""

import json
import logging
from typing import Dict, Any, Optional, List

from app.core.bootstrap.extensions import celery
from app.infrastructure.persistence.repositories.exams.core import ExamRepository
from app.infrastructure.persistence.repositories.exams.questions import (
    ExamQuestionRepository,
)
from app.domain.services.exam_topic_utils import normalize_topic
from app.infrastructure.ai.adapter import AIAdapter
from app.infrastructure.ai.exceptions import AIProviderError

logger = logging.getLogger(__name__)


_FALLBACK_TOPICS = (
    'subnetting, kalkulation, sql, erm, schutzbedarfsanalyse, '
    'osi_modell, dhcp, wlan, programmierung, itil, rechtsformen, '
    'organisationsformen, raid, virtualisierung, datenschutz, '
    'netzwerk, backup, it_sicherheit, projektmanagement, '
    'qualitaetsmanagement, datenbanken, hardware, software, '
    'cloud, verschluesselung, firewall, routing'
)

_ANALYSIS_PROMPT_TEMPLATE = """Du bist ein Experte für IHK-Prüfungen (Fachinformatiker AP1).
Analysiere den folgenden Prüfungstext und extrahiere ALLE Aufgaben strukturiert.

## Regeln:
1. Identifiziere jede Handlungssituation / jedes Firmenszenario
2. Extrahiere JEDE Teilfrage (1a, 1b, 2.1, 2.2 etc.)
3. Weise jedem Teilfrage einen question_type zu:
   - "mcq" (Multiple Choice)
   - "calculation" (Rechenaufgabe)
   - "essay" (Freitext / Erklärung)
   - "code" (Programmierung / SQL / Pseudocode)
   - "fill_blank" (Lückentext / Zuordnung)
   - "case_study" (Fallstudie / Szenario-Analyse)
4. Tagge Topics aus dieser Liste (mehrere möglich):
   {topic_list}
5. Generiere renderer_data passend zum question_type:
   - mcq: {{"questions": [{{"question": "...", "options": [...], "correctAnswers": [0], "explanation": "..."}}]}}
   - calculation: {{"problems": [{{"question": "...", "answer": "...", "hint": "..."}}]}}
   - essay: {{"question": "...", "hints": [...], "wordLimit": 300}}
   - code: {{"question": "...", "language": "sql", "starterCode": "", "solution": "..."}}
   - fill_blank: {{"sentences": [{{"text": "... {{{{blank}}}} ...", "answers": ["..."]}}]}}
   - case_study: {{"scenario": "...", "questions": [{{"question": "...", "answer": "..."}}]}}

## Ausgabeformat (strenges JSON):
```json
{{
  "scenarios": [
    {{
      "number": 1,
      "title": "Firmenszenario-Titel",
      "context": "Beschreibung der Handlungssituation..."
    }}
  ],
  "questions": [
    {{
      "scenario_number": 1,
      "question_number": "1a",
      "text": "Die vollständige Fragestellung...",
      "question_type": "mcq",
      "points": 5,
      "topics": ["netzwerk", "subnetting"],
      "renderer_data": {{}},
      "solution_text": "Musterlösung / Erwartungshorizont..."
    }}
  ]
}}
```

## WICHTIG:
- Gib NUR das JSON aus, keine zusätzliche Erklärung
- Extrahiere ALLE Teilfragen, keine auslassen
- Punkte möglichst aus dem Text übernehmen, sonst schätzen
- renderer_data MUSS zum question_type passen
- solution_text: Wenn Lösungstext vorhanden, übernehmen

{solution_section}

## Prüfungstext:
{exam_text}"""


def _build_topic_list(exam_type: str) -> str:
    """Build topic list for ANALYSIS_PROMPT from taxonomy, with fallback."""
    from app.infrastructure.persistence.repositories.exams.topic_taxonomy import (
        TopicTaxonomyRepository,
    )

    try:
        topics = TopicTaxonomyRepository.find_all_by_exam_type(exam_type)
    except Exception:
        logger.exception("Failed to load taxonomy for %s, using fallback", exam_type)
        return _FALLBACK_TOPICS

    if topics:
        topic_keys = sorted(set(t['topic_key'] for t in topics))
        return ', '.join(topic_keys)

    return _FALLBACK_TOPICS


def _build_analysis_prompt(
    exam_type: str, exam_text: str, solution_section: str,
) -> str:
    """Build the full ANALYSIS_PROMPT with dynamic topic list."""
    topic_list = _build_topic_list(exam_type)
    return _ANALYSIS_PROMPT_TEMPLATE.format(
        topic_list=topic_list,
        exam_text=exam_text,
        solution_section=solution_section,
    )


def _register_new_topics(
    exam_type: str, extracted_topics: List[str],
) -> None:
    """Check for new topics not in taxonomy and auto-classify them."""
    from app.infrastructure.persistence.repositories.exams.topic_taxonomy import (
        TopicTaxonomyRepository,
    )
    from app.application.services.exams.taxonomy_bootstrap_service import (
        TaxonomyBootstrapService,
    )

    try:
        known = TopicTaxonomyRepository.find_all_by_exam_type(exam_type)
    except Exception:
        logger.exception("Failed to load taxonomy for new topic registration")
        return

    known_keys = {t['topic_key'] for t in known}

    # Deduplicate to avoid redundant AI classification calls
    unique_topics = sorted(set(
        normalize_topic(t) for t in extracted_topics if t
    ))

    for normalized in unique_topics:
        if normalized and normalized not in known_keys:
            logger.info("New topic discovered: %s for %s", normalized, exam_type)
            try:
                TaxonomyBootstrapService.classify_orphan_topic(
                    exam_type=exam_type,
                    topic_key=normalized,
                )
            except Exception:
                logger.exception(
                    "Failed to classify orphan topic %s", normalized,
                )


@celery.task(bind=True, max_retries=2, default_retry_delay=30)
def analyze_exam_pdf_task(
    self,
    exam_id: str,
    provider: str = 'openai',
    model: str = 'gpt-4o'
) -> Dict[str, Any]:
    """
    Analyze a real IHK exam PDF using AI to extract structured questions.

    Args:
        exam_id: UUID of the exam record
        provider: AI provider name (not hardcoded, passed by caller)
        model: AI model ID (not hardcoded, passed by caller)

    Returns:
        Result dict with status and extracted question count
    """
    logger.info("Starting exam analysis for exam %s", exam_id)

    try:
        # 1. Load exam record
        exam = ExamRepository.find_by_id(exam_id)
        if not exam:
            logger.error("Exam %s not found", exam_id)
            return {'success': False, 'error': 'Exam not found'}

        raw_text = exam.get('raw_text')
        if not raw_text:
            logger.error("Exam %s has no raw_text", exam_id)
            _mark_failed(exam_id, 'No raw_text available')
            return {'success': False, 'error': 'No raw_text available'}

        # 2. Get solution text from settings JSONB
        settings = exam.get('settings') or {}
        if isinstance(settings, str):
            settings = json.loads(settings)
        solution_text = settings.get('solution_text', '')

        # 3. Mark as analyzing
        ExamRepository.update_analysis_status(exam_id, 'analyzing')

        # 4. Build prompt and call AI
        exam_type = exam.get('exam_type_key') or 'unknown'
        solution_section = ''
        if solution_text:
            solution_section = (
                f"## Lösungstext (zur Zuordnung):\n{solution_text[:8000]}"
            )

        prompt = _build_analysis_prompt(
            exam_type=exam_type,
            exam_text=raw_text[:12000],
            solution_section=solution_section,
        )

        adapter = AIAdapter(provider=provider, model=model)
        response = adapter.send_request(
            prompt=prompt,
            language='de',
            temperature=0.3,
            max_tokens=8000,
        )

        output_text = response.get('output_text', '')
        tokens_used = response.get('total_tokens', 0)

        # 5. Parse JSON from AI response
        parsed = _parse_ai_json(output_text)
        if not parsed:
            _mark_failed(exam_id, 'Failed to parse AI response as JSON')
            return {'success': False, 'error': 'JSON parse failed'}

        scenarios = parsed.get('scenarios', [])
        questions = parsed.get('questions', [])

        if not questions:
            _mark_failed(exam_id, 'AI returned no questions')
            return {'success': False, 'error': 'No questions extracted'}

        # 6. Build scenario lookup for titles
        scenario_map = {
            s['number']: s for s in scenarios
        }

        # 7. Insert questions via bulk_create
        question_records = _build_question_records(
            exam_id, questions, scenario_map
        )
        success = ExamQuestionRepository.bulk_create_questions(
            question_records
        )

        if not success:
            _mark_failed(exam_id, 'Failed to insert questions into DB')
            return {'success': False, 'error': 'DB insert failed'}

        # 8. Register new topics discovered by AI analysis
        all_topics = []
        for q in questions:
            all_topics.extend(q.get('topics') or [])
        if all_topics:
            _register_new_topics(exam_type, all_topics)

        # 9. Mark as ready
        ExamRepository.update_analysis_status(exam_id, 'ready')

        logger.info(
            "Exam analysis completed for %s: %d questions, %d tokens",
            exam_id, len(question_records), tokens_used,
        )

        return {
            'success': True,
            'exam_id': exam_id,
            'questions_count': len(question_records),
            'scenarios_count': len(scenarios),
            'tokens_used': tokens_used,
        }

    except AIProviderError as e:
        logger.error("AI provider error for exam %s: %s", exam_id, e)
        _mark_failed(exam_id, f'AI error: {e}')
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        return {'success': False, 'error': str(e)}

    except Exception as e:
        logger.exception("Exam analysis failed for %s: %s", exam_id, e)
        _mark_failed(exam_id, str(e))
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        return {'success': False, 'error': str(e)}


def _parse_ai_json(response_text: str) -> Optional[Dict]:
    """Extract JSON from AI response, handling ```json blocks."""
    # Try ```json block first
    if '```json' in response_text:
        start = response_text.find('```json') + 7
        end = response_text.find('```', start)
        if end > start:
            try:
                return json.loads(response_text[start:end].strip())
            except json.JSONDecodeError:
                pass

    # Try whole response as JSON
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Try finding JSON object boundaries
    start = response_text.find('{')
    end = response_text.rfind('}') + 1
    if start >= 0 and end > start:
        try:
            return json.loads(response_text[start:end])
        except json.JSONDecodeError:
            pass

    logger.error("Could not parse AI response as JSON")
    return None


def _build_question_records(
    exam_id: str,
    questions: List[Dict],
    scenario_map: Dict[int, Dict],
) -> List[Dict[str, Any]]:
    """
    Transform AI-extracted questions into DB-ready records.

    Args:
        exam_id: The parent exam UUID
        questions: Parsed question list from AI
        scenario_map: Mapping of scenario number to scenario data

    Returns:
        List of dicts ready for bulk_create_questions
    """
    records = []
    for idx, q in enumerate(questions):
        scenario_num = q.get('scenario_number')
        scenario = scenario_map.get(scenario_num, {})

        renderer_data = q.get('renderer_data', {})
        if isinstance(renderer_data, str):
            try:
                renderer_data = json.loads(renderer_data)
            except json.JSONDecodeError:
                renderer_data = {}

        record = {
            'exam_id': exam_id,
            'question_type': q.get('question_type', 'essay'),
            'question_text': q.get('text', ''),
            'points': q.get('points', 5),
            'order_index': idx + 1,
            'data': renderer_data,
            'scenario_title': scenario.get('title', ''),
            'scenario_text': scenario.get('context', ''),
            'question_number': q.get('question_number', str(idx + 1)),
            'topics': [normalize_topic(t) for t in (q.get('topics') or [])],
            'solution_text': q.get('solution_text', ''),
        }
        records.append(record)

    return records


def _mark_failed(exam_id: str, error_message: str) -> None:
    """Mark exam analysis as failed."""
    logger.error("Marking exam %s as failed: %s", exam_id, error_message)
    try:
        ExamRepository.update_analysis_status(exam_id, 'failed')
    except Exception as e:
        logger.error(
            "Could not update status for exam %s: %s", exam_id, e
        )
