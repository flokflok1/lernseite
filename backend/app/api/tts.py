"""
TTS API - Text-to-Speech mit Caching

Provides endpoints for:
- TTS Audio generierung mit Edge TTS (kostenlos) oder OpenAI
- Cached Audio abruf
- Voice Settings

Edge TTS: Microsoft Edge Stimmen - Premium Qualität, komplett kostenlos!
"""

from flask import request, jsonify, Response, send_file
from . import api_v1
from app.middleware.auth import token_required
from flask_jwt_extended import get_jwt_identity
import os
import re
import logging
import hashlib
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import TTS Service for pronunciation
try:
    from app.services.tts_service import TTSService
    TTS_SERVICE_AVAILABLE = True
except ImportError:
    TTS_SERVICE_AVAILABLE = False
    logger.warning("TTSService not available, using basic preprocessing")

# Try to import MediaCacheService, fallback to direct generation
try:
    from app.services.media_cache_service import MediaCacheService
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    logger.warning("MediaCacheService not available, using direct TTS generation")

# OpenAI TTS is our PRIMARY engine - best quality, no GPU needed
logger.info("Using OpenAI TTS as primary TTS engine")

# Available voices - OpenAI TTS (best quality)
AVAILABLE_VOICES = {
    'openai': {
        # OpenAI TTS-1 voices
        'alloy': {'name': 'Alloy', 'gender': 'neutral', 'style': 'balanced', 'model': 'tts-1'},
        'echo': {'name': 'Echo', 'gender': 'male', 'style': 'warm', 'model': 'tts-1'},
        'fable': {'name': 'Fable', 'gender': 'neutral', 'style': 'expressive', 'model': 'tts-1'},
        'onyx': {'name': 'Onyx', 'gender': 'male', 'style': 'deep', 'model': 'tts-1'},
        'nova': {'name': 'Nova', 'gender': 'female', 'style': 'friendly', 'model': 'tts-1'},
        'shimmer': {'name': 'Shimmer', 'gender': 'female', 'style': 'soft', 'model': 'tts-1'},
    }
}

# Default tutor voice (OpenAI Nova - friendly female voice)
DEFAULT_TUTOR_VOICE = 'nova'
DEFAULT_PROVIDER = 'openai'
DEFAULT_MODEL = 'tts-1'  # or 'tts-1-hd' for higher quality

# Valid OpenAI TTS models
VALID_TTS_MODELS = ['tts-1', 'tts-1-hd']


def _basic_preprocess(text: str, language: str = 'de') -> str:
    """Basic text preprocessing fallback when TTSService is not available."""
    if language != 'de':
        return text

    processed = text

    # Basic German replacements
    replacements = {
        '€': ' Euro ',
        '$': ' Dollar ',
        '%': ' Prozent ',
        '×': ' mal ',
        '÷': ' geteilt durch ',
        '+': ' plus ',
        '−': ' minus ',
        '=': ' gleich ',
        # Common compound words
        'Listeneinkaufspreis': 'Listen Einkaufs Preis',
        'Zieleinkaufspreis': 'Ziel Einkaufs Preis',
        'Bareinkaufspreis': 'Bar Einkaufs Preis',
        'Bezugskalkulation': 'Bezugs Kalkulation',
        'Handelskalkulation': 'Handels Kalkulation',
        'Verkaufspreis': 'Verkaufs Preis',
        'Selbstkostenpreis': 'Selbstkosten Preis',
        'Bezugskosten': 'Bezugs Kosten',
        'Lieferantenrabatt': 'Lieferannten Rabbatt',
        'Rabatt': 'Rabbatt',
        'Skonto': 'Skonnto',
        'Kalkulation': 'Kalkullazion',
        'Lieferant': 'Lieferannt',
        # Abbreviations
        'LEP': 'Listen Einkaufs Preis',
        'ZEP': 'Ziel Einkaufs Preis',
        'BEP': 'Bar Einkaufs Preis',
        'VKP': 'Verkaufs Preis',
        'MwSt': 'Mehrwertsteuer',
        'z.B.': 'zum Beispiel',
        'd.h.': 'das heißt',
        'bzw.': 'beziehungsweise',
        'ca.': 'zirka',
        'inkl.': 'inklusive',
        'exkl.': 'exklusive',
        'zzgl.': 'zuzüglich',
        'abzgl.': 'abzüglich',
    }

    # Apply replacements (case-insensitive for words)
    for original, replacement in replacements.items():
        if len(original) > 2:  # Word replacement
            pattern = re.compile(r'\b' + re.escape(original) + r'\b', re.IGNORECASE)
            processed = pattern.sub(replacement, processed)
        else:  # Symbol replacement
            processed = processed.replace(original, replacement)

    # Number with decimals: "35.67" -> "35 Komma 67"
    processed = re.sub(r'(\d+)[.,](\d+)', r'\1 Komma \2', processed)

    # Add pauses after sentences
    processed = re.sub(r'\. ', '. , ', processed)

    # Clean up multiple spaces
    processed = re.sub(r'\s+', ' ', processed).strip()

    return processed


def get_voice_info(voice: str) -> tuple[str, str, str]:
    """
    Get voice provider and voice_id from voice name.

    Returns: (provider, voice_id, display_name)
    """
    # Check OpenAI voices
    if voice in AVAILABLE_VOICES['openai']:
        info = AVAILABLE_VOICES['openai'][voice]
        return ('openai', voice, info['name'])

    # Default to OpenAI Nova
    return ('openai', 'nova', 'Nova')


@api_v1.route('/tts/speak', methods=['POST'])
@token_required
def generate_tts():
    """
    Generate TTS audio from text (with caching).

    Uses Edge TTS by default (FREE, premium quality!)
    Falls back to OpenAI TTS if Edge TTS fails.

    Request Body:
    {
        "text": "Text to speak",
        "voice": "de-katja",  // Edge TTS voice (free) or OpenAI voice
        "speed": 1.0,         // Optional, 0.5-2.0
        "provider": "edge"    // Optional: 'edge' (free) or 'openai' (paid)
    }

    Response:
    {
        "success": true,
        "data": {
            "audio_url": "/api/v1/tts/audio/abc123",
            "from_cache": true,
            "duration_ms": 3500,
            "text_length": 150,
            "provider": "edge"
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

        # Preprocess text for better pronunciation (from database)
        original_text = text
        if TTS_SERVICE_AVAILABLE:
            try:
                text = TTSService.preprocess_text(text, language)
                logger.debug(f"Preprocessed text: {original_text[:50]}... -> {text[:50]}...")
            except Exception as e:
                logger.warning(f"TTS preprocessing failed, using original: {e}")
        else:
            # Basic fallback preprocessing
            text = _basic_preprocess(text, language)

        # Determine provider and voice_id
        provider, voice_id, voice_name = get_voice_info(voice)

        # Override provider if specifically requested
        if requested_provider == 'openai' and voice in AVAILABLE_VOICES['openai']:
            provider = 'openai'
            voice_id = voice

        # Validate speed
        if not 0.5 <= speed <= 2.0:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_SPEED',
                    'message': 'Speed must be between 0.5 and 2.0'
                }
            }), 400

        # Limit text length
        max_length = 10000 if provider == 'edge' else 4096
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
        backend_root = Path(__file__).parent.parent.parent
        storage_dir = Path(os.getenv('MEDIA_CACHE_PATH', str(backend_root / 'storage' / 'media_cache'))) / 'tts' / text_hash[:2]
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
                # Only allow valid TTS models, fallback to default for invalid ones
                if requested_model not in VALID_TTS_MODELS:
                    logger.warning(f"Invalid TTS model '{requested_model}', using default '{DEFAULT_MODEL}'")
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


@api_v1.route('/tts/audio/<audio_id>', methods=['GET'])
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
            voice = parts[1]

            # Try to find in cache directory (relative to backend root)
            backend_root = Path(__file__).parent.parent.parent
            base_path = Path(os.getenv('MEDIA_CACHE_PATH', str(backend_root / 'storage' / 'media_cache')))
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


@api_v1.route('/tts/speak-stream', methods=['POST'])
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


@api_v1.route('/tts/voices', methods=['GET'])
def get_available_voices():
    """
    Get list of available TTS voices and models from database.

    Response:
    {
        "success": true,
        "data": {
            "voices": {...},
            "models": [...],
            "default": "de_speaker",
            "coqui_available": true
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
        from app.repositories.ai_models_repository import AIModelsRepository
        db_models = AIModelsRepository.get_models_by_category('audio')
        for model in db_models:
            audio_models.append({
                'model_id': model.get('model_id'),
                'model_name': model.get('model_name'),
                'display_name': model.get('display_name'),
                'provider': model.get('provider_name', 'openai'),
                'input_price': float(model.get('input_price_per_1k') or model.get('cost_per_1k_input') or 0),
                'output_price': float(model.get('output_price_per_1k') or model.get('cost_per_1k_output') or 0),
                'active': model.get('active', True),
                'is_tts': 'tts' in model.get('model_name', '').lower() or 'audio' in model.get('model_name', '').lower(),
                'is_transcription': 'whisper' in model.get('model_name', '').lower() or 'transcribe' in model.get('model_name', '').lower()
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
                {'voice': 'nova', 'name': 'Nova (OpenAI)', 'description': 'Natürliche weibliche Stimme', 'provider': 'openai', 'model': 'tts-1'},
                {'voice': 'alloy', 'name': 'Alloy (OpenAI)', 'description': 'Ausgewogene neutrale Stimme', 'provider': 'openai', 'model': 'tts-1'},
                {'voice': 'onyx', 'name': 'Onyx (OpenAI)', 'description': 'Tiefe männliche Stimme', 'provider': 'openai', 'model': 'tts-1'},
            ]
        }
    })


@api_v1.route('/tts/tutor-script', methods=['POST'])
@token_required
def generate_tutor_script():
    """
    Generate a complete tutor script with audio for multiple steps.
    Pre-generates all audio for a tutorial sequence.

    Uses Edge TTS by default (FREE!)

    Request Body:
    {
        "steps": [
            {"id": "intro", "text": "Willkommen! Heute lernen wir..."},
            {"id": "step1", "text": "Zuerst schauen wir uns an..."},
            {"id": "step2", "text": "Jetzt bist du dran!"}
        ],
        "voice": "de-katja",  // Edge TTS (free) or OpenAI voice
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
            "provider": "edge"
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
            backend_root = Path(__file__).parent.parent.parent
            storage_dir = Path(os.getenv('MEDIA_CACHE_PATH', str(backend_root / 'storage' / 'media_cache'))) / 'tts' / text_hash[:2]
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


# ============================================================================
# TUTOR KNOWLEDGE API
# ============================================================================

@api_v1.route('/tutor/knowledge', methods=['POST'])
@token_required
def get_tutor_knowledge():
    """
    Lädt Tutor-Wissen aus der Datenbank.

    Der Tutor verwendet dieses Wissen um kontextbezogene Erklärungen zu geben.

    Request Body:
    {
        "course_id": "uuid",       // Optional: Kurs-Kontext
        "chapter_id": "uuid",      // Optional: Kapitel-Kontext
        "lesson_id": 123,          // Optional: Lektions-Inhalt
        "method_id": "uuid",       // Optional: Lernmethoden-Daten
        "include_files": true,     // Optional: Kurs-Dateien
        "include_progress": true   // Optional: Lernfortschritt
    }

    Response:
    {
        "success": true,
        "data": {
            "context_prompt": "...",  // Formatierter Kontext-String
            "course": {...},          // Kurs-Details
            "chapter": {...},         // Kapitel-Details
            "lesson": {...},          // Lektions-Details
            "method": {...}           // Lernmethoden-Details
        }
    }
    """
    try:
        from app.services.tutor_knowledge_service import TutorKnowledgeService

        user_id = get_jwt_identity()
        data = request.get_json() or {}

        course_id = data.get('course_id')
        chapter_id = data.get('chapter_id')
        lesson_id = data.get('lesson_id')
        method_id = data.get('method_id')
        include_files = data.get('include_files', True)
        include_progress = data.get('include_progress', True)

        # Build context prompt
        context_prompt = TutorKnowledgeService.build_tutor_context_prompt(
            course_id=course_id,
            chapter_id=chapter_id,
            lesson_id=lesson_id,
            method_id=method_id,
            user_id=user_id if include_progress else None,
            include_files=include_files,
            include_progress=include_progress
        )

        # Also return individual data objects
        result_data = {
            'context_prompt': context_prompt
        }

        if course_id:
            result_data['course'] = TutorKnowledgeService.get_course_context(course_id)

        if chapter_id:
            result_data['chapter'] = TutorKnowledgeService.get_chapter_context(chapter_id)

        if lesson_id:
            result_data['lesson'] = TutorKnowledgeService.get_lesson_content(lesson_id)

        if method_id:
            result_data['method'] = TutorKnowledgeService.get_learning_method_data(method_id)

        return jsonify({
            'success': True,
            'data': result_data
        })

    except Exception as e:
        logger.error(f"Tutor knowledge error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {'code': 'KNOWLEDGE_ERROR', 'message': str(e)}
        }), 500


@api_v1.route('/tutor/course/<course_id>/context', methods=['GET'])
@token_required
def get_course_tutor_context(course_id: str):
    """
    Kurzform: Lädt Kurs-Kontext für den Tutor.

    URL Params:
        course_id: UUID des Kurses

    Response:
    {
        "success": true,
        "data": {
            "course": {...},
            "chapters": [...],
            "total_lessons": 42
        }
    }
    """
    try:
        from app.services.tutor_knowledge_service import TutorKnowledgeService

        context = TutorKnowledgeService.get_course_context(course_id)

        if not context:
            return jsonify({
                'success': False,
                'error': {'code': 'NOT_FOUND', 'message': 'Course not found'}
            }), 404

        return jsonify({
            'success': True,
            'data': context
        })

    except Exception as e:
        logger.error(f"Course context error: {e}")
        return jsonify({
            'success': False,
            'error': {'code': 'CONTEXT_ERROR', 'message': str(e)}
        }), 500


@api_v1.route('/tutor/chapter/<chapter_id>/context', methods=['GET'])
@token_required
def get_chapter_tutor_context(chapter_id: str):
    """
    Kurzform: Lädt Kapitel-Kontext für den Tutor.

    URL Params:
        chapter_id: UUID des Kapitels

    Response:
    {
        "success": true,
        "data": {
            "chapter": {...},
            "lessons": [...],
            "learning_methods": [...]
        }
    }
    """
    try:
        from app.services.tutor_knowledge_service import TutorKnowledgeService

        context = TutorKnowledgeService.get_chapter_context(chapter_id)

        if not context:
            return jsonify({
                'success': False,
                'error': {'code': 'NOT_FOUND', 'message': 'Chapter not found'}
            }), 404

        return jsonify({
            'success': True,
            'data': context
        })

    except Exception as e:
        logger.error(f"Chapter context error: {e}")
        return jsonify({
            'success': False,
            'error': {'code': 'CONTEXT_ERROR', 'message': str(e)}
        }), 500


# ============================================================================
# PRONUNCIATION API (Aussprache-Regeln aus DB)
# ============================================================================

@api_v1.route('/tts/pronunciations', methods=['GET'])
def get_pronunciations():
    """
    Get all pronunciation rules from database.

    Query Params:
        language: Language code (default: 'de')

    Response:
    {
        "success": true,
        "data": {
            "pronunciations": {"word": "phonetic", ...},
            "count": 50
        }
    }
    """
    try:
        language = request.args.get('language', 'de')

        if TTS_SERVICE_AVAILABLE:
            pronunciations = TTSService.load_pronunciations(language)
        else:
            # Return empty dict if service not available
            pronunciations = {}

        return jsonify({
            'success': True,
            'data': {
                'pronunciations': pronunciations,
                'count': len(pronunciations),
                'language': language
            }
        })
    except Exception as e:
        logger.error(f"Error getting pronunciations: {e}")
        return jsonify({
            'success': False,
            'error': {'message': str(e)}
        }), 500


@api_v1.route('/tts/pronunciations', methods=['POST'])
@token_required
def add_pronunciation():
    """
    Add a new pronunciation rule.

    Request Body:
    {
        "word": "Listeneinkaufspreis",
        "phonetic": "Listen Einkaufs Preis",
        "language": "de",
        "category": "business"
    }
    """
    try:
        data = request.get_json() or {}
        word = data.get('word')
        phonetic = data.get('phonetic')
        language = data.get('language', 'de')
        category = data.get('category')

        if not word or not phonetic:
            return jsonify({
                'success': False,
                'error': {'message': 'word and phonetic are required'}
            }), 400

        if TTS_SERVICE_AVAILABLE:
            success = TTSService.add_pronunciation(word, phonetic, language, category)
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Pronunciation added for "{word}"'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': {'message': 'Failed to add pronunciation'}
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': {'message': 'TTSService not available'}
            }), 503

    except Exception as e:
        logger.error(f"Error adding pronunciation: {e}")
        return jsonify({
            'success': False,
            'error': {'message': str(e)}
        }), 500


@api_v1.route('/tts/pronunciations/ai', methods=['POST'])
@token_required
async def generate_ai_pronunciation():
    """
    Generate pronunciation using AI for an unknown word.

    Request Body:
    {
        "word": "Selbstkostenpreis",
        "language": "de",
        "context": "Business calculation term"
    }
    """
    try:
        data = request.get_json() or {}
        word = data.get('word')
        language = data.get('language', 'de')
        context = data.get('context')

        if not word:
            return jsonify({
                'success': False,
                'error': {'message': 'word is required'}
            }), 400

        if not TTS_SERVICE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': {'message': 'TTSService not available'}
            }), 503

        # Check if already exists
        existing = TTSService.get_pronunciation(word, language)
        if existing:
            return jsonify({
                'success': True,
                'data': {
                    'word': word,
                    'phonetic': existing,
                    'source': 'database'
                }
            })

        # Generate with AI
        phonetic = await TTSService.generate_pronunciation_with_ai(word, language, context)

        if phonetic:
            # Save to database
            TTSService.add_pronunciation(word, phonetic, language, source='ai_generated')

            return jsonify({
                'success': True,
                'data': {
                    'word': word,
                    'phonetic': phonetic,
                    'source': 'ai_generated'
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': {'message': 'AI could not generate pronunciation'}
            }), 500

    except Exception as e:
        logger.error(f"Error generating AI pronunciation: {e}")
        return jsonify({
            'success': False,
            'error': {'message': str(e)}
        }), 500
