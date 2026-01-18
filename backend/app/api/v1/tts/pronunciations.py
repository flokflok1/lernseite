"""
LernsystemX TTS API - Pronunciation Rules

Pronunciation rule management endpoints for TTS system.

Pronunciation Rules:
- GET /tts/pronunciations - Get all pronunciation rules from database
- POST /tts/pronunciations - Add a new pronunciation rule
- POST /tts/pronunciations/ai - Generate pronunciation using AI for unknown word

All routes: /api/v1/tts/*
ISO 27001:2013 compliant - TTS security and caching
"""

import logging

from flask import Blueprint, request, jsonify

from app.api.middleware.auth import token_required
from app.api.v1.tts.core import TTS_SERVICE_AVAILABLE

logger = logging.getLogger(__name__)

# Note: Using same blueprint (tts_bp) for pronunciation endpoints
# This blueprint is registered in __init__.py
pronunciations_bp = Blueprint('tts_pronunciations', __name__, url_prefix='/tts')

__all__ = ['tts_pronunciations_bp']


# =============================================================================
# PRONUNCIATION RULES
# =============================================================================

@pronunciations_bp.route('/pronunciations', methods=['GET'])
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
            from app.services.tts_service import TTSService
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


@pronunciations_bp.route('/pronunciations', methods=['POST'])
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

    Response:
    {
        "success": true,
        "message": "Pronunciation added for \"Listeneinkaufspreis\""
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
            from app.services.tts_service import TTSService
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


@pronunciations_bp.route('/pronunciations/ai', methods=['POST'])
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

    Response:
    {
        "success": true,
        "data": {
            "word": "Selbstkostenpreis",
            "phonetic": "Selbstkosten Preis",
            "source": "ai_generated"
        }
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

        from app.services.tts_service import TTSService

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
