"""
Media Domain - Audio Analysis Routes (User Journey)

Oral explanation analysis endpoint for LM24.

Endpoints:
- POST /audio/analyze-oral - Analyze oral explanation (STT + AI eval)

Architecture: Journey-Based DDD (User)
Database: None (direct OpenAI API)
ISO 27001:2013 compliant - Audio analysis with AI evaluation
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
import os
import logging
import tempfile
import json
import re
from werkzeug.utils import secure_filename

from app.middleware.auth import token_required
from app.services.ai_adapter import AIAdapter

logger = logging.getLogger(__name__)

# Allowed audio formats
ALLOWED_AUDIO_FORMATS = {'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm', 'ogg', 'flac'}

audio_analysis_bp = Blueprint('audio_analysis', __name__)


def allowed_audio_file(filename: str) -> bool:
    """Check if the file has an allowed audio extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_FORMATS


@audio_analysis_bp.route('/audio/analyze-oral', methods=['POST'])
@token_required
def analyze_oral_explanation():
    """
    Analyze an oral explanation for LM24 (Mündliche Erklärung)

    This endpoint combines STT with AI analysis to evaluate
    the quality and accuracy of a spoken explanation.

    Request:
        Content-Type: multipart/form-data
        - audio: Audio file of the oral explanation
        - topic: The topic being explained
        - expected_points: JSON array of key points that should be mentioned
        - language: Language code (default: 'de')

    Response:
        200: Analysis successful
        {
            "success": true,
            "data": {
                "transcription": "...",
                "duration": 5.2,
                "analysis": {
                    "score": 85,
                    "feedback": "...",
                    "covered_points": [...],
                    "missing_points": [...],
                    "suggestions": [...]
                }
            }
        }

        400: Invalid request
        500: Analysis error

    Notes:
        - Two-step process: Whisper STT → GPT-4o-mini Analysis
        - Evaluates completeness, clarity, correctness, structure
        - Score range: 0-100
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
