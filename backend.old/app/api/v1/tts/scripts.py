"""
TTS Tutor Script Generation Endpoint.

Endpoint for generating complete tutor scripts with multiple audio steps.
"""

import os
import hashlib
import logging
from pathlib import Path

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.middleware.auth import token_required
from .config import AVAILABLE_VOICES, DEFAULT_TUTOR_VOICE, DEFAULT_MODEL
from .helpers import get_voice_info

logger = logging.getLogger(__name__)

# Blueprint for script generation
tts_scripts_bp = Blueprint('tts_scripts', __name__, url_prefix='/tts')


@tts_scripts_bp.route('/tutor-script', methods=['POST'])
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
