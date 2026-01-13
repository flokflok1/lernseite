"""
Tutor User TTS Endpoints (DDD)

User-facing TTS endpoints for text-to-speech and voice selection.
Uses TutorSessionFactory and TTSVoice value objects.
"""

from flask import request, jsonify, Response, g
from typing import Dict, Any, Tuple
import logging

from app.extensions import limiter
from app.middleware.auth import token_required
from app.services.ai_adapter import AIAdapter

from app.api.v1.tutor.factory import TutorSessionFactory
from app.api.v1.tutor.value_objects import TTSVoice, AVAILABLE_VOICES

from .blueprints import tutor_user_tts_bp

logger = logging.getLogger(__name__)


@tutor_user_tts_bp.route('/tts', methods=['POST'])
@token_required
@limiter.limit("20 per minute")
def tutor_tts() -> Response:
    """
    Generate TTS audio for text using OpenAI TTS.

    Request Body:
        text (str): Text to convert to speech
        voice (str): Voice ID (alloy, echo, fable, onyx, nova, shimmer)

    Returns:
        audio/mpeg binary data

    DDD: Uses TutorSessionFactory for request validation
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

        # DDD: Use Factory to create TTS request (validates and sanitizes)
        tts_request = TutorSessionFactory.create_tts_request(
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


@tutor_user_tts_bp.route('/voices', methods=['GET'])
@token_required
def get_tts_voices() -> Tuple[Dict[str, Any], int]:
    """
    Get available TTS voices.

    Returns:
        JSON response with list of available voices

    DDD: Uses TTSVoice value objects
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
