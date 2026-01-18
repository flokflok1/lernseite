"""
i18n Suggestions Endpoints
==========================

Authenticated endpoints for translation suggestions and voting.

Endpoints:
    POST /i18n/suggestions              - Submit a translation suggestion
    GET  /i18n/suggestions              - Get translation suggestions
    POST /i18n/suggestions/<id>/vote    - Vote for a suggestion
    POST /i18n/request-translation      - Request translation for a language
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.i18n_service import I18nService
import logging

logger = logging.getLogger(__name__)

i18n_suggestions_bp = Blueprint('i18n_suggestions', __name__, url_prefix='/i18n')


@i18n_suggestions_bp.route('/suggestions', methods=['POST'])
@jwt_required()
def submit_suggestion():
    """
    Submit a translation suggestion.

    Request Body:
        suggested_value: The suggested translation text (required)
        language_code: Target language code (required)
        translation_id: ID of existing translation to improve (optional)
        key_id: ID of key to translate (optional)
        reason: Reason for suggestion (optional)

    Returns:
        suggestion_id of created suggestion
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get('suggested_value') or not data.get('language_code'):
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_INPUT', 'message': 'suggested_value and language_code required'}
        }), 400

    suggestion_id = I18nService.submit_suggestion(
        user_id=user_id,
        language_code=data['language_code'],
        suggested_value=data['suggested_value'],
        translation_id=data.get('translation_id'),
        key_id=data.get('key_id'),
        reason=data.get('reason')
    )

    if not suggestion_id:
        return jsonify({
            'success': False,
            'error': {'code': 'CREATE_FAILED', 'message': 'Failed to submit suggestion'}
        }), 500

    return jsonify({
        'success': True,
        'data': {'suggestion_id': suggestion_id}
    }), 201


@i18n_suggestions_bp.route('/suggestions', methods=['GET'])
@jwt_required()
def get_suggestions():
    """
    Get translation suggestions.

    Query Params:
        language_code: Filter by language (optional)
        status: Filter by status, default 'pending' (optional)
        limit: Max results, default 50, max 100 (optional)

    Returns:
        List of translation suggestions
    """
    language_code = request.args.get('language_code')
    status = request.args.get('status', 'pending')
    limit = min(int(request.args.get('limit', 50)), 100)

    suggestions = I18nService.get_suggestions(
        language_code=language_code,
        status=status,
        limit=limit
    )

    return jsonify({
        'success': True,
        'data': suggestions
    })


@i18n_suggestions_bp.route('/suggestions/<suggestion_id>/vote', methods=['POST'])
@jwt_required()
def vote_suggestion(suggestion_id: str):
    """
    Vote for a suggestion.

    Args:
        suggestion_id: ID of suggestion to vote on

    Request Body:
        vote_type: 'up' or 'down'

    Returns:
        Success status
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    vote_type = data.get('vote_type')
    if vote_type not in ('up', 'down'):
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_INPUT', 'message': 'vote_type must be up or down'}
        }), 400

    success = I18nService.vote_suggestion(user_id, suggestion_id, vote_type)

    return jsonify({'success': success})


@i18n_suggestions_bp.route('/request-translation', methods=['POST'])
@jwt_required()
def request_translation():
    """
    Request translation for a language.

    Request Body:
        target_language: Language code to translate to (required)
        scope: 'full' or 'partial', default 'full' (optional)
        namespace_id: Specific namespace to translate (optional)

    Returns:
        Translation request details
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get('target_language'):
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_INPUT', 'message': 'target_language required'}
        }), 400

    result = I18nService.request_translation(
        user_id=user_id,
        target_language=data['target_language'],
        scope=data.get('scope', 'full'),
        namespace_id=data.get('namespace_id')
    )

    if not result:
        return jsonify({
            'success': False,
            'error': {'code': 'REQUEST_FAILED', 'message': 'Failed to request translation'}
        }), 500

    return jsonify({
        'success': True,
        'data': result
    })
