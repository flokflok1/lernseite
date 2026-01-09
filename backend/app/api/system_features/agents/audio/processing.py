"""
LernsystemX Agent API - Audio/Voice Endpoints

Audio and voice-related agent endpoints:
- POST   /api/v1/agents/:course_id/ask/audio  - Ask with TTS audio response
- POST   /api/v1/agents/:course_id/ask/voice  - Ask via voice (transcribe + respond + TTS)

ISO 9001:2015 compliant - Agent Audio Layer
Refactored: 2026-01-07 per Developer-Guide-KI Section 10
"""

import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from app.services.agent_service import AgentService
from app.services.media_cache_service import MediaCacheService
from app.repositories.agent import AgentRepository
from app.middleware.auth import token_required, get_current_user

from app.api.system_features.agents._helpers import (
    validate_course_exists,
    error_response,
    UPLOAD_TEMP_PATH,
    ALLOWED_AUDIO_EXTENSIONS
)

# Blueprint for audio/voice endpoints
agents_audio_bp = Blueprint('agents_audio', __name__, url_prefix='/agents')


@agents_audio_bp.route('/<course_id>/ask/audio', methods=['POST'])
@token_required
def agent_ask_with_audio(course_id: str):
    """
    Ask the agent with TTS audio response

    Request Body:
        question: str (required) - The question to ask
        context: dict (optional) - Context information
        language: str (optional) - Response language (default: de)
        voice: str (optional) - TTS voice (nova, alloy, echo, fable, onyx, shimmer)
        speed: float (optional) - Speech speed (0.25-4.0, default: 1.0)

    Response:
        200: Agent response with text and audio URL
        400: Invalid request
        404: Course not found
    """
    try:
        user = get_current_user()
        if not user:
            return error_response('Authentication required', code=401)

        course, err = validate_course_exists(course_id)
        if err:
            return err

        data = request.get_json()
        question = data.get('question', '').strip()

        if not question or len(question) < 3:
            return error_response('Question must be at least 3 characters', code=400)

        result = AgentService.ask_with_audio(
            course_id=course_id,
            user_id=str(user['user_id']),
            question=question,
            context=data.get('context'),
            language=data.get('language', 'de'),
            organization_id=user.get('organization_id'),
            voice=data.get('voice', 'nova'),
            speech_speed=float(data.get('speed', 1.0))
        )

        return jsonify({
            'success': True,
            'data': result
        }), 200

    except Exception as e:
        return error_response('Failed to process audio request', details=str(e))


@agents_audio_bp.route('/<course_id>/ask/voice', methods=['POST'])
@token_required
def agent_ask_voice(course_id: str):
    """
    Voice-to-Voice: Upload audio question, get audio response

    This endpoint:
    1. Transcribes the uploaded audio (with caching)
    2. Gets the agent's text response (with caching)
    3. Generates TTS audio response (with caching)

    Request:
        audio: file (required) - Audio file (mp3, wav, webm, m4a)
        voice: str (optional) - Response voice
        language: str (optional) - Language hint

    Response:
        200: {
            user_text: str,
            agent_text: str,
            audio_url: str,
            transcription_from_cache: bool,
            response_from_cache: bool,
            tts_from_cache: bool
        }
    """
    try:
        user = get_current_user()
        if not user:
            return error_response('Authentication required', code=401)

        course, err = validate_course_exists(course_id)
        if err:
            return err

        # Check for audio file
        if 'audio' not in request.files:
            return error_response('No audio file provided', code=400)

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return error_response('No audio file selected', code=400)

        # Validate file type
        ext = audio_file.filename.rsplit('.', 1)[-1].lower() if '.' in audio_file.filename else ''
        if ext not in ALLOWED_AUDIO_EXTENSIONS:
            return error_response(
                f'Invalid audio format. Allowed: {", ".join(ALLOWED_AUDIO_EXTENSIONS)}',
                code=400
            )

        # Save temporarily
        os.makedirs(UPLOAD_TEMP_PATH, exist_ok=True)
        filename = secure_filename(f"{user['user_id']}_{audio_file.filename}")
        temp_path = os.path.join(UPLOAD_TEMP_PATH, filename)
        audio_file.save(temp_path)

        try:
            # Start or get session
            session = MediaCacheService.start_realtime_session(
                agent_id=str(AgentRepository.get_or_create_agent(course_id)['agent_id']),
                user_id=str(user['user_id']),
                session_type='voice_chat'
            )

            # Process voice turn
            result = AgentService.voice_conversation_turn(
                course_id=course_id,
                user_id=str(user['user_id']),
                audio_path=temp_path,
                session=session,
                voice=request.form.get('voice', 'nova'),
                language=request.form.get('language', 'de')
            )

            return jsonify({
                'success': True,
                'data': result
            }), 200

        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        return error_response('Failed to process voice request', details=str(e))
