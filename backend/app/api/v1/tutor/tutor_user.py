"""
LernsystemX Tutor User API - Chat & TTS Endpoints

User-facing endpoints for tutor interaction:
- POST /tutor/chat - Chat with AI tutor
- POST /tutor/tts - Generate TTS audio
- GET /tutor/voices - Get available TTS voices

ISO 9001:2015 compliant - AI Tutor User Layer
"""

from flask import Blueprint, request, jsonify, Response, g
from typing import Dict, Any, Tuple
import logging

from app.extensions import limiter
from app.api.middleware.auth import token_required
from app.services.ai_adapter import AIAdapter
from app.api.v1.tutor.tutor_core import (
    TutorContext,
    AVAILABLE_VOICES,
    DEFAULT_TUTOR_PROMPT,
    create_chat_session,
    create_tts_request,
    build_context_for_chat
)
from app.services.tutor_knowledge import TutorKnowledgeService as BaseTutorKnowledgeService

logger = logging.getLogger(__name__)

# Blueprint
tutor_bp = Blueprint('tutor', __name__, url_prefix='/tutor')

__all__ = ['tutor_bp']


@tutor_bp.route('/chat', methods=['POST'])
@token_required
@limiter.limit("30 per minute")
def tutor_chat() -> Tuple[Dict[str, Any], int]:
    """
    Chat with the AI Tutor (context-aware).

    Request Body:
        message (str): User's message
        context (str): Page context (optional)
        systemPrompt (str): Custom system prompt (optional)
        history (list): Chat history (optional, max 10 messages)
        courseId (str): Current course ID (optional)
        chapterId (str): Current chapter ID (optional)
        lessonId (int): Current lesson ID (optional)
        methodId (str): Current learning method ID (optional)

    Response:
        200: Tutor response with message, tokens used, context status
        400: Invalid request
        500: Server error
    """
    try:
        user_id = g.current_user['user_id']
        data = request.get_json()

        if not data or not data.get('message'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Message is required'
                }
            }), 400

        message = data['message']
        page_context = data.get('context', '')
        custom_system_prompt = data.get('systemPrompt', DEFAULT_TUTOR_PROMPT)
        history = data.get('history', [])

        # Create TutorContext value object
        context = TutorContext(
            user_id=user_id,
            course_id=data.get('courseId'),
            chapter_id=data.get('chapterId'),
            lesson_id=data.get('lessonId'),
            method_id=data.get('methodId'),
            page_context=page_context
        )

        # Create session
        session = create_chat_session(
            user_id=user_id,
            message=message,
            context=context,
            history=history
        )

        # Build knowledge context
        knowledge_context = ''
        context_used = False

        if context.has_course_context():
            knowledge_context = build_context_for_chat(
                context=context,
                include_files=True,
                include_progress=True
            )
            if knowledge_context and knowledge_context != "Kein spezifischer Kurs-Kontext verfügbar.":
                context_used = True
                logger.debug(f"Loaded tutor context for course={context.course_id}, chapter={context.chapter_id}")

        # Build the full system prompt with context
        system_prompt = custom_system_prompt

        # Add page context (where user is in the app)
        if page_context:
            system_prompt += f"\n\nAktueller Seitenkontext: {page_context}"

        # Add knowledge context from DB (course/chapter/lesson content)
        if knowledge_context:
            system_prompt += f"\n\n{knowledge_context}"

        # Build messages for the AI
        messages = []

        # Add history (limit already applied by factory)
        for msg in session['history']:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })

        # Add current message
        messages.append({
            'role': 'user',
            'content': message
        })

        # Call AI
        response = AIAdapter.chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            model='gpt-4o-mini',  # Use fast model for chat
            max_tokens=800 if context_used else 500,  # More tokens when using context
            temperature=0.7,
            user_id=user_id
        )

        return jsonify({
            'success': True,
            'data': {
                'message': response.get('content', ''),
                'tokens_used': response.get('usage', {}).get('total_tokens', 0),
                'context_used': context_used,
                'session_id': session['session_id']
            }
        }), 200

    except Exception as e:
        logger.error(f"Tutor chat error: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'CHAT_ERROR',
                'message': str(e)
            }
        }), 500


@tutor_bp.route('/tts', methods=['POST'])
@token_required
@limiter.limit("20 per minute")
def tutor_tts() -> Response:
    """
    Generate TTS audio for text using OpenAI TTS.

    Request Body:
        text (str): Text to convert to speech
        voice (str): Voice ID (alloy, echo, fable, onyx, nova, shimmer)

    Response:
        200: audio/mpeg binary data
        400: Invalid request
        500: Server error
    """
    try:
        user_id = g.current_user['user_id']
        data = request.get_json()

        if not data or not data.get('text'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Text is required'
                }
            }), 400

        text = data['text']
        voice = data.get('voice', 'alloy')

        # Create TTS request (validates and sanitizes)
        tts_request = create_tts_request(
            user_id=user_id,
            text=text,
            voice=voice
        )

        # Generate TTS using OpenAI
        audio_data = AIAdapter.text_to_speech(
            text=tts_request['text'],
            voice=tts_request['voice'],
            model='tts-1'  # Use standard model (tts-1-hd for higher quality)
        )

        if not audio_data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'TTS_ERROR',
                    'message': 'Failed to generate audio'
                }
            }), 500

        return Response(
            audio_data,
            mimetype='audio/mpeg',
            headers={
                'Content-Disposition': 'inline',
                'Cache-Control': 'no-cache'
            }
        )

    except ValueError as ve:
        # Factory validation error
        logger.warning(f"TTS validation error: {ve}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(ve)
            }
        }), 400

    except Exception as e:
        logger.error(f"Tutor TTS error: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'TTS_ERROR',
                'message': str(e)
            }
        }), 500


@tutor_bp.route('/voices', methods=['GET'])
@token_required
def get_tts_voices() -> Tuple[Dict[str, Any], int]:
    """
    Get available TTS voices.

    Response:
        200: List of available voices
        500: Server error
    """
    try:
        return jsonify({
            'success': True,
            'data': {
                'voices': [voice.to_dict() for voice in AVAILABLE_VOICES]
            }
        }), 200

    except Exception as e:
        logger.error(f"Get voices error: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'VOICES_ERROR',
                'message': str(e)
            }
        }), 500
