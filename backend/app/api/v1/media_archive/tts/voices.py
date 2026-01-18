"""
TTS Voices Endpoint.

Endpoint for listing available TTS voices and models.
"""

import logging

from flask import Blueprint, jsonify

from .config import (
    AVAILABLE_VOICES, DEFAULT_TUTOR_VOICE, DEFAULT_PROVIDER, DEFAULT_MODEL
)

logger = logging.getLogger(__name__)

# Blueprint for voice management
tts_voices_bp = Blueprint('tts_voices', __name__, url_prefix='/tts')


@tts_voices_bp.route('/voices', methods=['GET'])
def get_available_voices():
    """
    Get list of available TTS voices and models from database.

    Response:
    {
        "success": true,
        "data": {
            "voices": {...},
            "models": [...],
            "default": "nova",
            "recommended": [...]
        }
    }
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
        from app.infrastructure.persistence.repositories.ai_models import AIModelsRepository
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
