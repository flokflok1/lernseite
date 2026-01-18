"""
LernsystemX Exam Generation Celery Task

Background task for AI-powered exam simulation generation.
Uses ExamContextDetector to get context and AIAdapter to generate questions.
"""

import json
import logging
from typing import Dict, Any
from datetime import datetime

from app.core.bootstrap.extensions import celery
from app.infrastructure.persistence.database.connection import fetch_one, execute_query
from app.application.services.ai_adapter import AIAdapter, AIProviderError

logger = logging.getLogger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def generate_exam_task(self, simulation_id: str) -> Dict[str, Any]:
    """
    Generate exam simulation questions using AI.

    Args:
        simulation_id: UUID of the exam_simulation record

    Returns:
        Result dict with status and generated questions count
    """
    logger.info(f"Starting exam generation for simulation {simulation_id}")

    try:
        # 1. Load simulation data
        sim = fetch_one(
            """
            SELECT
                es.*,
                c.title as course_title,
                c.description as course_description
            FROM exam_simulations es
            JOIN courses c ON c.course_id = es.course_id
            WHERE es.simulation_id = %s
            """,
            (simulation_id,)
        )

        if not sim:
            logger.error(f"Simulation {simulation_id} not found")
            return {'success': False, 'error': 'Simulation not found'}

        context = sim['context_json'] or {}
        config = sim['config_json'] or {}

        # 2. Build prompt for AI
        prompt = _build_exam_prompt(context, config, sim['course_title'], sim['course_description'])

        # 3. Call AI to generate exam
        try:
            adapter = AIAdapter(provider='openai', model='gpt-4o')
            response = adapter.send_request(
                prompt=prompt,
                context=f"Kurs: {sim['course_title']}",
                language='de',
                temperature=0.7,
                max_tokens=8000
            )

            output_text = response['output_text']
            tokens_used = response['total_tokens']
            model_used = response['model']

        except AIProviderError as e:
            logger.error(f"AI provider error: {e}")
            _mark_simulation_failed(simulation_id, str(e))
            return {'success': False, 'error': str(e)}

        # 4. Parse AI response
        result_json = _parse_exam_response(output_text, context, config)

        if not result_json.get('questions'):
            _mark_simulation_failed(simulation_id, 'No questions generated')
            return {'success': False, 'error': 'No questions generated'}

        # 5. Update simulation with result
        execute_query(
            """
            UPDATE exam_simulations
            SET
                result_json = %s,
                status = 'ready',
                generation_completed_at = NOW(),
                tokens_used = %s,
                model_used = %s
            WHERE simulation_id = %s
            """,
            (json.dumps(result_json), tokens_used, model_used, simulation_id)
        )

        logger.info(f"Exam generation completed for {simulation_id}: {len(result_json['questions'])} questions")

        return {
            'success': True,
            'simulation_id': simulation_id,
            'questions_count': len(result_json['questions']),
            'total_points': result_json.get('total_points', 100)
        }

    except Exception as e:
        logger.exception(f"Exam generation failed for {simulation_id}: {e}")
        _mark_simulation_failed(simulation_id, str(e))

        # Retry on transient errors
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)

        return {'success': False, 'error': str(e)}


def _build_exam_prompt(context: Dict, config: Dict, course_title: str, course_description: str) -> str:
    """Build the AI prompt for exam generation."""

    profession = context.get('profession', 'Fachinformatiker')
    exam_level = context.get('exam_level', 'AP1')
    region = context.get('region', 'Deutschland')
    difficulty = config.get('difficulty', 'realistic')
    time_limit = config.get('time_limit_minutes', 90)
    focus_distribution = config.get('focus_distribution', {})
    weak_topics = context.get('weak_topics', [])
    strong_topics = context.get('strong_topics', [])

    # Build focus section
    focus_section = ""
    if focus_distribution:
        focus_items = [f"- {topic}: {percent}%" for topic, percent in focus_distribution.items()]
        focus_section = f"""
## Themenverteilung (Fokus auf Schwächen):
{chr(10).join(focus_items)}
"""

    # Build weakness section
    weakness_section = ""
    if weak_topics:
        weak_items = [f"- {t.get('topic', t)}: {t.get('score', 'unbekannt')}%" for t in weak_topics]
        weakness_section = f"""
## Schwache Themen (mehr Aufgaben hier):
{chr(10).join(weak_items)}
"""

    difficulty_desc = {
        'easy': 'einfach (für Anfänger, grundlegende Konzepte)',
        'realistic': 'realistisch (wie echte IHK-Prüfung)',
        'hard': 'schwer (herausfordernd, komplexe Szenarien)'
    }

    prompt = f"""Du bist ein Experte für IHK-Prüfungen und erstellst eine Prüfungssimulation.

## Kontext:
- Beruf: {profession}
- Prüfung: {exam_level}
- Region: {region}
- Kurs: {course_title}
- Schwierigkeit: {difficulty_desc.get(difficulty, 'realistisch')}
- Zeitlimit: {time_limit} Minuten
{focus_section}
{weakness_section}

## Aufgabe:
Erstelle eine vollständige Prüfungssimulation mit gemischten Fragetypen.
Die Prüfung soll 100 Punkte insgesamt haben.

## Fragetypen:
1. **mc** (Multiple Choice): 4 Optionen, eine richtig
2. **calculation** (Rechenaufgabe): Zahlenbasiert mit Lösungsweg
3. **scenario** (Szenario): Situationsbeschreibung mit Aufgaben
4. **free_text** (Freitext): Offene Erklärungsfragen

## Ausgabeformat (JSON):
```json
{{
  "summary": "Kurze Beschreibung der Prüfung",
  "topics_covered": ["Thema1", "Thema2"],
  "total_points": 100,
  "questions": [
    {{
      "question_id": "q1",
      "type": "mc",
      "topic": "Kalkulation",
      "difficulty": "realistic",
      "points": 5,
      "question": "Die vollständige Frage hier...",
      "options": ["A: Option 1", "B: Option 2", "C: Option 3", "D: Option 4"],
      "correct_answer": "B",
      "explanation": "Erklärung warum B richtig ist...",
      "ihk_reference": "z.B. AP1 Herbst 2023, Aufgabe 3"
    }},
    {{
      "question_id": "q2",
      "type": "calculation",
      "topic": "Bezugskalkulation",
      "difficulty": "realistic",
      "points": 10,
      "question": "Ein Händler kauft Ware ein...",
      "correct_answer": "523,25 EUR",
      "explanation": "Schritt 1: ... Schritt 2: ...",
      "ihk_reference": "IHK Standardaufgabe"
    }}
  ]
}}
```

## Wichtige Regeln:
1. Erstelle 10-15 Aufgaben mit insgesamt 100 Punkten
2. Variiere die Fragetypen (mind. 3 verschiedene)
3. Passe Schwierigkeit an: {difficulty}
4. Fokussiere auf schwache Themen
5. Alle Antworten müssen korrekt und nachvollziehbar sein
6. IHK-Stil beibehalten (formell, präzise)
7. Nur das JSON ausgeben, keine zusätzliche Erklärung

Erstelle jetzt die Prüfungssimulation als JSON:"""

    return prompt


def _parse_exam_response(response_text: str, context: Dict, config: Dict) -> Dict[str, Any]:
    """Parse the AI response and extract exam data."""

    # Try to extract JSON from response
    result = None

    # Look for JSON block
    if '```json' in response_text:
        start = response_text.find('```json') + 7
        end = response_text.find('```', start)
        json_str = response_text[start:end].strip()
        try:
            result = json.loads(json_str)
        except json.JSONDecodeError:
            pass

    # Try parsing whole response as JSON
    if not result:
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            pass

    # Try finding JSON object
    if not result:
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start >= 0 and end > start:
            try:
                result = json.loads(response_text[start:end])
            except json.JSONDecodeError:
                pass

    if not result:
        logger.error("Could not parse AI response as JSON")
        return {
            'summary': 'Prüfung konnte nicht generiert werden',
            'topics_covered': [],
            'total_points': 0,
            'questions': []
        }

    # Validate and clean up
    questions = result.get('questions', [])
    for i, q in enumerate(questions):
        if 'question_id' not in q:
            q['question_id'] = f'q{i+1}'
        if 'points' not in q:
            q['points'] = 5

    # Calculate total points
    total_points = sum(q.get('points', 5) for q in questions)

    return {
        'summary': result.get('summary', 'KI-generierte Prüfungssimulation'),
        'topics_covered': result.get('topics_covered', []),
        'total_points': total_points,
        'questions': questions
    }


def _mark_simulation_failed(simulation_id: str, error_message: str):
    """Mark simulation as failed in database."""
    execute_query(
        """
        UPDATE exam_simulations
        SET status = 'failed', error_message = %s, generation_completed_at = NOW()
        WHERE simulation_id = %s
        """,
        (error_message, simulation_id)
    )
