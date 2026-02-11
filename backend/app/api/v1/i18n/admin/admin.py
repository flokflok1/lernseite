"""
i18n Admin API - Administrative Endpoints for Translation Management
====================================================================

Admin endpoints for translation approval, quality monitoring, and statistics.

Endpoints:
    POST /i18n/admin/translations/approve/<id>    - Approve translation
    GET  /i18n/admin/statistics/language/<code>    - Get language statistics
    GET  /i18n/admin/quality/low-quality           - Get low-quality translations
"""

from flask import Blueprint, jsonify, request, g
import logging

from app.application.services.i18n.legacy.service import I18nService
from app.api.middleware.auth import permission_required

logger = logging.getLogger(__name__)

i18n_admin_bp = Blueprint('i18n_admin', __name__, url_prefix='/i18n')


@i18n_admin_bp.route('/admin/translations/approve/<translation_id>', methods=['POST'])
@permission_required('admin.system:write')
def approve_translation(translation_id: str):
    """
    Approve translation for publication.

    Args:
        translation_id: ID of translation to approve

    Returns:
        Approved translation
    """
    try:
        translation = I18nService.approve_translation(translation_id, g.current_user.id)

        return jsonify({
            'success': True,
            'data': translation
        }), 200

    except Exception as e:
        logger.error(f"Error approving translation: {e}")
        return jsonify({
            'success': False,
            'error': {'code': 'INTERNAL_ERROR', 'message': 'Failed to approve translation'}
        }), 500


@i18n_admin_bp.route('/admin/statistics/language/<language_code>', methods=['GET'])
@permission_required('admin.system:read')
def get_language_stats(language_code: str):
    """
    Get translation progress statistics for a language.

    Args:
        language_code: ISO language code

    Returns:
        Language progress statistics
    """
    progress = I18nService.get_language_progress(language_code)

    if not progress:
        return jsonify({
            'success': False,
            'error': {'code': 'NOT_FOUND', 'message': f'No progress data for language: {language_code}'}
        }), 404

    return jsonify({
        'success': True,
        'data': progress
    })


@i18n_admin_bp.route('/admin/quality/low-quality', methods=['GET'])
@permission_required('admin.system:read')
def get_low_quality_translations():
    """
    Get translations flagged by AI as low quality.

    Query Params:
        threshold: Quality threshold (0.0-1.0, default: 0.7)
        language: Filter by language (optional)
        limit: Max results (default: 100)

    Returns:
        List of low-quality translations with AI feedback
    """
    try:
        threshold = float(request.args.get('threshold', 0.7))
        language = request.args.get('language')
        limit = int(request.args.get('limit', 100))

        translations = I18nService.get_low_quality_translations(
            threshold, language, limit
        )

        return jsonify({
            'success': True,
            'data': translations,
            'total': len(translations),
            'threshold': threshold
        })

    except ValueError:
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': 'Invalid threshold or limit'}
        }), 400

    except Exception as e:
        logger.error(f"Error getting low-quality translations: {e}")
        return jsonify({
            'success': False,
            'error': {'code': 'INTERNAL_ERROR', 'message': 'Failed to retrieve translations'}
        }), 500
