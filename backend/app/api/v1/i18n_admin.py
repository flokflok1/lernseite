"""
i18n Admin API - Administrative Endpoints for Translation Management

Provides REST API for admin-only operations:
- Translation approval and workflow management
- Translation quality statistics and monitoring
- Cache management and invalidation
"""

from flask import Blueprint, jsonify, request, g
import logging
from typing import Dict, Any

from app.services.i18n_service import I18nService
from app.database import get_connection
from app.repositories.i18n_repository import I18nRepository
from app.utils.exceptions import NotFoundError, ValidationError
from app.middleware.auth import token_required, role_required

logger = logging.getLogger(__name__)

bp = Blueprint('i18n_admin', __name__, url_prefix='/api/v1/i18n')


# ============================================================================
# ADMIN ENDPOINTS - Require admin role
# ============================================================================

@bp.route('/admin/translations/approve/<translation_id>', methods=['POST'])
@role_required('admin', 'moderator')
def approve_translation(translation_id: str):
    """
    POST /api/v1/i18n/admin/translations/approve/{translation_id}

    Approve translation for publication.

    Admin only.

    Returns:
        200: Approved translation
        403: Forbidden
        404: Translation not found
    """
    try:
        translation = I18nService.approve_translation(translation_id, g.current_user.id)

        return jsonify({
            'data': translation,
            'message': 'Translation approved'
        }), 200

    except Exception as e:
        logger.error(f"Error approving translation: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to approve translation'
            }
        }), 500


@bp.route('/admin/statistics/language/<language_code>', methods=['GET'])
@role_required('admin')
def get_language_stats(language_code: str):
    """
    GET /api/v1/i18n/admin/statistics/language/{language_code}

    Get translation progress statistics for a language.

    Admin only.

    Returns:
        200: Language progress statistics
    """
    try:
        progress = I18nService.get_language_progress(language_code)

        if not progress:
            raise NotFoundError(f"No progress data for language: {language_code}")

        return jsonify({
            'data': progress
        }), 200

    except NotFoundError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404

    except Exception as e:
        logger.error(f"Error getting language statistics: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to retrieve statistics'
            }
        }), 500


@bp.route('/admin/quality/low-quality', methods=['GET'])
@role_required('admin')
def get_low_quality_translations():
    """
    GET /api/v1/i18n/admin/quality/low-quality

    Get translations flagged by AI as low quality.

    Admin only.

    Query Parameters:
        - threshold: Quality threshold (0.0-1.0, default: 0.7)
        - language: Filter by language (optional)
        - limit: Max results (default: 100)

    Returns:
        200: List of low-quality translations with AI feedback
    """
    try:
        threshold = float(request.args.get('threshold', 0.7))
        language = request.args.get('language')
        limit = int(request.args.get('limit', 100))

        translations = I18nService.get_low_quality_translations(
            threshold, language, limit
        )

        return jsonify({
            'data': translations,
            'total': len(translations),
            'threshold': threshold
        }), 200

    except ValueError as e:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid threshold or limit'
            }
        }), 400

    except Exception as e:
        logger.error(f"Error getting low-quality translations: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to retrieve translations'
            }
        }), 500


@bp.route('/admin/cache/invalidate', methods=['POST'])
@role_required('admin')
def invalidate_cache():
    """
    POST /api/v1/i18n/admin/cache/invalidate

    Invalidate translation caches.

    Admin only.

    Request Body:
        - language: Language code (optional) - if not provided, invalidates all

    Returns:
        200: Cache invalidated
    """
    try:
        data = request.get_json() or {}
        language = data.get('language')

        if language:
            I18nService.invalidate_bundle_cache(language)
            message = f"Cache invalidated for language: {language}"
        else:
            I18nService.invalidate_all_caches()
            message = "All translation caches invalidated"

        logger.info(f"Cache invalidation triggered by admin: {g.current_user.id}")

        return jsonify({
            'data': {'message': message}
        }), 200

    except Exception as e:
        logger.error(f"Error invalidating cache: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to invalidate cache'
            }
        }), 500
