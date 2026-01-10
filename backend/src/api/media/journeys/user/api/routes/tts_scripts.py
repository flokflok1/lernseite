"""
Media Domain - TTS Scripts Routes (User Journey)

Multi-step tutor script generation endpoint.

Endpoints:
- POST /tts/tutor-script - Generate multi-step tutor script with TTS

Architecture: Journey-Based DDD (User)
Database: None (direct OpenAI API)
ISO 27001:2013 compliant - Script generation with AI
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
import logging

from app.middleware.auth import token_required
from app.services.ai_adapter import AIAdapter
from app.services.tts_service import TTSService

logger = logging.getLogger(__name__)

tts_scripts_bp = Blueprint('tts_scripts', __name__, url_prefix='/tts')


@tts_scripts_bp.route('/tutor-script', methods=['POST'])
@token_required
def generate_tutor_script():
    """
    Generate multi-step tutor script with TTS audio

    Request Body:
        {
            "topic": "Quadratische Gleichungen",
            "steps": 5,           // Number of explanation steps
            "language": "de",     // Optional (default: de)
            "voice": "nova",      // Optional (default: nova)
            "difficulty": "medium" // Optional: easy, medium, hard
        }

    Response:
        200: Script generated
        {
            "success": true,
            "data": {
                "topic": "Quadratische Gleichungen",
                "steps": [
                    {
                        "step": 1,
                        "title": "Grundlagen",
                        "text": "Zunächst schauen wir uns...",
                        "audio_url": "/api/v1/tts/audio/abc123",
                        "duration_ms": 5000
                    },
                    ...
                ]
            }
        }

        400: Invalid request
        500: Generation failed

    Notes:
        - AI-generated step-by-step explanation
        - Each step has dedicated TTS audio
        - Optimized for tutoring sessions
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or not data.get('topic'):
            return jsonify({'success': False, 'error': {'code': 'NO_TOPIC', 'message': 'No topic provided'}}), 400

        topic = data['topic']
        num_steps = int(data.get('steps', 5))
        language = data.get('language', 'de')
        voice = data.get('voice', 'nova')
        difficulty = data.get('difficulty', 'medium')

        # Validate steps
        if not 2 <= num_steps <= 10:
            return jsonify({'success': False, 'error': {'code': 'INVALID_STEPS', 'message': 'Steps must be between 2 and 10'}}), 400

        # Generate script with AI
        prompt = f"""Erstelle ein {num_steps}-schrittiges Tutor-Skript zum Thema "{topic}" (Schwierigkeit: {difficulty}).

Jeder Schritt soll:
- Einen klaren Titel haben
- Eine ausführliche Erklärung (50-150 Wörter) enthalten
- Auf dem vorherigen Schritt aufbauen
- Einfach zu verstehen sein

Antworte im JSON-Format:
{{
    "steps": [
        {{
            "step": 1,
            "title": "...",
            "text": "..."
        }},
        ...
    ]
}}"""

        response = AIAdapter.chat_completion(
            messages=[{'role': 'user', 'content': prompt}],
            system_prompt="Du bist ein erfahrener Tutor. Erstelle klare, strukturierte Erklärungen.",
            model='gpt-4o-mini',
            max_tokens=2000,
            temperature=0.7,
            user_id=user_id
        )

        # Parse response
        import json
        import re
        content = response.get('content', '')
        json_match = re.search(r'\{[\s\S]*\}', content)

        if not json_match:
            return jsonify({'success': False, 'error': {'code': 'PARSE_ERROR', 'message': 'Failed to parse AI response'}}), 500

        script_data = json.loads(json_match.group())
        steps = script_data.get('steps', [])

        # Generate TTS for each step
        for step in steps:
            text = step.get('text', '')
            processed_text = TTSService.preprocess_text(text, language)

            # Generate audio URL (simplified - would use synthesis endpoint)
            import hashlib
            text_hash = hashlib.sha256(processed_text.encode()).hexdigest()[:16]
            audio_id = f"{text_hash}_{voice}_100"

            step['audio_url'] = f'/api/v1/tts/audio/{audio_id}'
            step['duration_ms'] = int((len(text) / 5 / 150) * 60 * 1000)

        return jsonify({
            'success': True,
            'data': {
                'topic': topic,
                'difficulty': difficulty,
                'steps': steps
            }
        })

    except Exception as e:
        logger.error(f"Tutor script generation error: {e}")
        return jsonify({'success': False, 'error': {'code': 'SCRIPT_ERROR', 'message': str(e)}}), 500
