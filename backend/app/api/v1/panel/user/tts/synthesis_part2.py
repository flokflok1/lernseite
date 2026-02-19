"""
LernsystemX TTS API - Voice Management & Script Generation

Continuation of synthesis.py (Quality Gate G01: max 500 lines per file).

Voice Management:
- GET /tts/voices - Get list of available TTS voices and models

Script Generation:
- POST /tts/tutor-script - Generate complete tutor script with audio for multiple steps

All routes: /api/v1/tts/*
ISO 27001:2013 compliant - TTS security and caching
"""

import os
import hashlib
import logging
from pathlib import Path

from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.api.middleware.auth import token_required
from app.api.v1.panel.user.tts.core import (
    AVAILABLE_VOICES,
    DEFAULT_TUTOR_VOICE,
    DEFAULT_PROVIDER,
    DEFAULT_MODEL,
    get_voice_info,
)

# Import the blueprint from the main module to register routes on it
from app.api.v1.panel.user.tts.synthesis import synthesis_bp

logger = logging.getLogger(__name__)


# =============================================================================
# VOICE MANAGEMENT
# =============================================================================

@synthesis_bp.route('/voices', methods=['GET'])
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


# =============================================================================
# SCRIPT GENERATION
# =============================================================================

@synthesis_bp.route('/tutor-script', methods=['POST'])
@token_required
def generate_tutor_script():
    """
    Generate a complete tutor script with audio for multiple steps.
    Pre-generates all audio for a tutorial sequence.

    Uses OpenAI TTS as primary engine.

    Request Body:
    {
        "steps": [
            {"id": "intro", "text": "Willkommen! Heute lernen wir..."},
            {"id": "step1", "text": "Zuerst schauen wir uns an..."},
            {"id": "step2", "text": "Jetzt bist du dran!"}
        ],
        "voice": "nova",
        "speed": 1.0
    }

    Response:
    {
        "success": true,
        "data": {
            "script": [
                {"id": "intro", "audio_url": "...", "duration_ms": 2500},
                {"id": "step1", "audio_url": "...", "duration_ms": 3200},
                ...
            ],
            "total_duration_ms": 8500,
            "from_cache_count": 2,
            "generated_count": 1,
            "provider": "openai"
        }
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or not data.get('steps'):
            return jsonify({
                'success': False,
                'error': {'code': 'NO_STEPS', 'message': 'No steps provided'}
            }), 400

        steps = data['steps']
        voice = data.get('voice', DEFAULT_TUTOR_VOICE)
        speed = float(data.get('speed', 1.0))

        # Determine provider and voice_id
        provider, voice_id, voice_name = get_voice_info(voice)

        results = []
        total_duration = 0
        cache_hits = 0
        cache_misses = 0

        for step in steps:
            step_id = step.get('id', f'step_{len(results)}')
            text = step.get('text', '')

            if not text:
                continue

            text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
            audio_id = f"{text_hash}_{voice}_{int(speed*100)}"
            duration = int((len(text) / 5 / 150) * 60 * 1000)

            # Storage path (relative to backend root)
            backend_root = Path(__file__).parent.parent.parent.parent
            storage_dir = Path(
                os.getenv('MEDIA_CACHE_PATH', str(backend_root / 'storage' / 'media_cache'))
            ) / 'tts' / text_hash[:2]
            storage_dir.mkdir(parents=True, exist_ok=True)
            file_path = storage_dir / f"{text_hash}_{voice}.mp3"

            # Check cache
            from_cache = file_path.exists()

            if from_cache:
                cache_hits += 1
                logger.info(f"TTS cache hit for step {step_id}")
            else:
                # Generate with OpenAI TTS
                try:
                    from app.application.services.ai.adapter import AIAdapter
                    openai_voice = voice if voice in AVAILABLE_VOICES['openai'] else 'nova'
                    audio_bytes = AIAdapter.text_to_speech(
                        text=text,
                        voice=openai_voice,
                        model=DEFAULT_MODEL,
                        speed=speed
                    )
                    with open(file_path, 'wb') as f:
                        f.write(audio_bytes)
                    cache_misses += 1
                except Exception as e:
                    logger.error(f"TTS generation failed for step {step_id}: {e}")
                    continue

            total_duration += duration

            results.append({
                'id': step_id,
                'audio_url': f'/api/v1/tts/audio/{audio_id}',
                'audio_path': str(file_path),
                'duration_ms': duration,
                'from_cache': from_cache
            })

        return jsonify({
            'success': True,
            'data': {
                'script': results,
                'total_duration_ms': total_duration,
                'from_cache_count': cache_hits,
                'generated_count': cache_misses,
                'voice': voice,
                'voice_name': voice_name,
                'speed': speed,
                'provider': 'openai',
                'model': DEFAULT_MODEL
            }
        })

    except Exception as e:
        logger.error(f"Tutor script generation error: {e}")
        return jsonify({
            'success': False,
            'error': {'code': 'SCRIPT_ERROR', 'message': str(e)}
        }), 500
