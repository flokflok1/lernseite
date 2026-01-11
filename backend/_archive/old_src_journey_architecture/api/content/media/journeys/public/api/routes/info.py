"""
Media Domain - Info Routes (Public Journey)

Public information endpoints for media capabilities.

Endpoints:
- GET /audio/supported-formats - List supported audio formats
- GET /tts/voices - List available TTS voices and models

Architecture: Journey-Based DDD (Public)
Database: PostgreSQL via AIModelsRepository (direct SQL)
ISO 27001:2013 compliant - Media information
"""

import logging
from flask import Blueprint, jsonify

from app.repositories.ai_models import AIModelsRepository

logger = logging.getLogger(__name__)


# Constants from config
ALLOWED_AUDIO_FORMATS = {'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm', 'ogg', 'flac'}
MAX_AUDIO_SIZE = 25 * 1024 * 1024  # 25MB - OpenAI Whisper limit

# TTS Configuration (from app/api/shared/media/tts/config.py)
AVAILABLE_VOICES = {
    'openai': {
        'alloy': {'name': 'Alloy', 'gender': 'neutral', 'style': 'balanced'},
        'echo': {'name': 'Echo', 'gender': 'male', 'style': 'confident'},
        'fable': {'name': 'Fable', 'gender': 'neutral', 'style': 'expressive'},
        'onyx': {'name': 'Onyx', 'gender': 'male', 'style': 'deep'},
        'nova': {'name': 'Nova', 'gender': 'female', 'style': 'natural'},
        'shimmer': {'name': 'Shimmer', 'gender': 'female', 'style': 'soft'},
    }
}
DEFAULT_TUTOR_VOICE = 'nova'
DEFAULT_PROVIDER = 'openai'
DEFAULT_MODEL = 'tts-1'


# Blueprint for public media info endpoints
media_info_bp = Blueprint('media_info', __name__)


@media_info_bp.route('/audio/supported-formats', methods=['GET'])
def get_supported_audio_formats():
    """
    Get list of supported audio formats for STT (Speech-to-Text)

    Response:
        200: List of supported formats
        {
            "success": true,
            "data": {
                "formats": ["mp3", "mp4", "wav", "webm", ...],
                "max_size_mb": 25
            }
        }

    Notes:
        - Maximum file size: 25 MB (OpenAI Whisper limit)
        - Formats: mp3, mp4, mpeg, mpga, m4a, wav, webm, ogg, flac
    """
    return jsonify({
        'success': True,
        'data': {
            'formats': sorted(list(ALLOWED_AUDIO_FORMATS)),
            'max_size_mb': MAX_AUDIO_SIZE // (1024 * 1024)
        }
    })


@media_info_bp.route('/tts/voices', methods=['GET'])
def get_available_voices():
    """
    Get list of available TTS voices and models from database

    Response:
        200: List of voices and models
        {
            "success": true,
            "data": {
                "openai": {
                    "nova": {
                        "name": "Nova",
                        "gender": "female",
                        "style": "natural",
                        "provider": "openai",
                        "model": "tts-1",
                        "is_free": false
                    },
                    ...
                },
                "all_voices": {...},
                "models": [...],
                "tts_models": [...],
                "default": "nova",
                "default_provider": "openai",
                "default_model": "tts-1",
                "recommended": [...]
            }
        }

    Notes:
        - Loads audio models from database (ai_models table)
        - Filters by category='audio'
        - Returns TTS and transcription models
        - Includes pricing information
    """
    # Build OpenAI voice list
    openai_voices = {}
    for voice_key, info in AVAILABLE_VOICES['openai'].items():
        openai_voices[voice_key] = {
            'name': info['name'],
            'gender': info['gender'],
            'style': info['style'],
            'provider': 'openai',
            'model': info.get('model', 'tts-1'),
            'is_free': False
        }

    # Load audio models from database
    audio_models = []
    try:
        db_models = AIModelsRepository.get_models_by_category('audio')
        for model in db_models:
            audio_models.append({
                'model_id': model.get('model_id'),
                'model_name': model.get('model_name'),
                'display_name': model.get('display_name'),
                'provider': model.get('provider_name', 'openai'),
                'input_price': float(
                    model.get('input_price_per_1k') or model.get('cost_per_1k_input') or 0
                ),
                'output_price': float(
                    model.get('output_price_per_1k') or model.get('cost_per_1k_output') or 0
                ),
                'active': model.get('active', True),
                'is_tts': (
                    'tts' in model.get('model_name', '').lower() or
                    'audio' in model.get('model_name', '').lower()
                ),
                'is_transcription': (
                    'whisper' in model.get('model_name', '').lower() or
                    'transcribe' in model.get('model_name', '').lower()
                )
            })
    except Exception as e:
        logger.warning(f"Could not load audio models from DB: {e}")

    return jsonify({
        'success': True,
        'data': {
            'openai': openai_voices,
            'all_voices': openai_voices,
            'models': audio_models,
            'tts_models': [m for m in audio_models if m.get('is_tts')],
            'default': DEFAULT_TUTOR_VOICE,
            'default_provider': DEFAULT_PROVIDER,
            'default_model': DEFAULT_MODEL,
            'recommended': [
                {
                    'voice': 'nova',
                    'name': 'Nova (OpenAI)',
                    'description': 'Natuerliche weibliche Stimme',
                    'provider': 'openai',
                    'model': 'tts-1'
                },
                {
                    'voice': 'alloy',
                    'name': 'Alloy (OpenAI)',
                    'description': 'Ausgewogene neutrale Stimme',
                    'provider': 'openai',
                    'model': 'tts-1'
                },
                {
                    'voice': 'onyx',
                    'name': 'Onyx (OpenAI)',
                    'description': 'Tiefe maennliche Stimme',
                    'provider': 'openai',
                    'model': 'tts-1'
                },
            ]
        }
    })
