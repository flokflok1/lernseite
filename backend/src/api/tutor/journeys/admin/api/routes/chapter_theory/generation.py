"""
Chapter Theory Generation Endpoint (DDD)

Generates AI-powered theory sheets for chapters.
Uses TutorGenerationFactory for request creation.
"""

from flask import request, jsonify, g
from typing import Dict, Any, Tuple
import logging
import time
import uuid
from datetime import datetime

from app.extensions import limiter
from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.repositories.courses.chapters import ChapterRepository
from app.repositories.courses.lessons import LessonRepository
from app.services.ai_adapter import AIAdapter

# DDD Core Domain
from app.api.system_features.tutor.core import (
    TutorGenerationFactory,
    TutorKnowledgeService,
    TutorResponseService,
    TutorStyleService,
    GenerationStyle
)
from app.api.system_features.tutor.core.events import (
    ChapterTheoryGeneratedEvent,
    EventPublisher,
    EventPriority
)

from . import tutor_chapter_theory_bp

logger = logging.getLogger(__name__)


@tutor_chapter_theory_bp.route('/generate-chapter-theory', methods=['POST'])
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
        generate_tts (bool): Generate audio version
        tts_voice (str): TTS voice ID

    Returns:
        JSON response with theory data

    DDD: Uses TutorGenerationFactory, TutorKnowledgeService
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

        # DDD: Use Factory to create generation request
        gen_request = TutorGenerationFactory.create_chapter_theory_request(
            chapter_id=chapter_id,
            chapter_title=chapter_title,
            course_title=course_title,
            style=style,
            user_id=user_id,
            custom_title=data.get('title'),
            generate_tts=data.get('generate_tts', False),
            tts_voice=data.get('tts_voice', 'alloy')
        )

        # Build context using Service
        context = TutorKnowledgeService.build_context_for_generation(
            course_title=course_title,
            chapter_title=chapter_title,
            chapter_description=chapter_description,
            lesson_titles=lesson_titles
        )

        # Get style configuration
        style_config = TutorStyleService.get_style_instructions(style)

        # Build AI prompt
        system_prompt = _build_system_prompt(style, style_config)
        user_prompt = _build_user_prompt(context)

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
        theory_data = TutorResponseService.parse_json_response(output_text, chapter_title)

        response_time_ms = int((time.time() - start_time) * 1000)

        # Save to database
        _save_chapter_theory(
            chapter_id=chapter_id,
            style=style.value,
            theory_data=theory_data,
            tokens_used=result.get('usage', {}).get('total_tokens', 0),
            user_id=user_id
        )

        # DDD: Publish Domain Event
        event = ChapterTheoryGeneratedEvent(
            event_id=str(uuid.uuid4()),
            occurred_at=datetime.utcnow(),
            aggregate_id=chapter_id,
            chapter_id=chapter_id,
            style=style.value,
            tokens_used=result.get('usage', {}).get('total_tokens', 0),
            has_tts=gen_request['generate_tts'],
            user_id=user_id,
            priority=EventPriority.MEDIUM
        )
        EventPublisher.publish(event)

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


def _build_system_prompt(style: GenerationStyle, config: dict) -> str:
    """Build system prompt for theory generation."""
    instructions = '\n'.join(f'- {instr}' for instr in config['instructions'])

    return f"""Du bist ein KI-Tutor für Fachinformatiker Systemintegration (FISI).
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


def _build_user_prompt(context: dict) -> str:
    """Build user prompt with context."""
    return f"""Erstelle ein Theorie-Sheet für:

Kurs: {context['course_title']}
Kapitel: {context['chapter_title']}
Beschreibung: {context['chapter_description']}
Lektionen im Kapitel: {context['lesson_titles']}

Zielgruppe: {context['target_audience']}"""


def _save_chapter_theory(chapter_id: str, style: str, theory_data: dict, tokens_used: int, user_id: str):
    """Save theory to database."""
    try:
        from app.repositories.chapter_theory import ChapterTheoryRepository
        ChapterTheoryRepository.create({
            'chapter_id': chapter_id,
            'style': style,
            'theory_data': theory_data,
            'title': theory_data.get('title'),
            'tokens_used': tokens_used,
            'created_by': user_id
        })
    except Exception as e:
        logger.warning(f"Could not save chapter theory to DB: {e}")
