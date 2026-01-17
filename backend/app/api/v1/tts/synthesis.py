"""
LernsystemX TTS API - Synthesis & Voice Management

Text-to-Speech synthesis endpoints with caching and voice management.

TTS Synthesis:
- POST /tts/speak - Generate TTS audio from text (with caching)
- GET /tts/audio/<audio_id> - Get cached TTS audio file
- POST /tts/speak-stream - Generate TTS and stream audio directly (no caching)

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
from typing import Tuple

from flask import Blueprint, request, jsonify, Response, send_file
from flask_jwt_extended import get_jwt_identity

from app.middleware.auth import token_required
from app.api.v1.tts.core import (
    AVAILABLE_VOICES,
    DEFAULT_TUTOR_VOICE,
    DEFAULT_PROVIDER,
    DEFAULT_MODEL,
    VALID_TTS_MODELS,
    MAX_TEXT_LENGTH,
    MIN_SPEED,
    MAX_SPEED,
    get_voice_info,
    preprocess_text,
)

logger = logging.getLogger(__name__)

synthesis_bp = Blueprint('tts_synthesis', __name__, url_prefix='/tts')

__all__ = ['tts_bp']


# =============================================================================
# TTS SYNTHESIS
# =============================================================================

@synthesis_bp.route('/speak', methods=['POST'])
@token_required
def generate_tts():
    """
    Generate TTS audio from text (with caching).

    Uses OpenAI TTS as primary engine (best quality).

    Request Body:
    {
        "text": "Text to speak",
        "voice": "nova",        // OpenAI voice
        "speed": 1.0,           // Optional, 0.5-2.0
        "provider": "openai",   // Optional
        "language": "de",       // Optional, for preprocessing
        "model": "tts-1"        // Optional: 'tts-1' or 'tts-1-hd'
    }

    Response:
    {
        "success": true,
        "data": {
            "audio_url": "/api/v1/tts/audio/abc123",
            "from_cache": true,
            "duration_ms": 3500,
            "text_length": 150,
            "provider": "openai"
        }
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or not data.get('text'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NO_TEXT',
                    'message': 'No text provided'
                }
            }), 400

        text = data['text'].strip()
        voice = data.get('voice', DEFAULT_TUTOR_VOICE)
        speed = float(data.get('speed', 1.0))
        requested_provider = data.get('provider', DEFAULT_PROVIDER)
        language = data.get('language', 'de')

        # Preprocess text for better pronunciation
        original_text = text
        text = preprocess_text(text, language)
        logger.debug(f"Preprocessed text: {original_text[:50]}... -> {text[:50]}...")

        # Determine provider and voice_id
        provider, voice_id, voice_name = get_voice_info(voice)

        # Override provider if specifically requested
        if requested_provider == 'openai' and voice in AVAILABLE_VOICES['openai']:
            provider = 'openai'
            voice_id = voice

        # Validate speed
        if not MIN_SPEED <= speed <= MAX_SPEED:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_SPEED',
                    'message': f'Speed must be between {MIN_SPEED} and {MAX_SPEED}'
                }
            }), 400

        # Limit text length
        max_length = MAX_TEXT_LENGTH.get(provider, MAX_TEXT_LENGTH['default'])
        if len(text) > max_length:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'TEXT_TOO_LONG',
                    'message': f'Text too long. Maximum {max_length} characters.'
                }
            }), 400

        # Generate audio URL with hash for retrieval
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        audio_id = f"{text_hash}_{voice}_{int(speed*100)}"

        # Storage path (relative to backend root)
        backend_root = Path(__file__).parent.parent.parent.parent
        storage_dir = Path(
            os.getenv('MEDIA_CACHE_PATH', str(backend_root / 'storage' / 'media_cache'))
        ) / 'tts' / text_hash[:2]
        storage_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{text_hash}_{voice}.mp3"
        file_path = storage_dir / filename

        # Check if already cached
        from_cache = False

        if file_path.exists():
            from_cache = True
            logger.info(f"TTS cache hit: {audio_id}")
        else:
            # Generate with OpenAI TTS
            try:
                logger.info(f"Generating with OpenAI TTS (voice={voice})")
                from app.services.ai_adapter import AIAdapter

                openai_voice = voice if voice in AVAILABLE_VOICES['openai'] else 'nova'

                # Use requested model or default - VALIDATE model name!
                requested_model = data.get('model', DEFAULT_MODEL)
                if requested_model not in VALID_TTS_MODELS:
                    logger.warning(
                        f"Invalid TTS model '{requested_model}', using default '{DEFAULT_MODEL}'"
                    )
                    tts_model = DEFAULT_MODEL
                else:
                    tts_model = requested_model

                audio_bytes = AIAdapter.text_to_speech(
                    text=text,
                    voice=openai_voice,
                    model=tts_model,
                    speed=speed
                )

                with open(file_path, 'wb') as f:
                    f.write(audio_bytes)

                provider = 'openai'
                voice_name = AVAILABLE_VOICES['openai'].get(openai_voice, {}).get('name', 'OpenAI')
                logger.info(f"OpenAI TTS generation successful (model={tts_model})")
            except Exception as e:
                import traceback
                logger.error(f"OpenAI TTS failed: {e}")
                logger.error(traceback.format_exc())
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'TTS_FAILED',
                        'message': f'TTS generation failed: {str(e)}',
                        'details': traceback.format_exc()
                    }
                }), 503

        # Estimate duration (roughly 150 words per minute, 5 chars per word)
        duration_ms = int((len(text) / 5 / 150) * 60 * 1000)

        return jsonify({
            'success': True,
            'data': {
                'audio_url': f'/api/v1/tts/audio/{audio_id}',
                'audio_path': str(file_path),
                'from_cache': from_cache,
                'duration_ms': duration_ms,
                'text_length': len(text),
                'voice': voice,
                'voice_name': voice_name,
                'provider': provider,
                'cost_saved': 1 if from_cache else 0,
                'is_free': provider in ('edge', 'gtts', 'piper')
            }
        })

    except Exception as e:
        logger.error(f"TTS generation error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'TTS_ERROR',
                'message': str(e)
            }
        }), 500


@synthesis_bp.route('/audio/<audio_id>', methods=['GET'])
def get_tts_audio(audio_id: str):
    """
    Get cached TTS audio file.

    URL Params:
        audio_id: Hash-based audio identifier

    Query Params:
        path: Direct file path (development only)

    Returns:
        Audio file (audio/mpeg or audio/wav)
    """
    try:
        # Option 1: Direct path (for development)
        direct_path = request.args.get('path')
        if direct_path and os.path.exists(direct_path):
            mimetype = 'audio/wav' if direct_path.endswith('.wav') else 'audio/mpeg'
            return send_file(
                direct_path,
                mimetype=mimetype,
                as_attachment=False
            )

        # Option 2: Look up by audio_id
        # Parse audio_id: text_hash_voice_speed
        parts = audio_id.rsplit('_', 2)
        if len(parts) >= 3:
            text_hash = parts[0]

            # Try to find in cache directory (relative to backend root)
            backend_root = Path(__file__).parent.parent.parent.parent
            base_path = Path(
                os.getenv('MEDIA_CACHE_PATH', str(backend_root / 'storage' / 'media_cache'))
            )
            tts_dir = base_path / 'tts' / text_hash[:2]

            # Look for matching file (mp3 or wav)
            if tts_dir.exists():
                # Try WAV first (Piper), then MP3
                for ext in ['.wav', '.mp3']:
                    for file in tts_dir.glob(f"{text_hash}*{ext}"):
                        mimetype = 'audio/wav' if ext == '.wav' else 'audio/mpeg'
                        return send_file(
                            str(file),
                            mimetype=mimetype,
                            as_attachment=False
                        )

        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Audio not found'
            }
        }), 404

    except Exception as e:
        logger.error(f"TTS audio retrieval error: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'RETRIEVAL_ERROR',
                'message': str(e)
            }
        }), 500


@synthesis_bp.route('/speak-stream', methods=['POST'])
@token_required
def generate_tts_stream():
    """
    Generate TTS and stream audio directly (no caching).
    Useful for dynamic/one-time content.

    Request Body:
    {
        "text": "Text to speak",
        "voice": "nova",
        "speed": 1.0
    }

    Returns:
        Streamed audio/mpeg
    """
    try:
        from app.services.ai_adapter import AIAdapter

        data = request.get_json()

        if not data or not data.get('text'):
            return jsonify({
                'success': False,
                'error': {'code': 'NO_TEXT', 'message': 'No text provided'}
            }), 400

        text = data['text'].strip()
        voice = data.get('voice', DEFAULT_TUTOR_VOICE)
        speed = float(data.get('speed', 1.0))

        # Generate audio
        audio_bytes = AIAdapter.text_to_speech(
            text=text,
            voice=voice,
            model='tts-1',
            speed=speed
        )

        return Response(
            audio_bytes,
            mimetype='audio/mpeg',
            headers={
                'Content-Disposition': 'inline',
                'Cache-Control': 'no-cache'
            }
        )

    except Exception as e:
        logger.error(f"TTS stream error: {e}")
        return jsonify({
            'success': False,
            'error': {'code': 'TTS_ERROR', 'message': str(e)}
        }), 500


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
        from app.repositories.ai_models import AIModelsRepository
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
                    from app.services.ai_adapter import AIAdapter
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
