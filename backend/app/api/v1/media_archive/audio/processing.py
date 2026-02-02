"""
Audio Processing API - Speech-to-Text (STT)

Provides endpoints for:
- Whisper STT from file upload
- Whisper STT from base64-encoded audio

Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm, ogg, flac
Maximum file size: 25MB (OpenAI limit)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
import os
import logging
import base64
import tempfile
from werkzeug.utils import secure_filename

from app.api.middleware.auth import token_required
from app.application.services.ai_adapter import AIAdapter

logger = logging.getLogger(__name__)

# Allowed audio formats
ALLOWED_AUDIO_FORMATS = {'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm', 'ogg', 'flac'}

# Maximum audio file size (25MB - OpenAI limit)
MAX_AUDIO_SIZE = 25 * 1024 * 1024

audio_processing_bp = Blueprint('audio_processing', __name__)


def allowed_audio_file(filename: str) -> bool:
    """Check if the file has an allowed audio extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_FORMATS


@audio_processing_bp.route('/audio/transcribe', methods=['POST'])
@token_required
def transcribe_audio():
    """
    Transcribe audio to text using OpenAI Whisper.

    Request:
    - Content-Type: multipart/form-data
    - audio: Audio file (mp3, wav, webm, etc.)
    - language: Optional language code (e.g., 'de', 'en')
    - prompt: Optional context prompt to improve accuracy

    Response:
    {
        "success": true,
        "data": {
            "text": "Transcribed text here...",
            "language": "de",
            "duration": 5.2
        }
    }
    """
    try:
        user_id = get_jwt_identity()

        # Check if audio file is present
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NO_AUDIO_FILE',
                    'message': 'No audio file provided'
                }
            }), 400

        audio_file = request.files['audio']

        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'EMPTY_FILENAME',
                    'message': 'No audio file selected'
                }
            }), 400

        # Validate file type
        if not allowed_audio_file(audio_file.filename):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_FORMAT',
                    'message': f'Invalid audio format. Allowed: {", ".join(ALLOWED_AUDIO_FORMATS)}'
                }
            }), 400

        # Check file size
        audio_file.seek(0, 2)  # Seek to end
        file_size = audio_file.tell()
        audio_file.seek(0)  # Reset to beginning

        if file_size > MAX_AUDIO_SIZE:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'FILE_TOO_LARGE',
                    'message': f'Audio file too large. Maximum size: 25MB'
                }
            }), 400

        # Get optional parameters
        language = request.form.get('language', None)
        prompt = request.form.get('prompt', None)

        # Save to temp file
        filename = secure_filename(audio_file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            audio_file.save(tmp.name)
            tmp_path = tmp.name

        try:
            # Transcribe using Whisper
            result = AIAdapter.transcribe_audio(
                audio_path=tmp_path,
                language=language,
                prompt=prompt
            )

            return jsonify({
                'success': True,
                'data': {
                    'text': result.get('text', ''),
                    'language': result.get('language', language),
                    'duration': result.get('duration', 0),
                    'segments': result.get('segments', [])
                }
            })

        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except Exception as e:
        logger.error(f"Audio transcription error: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'TRANSCRIPTION_ERROR',
                'message': str(e)
            }
        }), 500


@audio_processing_bp.route('/audio/transcribe-base64', methods=['POST'])
@token_required
def transcribe_audio_base64():
    """
    Transcribe audio from base64-encoded data.

    Request Body:
    {
        "audio": "base64_encoded_audio_data",
        "format": "webm",  // Audio format
        "language": "de",  // Optional
        "prompt": "Context..."  // Optional
    }

    Response:
    {
        "success": true,
        "data": {
            "text": "Transcribed text here..."
        }
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or not data.get('audio'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NO_AUDIO_DATA',
                    'message': 'No audio data provided'
                }
            }), 400

        audio_base64 = data['audio']
        audio_format = data.get('format', 'webm')
        language = data.get('language', None)
        prompt = data.get('prompt', None)

        # Validate format
        if audio_format not in ALLOWED_AUDIO_FORMATS:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_FORMAT',
                    'message': f'Invalid audio format. Allowed: {", ".join(ALLOWED_AUDIO_FORMATS)}'
                }
            }), 400

        # Decode base64
        try:
            audio_data = base64.b64decode(audio_base64)
        except Exception:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_BASE64',
                    'message': 'Invalid base64 audio data'
                }
            }), 400

        # Check size
        if len(audio_data) > MAX_AUDIO_SIZE:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'FILE_TOO_LARGE',
                    'message': 'Audio data too large. Maximum size: 25MB'
                }
            }), 400

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{audio_format}') as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name

        try:
            # Transcribe using Whisper
            result = AIAdapter.transcribe_audio(
                audio_path=tmp_path,
                language=language,
                prompt=prompt
            )

            return jsonify({
                'success': True,
                'data': {
                    'text': result.get('text', ''),
                    'language': result.get('language', language),
                    'duration': result.get('duration', 0)
                }
            })

        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except Exception as e:
        logger.error(f"Audio transcription error: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'TRANSCRIPTION_ERROR',
                'message': str(e)
            }
        }), 500
