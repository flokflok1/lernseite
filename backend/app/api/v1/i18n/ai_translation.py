"""
i18n Admin AI Translation Endpoints
===================================

Admin endpoints for AI-powered translation generation and seeding.

Endpoints:
    POST /i18n/admin/ai/translate       - Generate AI translation for single key
    POST /i18n/admin/ai/translate/bulk  - Generate AI translations for multiple keys
    POST /i18n/admin/seed-keys          - Seed keys from frontend messages
    POST /i18n/admin/seed-all-locales   - Seed all locales at once
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.application.services.i18n_service import I18nService
from app.api.middleware.auth import permission_required
import logging

logger = logging.getLogger(__name__)

i18n_ai_translation_bp = Blueprint('i18n_ai_translation', __name__, url_prefix='/i18n')


@i18n_ai_translation_bp.route('/admin/ai/translate', methods=['POST'])
@permission_required('i18n.config')
def ai_translate():
    """
    Generate AI translation for a single key.

    Request Body:
        key_id: ID of key to translate (required)
        target_language: Target language code (required)

    Returns:
        Generated translation with metadata
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get('key_id') or not data.get('target_language'):
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_INPUT', 'message': 'key_id and target_language required'}
        }), 400

    result = I18nService.generate_ai_translation(
        key_id=data['key_id'],
        target_language=data['target_language'],
        user_id=user_id
    )

    if not result or not result.get('success'):
        return jsonify({
            'success': False,
            'error': {'code': 'TRANSLATION_FAILED', 'message': result.get('error', 'Translation failed')}
        }), 500

    return jsonify({
        'success': True,
        'data': result
    })


@i18n_ai_translation_bp.route('/admin/ai/translate/bulk', methods=['POST'])
@permission_required('i18n.config')
def ai_translate_bulk():
    """
    Generate AI translations for multiple missing keys.

    Request Body:
        target_language: Target language code (required)
        namespace_id: Filter by namespace (optional)
        limit: Max keys to translate, default 50, max 100 (optional)

    Returns:
        Bulk translation results with success/failure counts
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get('target_language'):
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_INPUT', 'message': 'target_language required'}
        }), 400

    result = I18nService.bulk_generate_translations(
        target_language=data['target_language'],
        namespace_id=data.get('namespace_id'),
        user_id=user_id,
        limit=min(data.get('limit', 50), 100)
    )

    return jsonify({
        'success': True,
        'data': result
    })


@i18n_ai_translation_bp.route('/admin/seed-keys', methods=['POST'])
@permission_required('i18n.config')
def seed_keys():
    """
    Seed i18n keys from frontend default messages.

    Request Body:
        messages: Dictionary of key_path -> value (required)

    Returns:
        Seed results with created/updated counts
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    messages = data.get('messages', {})

    if not messages:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_INPUT', 'message': 'messages object required'}
        }), 400

    try:
        from app.infrastructure.persistence.database.connection import fetch_one, fetch_all

        results = {'created': 0, 'updated': 0, 'errors': []}

        # Get namespace mapping
        ns_query = "SELECT namespace_id, namespace_code FROM i18n_namespaces"
        ns_rows = fetch_all(ns_query) or []
        ns_map = {r['namespace_code']: r['namespace_id'] for r in ns_rows}

        for key_path, value in messages.items():
            # Extract namespace from key (first part before .)
            parts = key_path.split('.')
            ns_code = parts[0] if len(parts) > 1 else 'common'
            namespace_id = ns_map.get(ns_code, ns_map.get('common', 1))

            # Check if key exists
            check = fetch_one(
                "SELECT key_id FROM i18n_keys WHERE key_path = %s",
                (key_path,)
            )

            if check:
                key_id = check['key_id']
                results['updated'] += 1
            else:
                # Create new key
                result = fetch_one(
                    "INSERT INTO i18n_keys (namespace_id, key_path) VALUES (%s, %s) RETURNING key_id",
                    (namespace_id, key_path)
                )
                key_id = result['key_id'] if result else None
                results['created'] += 1

            if key_id:
                # Set German translation
                I18nService.set_translation(
                    key_id=key_id,
                    language_code='de',
                    value=value,
                    translator_id=user_id,
                    is_machine_translated=False
                )

        return jsonify({
            'success': True,
            'data': results
        })

    except Exception as e:
        logger.error(f"Error seeding keys: {e}")
        return jsonify({
            'success': False,
            'error': {'code': 'SEED_FAILED', 'message': str(e)}
        }), 500


@i18n_ai_translation_bp.route('/admin/seed-all-locales', methods=['POST'])
@permission_required('i18n.config')
def seed_all_locales():
    """
    Seed all i18n keys and translations from multiple locale files at once.

    Request Body:
        locales: Dictionary of language_code -> messages dict (required)
            e.g. {"de": {"common.loading": "Laden..."}, "en": {...}}
        primary_language: Primary language code, default 'de' (optional)

    Returns:
        Seed results with keys created/updated and translations set counts
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    locales = data.get('locales', {})
    primary_lang = data.get('primary_language', 'de')

    if not locales or primary_lang not in locales:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_INPUT', 'message': 'locales object with primary_language required'}
        }), 400

    try:
        from app.infrastructure.persistence.database.connection import fetch_one, fetch_all

        results = {'keys_created': 0, 'keys_updated': 0, 'translations_set': 0}

        # Get namespace mapping
        ns_query = "SELECT namespace_id, namespace_code FROM i18n_namespaces"
        ns_rows = fetch_all(ns_query) or []
        ns_map = {r['namespace_code']: r['namespace_id'] for r in ns_rows}

        # First pass: Create all keys from primary language
        primary_messages = locales.get(primary_lang, {})
        key_id_map = {}  # key_path -> key_id

        for key_path, value in primary_messages.items():
            parts = key_path.split('.')
            ns_code = parts[0] if len(parts) > 1 else 'common'
            namespace_id = ns_map.get(ns_code, ns_map.get('common', 1))

            # Check if key exists
            check = fetch_one(
                "SELECT key_id FROM i18n_keys WHERE key_path = %s",
                (key_path,)
            )

            if check:
                key_id = check['key_id']
                results['keys_updated'] += 1
            else:
                result = fetch_one(
                    "INSERT INTO i18n_keys (namespace_id, key_path) VALUES (%s, %s) RETURNING key_id",
                    (namespace_id, key_path)
                )
                key_id = result['key_id'] if result else None
                results['keys_created'] += 1

            if key_id:
                key_id_map[key_path] = key_id
                # Set primary language translation
                I18nService.set_translation(
                    key_id=key_id,
                    language_code=primary_lang,
                    value=value,
                    translator_id=user_id,
                    is_machine_translated=False
                )
                results['translations_set'] += 1

        # Second pass: Set translations for other languages
        for lang_code, messages in locales.items():
            if lang_code == primary_lang:
                continue

            for key_path, value in messages.items():
                key_id = key_id_map.get(key_path)
                if key_id:
                    I18nService.set_translation(
                        key_id=key_id,
                        language_code=lang_code,
                        value=value,
                        translator_id=user_id,
                        is_machine_translated=False
                    )
                    results['translations_set'] += 1

        I18nService.invalidate_cache()

        return jsonify({
            'success': True,
            'data': results
        })

    except Exception as e:
        logger.error(f"Error seeding all locales: {e}")
        return jsonify({
            'success': False,
            'error': {'code': 'SEED_FAILED', 'message': str(e)}
        }), 500
