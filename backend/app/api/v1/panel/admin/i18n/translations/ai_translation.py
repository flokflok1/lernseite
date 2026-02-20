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
from app.application.services.i18n.bridge import I18nService
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
        from app.infrastructure.persistence.repositories.i18n.admin_queries import I18nAdminQueryRepository

        results = {'created': 0, 'updated': 0, 'errors': []}

        # Get existing namespaces
        ns_rows = I18nAdminQueryRepository.get_all_namespaces()
        existing_ns = {r['namespace_code'] for r in ns_rows}

        for key_path, value in messages.items():
            parts = key_path.split('.')
            ns_code = parts[0] if len(parts) > 1 else 'common'

            # Auto-create namespace if missing
            if ns_code not in existing_ns:
                I18nAdminQueryRepository.create_namespace(
                    ns_code, ns_code.replace('.', ' > ').title()
                )
                existing_ns.add(ns_code)

            # Upsert key
            result = I18nAdminQueryRepository.upsert_key_with_default(
                ns_code, key_path, value
            )

            if result:
                key_id = result['key_id']
                if result.get('is_new'):
                    results['created'] += 1
                else:
                    results['updated'] += 1

                # Set German translation
                I18nAdminQueryRepository.upsert_translation(
                    key_id, 'de', value, user_id
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
        from app.infrastructure.persistence.repositories.i18n.bulk_seed import I18nBulkSeedRepository

        results = I18nBulkSeedRepository.seed_all_locales(
            locales=locales,
            primary_lang=primary_lang,
            user_id=str(user_id)
        )

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
