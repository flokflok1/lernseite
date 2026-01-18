"""
i18n Public API - Public and Authenticated User Endpoints

Provides REST API for:
- Translation bundle retrieval (for frontend)
- Language management
- Community translation suggestions and voting
"""

from flask import Blueprint, jsonify, request, g
import logging
from typing import Dict, Any

from app.services.i18n_service import I18nService
from app.infrastructure.persistence.database import get_connection
from app.infrastructure.persistence.repositories.i18n_repository import I18nRepository
from app.infrastructure.utils.exceptions import NotFoundError, ValidationError, UnauthorizedError
from app.api.middleware.auth import token_required, role_required

logger = logging.getLogger(__name__)

public_bp = Blueprint('i18n_public', __name__, url_prefix='/i18n')


# ============================================================================
# PUBLIC ENDPOINTS - No authentication required
# ============================================================================

@public_bp.route('/languages', methods=['GET'])
def get_languages():
    """
    GET /api/v1/i18n/languages

    Get all supported languages.

    Query Parameters:
        - primary_only: Return only primary languages (true/false, default: false)

    Returns:
        200: {data: Language[], total: int}

    Example:
        GET /api/v1/i18n/languages
        {
            "data": [
                {"code": "de", "name": "Deutsch", "priority": 1, "is_primary": true},
                {"code": "pl", "name": "Polski", "priority": 2, "is_primary": true},
                {"code": "en", "name": "English", "priority": 3, "is_primary": true}
            ],
            "total": 3
        }
    """
    try:
        primary_only = request.args.get('primary_only', 'false').lower() == 'true'

        if primary_only:
            languages = I18nService.get_primary_languages()
        else:
            languages = I18nService.get_supported_languages()

        return jsonify({
            'data': languages,
            'total': len(languages)
        }), 200

    except Exception as e:
        logger.error(f"Error getting languages: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to retrieve languages'
            }
        }), 500


@public_bp.route('/bundle/<language_code>', methods=['GET'])
def get_bundle(language_code: str):
    """
    GET /api/v1/i18n/bundle/{language_code}

    Get translation bundle for frontend (entire language).

    Path Parameters:
        - language_code: Language code (de, en, pl, etc.)

    Query Parameters:
        - namespace: Optional namespace filter (admin, common, etc.)

    Returns:
        200: Nested dictionary of all translations
        404: Language not found

    Example:
        GET /api/v1/i18n/bundle/de
        {
            "admin": {
                "users": {"title": "Benutzer", "description": "Verwalten Sie Benutzer"},
                "courses": {"title": "Kurse"}
            },
            "common": {
                "ok": "OK",
                "cancel": "Abbrechen"
            }
        }
    """
    try:
        # Verify language exists
        languages = I18nService.get_supported_languages()
        if not any(l['language_code'] == language_code for l in languages):
            raise NotFoundError(f"Language {language_code} not supported")

        namespace = request.args.get('namespace')

        # Get bundle
        bundle = I18nService.get_translation_bundle(language_code, namespace)

        return jsonify(bundle), 200

    except NotFoundError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404

    except Exception as e:
        logger.error(f"Error getting bundle for {language_code}: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to retrieve translation bundle'
            }
        }), 500


@public_bp.route('/translation/<namespace>/<key_path>/<language_code>', methods=['GET'])
def get_translation(namespace: str, key_path: str, language_code: str):
    """
    GET /api/v1/i18n/translation/{namespace}/{key_path}/{language_code}

    Get single translation with fallback support.

    Path Parameters:
        - namespace: Namespace (admin, common, etc.)
        - key_path: Key path (users.title, etc.)
        - language_code: Language code

    Query Parameters:
        - fallback: Use fallback languages (true/false, default: true)

    Returns:
        200: {data: {text: string}}
        404: Translation not found
    """
    try:
        fallback = request.args.get('fallback', 'true').lower() == 'true'

        text = I18nService.get_translation(namespace, key_path, language_code, fallback)

        if not text:
            raise NotFoundError(f"Translation not found: {namespace}/{key_path}/{language_code}")

        return jsonify({
            'data': {'text': text}
        }), 200

    except NotFoundError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404

    except Exception as e:
        logger.error(f"Error getting translation {namespace}/{key_path}/{language_code}: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to retrieve translation'
            }
        }), 500


@public_bp.route('/suggestions', methods=['GET'])
def get_suggestions():
    """
    GET /api/v1/i18n/suggestions

    Get pending community translation suggestions.

    Query Parameters:
        - language: Filter by language (optional)
        - limit: Max results (default: 100, max: 500)

    Returns:
        200: {data: Suggestion[], total: int}
    """
    try:
        language = request.args.get('language')
        limit = min(int(request.args.get('limit', 100)), 500)

        suggestions = I18nService.get_pending_suggestions(language, limit)

        return jsonify({
            'data': suggestions,
            'total': len(suggestions)
        }), 200

    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to retrieve suggestions'
            }
        }), 500


# ============================================================================
# AUTHENTICATED ENDPOINTS - Require login
# ============================================================================

@public_bp.route('/suggest', methods=['POST'])
@token_required
def create_suggestion():
    """
    POST /api/v1/i18n/suggest

    Create community translation suggestion.

    Request Body:
        - namespace: Namespace code (required)
        - key_path: Key path (required)
        - language_code: Language code (required)
        - suggested_text: Suggested translation (required)
        - reason: Reason for suggestion (optional)

    Returns:
        201: Created suggestion
        400: Validation error
        401: Unauthorized

    Example:
        POST /api/v1/i18n/suggest
        {
            "namespace": "admin",
            "key_path": "users.title",
            "language_code": "de",
            "suggested_text": "Benutzer",
            "reason": "Better phrasing"
        }
    """
    try:
        data = request.get_json()

        # Validate required fields
        required = ['namespace', 'key_path', 'language_code', 'suggested_text']
        missing = [f for f in required if f not in data]
        if missing:
            raise ValidationError(f"Missing required fields: {', '.join(missing)}")

        # Create suggestion
        suggestion = I18nService.suggest_translation(
            namespace_code=data['namespace'],
            key_path=data['key_path'],
            language_code=data['language_code'],
            suggested_text=data['suggested_text'],
            user_id=g.current_user.id,
            reason=data.get('reason', '')
        )

        return jsonify({
            'data': suggestion,
            'message': 'Translation suggestion created'
        }), 201

    except ValidationError as e:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400

    except Exception as e:
        logger.error(f"Error creating suggestion: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to create suggestion'
            }
        }), 500


@public_bp.route('/suggestion/<suggestion_id>/vote', methods=['POST'])
@token_required
def vote_suggestion(suggestion_id: str):
    """
    POST /api/v1/i18n/suggestion/{suggestion_id}/vote

    Vote on translation suggestion (+1 upvote, -1 downvote).

    Request Body:
        - vote: 1 (upvote) or -1 (downvote)

    Returns:
        200: Updated suggestion with vote score
        400: Invalid vote value
        404: Suggestion not found
    """
    try:
        data = request.get_json()

        if 'vote' not in data:
            raise ValidationError("Missing 'vote' field")

        vote_value = int(data['vote'])
        if vote_value not in [-1, 1]:
            raise ValidationError("Vote must be 1 (upvote) or -1 (downvote)")

        suggestion = I18nService.vote_on_suggestion(
            suggestion_id,
            g.current_user.id,
            vote_value
        )

        return jsonify({
            'data': suggestion,
            'message': 'Vote recorded'
        }), 200

    except ValueError as e:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid vote value'
            }
        }), 400

    except ValidationError as e:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400

    except Exception as e:
        logger.error(f"Error voting on suggestion: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to record vote'
            }
        }), 500
