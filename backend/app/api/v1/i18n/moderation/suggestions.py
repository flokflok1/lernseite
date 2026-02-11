"""
i18n Community Suggestions Endpoints
=====================================

Endpoints for community translation suggestions and voting.

Endpoints:
    POST /i18n/suggestions                    - Submit a suggestion
    GET  /i18n/suggestions                    - Get suggestions for a key
    POST /i18n/suggestions/<id>/vote          - Vote on a suggestion
    POST /i18n/request-translation            - Request translation for a key
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.application.services.i18n.legacy.service import I18nService
import logging

logger = logging.getLogger(__name__)

i18n_suggestions_bp = Blueprint('i18n_suggestions', __name__, url_prefix='/i18n')


@i18n_suggestions_bp.route('/suggestions', methods=['POST'])
@jwt_required()
def submit_suggestion():
    """
    Submit a translation suggestion.

    Request Body:
        key_id: ID of the translation key (required)
        language_code: Target language code (required)
        suggested_value: Suggested translation (required)
        comment: Optional comment about the suggestion

    Returns:
        Created suggestion with ID
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get('key_id') or not data.get('language_code') or not data.get('suggested_value'):
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_INPUT', 'message': 'key_id, language_code, and suggested_value required'}
        }), 400

    suggestion = I18nService.submit_suggestion(
        key_id=data['key_id'],
        language_code=data['language_code'],
        suggested_value=data['suggested_value'],
        user_id=user_id,
        comment=data.get('comment')
    )

    if not suggestion:
        return jsonify({
            'success': False,
            'error': {'code': 'CREATE_FAILED', 'message': 'Failed to create suggestion'}
        }), 500

    return jsonify({
        'success': True,
        'data': suggestion
    }), 201


@i18n_suggestions_bp.route('/suggestions', methods=['GET'])
def get_suggestions():
    """
    Get suggestions for a translation key.

    Query Params:
        key_id: Filter by key ID (optional)
        language_code: Filter by language (optional)
        status: Filter by status (optional)
        limit: Max results, default 50 (optional)

    Returns:
        List of translation suggestions
    """
    key_id = request.args.get('key_id', type=int)
    language_code = request.args.get('language_code')
    status = request.args.get('status')
    limit = min(int(request.args.get('limit', 50)), 100)

    suggestions = I18nService.get_suggestions(
        key_id=key_id,
        language_code=language_code,
        status=status,
        limit=limit
    )

    return jsonify({
        'success': True,
        'data': suggestions
    })


@i18n_suggestions_bp.route('/suggestions/<int:suggestion_id>/vote', methods=['POST'])
@jwt_required()
def vote_suggestion(suggestion_id: int):
    """
    Vote on a translation suggestion.

    Args:
        suggestion_id: ID of the suggestion to vote on

    Request Body:
        vote: 1 (upvote) or -1 (downvote)

    Returns:
        Updated vote count
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    vote = data.get('vote')
    if vote not in (1, -1):
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_INPUT', 'message': 'vote must be 1 or -1'}
        }), 400

    result = I18nService.vote_suggestion(
        suggestion_id=suggestion_id,
        user_id=user_id,
        vote=vote
    )

    return jsonify({
        'success': True,
        'data': result
    })


@i18n_suggestions_bp.route('/request-translation', methods=['POST'])
@jwt_required()
def request_translation():
    """
    Request translation for a key that is missing in a language.

    Request Body:
        key_id: ID of the translation key (required)
        language_code: Target language code (required)

    Returns:
        Success status
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get('key_id') or not data.get('language_code'):
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_INPUT', 'message': 'key_id and language_code required'}
        }), 400

    success = I18nService.request_translation(
        key_id=data['key_id'],
        language_code=data['language_code'],
        user_id=user_id
    )

    return jsonify({'success': success})
