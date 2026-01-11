"""
Media Domain - TTS Pronunciation Routes (User Journey)

Pronunciation rules management endpoints.

Endpoints:
- GET /tts/pronunciations - Get pronunciation rules
- POST /tts/pronunciations - Add pronunciation rule
- POST /tts/pronunciations/ai - Generate pronunciation with AI

Architecture: Journey-Based DDD (User)
Database: PostgreSQL via TTSRepository (direct SQL)
ISO 27001:2013 compliant - Pronunciation management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
import logging
from pydantic import ValidationError

from app.middleware.auth import token_required
from app.repositories.tts.core import TTSRepository
from app.services.tts_service import TTSService

logger = logging.getLogger(__name__)

tts_pronunciation_bp = Blueprint('tts_pronunciation', __name__, url_prefix='/tts')


@tts_pronunciation_bp.route('/pronunciations', methods=['GET'])
def get_pronunciations():
    """
    Get pronunciation rules (Public - no auth required)

    Query Parameters:
        language: Language code (default: de)
        search: Search query (optional)

    Response:
        200: List of pronunciation rules
        {
            "success": true,
            "data": {
                "pronunciations": [
                    {
                        "pronunciation_id": "...",
                        "original_word": "Skonto",
                        "phonetic_spelling": "Skonnto",
                        "language": "de",
                        "category": "business"
                    },
                    ...
                ],
                "total": 150
            }
        }

    Notes:
        - Public endpoint for pronunciation lookup
        - Used by TTS preprocessing
        - Cached in-memory after first load
    """
    try:
        language = request.args.get('language', 'de')
        search = request.args.get('search', None)

        if search:
            pronunciations = TTSRepository.search_pronunciations(search, language)
        else:
            pronunciations = TTSRepository.get_all_pronunciations(language)

        return jsonify({
            'success': True,
            'data': {
                'pronunciations': pronunciations,
                'total': len(pronunciations),
                'language': language
            }
        })

    except Exception as e:
        logger.error(f"Get pronunciations error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@tts_pronunciation_bp.route('/pronunciations', methods=['POST'])
@token_required
def add_pronunciation():
    """
    Add pronunciation rule (User auth required)

    Request Body:
        {
            "original_word": "Skonto",
            "phonetic_spelling": "Skonnto",
            "language": "de",
            "category": "business",
            "word_type": "noun"
        }

    Response:
        201: Pronunciation added
        {
            "success": true,
            "data": {
                "pronunciation_id": "...",
                "original_word": "Skonto",
                "phonetic_spelling": "Skonnto"
            }
        }

        400: Validation error
        500: Database error

    Notes:
        - Requires authentication
        - Immediately available for TTS
        - Validated by Pydantic model
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or not data.get('original_word') or not data.get('phonetic_spelling'):
            return jsonify({'success': False, 'error': {'code': 'MISSING_FIELDS', 'message': 'original_word and phonetic_spelling required'}}), 400

        # Add pronunciation
        pronunciation_id = TTSRepository.add_pronunciation(
            original_word=data['original_word'],
            phonetic_spelling=data['phonetic_spelling'],
            language=data.get('language', 'de'),
            category=data.get('category'),
            word_type=data.get('word_type'),
            source='manual',
            is_verified=False
        )

        return jsonify({
            'success': True,
            'data': {
                'pronunciation_id': pronunciation_id,
                'original_word': data['original_word'],
                'phonetic_spelling': data['phonetic_spelling']
            }
        }), 201

    except ValidationError as e:
        return jsonify({'success': False, 'error': {'code': 'VALIDATION_ERROR', 'details': e.errors()}}), 400
    except Exception as e:
        logger.error(f"Add pronunciation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@tts_pronunciation_bp.route('/pronunciations/ai', methods=['POST'])
@token_required
def generate_pronunciation_ai():
    """
    Generate pronunciation with AI (User auth required)

    Request Body:
        {
            "word": "Listeneinkaufspreis",
            "language": "de",
            "context": "Optional context..."
        }

    Response:
        200: Pronunciation generated
        {
            "success": true,
            "data": {
                "word": "Listeneinkaufspreis",
                "phonetic_spelling": "Listen Einkaufs Preis",
                "pronunciation_id": "...",
                "source": "ai_gpt4o-mini"
            }
        }

        400: Invalid request
        500: AI generation failed

    Notes:
        - AI-powered pronunciation generation
        - Uses GPT-4o-mini for analysis
        - Automatically saved to database
        - Requires verification before production use
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or not data.get('word'):
            return jsonify({'success': False, 'error': {'code': 'NO_WORD', 'message': 'Word required'}}), 400

        word = data['word']
        language = data.get('language', 'de')
        context = data.get('context', '')

        # Generate pronunciation with AI
        phonetic_spelling = TTSService.generate_pronunciation_with_ai(word, language, context)

        # Save to database
        pronunciation_id = TTSRepository.add_pronunciation(
            original_word=word,
            phonetic_spelling=phonetic_spelling,
            language=language,
            source='ai_gpt4o-mini',
            is_verified=False
        )

        return jsonify({
            'success': True,
            'data': {
                'word': word,
                'phonetic_spelling': phonetic_spelling,
                'pronunciation_id': pronunciation_id,
                'source': 'ai_gpt4o-mini',
                'verified': False
            }
        })

    except Exception as e:
        logger.error(f"AI pronunciation generation error: {e}")
        return jsonify({'success': False, 'error': {'code': 'AI_ERROR', 'message': str(e)}}), 500
