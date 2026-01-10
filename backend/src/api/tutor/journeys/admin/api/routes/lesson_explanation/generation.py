"""
Lesson Explanation Generation Endpoints (DDD)

Generates AI-powered explanations for lessons.
"""

from flask import request, jsonify, g
from typing import Dict, Any, Tuple
import logging
import uuid
from datetime import datetime

from app.extensions import limiter
from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.services.ai_adapter import AIAdapter

from app.api.system_features.tutor.core import (
    TutorGenerationFactory,
    GenerationStyle,
    TutorStyleService
)
from app.api.system_features.tutor.core.events import (
    LessonExplanationGeneratedEvent,
    EventPublisher,
    EventPriority
)

from . import tutor_lesson_explanation_bp

logger = logging.getLogger(__name__)


@tutor_lesson_explanation_bp.route('/generate-lesson-steps', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("10 per minute")
def generate_lesson_steps() -> Tuple[Dict[str, Any], int]:
    """
    Generate step-by-step lesson explanation.

    DDD: Uses TutorGenerationFactory
    """
    return _generate_lesson_explanation('steps')


@tutor_lesson_explanation_bp.route('/generate-lesson-detailed', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("10 per minute")
def generate_lesson_detailed() -> Tuple[Dict[str, Any], int]:
    """
    Generate detailed lesson explanation.

    DDD: Uses TutorGenerationFactory
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

        # DDD: Use Factory
        gen_request = TutorGenerationFactory.create_lesson_explanation_request(
            lesson_id=lesson_id,
            lesson_title=data.get('lesson_title', ''),
            chapter_title=data.get('chapter_title', ''),
            course_title=data.get('course_title', ''),
            style=style,
            user_id=user_id,
            explanation_type=explanation_type,
            generate_tts=data.get('generate_tts', False),
            tts_voice=data.get('tts_voice', 'alloy')
        )

        # Get style config
        style_config = TutorStyleService.get_style_instructions(style)

        # Build prompt
        system_prompt = f"""Du bist ein KI-Tutor. Erstelle eine {explanation_type}-Erklärung im {style.display_name}-Stil.

Formatiere als JSON:
{{
    "title": "Titel",
    "steps": [...] // für steps
    oder
    "content": "..." // für detailed
}}"""

        user_prompt = f"""Erkläre die Lektion: {gen_request['lesson_title']}
Kapitel: {gen_request['chapter_title']}
Kurs: {gen_request['course_title']}"""

        # Call AI
        result = AIAdapter.chat_completion(
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            model='gpt-4o-mini',
            temperature=style_config['temperature'],
            max_tokens=style_config['max_tokens'],
            user_id=user_id
        )

        # Parse response
        import json
        try:
            explanation_data = json.loads(result.get('content', '{}'))
        except:
            explanation_data = {'title': gen_request['lesson_title'], 'content': result.get('content', '')}

        # Publish Event
        event = LessonExplanationGeneratedEvent(
            event_id=str(uuid.uuid4()),
            occurred_at=datetime.utcnow(),
            aggregate_id=str(lesson_id),
            lesson_id=lesson_id,
            explanation_type=explanation_type,
            style=style.value,
            tokens_used=result.get('usage', {}).get('total_tokens', 0),
            has_tts=gen_request['generate_tts'],
            user_id=user_id,
            priority=EventPriority.MEDIUM
        )
        EventPublisher.publish(event)

        return jsonify({
            'success': True,
            'data': explanation_data,
            'style': style.value,
            'tokens_used': result.get('usage', {}).get('total_tokens', 0)
        }), 200

    except Exception as e:
        logger.error(f"Error generating lesson explanation: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
