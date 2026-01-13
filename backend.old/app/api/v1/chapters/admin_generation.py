"""
LernsystemX Chapter Theory Generation (Admin)

KI-powered theory generation endpoint and main logic.
Supports multiple styles: adhs, detailed, short, exam_focus, standard.

Endpoints:
- POST /api/v1/chapters/:chapter_id/theory/generate - Generate theory via KI

Functions:
- generate_theory_content: Call OpenAI to generate theory
- parse_json_response: Parse AI response with fallback
- get_theory_prompts: Get style-specific prompts (from templates)

DDD Refactored: 2026-01-08 - Moved from generation/core.py
Admin-only operation (requires KI access and token budget)
"""

from flask import Blueprint, request, jsonify, g
import json
import logging
import time

from app.extensions import limiter
from app.middleware.auth import token_required

from .repository import (
    get_chapter_theory,
    get_chapter_info,
    get_chapter_lessons,
    save_chapter_theory,
)
from .admin_media import generate_theory_audio
from .admin_templates import get_theory_prompts

logger = logging.getLogger(__name__)

# Blueprint for generation endpoints
chapter_theory_gen_bp = Blueprint(
    'chapter_theory_gen',
    __name__,
    url_prefix=''
)


@chapter_theory_gen_bp.route('/chapters/<chapter_id>/theory/generate', methods=['POST'])
@token_required
@limiter.limit("5 per minute")
def generate_theory(chapter_id: str):
    """
    Generate chapter theory via KI.

    Only generates if theory doesn't exist yet (to save tokens).
    Use force=true to regenerate.

    Request Body:
        {
            "style": "adhs",
            "generateTts": true,
            "ttsVoice": "nova",
            "force": false
        }

    Response 200:
        {
            "success": true,
            "data": {...},
            "tokensUsed": 1234,
            "cached": false
        }
    """
    try:
        data = request.get_json() or {}
        style = data.get('style', 'adhs')
        generate_tts = data.get('generateTts', True)
        tts_voice = data.get('ttsVoice', 'nova')
        force = data.get('force', False)

        user_id = g.current_user['user_id']

        # Check if theory already exists
        existing = get_chapter_theory(chapter_id, style)
        if existing and not force:
            # Return cached version
            theory_data = existing.get('theory_data', {})
            if isinstance(theory_data, str):
                theory_data = json.loads(theory_data)

            return jsonify({
                'success': True,
                'data': theory_data,
                'audioUrl': existing.get('audio_url'),
                'style': style,
                'tokensUsed': 0,
                'cached': True,
                'message': 'Theory already exists. Use force=true to regenerate.'
            }), 200

        # Get chapter info for context
        chapter = get_chapter_info(chapter_id)
        if not chapter:
            return jsonify({
                'success': False,
                'error': 'Chapter not found'
            }), 404

        lessons = get_chapter_lessons(chapter_id)
        lesson_titles = [l.get('title', '') for l in lessons]

        # Build context
        context = {
            'chapter_title': chapter.get('title', ''),
            'course_title': chapter.get('course_title', ''),
            'chapter_description': chapter.get('description', ''),
            'lesson_titles': ', '.join(lesson_titles) if lesson_titles else 'Keine Lektionen',
            'target_audience': 'Fachinformatiker Systemintegration (FISI) in Pruefungsvorbereitung'
        }

        start_time = time.time()

        # Generate theory via KI
        theory_data, tokens_used, model = generate_theory_content(style, context)

        # Generate TTS if requested
        audio_url = None
        audio_duration = None
        if generate_tts and theory_data:
            audio_result = generate_theory_audio(theory_data, tts_voice, chapter_id, user_id)
            if audio_result and 'url' in audio_result:
                audio_url = audio_result.get('url')
                audio_duration = audio_result.get('duration_seconds')

        # Save to database
        save_chapter_theory(
            chapter_id=chapter_id,
            style=style,
            theory_data=theory_data,
            audio_url=audio_url,
            audio_duration=audio_duration,
            tokens_used=tokens_used,
            model_used=model,
            user_id=user_id
        )

        response_time = int((time.time() - start_time) * 1000)

        logger.info(f"Generated chapter theory ({style}) for {chapter_id}, tokens: {tokens_used}")

        return jsonify({
            'success': True,
            'data': theory_data,
            'audioUrl': audio_url,
            'style': style,
            'tokensUsed': tokens_used,
            'responseTimeMs': response_time,
            'cached': False
        }), 200

    except Exception as e:
        logger.error(f"Error generating chapter theory: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to generate chapter theory',
            'message': str(e)
        }), 500


def generate_theory_content(style: str, context: dict) -> tuple[dict, int, str]:
    """Generate theory content via OpenAI.

    Args:
        style: Theory style (adhs, detailed, short, exam_focus, standard)
        context: Dict with chapter_title, course_title, etc.

    Returns:
        Tuple of (theory_data dict, tokens_used int, model str)
    """
    from app.services.ai_adapter import AIAdapter

    system_prompt, user_prompt = get_theory_prompts(style, context)

    adapter = AIAdapter(provider='openai', model='gpt-4o-mini')

    result = adapter.send_messages(
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        temperature=0.7,
        max_tokens=4000
    )

    output_text = result.get('output_text', '{}')
    tokens_used = result.get('total_tokens', 0)
    model = 'gpt-4o-mini'

    # Parse JSON response
    theory_data = parse_json_response(output_text, context.get('chapter_title', ''))

    return theory_data, tokens_used, model


def parse_json_response(output_text: str, chapter_title: str) -> dict:
    """Parse JSON response from AI, with fallback.

    Args:
        output_text: Raw AI response
        chapter_title: Chapter title for fallback content

    Returns:
        Parsed theory data dict
    """
    try:
        # Clean up potential markdown code blocks
        if output_text.startswith('```'):
            output_text = output_text.split('```')[1]
            if output_text.startswith('json'):
                output_text = output_text[4:]

        return json.loads(output_text.strip())
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        return {
            'overview': f'Uebersicht fuer {chapter_title}',
            'learningGoals': ['Die Grundlagen verstehen', 'Anwendung in der Praxis'],
            'concepts': [{'title': chapter_title, 'description': 'Kerninhalt des Kapitels'}],
            'terms': [],
            'examRelevance': 'Pruefungsrelevant fuer IHK AP1'
        }
