"""
Media Domain - TTS Synthesis Routes (User Journey)

Text-to-Speech synthesis endpoints with caching.

Endpoints:
- POST /tts/speak - Generate TTS audio (cached)
- GET /tts/audio/<id> - Retrieve cached TTS audio
- POST /tts/speak-stream - Generate streaming TTS audio

Architecture: Journey-Based DDD (User)
Database: None (file-based caching)
ISO 27001:2013 compliant - TTS synthesis with secure file handling
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import get_jwt_identity
import os
import logging
import hashlib
from pathlib import Path

from app.middleware.auth import token_required
from app.services.ai_adapter import AIAdapter
from app.services.tts_service import TTSService

logger = logging.getLogger(__name__)

# TTS Configuration
DEFAULT_TUTOR_VOICE = 'nova'
DEFAULT_MODEL = 'tts-1'
MIN_SPEED = 0.5
MAX_SPEED = 2.0
MAX_TEXT_LENGTH = 4096

AVAILABLE_VOICES = {
    'alloy': {'name': 'Alloy'},
    'echo': {'name': 'Echo'},
    'fable': {'name': 'Fable'},
    'onyx': {'name': 'Onyx'},
    'nova': {'name': 'Nova'},
    'shimmer': {'name': 'Shimmer'},
}

tts_synthesis_bp = Blueprint('tts_synthesis', __name__, url_prefix='/tts')


@tts_synthesis_bp.route('/speak', methods=['POST'])
@token_required
def generate_tts():
    """
    Generate TTS audio with caching

    Request Body:
        {
            "text": "Text to synthesize",
            "voice": "nova",  // Optional (default: nova)
            "speed": 1.0,     // Optional 0.5-2.0 (default: 1.0)
            "language": "de", // Optional (default: de)
            "model": "tts-1"  // Optional (default: tts-1)
        }

    Response:
        200: Audio generated
        {
            "success": true,
            "data": {
                "audio_url": "/api/v1/tts/audio/abc123",
                "from_cache": false,
                "duration_ms": 3500,
                "text_length": 150,
                "provider": "openai"
            }
        }

        400: Invalid request
        500: TTS generation failed

    Notes:
        - Text preprocessed for better pronunciation
        - Results cached by hash(text + voice + speed)
        - Max text length: 4096 characters
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or not data.get('text'):
            return jsonify({'success': False, 'error': {'code': 'NO_TEXT', 'message': 'No text provided'}}), 400

        text = data['text'].strip()
        voice = data.get('voice', DEFAULT_TUTOR_VOICE)
        speed = float(data.get('speed', 1.0))
        language = data.get('language', 'de')
        model = data.get('model', DEFAULT_MODEL)

        # Validate speed
        if not MIN_SPEED <= speed <= MAX_SPEED:
            return jsonify({'success': False, 'error': {'code': 'INVALID_SPEED', 'message': f'Speed must be between {MIN_SPEED} and {MAX_SPEED}'}}), 400

        # Validate text length
        if len(text) > MAX_TEXT_LENGTH:
            return jsonify({'success': False, 'error': {'code': 'TEXT_TOO_LONG', 'message': f'Text too long. Maximum {MAX_TEXT_LENGTH} characters.'}}), 400

        # Preprocess text
        processed_text = TTSService.preprocess_text(text, language)

        # Generate cache key
        text_hash = hashlib.sha256(processed_text.encode()).hexdigest()[:16]
        audio_id = f"{text_hash}_{voice}_{int(speed*100)}"

        # Storage path
        backend_root = Path(__file__).parent.parent.parent.parent.parent.parent
        storage_dir = Path(os.getenv('MEDIA_CACHE_PATH', str(backend_root / 'storage' / 'media_cache'))) / 'tts' / text_hash[:2]
        storage_dir.mkdir(parents=True, exist_ok=True)
        file_path = storage_dir / f"{text_hash}_{voice}.mp3"

        # Check cache
        from_cache = file_path.exists()

        if not from_cache:
            # Generate with OpenAI TTS
            audio_bytes = AIAdapter.text_to_speech(text=processed_text, voice=voice, model=model, speed=speed)
            with open(file_path, 'wb') as f:
                f.write(audio_bytes)

        # Estimate duration
        duration_ms = int((len(processed_text) / 5 / 150) * 60 * 1000)

        return jsonify({
            'success': True,
            'data': {
                'audio_url': f'/api/v1/tts/audio/{audio_id}',
                'from_cache': from_cache,
                'duration_ms': duration_ms,
                'text_length': len(text),
                'voice': voice,
                'provider': 'openai'
            }
        })

    except Exception as e:
        logger.error(f"TTS generation error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': {'code': 'TTS_ERROR', 'message': str(e)}}), 500


@tts_synthesis_bp.route('/audio/<audio_id>', methods=['GET'])
@token_required
def get_tts_audio(audio_id: str):
    """
    Retrieve cached TTS audio

    Path Parameters:
        audio_id: Audio identifier from /speak response

    Response:
        200: Audio file (audio/mpeg)
        404: Audio not found

    Notes:
        - Serves cached MP3 files
        - Efficient file streaming
    """
    try:
        # Parse audio_id to get file path
        parts = audio_id.split('_')
        if len(parts) < 2:
            return jsonify({'success': False, 'error': 'Invalid audio ID'}), 400

        text_hash = parts[0]
        voice = parts[1] if len(parts) > 1 else DEFAULT_TUTOR_VOICE

        # Storage path
        backend_root = Path(__file__).parent.parent.parent.parent.parent.parent
        storage_dir = Path(os.getenv('MEDIA_CACHE_PATH', str(backend_root / 'storage' / 'media_cache'))) / 'tts' / text_hash[:2]
        file_path = storage_dir / f"{text_hash}_{voice}.mp3"

        if not file_path.exists():
            return jsonify({'success': False, 'error': 'Audio not found'}), 404

        return send_file(str(file_path), mimetype='audio/mpeg')

    except Exception as e:
        logger.error(f"TTS audio retrieval error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@tts_synthesis_bp.route('/speak-stream', methods=['POST'])
@token_required
def generate_tts_stream():
    """
    Generate streaming TTS audio (real-time)

    Request Body: Same as /speak

    Response:
        200: Audio stream (audio/mpeg)
        400: Invalid request
        500: TTS generation failed

    Notes:
        - Direct streaming without caching
        - Lower latency for real-time use
        - Same text preprocessing
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or not data.get('text'):
            return jsonify({'success': False, 'error': {'code': 'NO_TEXT'}}), 400

        text = data['text'].strip()
        voice = data.get('voice', DEFAULT_TUTOR_VOICE)
        speed = float(data.get('speed', 1.0))
        language = data.get('language', 'de')
        model = data.get('model', DEFAULT_MODEL)

        # Validate
        if not MIN_SPEED <= speed <= MAX_SPEED:
            return jsonify({'success': False, 'error': {'code': 'INVALID_SPEED'}}), 400

        if len(text) > MAX_TEXT_LENGTH:
            return jsonify({'success': False, 'error': {'code': 'TEXT_TOO_LONG'}}), 400

        # Preprocess and generate
        processed_text = TTSService.preprocess_text(text, language)
        audio_bytes = AIAdapter.text_to_speech(text=processed_text, voice=voice, model=model, speed=speed)

        # Return audio stream
        from io import BytesIO
        return send_file(BytesIO(audio_bytes), mimetype='audio/mpeg')

    except Exception as e:
        logger.error(f"TTS streaming error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
