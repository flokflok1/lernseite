"""
i18n Public API Endpoints
==========================

Public endpoints for retrieving translations and language information.
These endpoints do NOT require authentication.

Endpoints:
  GET /i18n/bundle/{language_code}   - Get translation bundle for a language
  GET /i18n/languages                - Get all available languages with progress
"""

from flask import Blueprint, request, jsonify
from typing import Tuple, Dict, Any
from app.services.i18n.translations import TranslationManager
from app.services.i18n.languages import LanguageManager
import logging

logger = logging.getLogger(__name__)

i18n_public_bp = Blueprint('i18n_public', __name__, url_prefix='/i18n')


@i18n_public_bp.route('/bundle/<language_code>', methods=['GET'])
def get_translation_bundle(language_code: str) -> Tuple[Dict[str, Any], int]:
    """
    Get translation bundle for a specific language.

    Args:
        language_code: ISO language code (de, en, pl, etc.)

    Query Parameters:
        namespace: Optional namespace filter

    Returns:
        Translation bundle with all key-value pairs for the language
    """
    try:
        namespace = request.args.get('namespace', type=str, default=None)

        bundle = TranslationManager.get_bundle(language_code, namespace)

        return jsonify({
            'success': True,
            'data': bundle,
            'meta': {
                'language_code': language_code,
                'namespace': namespace,
                'count': len(bundle)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching i18n bundle: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'BUNDLE_FETCH_FAILED',
                'message': f'Failed to fetch bundle for language: {language_code}'
            }
        }), 500


@i18n_public_bp.route('/languages', methods=['GET'])
def get_languages() -> Tuple[Dict[str, Any], int]:
    """
    Get all available languages with translation progress.

    Returns:
        List of language records with metadata and progress stats
    """
    try:
        languages = LanguageManager.get_languages()

        return jsonify({
            'success': True,
            'data': languages,
            'meta': {
                'count': len(languages),
                'timestamp': None  # Added by response middleware if needed
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching languages: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'LANGUAGES_FETCH_FAILED',
                'message': 'Failed to fetch available languages'
            }
        }), 500
