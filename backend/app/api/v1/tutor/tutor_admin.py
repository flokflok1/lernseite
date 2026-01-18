"""
LernsystemX Tutor Admin API - Content Generation Endpoints

Admin endpoints for AI-powered content generation:
- POST /admin-panel/tutor/generate-chapter-theory - Generate chapter theory sheet
- POST /admin-panel/tutor/generate-lesson-steps - Generate step-by-step lesson
- POST /admin-panel/tutor/generate-lesson-detailed - Generate detailed lesson explanation

ISO 9001:2015 compliant - AI Tutor Admin Layer
"""

from flask import Blueprint, request, jsonify, g
from typing import Dict, Any, Tuple
import logging
import time

from app.extensions import limiter
from app.api.middleware.auth import token_required
from app.infrastructure.security.permissions import require_permission, Permissions
from app.services.ai_adapter import AIAdapter
from app.infrastructure.persistence.repositories.courses.chapters import ChapterRepository
from app.infrastructure.persistence.repositories.courses.lessons import LessonRepository
from app.api.v1.tutor.tutor_core import (
    GenerationStyle,
    build_context_for_generation,
    parse_json_response,
    get_style_config,
    save_chapter_theory
)

logger = logging.getLogger(__name__)

# Blueprint
tutor_admin_bp = Blueprint('tutor_admin', __name__, url_prefix='/admin-panel/tutor')

__all__ = ['tutor_admin_bp']


@tutor_admin_bp.route('/generate-chapter-theory', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("10 per minute")
def generate_chapter_theory() -> Tuple[Dict[str, Any], int]:
    """
    Generate comprehensive theory sheet for a chapter using AI.

    Request Body:
        chapter_id (str): Chapter UUID
        chapter_title (str): Chapter title
        course_title (str): Course title
        style (str): Generation style (adhs, detailed, short, exam_focus)
        generate_tts (bool): Generate audio version (optional)
        tts_voice (str): TTS voice ID (optional)

    Response:
        200: Theory data with title, sections, summary, key points
        400: Invalid request
        500: Server error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Request body required'}), 400

        # Validate required fields
        chapter_id = data.get('chapter_id')
        chapter_title = data.get('chapter_title', '')
        course_title = data.get('course_title', '')

        if not chapter_id or not chapter_title:
            return jsonify({
                'success': False,
                'error': 'chapter_id and chapter_title are required'
            }), 400

        # Parse style
        try:
            style = GenerationStyle.from_string(data.get('style', 'adhs'))
        except ValueError as ve:
            return jsonify({'success': False, 'error': str(ve)}), 400

        user_id = g.current_user['user_id']
        start_time = time.time()

        # Get chapter context
        chapter = ChapterRepository.find_by_id(chapter_id)
        chapter_description = chapter.get('description', '') if chapter else ''

        # Get lesson titles for context
        lessons = LessonRepository.find_by_chapter(chapter_id)
        lesson_titles = [l.get('title', '') for l in lessons[:10]]

        # Build context
        context = build_context_for_generation(
            course_title=course_title,
            chapter_title=chapter_title,
            chapter_description=chapter_description,
            lesson_titles=lesson_titles
        )

        # Get style configuration
        style_config = get_style_config(style)

        # Build AI prompt
        instructions = '\n'.join(f'- {instr}' for instr in style_config['instructions'])

        system_prompt = f"""Du bist ein KI-Tutor für Fachinformatiker Systemintegration (FISI).
Erstelle ein umfassendes Theorie-Sheet im {style.display_name}-Stil.

Formatierungs-Anforderungen:
{instructions}

Ausgabe-Format (JSON):
{{
    "title": "Titel des Theorie-Sheets",
    "introduction": "Kurze Einführung (2-3 Sätze)",
    "sections": [
        {{
            "title": "Abschnittstitel",
            "content": "Inhalt des Abschnitts",
            "subsections": []
        }}
    ],
    "summary": "Zusammenfassung der wichtigsten Punkte",
    "key_points": ["Punkt 1", "Punkt 2", ...]
}}"""

        user_prompt = f"""Erstelle ein Theorie-Sheet für:

Kurs: {context['course_title']}
Kapitel: {context['chapter_title']}
Beschreibung: {context['chapter_description']}
Lektionen im Kapitel: {context['lesson_titles']}

Zielgruppe: {context['target_audience']}"""

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]

        # Call AI
        result = AIAdapter.chat_completion(
            messages=messages,
            model='gpt-4o-mini',
            temperature=style_config['temperature'],
            max_tokens=style_config['max_tokens'],
            user_id=user_id
        )

        # Parse response
        output_text = result.get('content', '{}')
        theory_data = parse_json_response(output_text, chapter_title)

        response_time_ms = int((time.time() - start_time) * 1000)

        # Save to database
        save_chapter_theory(
            chapter_id=chapter_id,
            style=style.value,
            theory_data=theory_data,
            tokens_used=result.get('usage', {}).get('total_tokens', 0),
            user_id=user_id
        )

        return jsonify({
            'success': True,
            'data': theory_data,
            'style': style.value,
            'tokens_used': result.get('usage', {}).get('total_tokens', 0),
            'response_time_ms': response_time_ms
        }), 200

    except Exception as e:
        logger.error(f"Error generating chapter theory: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate chapter theory',
            'message': str(e)
        }), 500


@tutor_admin_bp.route('/generate-lesson-steps', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("10 per minute")
def generate_lesson_steps() -> Tuple[Dict[str, Any], int]:
    """
    Generate step-by-step lesson explanation.

    Request Body:
        lesson_id (str): Lesson ID
        lesson_title (str): Lesson title
        chapter_title (str): Chapter title (optional)
        course_title (str): Course title (optional)
        style (str): Generation style (adhs, detailed, short, exam_focus)

    Response:
        200: Lesson explanation with steps
        400: Invalid request
        500: Server error
    """
    return _generate_lesson_explanation('steps')


@tutor_admin_bp.route('/generate-lesson-detailed', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("10 per minute")
def generate_lesson_detailed() -> Tuple[Dict[str, Any], int]:
    """
    Generate detailed lesson explanation.

    Request Body:
        lesson_id (str): Lesson ID
        lesson_title (str): Lesson title
        chapter_title (str): Chapter title (optional)
        course_title (str): Course title (optional)
        style (str): Generation style (adhs, detailed, short, exam_focus)

    Response:
        200: Detailed lesson explanation
        400: Invalid request
        500: Server error
    """
    return _generate_lesson_explanation('detailed')


def _generate_lesson_explanation(explanation_type: str) -> Tuple[Dict[str, Any], int]:
    """Generate lesson explanation (steps or detailed)."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Request body required'}), 400

        lesson_id = data.get('lesson_id')
        if not lesson_id:
            return jsonify({'success': False, 'error': 'lesson_id required'}), 400

        # Parse style
        try:
            style = GenerationStyle.from_string(data.get('style', 'adhs'))
        except ValueError as ve:
            return jsonify({'success': False, 'error': str(ve)}), 400

        user_id = g.current_user['user_id']

        # Get style config
        style_config = get_style_config(style)

        # Build prompt
        instructions = '\n'.join(f'- {instr}' for instr in style_config['instructions'])

        if explanation_type == 'steps':
            format_description = """{
    "title": "Titel",
    "steps": [
        {
            "step_number": 1,
            "title": "Schritt-Titel",
            "content": "Beschreibung",
            "tips": ["Tipp 1", "Tipp 2"]
        }
    ]
}"""
        else:  # detailed
            format_description = """{
    "title": "Titel",
    "introduction": "Einführung",
    "main_content": "Hauptinhalt",
    "examples": ["Beispiel 1", "Beispiel 2"],
    "summary": "Zusammenfassung"
}"""

        system_prompt = f"""Du bist ein KI-Tutor. Erstelle eine {explanation_type}-Erklärung im {style.display_name}-Stil.

Formatierungs-Anforderungen:
{instructions}

Formatiere als JSON:
{format_description}"""

        user_prompt = f"""Erstelle eine {explanation_type}-Erklärung für:

Kurs: {data.get('course_title', 'Unbekannt')}
Kapitel: {data.get('chapter_title', 'Unbekannt')}
Lektion: {data.get('lesson_title', 'Unbekannt')}

Zielgruppe: Fachinformatiker Systemintegration (FISI)"""

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]

        # Call AI
        result = AIAdapter.chat_completion(
            messages=messages,
            model='gpt-4o-mini',
            temperature=style_config['temperature'],
            max_tokens=style_config['max_tokens'],
            user_id=user_id
        )

        # Parse response
        output_text = result.get('content', '{}')
        explanation_data = parse_json_response(output_text, data.get('lesson_title', 'Lektion'))

        return jsonify({
            'success': True,
            'data': explanation_data,
            'style': style.value,
            'explanation_type': explanation_type,
            'tokens_used': result.get('usage', {}).get('total_tokens', 0)
        }), 200

    except Exception as e:
        logger.error(f"Error generating lesson explanation: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate lesson explanation',
            'message': str(e)
        }), 500
