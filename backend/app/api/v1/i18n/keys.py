"""
i18n Admin Keys & Translations Endpoints
========================================

Admin endpoints for managing translation keys and translations.

Endpoints:
    GET  /i18n/admin/namespaces                         - Get all namespaces
    GET  /i18n/admin/keys                               - Get translation keys
    POST /i18n/admin/keys                               - Create a new key
    GET  /i18n/admin/keys/<key_id>/translations         - Get translations for a key
    PUT  /i18n/admin/keys/<key_id>/translations/<lang>  - Set/update translation
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.application.services.i18n_service import I18nService
from app.api.middleware.auth import permission_required
import logging

logger = logging.getLogger(__name__)

i18n_keys_bp = Blueprint('i18n_keys', __name__, url_prefix='/i18n')


@i18n_keys_bp.route('/admin/namespaces', methods=['GET'])
@permission_required('i18n.view')
def get_namespaces():
    """
    Get all namespaces.

    Returns:
        List of all i18n namespaces
    """
    namespaces = I18nService.get_namespaces()

    return jsonify({
        'success': True,
        'data': namespaces
    })


@i18n_keys_bp.route('/admin/keys', methods=['GET'])
@permission_required('i18n.view')
def get_keys():
    """
    Get translation keys.

    Query Params:
        namespace_id: Filter by namespace (optional)
        search: Search in key paths (optional)
        limit: Max results, default 100, max 500 (optional)
        offset: Pagination offset (optional)

    Returns:
        List of translation keys with metadata
    """
    namespace_id = request.args.get('namespace_id', type=int)
    search = request.args.get('search')
    limit = min(int(request.args.get('limit', 100)), 500)
    offset = int(request.args.get('offset', 0))

    keys = I18nService.get_keys(
        namespace_id=namespace_id,
        search=search,
        limit=limit,
        offset=offset
    )

    return jsonify({
        'success': True,
        'data': keys
    })


@i18n_keys_bp.route('/admin/keys', methods=['POST'])
@permission_required('i18n.config')
def create_key():
    """
    Create a new translation key.

    Request Body:
        namespace_id: Namespace for the key (required)
        key_path: Full key path e.g. 'common.loading' (required)
        description: Key description (optional)
        context_hint: Context for translators (optional)
        max_length: Max translation length (optional)
        placeholders: List of placeholder names (optional)

    Returns:
        key_id of created key
    """
    data = request.get_json()

    if not data.get('namespace_id') or not data.get('key_path'):
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_INPUT', 'message': 'namespace_id and key_path required'}
        }), 400

    key_id = I18nService.create_key(
        namespace_id=data['namespace_id'],
        key_path=data['key_path'],
        description=data.get('description'),
        context_hint=data.get('context_hint'),
        max_length=data.get('max_length'),
        placeholders=data.get('placeholders')
    )

    if not key_id:
        return jsonify({
            'success': False,
            'error': {'code': 'CREATE_FAILED', 'message': 'Failed to create key'}
        }), 500

    return jsonify({
        'success': True,
        'data': {'key_id': key_id}
    }), 201


@i18n_keys_bp.route('/admin/keys/<key_id>/translations', methods=['GET'])
@permission_required('i18n.view')
def get_key_translations(key_id: str):
    """
    Get translations for a key.

    Args:
        key_id: ID of the translation key

    Returns:
        Dictionary of language_code -> translation value
    """
    translations = I18nService.get_key_translations(key_id)

    return jsonify({
        'success': True,
        'data': translations
    })


@i18n_keys_bp.route('/admin/keys/<int:key_id>/translations/<language_code>', methods=['PUT'])
@permission_required('i18n.config')
def set_translation(key_id: int, language_code: str):
    """
    Set or update a translation.

    Args:
        key_id: ID of the translation key
        language_code: Target language code

    Request Body:
        value: Translation value (required)
        is_machine_translated: Whether this is machine translated (optional)

    Returns:
        Success status
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get('value'):
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_INPUT', 'message': 'value is required'}
        }), 400

    success = I18nService.set_translation(
        key_id=key_id,
        language_code=language_code,
        value=data['value'],
        translator_id=user_id,
        is_machine_translated=data.get('is_machine_translated', False)
    )

    return jsonify({'success': success})
