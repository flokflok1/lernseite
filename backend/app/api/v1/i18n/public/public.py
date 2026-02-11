"""
i18n Public Endpoints
=====================

Public endpoints for translation bundle retrieval and language information.
No authentication required.

Endpoints:
    GET /i18n/bundle/<language_code>                             - Get translation bundle
    GET /i18n/languages                                          - Get available languages
    GET /i18n/languages/<language_code>/progress                 - Get language progress
    GET /i18n/translation/<namespace>/<key_path>/<language_code> - Get single translation
"""

from flask import Blueprint, request, jsonify
from app.application.services.i18n.legacy.service import I18nService
import logging

logger = logging.getLogger(__name__)

i18n_public_bp = Blueprint('i18n_public', __name__, url_prefix='/i18n')


@i18n_public_bp.route('/bundle/<language_code>', methods=['GET'])
def get_bundle(language_code: str):
    """
    Get translation bundle for a language.

    Args:
        language_code: ISO language code (e.g., 'de', 'en', 'pl')

    Query Params:
        namespace: Optional namespace filter

    Returns:
        Translation bundle as nested JSON object
    """
    namespace = request.args.get('namespace')
    bundle = I18nService.get_bundle(language_code, namespace)

    return jsonify({
        'success': True,
        'data': bundle
    })


@i18n_public_bp.route('/languages', methods=['GET'])
def get_languages():
    """
    Get available languages with progress.

    Returns:
        List of available languages with translation progress
    """
    languages = I18nService.get_languages()

    return jsonify({
        'success': True,
        'data': languages
    })


@i18n_public_bp.route('/languages/<language_code>/progress', methods=['GET'])
def get_language_progress(language_code: str):
    """
    Get detailed progress for a language.

    Args:
        language_code: ISO language code

    Returns:
        Detailed translation progress including per-namespace breakdown
    """
    data = I18nService.get_language_progress(language_code)

    if not data:
        return jsonify({
            'success': False,
            'error': {'code': 'NOT_FOUND', 'message': 'Language not found'}
        }), 404

    return jsonify({
        'success': True,
        'data': data
    })


@i18n_public_bp.route('/translation/<namespace>/<key_path>/<language_code>', methods=['GET'])
def get_translation(namespace: str, key_path: str, language_code: str):
    """
    Get single translation with fallback support.

    Args:
        namespace: Namespace (admin, common, etc.)
        key_path: Key path (users.title, etc.)
        language_code: Language code

    Query Params:
        fallback: Use fallback languages (true/false, default: true)

    Returns:
        Translation text or 404
    """
    fallback = request.args.get('fallback', 'true').lower() == 'true'

    text = I18nService.get_translation(namespace, key_path, language_code, fallback)

    if not text:
        return jsonify({
            'success': False,
            'error': {'code': 'NOT_FOUND', 'message': f'Translation not found: {namespace}/{key_path}/{language_code}'}
        }), 404

    return jsonify({
        'success': True,
        'data': {'text': text}
    })
