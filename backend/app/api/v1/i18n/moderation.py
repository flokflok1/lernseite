"""
i18n Admin Moderation Endpoints
===============================

Admin endpoints for translation moderation, AI review, and configuration.

Endpoints:
    GET  /i18n/admin/moderation/dashboard      - Get moderation dashboard
    GET  /i18n/admin/moderation/queue          - Get moderation queue
    POST /i18n/admin/moderation/queue/<id>/review - Review queue item
    POST /i18n/admin/moderation/ai-review      - Trigger AI review
    GET  /i18n/admin/config                    - Get AI config
    PUT  /i18n/admin/config                    - Update AI config
    POST /i18n/admin/cache/invalidate          - Invalidate cache
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.application.services.i18n_service import I18nService
from app.api.middleware.auth import permission_required
import logging

logger = logging.getLogger(__name__)

i18n_moderation_bp = Blueprint('i18n_moderation', __name__, url_prefix='/i18n')


@i18n_moderation_bp.route('/admin/moderation/dashboard', methods=['GET'])
@permission_required('i18n.moderate')
def get_moderation_dashboard():
    """
    Get moderation dashboard.

    Returns:
        Dashboard statistics including pending items, recent activity
    """
    data = I18nService.get_moderation_dashboard()

    return jsonify({
        'success': True,
        'data': data
    })


@i18n_moderation_bp.route('/admin/moderation/queue', methods=['GET'])
@permission_required('i18n.moderate')
def get_moderation_queue():
    """
    Get moderation queue.

    Query Params:
        status: Filter by status (optional)
        language_code: Filter by language (optional)
        limit: Max results, default 50, max 100 (optional)

    Returns:
        List of items in moderation queue
    """
    status = request.args.get('status')
    language_code = request.args.get('language_code')
    limit = min(int(request.args.get('limit', 50)), 100)

    queue = I18nService.get_moderation_queue(
        status=status,
        language_code=language_code,
        limit=limit
    )

    return jsonify({
        'success': True,
        'data': queue
    })


@i18n_moderation_bp.route('/admin/moderation/queue/<queue_id>/review', methods=['POST'])
@permission_required('i18n.moderate')
def review_queue_item(queue_id: str):
    """
    Review a queue item.

    Args:
        queue_id: ID of queue item to review

    Request Body:
        decision: 'approve' or 'reject'
        comment: Optional review comment

    Returns:
        Success status
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    decision = data.get('decision')
    if decision not in ('approve', 'reject'):
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_INPUT', 'message': 'decision must be approve or reject'}
        }), 400

    success = I18nService.review_queue_item(
        queue_id=queue_id,
        user_id=user_id,
        decision=decision,
        comment=data.get('comment')
    )

    return jsonify({'success': success})


@i18n_moderation_bp.route('/admin/moderation/ai-review', methods=['POST'])
@permission_required('i18n.moderate')
def trigger_ai_review():
    """
    Trigger AI review for a translation/suggestion.

    Returns:
        AI review result with quality score and recommendation
    """
    # TODO: Implement AI review
    return jsonify({
        'success': True,
        'data': {
            'review_id': None,
            'quality_score': 0.85,
            'recommendation': 'approve'
        }
    })


@i18n_moderation_bp.route('/admin/config', methods=['GET'])
@permission_required('i18n.config')
def get_ai_config():
    """
    Get AI moderation config.

    Returns:
        Current AI moderation configuration
    """
    config = I18nService.get_ai_config()

    return jsonify({
        'success': True,
        'data': config
    })


@i18n_moderation_bp.route('/admin/config', methods=['PUT'])
@permission_required('i18n.config')
def update_ai_config():
    """
    Update AI moderation config.

    Request Body:
        moderation_model: AI model for moderation (optional)
        auto_approve_threshold: Threshold for auto-approval (optional)
        auto_reject_threshold: Threshold for auto-rejection (optional)
        human_review_threshold: Threshold for human review (optional)
        enabled_languages: List of enabled language codes (optional)

    Returns:
        Updated configuration
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_INPUT', 'message': 'No config data provided'}
        }), 400

    # Valid config keys
    valid_keys = [
        'moderation_model',
        'auto_approve_threshold',
        'auto_reject_threshold',
        'human_review_threshold',
        'moderation_prompt',
        'batch_size',
        'enabled_languages'
    ]

    updated = []
    for key, value in data.items():
        if key in valid_keys:
            success = I18nService.update_ai_config(key, value, user_id)
            if success:
                updated.append(key)

    return jsonify({
        'success': True,
        'data': {
            'updated_keys': updated,
            'config': I18nService.get_ai_config()
        }
    })


@i18n_moderation_bp.route('/admin/cache/invalidate', methods=['POST'])
@permission_required('i18n.config')
def invalidate_cache():
    """
    Invalidate translation cache.

    Request Body:
        language_code: Specific language to invalidate (optional, all if not provided)

    Returns:
        Success status
    """
    data = request.get_json() or {}
    language_code = data.get('language_code')

    I18nService.invalidate_cache(language_code)

    return jsonify({'success': True})
