"""
Tutor API - Backend endpoints for the 3D AI Tutor Companion

Provides chat and TTS functionality for the global tutor companion.
"""

from flask import request, jsonify, Response
from . import api_v1
from app.middleware.auth import token_required
from app.services.ai_adapter import AIAdapter
from flask_jwt_extended import get_jwt_identity
import os
import logging

logger = logging.getLogger(__name__)

# Available TTS voices (OpenAI)
TTS_VOICES = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']

# Default system prompt for the tutor
DEFAULT_TUTOR_PROMPT = """Du bist ein freundlicher und hilfreicher KI-Tutor auf LernsystemX.
Du begleitest Lernende durch ihre Lernreise und hilfst bei Fragen zu Kursen und Lernmethoden.
Du bist geduldig, ermutigend und erklärst Konzepte klar und verständlich.
Antworte immer auf Deutsch, es sei denn der User spricht eine andere Sprache.
Halte deine Antworten prägnant aber hilfreich - idealerweise 2-4 Sätze."""


@api_v1.route('/tutor/chat', methods=['POST'])
@token_required
def tutor_chat():
    """
    Chat with the AI Tutor.

    Request Body:
    {
        "message": "Wie funktioniert das Lernsystem?",
        "context": "Der User ist auf der Dashboard-Seite.",
        "systemPrompt": "Du bist ein freundlicher Tutor...",
        "history": [
            {"role": "user", "content": "Hallo"},
            {"role": "assistant", "content": "Hallo! Wie kann ich helfen?"}
        ]
    }

    Response:
    {
        "success": true,
        "data": {
            "message": "Das Lernsystem bietet dir 33 verschiedene Lernmethoden...",
            "tokens_used": 150
        }
    }
    """
    try:
        user_id = get_jwt_identity()
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
        context = data.get('context', '')
        custom_system_prompt = data.get('systemPrompt', DEFAULT_TUTOR_PROMPT)
        history = data.get('history', [])

        # Build the full system prompt with context
        system_prompt = custom_system_prompt
        if context:
            system_prompt += f"\n\nAktueller Kontext: {context}"

        # Build messages for the AI
        messages = []

        # Add history (limit to last 10 messages)
        for msg in history[-10:]:
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
            max_tokens=500,
            temperature=0.7,
            user_id=user_id
        )

        return jsonify({
            'success': True,
            'data': {
                'message': response.get('content', ''),
                'tokens_used': response.get('usage', {}).get('total_tokens', 0)
            }
        })

    except Exception as e:
        logger.error(f"Tutor chat error: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'CHAT_ERROR',
                'message': str(e)
            }
        }), 500


@api_v1.route('/tutor/tts', methods=['POST'])
@token_required
def tutor_tts():
    """
    Generate TTS audio for text using OpenAI TTS.

    Request Body:
    {
        "text": "Hallo, ich bin dein Tutor!",
        "voice": "alloy"  // alloy, echo, fable, onyx, nova, shimmer
    }

    Response: audio/mpeg binary data
    """
    try:
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

        # Validate voice
        if voice not in TTS_VOICES:
            voice = 'alloy'

        # Limit text length
        if len(text) > 4096:
            text = text[:4096]

        # Generate TTS using OpenAI
        audio_data = AIAdapter.text_to_speech(
            text=text,
            voice=voice,
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

    except Exception as e:
        logger.error(f"Tutor TTS error: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'TTS_ERROR',
                'message': str(e)
            }
        }), 500


@api_v1.route('/tutor/voices', methods=['GET'])
@token_required
def get_tts_voices():
    """
    Get available TTS voices.

    Response:
    {
        "success": true,
        "data": {
            "voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        }
    }
    """
    return jsonify({
        'success': True,
        'data': {
            'voices': TTS_VOICES
        }
    })
