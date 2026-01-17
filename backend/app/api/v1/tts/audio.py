"""
Audio Processing API (Consolidated)

Provides endpoints for:
- Speech-to-Text (STT) using OpenAI Whisper
- Oral explanation analysis (STT + AI evaluation)

Consolidated from:
- media/audio/processing.py (260 LOC)
- media/audio/streaming.py (238 LOC)

Total: 498 LOC
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
import os
import logging
import base64
import tempfile
import json
import re
from werkzeug.utils import secure_filename

from app.middleware.auth import token_required
from app.services.ai_adapter import AIAdapter

logger = logging.getLogger(__name__)

# Allowed audio formats
ALLOWED_AUDIO_FORMATS = {'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm', 'ogg', 'flac'}

# Maximum audio file size (25MB - OpenAI limit)
MAX_AUDIO_SIZE = 25 * 1024 * 1024

# Blueprint
audio_bp = Blueprint('audio', __name__, url_prefix='/api/v1/audio')


def allowed_audio_file(filename: str) -> bool:
    """Check if the file has an allowed audio extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_FORMATS


# ============================================================================
# Speech-to-Text (Whisper) Endpoints
# ============================================================================

@audio_bp.route('/transcribe', methods=['POST'])
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


@audio_bp.route('/transcribe-base64', methods=['POST'])
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


# ============================================================================
# Oral Explanation Analysis (LM24)
# ============================================================================

@audio_bp.route('/analyze-oral', methods=['POST'])
@token_required
def analyze_oral_explanation():
    """
    Analyze an oral explanation for LM24 (Mündliche Erklärung).

    This endpoint combines STT with AI analysis to evaluate
    the quality and accuracy of a spoken explanation.

    Request:
    - Content-Type: multipart/form-data
    - audio: Audio file of the oral explanation
    - topic: The topic being explained
    - expected_points: JSON array of key points that should be mentioned
    - language: Language code (default: 'de')

    Response:
    {
        "success": true,
        "data": {
            "transcription": "...",
            "analysis": {
                "score": 85,
                "feedback": "...",
                "covered_points": [...],
                "missing_points": [...],
                "suggestions": [...]
            }
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
        topic = request.form.get('topic', '')
        expected_points_json = request.form.get('expected_points', '[]')
        language = request.form.get('language', 'de')

        try:
            expected_points = json.loads(expected_points_json)
        except json.JSONDecodeError:
            expected_points = []

        # Validate file
        if not allowed_audio_file(audio_file.filename):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_FORMAT',
                    'message': f'Invalid audio format'
                }
            }), 400

        # Save to temp file
        filename = secure_filename(audio_file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            audio_file.save(tmp.name)
            tmp_path = tmp.name

        try:
            # Step 1: Transcribe audio
            transcription_result = AIAdapter.transcribe_audio(
                audio_path=tmp_path,
                language=language,
                prompt=f"Erklärung zum Thema: {topic}" if topic else None
            )

            transcribed_text = transcription_result.get('text', '')

            if not transcribed_text.strip():
                return jsonify({
                    'success': True,
                    'data': {
                        'transcription': '',
                        'analysis': {
                            'score': 0,
                            'feedback': 'Keine Sprache erkannt. Bitte sprechen Sie deutlich und versuchen Sie es erneut.',
                            'covered_points': [],
                            'missing_points': expected_points,
                            'suggestions': ['Sprechen Sie lauter und deutlicher', 'Stellen Sie sicher, dass das Mikrofon funktioniert']
                        }
                    }
                })

            # Step 2: Analyze the explanation with AI
            analysis_prompt = f"""Analysiere die folgende mündliche Erklärung zum Thema "{topic}":

TRANSKRIPTION:
{transcribed_text}

ERWARTETE KERNPUNKTE:
{json.dumps(expected_points, ensure_ascii=False) if expected_points else "Keine spezifischen Punkte vorgegeben"}

Bewerte die Erklärung nach folgenden Kriterien:
1. Vollständigkeit (wurden alle Kernpunkte abgedeckt?)
2. Klarheit (war die Erklärung verständlich?)
3. Fachliche Korrektheit
4. Struktur und Aufbau

Antworte im JSON-Format:
{{
    "score": <0-100>,
    "feedback": "<Zusammenfassendes Feedback in 2-3 Sätzen>",
    "covered_points": ["<Punkt 1>", "<Punkt 2>", ...],
    "missing_points": ["<Fehlender Punkt 1>", ...],
    "suggestions": ["<Verbesserungsvorschlag 1>", ...]
}}"""

            analysis_response = AIAdapter.chat_completion(
                messages=[{'role': 'user', 'content': analysis_prompt}],
                system_prompt="Du bist ein erfahrener Prüfer und Lehrer. Analysiere mündliche Erklärungen fair aber gründlich. Antworte ausschließlich im angeforderten JSON-Format.",
                model='gpt-4o-mini',
                max_tokens=1000,
                temperature=0.3,
                user_id=user_id
            )

            # Parse the analysis
            analysis_text = analysis_response.get('content', '')

            # Try to extract JSON from the response
            json_match = re.search(r'\{[\s\S]*\}', analysis_text)

            if json_match:
                try:
                    analysis = json.loads(json_match.group())
                except json.JSONDecodeError:
                    analysis = {
                        'score': 50,
                        'feedback': analysis_text,
                        'covered_points': [],
                        'missing_points': [],
                        'suggestions': []
                    }
            else:
                analysis = {
                    'score': 50,
                    'feedback': analysis_text,
                    'covered_points': [],
                    'missing_points': [],
                    'suggestions': []
                }

            return jsonify({
                'success': True,
                'data': {
                    'transcription': transcribed_text,
                    'duration': transcription_result.get('duration', 0),
                    'analysis': analysis
                }
            })

        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except Exception as e:
        logger.error(f"Oral explanation analysis error: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'ANALYSIS_ERROR',
                'message': str(e)
            }
        }), 500


# ============================================================================
# Utility Endpoints
# ============================================================================

@audio_bp.route('/supported-formats', methods=['GET'])
def get_supported_audio_formats():
    """
    Get list of supported audio formats.

    Response:
    {
        "success": true,
        "data": {
            "formats": ["mp3", "wav", "webm", ...],
            "max_size_mb": 25
        }
    }
    """
    return jsonify({
        'success': True,
        'data': {
            'formats': list(ALLOWED_AUDIO_FORMATS),
            'max_size_mb': MAX_AUDIO_SIZE // (1024 * 1024)
        }
    })
