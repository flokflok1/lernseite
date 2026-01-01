"""
i18n API Endpoints
==================
Public and admin endpoints for internationalization.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.i18n_service import I18nService
from app.middleware.auth import permission_required
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('i18n', __name__, url_prefix='/i18n')


# =============================================================================
# Public Endpoints
# =============================================================================

@bp.route('/bundle/<language_code>', methods=['GET'])
def get_bundle(language_code: str):
    """Get translation bundle for a language."""
    namespace = request.args.get('namespace')
    bundle = I18nService.get_bundle(language_code, namespace)

    return jsonify({
        'success': True,
        'data': bundle
    })


@bp.route('/languages', methods=['GET'])
def get_languages():
    """Get available languages with progress."""
    languages = I18nService.get_languages()

    return jsonify({
        'success': True,
        'data': languages
    })


@bp.route('/languages/<language_code>/progress', methods=['GET'])
def get_language_progress(language_code: str):
    """Get detailed progress for a language."""
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


# =============================================================================
# Authenticated Endpoints - Suggestions
# =============================================================================

@bp.route('/suggestions', methods=['POST'])
@jwt_required()
def submit_suggestion():
    """Submit a translation suggestion."""
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


@bp.route('/suggestions', methods=['GET'])
@jwt_required()
def get_suggestions():
    """Get translation suggestions."""
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


@bp.route('/suggestions/<suggestion_id>/vote', methods=['POST'])
@jwt_required()
def vote_suggestion(suggestion_id: str):
    """Vote for a suggestion."""
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


@bp.route('/request-translation', methods=['POST'])
@jwt_required()
def request_translation():
    """Request translation for a language."""
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


# =============================================================================
# Admin Endpoints - Moderation
# =============================================================================

@bp.route('/admin/moderation/dashboard', methods=['GET'])
@permission_required('i18n.moderate')
def get_moderation_dashboard():
    """Get moderation dashboard."""
    data = I18nService.get_moderation_dashboard()

    return jsonify({
        'success': True,
        'data': data
    })


@bp.route('/admin/moderation/queue', methods=['GET'])
@permission_required('i18n.moderate')
def get_moderation_queue():
    """Get moderation queue."""
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


@bp.route('/admin/moderation/queue/<queue_id>/review', methods=['POST'])
@permission_required('i18n.moderate')
def review_queue_item(queue_id: str):
    """Review a queue item."""
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


@bp.route('/admin/moderation/ai-review', methods=['POST'])
@permission_required('i18n.moderate')
def trigger_ai_review():
    """Trigger AI review for a translation/suggestion."""
    # TODO: Implement AI review
    return jsonify({
        'success': True,
        'data': {
            'review_id': None,
            'quality_score': 0.85,
            'recommendation': 'approve'
        }
    })


@bp.route('/admin/config', methods=['GET'])
@permission_required('i18n.config')
def get_ai_config():
    """Get AI moderation config."""
    config = I18nService.get_ai_config()

    return jsonify({
        'success': True,
        'data': config
    })


@bp.route('/admin/config', methods=['PUT'])
@permission_required('i18n.config')
def update_ai_config():
    """
    Update AI moderation config.

    Request Body:
    {
        "moderation_model": "claude-sonnet-4-20250514",
        "auto_approve_threshold": 0.95,
        "auto_reject_threshold": 0.3,
        "human_review_threshold": 0.7,
        "enabled_languages": ["de", "pl", "en"]
    }
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


@bp.route('/admin/cache/invalidate', methods=['POST'])
@permission_required('i18n.config')
def invalidate_cache():
    """Invalidate translation cache."""
    data = request.get_json() or {}
    language_code = data.get('language_code')

    I18nService.invalidate_cache(language_code)

    return jsonify({'success': True})


# =============================================================================
# Admin Endpoints - Keys & Translations
# =============================================================================

@bp.route('/admin/namespaces', methods=['GET'])
@permission_required('i18n.view')
def get_namespaces():
    """Get all namespaces."""
    namespaces = I18nService.get_namespaces()

    return jsonify({
        'success': True,
        'data': namespaces
    })


@bp.route('/admin/keys', methods=['GET'])
@permission_required('i18n.view')
def get_keys():
    """Get translation keys."""
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


@bp.route('/admin/keys', methods=['POST'])
@permission_required('i18n.config')
def create_key():
    """Create a new translation key."""
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


@bp.route('/admin/keys/<key_id>/translations', methods=['GET'])
@permission_required('i18n.view')
def get_key_translations(key_id: str):
    """Get translations for a key."""
    translations = I18nService.get_key_translations(key_id)

    return jsonify({
        'success': True,
        'data': translations
    })


@bp.route('/admin/keys/<int:key_id>/translations/<language_code>', methods=['PUT'])
@permission_required('i18n.config')
def set_translation(key_id: int, language_code: str):
    """Set or update a translation."""
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


# =============================================================================
# Admin Endpoints - AI Translation
# =============================================================================

@bp.route('/admin/ai/translate', methods=['POST'])
@permission_required('i18n.config')
def ai_translate():
    """Generate AI translation for a single key."""
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


@bp.route('/admin/ai/translate/bulk', methods=['POST'])
@permission_required('i18n.config')
def ai_translate_bulk():
    """Generate AI translations for multiple missing keys."""
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


@bp.route('/admin/seed-keys', methods=['POST'])
@permission_required('i18n.config')
def seed_keys():
    """Seed i18n keys from frontend default messages."""
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    # Get all keys from request or use defaults
    messages = data.get('messages', {})

    if not messages:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_INPUT', 'message': 'messages object required'}
        }), 400

    try:
        from app.database.connection import fetch_one, fetch_all, execute_query

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


@bp.route('/admin/seed-all-locales', methods=['POST'])
@permission_required('i18n.config')
def seed_all_locales():
    """
    Seed all i18n keys and translations from multiple locale files at once.

    Request Body:
    {
        "locales": {
            "de": {"common.loading": "Laden...", ...},
            "en": {"common.loading": "Loading...", ...},
            "pl": {"common.loading": "Ładowanie...", ...}
        },
        "primary_language": "de"
    }
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
        from app.database.connection import fetch_one, fetch_all, execute_query

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


# =============================================================================
# Admin Endpoints - Language Management
# =============================================================================

@bp.route('/admin/languages', methods=['GET'])
@permission_required('i18n.view')
def admin_get_languages():
    """Get all languages (admin view with more details)."""
    languages = I18nService.get_languages()
    return jsonify({
        'success': True,
        'data': languages
    })


@bp.route('/admin/languages', methods=['POST'])
@permission_required('i18n.config')
def create_language():
    """Create a new language."""
    from app.database.connection import execute_query, fetch_one

    data = request.get_json()

    required = ['language_code', 'language_name', 'native_name', 'flag_emoji']
    for field in required:
        if not data.get(field):
            return jsonify({
                'success': False,
                'error': {'code': 'INVALID_INPUT', 'message': f'{field} is required'}
            }), 400

    try:
        # Check if language already exists
        check = fetch_one(
            "SELECT 1 FROM supported_languages WHERE language_code = %s",
            (data['language_code'],)
        )
        if check:
            return jsonify({
                'success': False,
                'error': {'code': 'DUPLICATE', 'message': 'Language already exists'}
            }), 409

        # Insert new language
        execute_query("""
            INSERT INTO supported_languages (
                language_code, language_name, native_name, flag_emoji,
                active, rtl, is_primary, priority, fallback_language
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['language_code'],
            data['language_name'],
            data['native_name'],
            data['flag_emoji'],
            data.get('active', True),
            data.get('rtl', False),
            data.get('is_primary', False),
            data.get('priority', 100),
            data.get('fallback_language') or None
        ))

        I18nService.invalidate_cache()

        return jsonify({
            'success': True,
            'data': {'language_code': data['language_code']}
        }), 201

    except Exception as e:
        logger.error(f"Failed to create language: {e}")
        return jsonify({
            'success': False,
            'error': {'code': 'CREATE_FAILED', 'message': str(e)}
        }), 500


@bp.route('/admin/languages/<language_code>', methods=['PUT'])
@permission_required('i18n.config')
def update_language(language_code: str):
    """Update a language."""
    from app.database.connection import execute_query, fetch_one

    data = request.get_json()

    try:
        # Check if language exists
        check = fetch_one(
            "SELECT 1 FROM supported_languages WHERE language_code = %s",
            (language_code,)
        )
        if not check:
            return jsonify({
                'success': False,
                'error': {'code': 'NOT_FOUND', 'message': 'Language not found'}
            }), 404

        # Build update query dynamically
        updates = []
        params = []

        if 'language_name' in data:
            updates.append("language_name = %s")
            params.append(data['language_name'])
        if 'native_name' in data:
            updates.append("native_name = %s")
            params.append(data['native_name'])
        if 'flag_emoji' in data:
            updates.append("flag_emoji = %s")
            params.append(data['flag_emoji'])
        if 'active' in data:
            updates.append("active = %s")
            params.append(data['active'])
        if 'rtl' in data:
            updates.append("rtl = %s")
            params.append(data['rtl'])
        if 'is_primary' in data:
            updates.append("is_primary = %s")
            params.append(data['is_primary'])
        if 'priority' in data:
            updates.append("priority = %s")
            params.append(data['priority'])
        if 'fallback_language' in data:
            updates.append("fallback_language = %s")
            params.append(data['fallback_language'] if data['fallback_language'] else None)

        if not updates:
            return jsonify({
                'success': False,
                'error': {'code': 'INVALID_INPUT', 'message': 'No fields to update'}
            }), 400

        params.append(language_code)

        execute_query(f"""
            UPDATE supported_languages
            SET {', '.join(updates)}
            WHERE language_code = %s
        """, tuple(params))

        I18nService.invalidate_cache(language_code)

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Failed to update language: {e}")
        return jsonify({
            'success': False,
            'error': {'code': 'UPDATE_FAILED', 'message': str(e)}
        }), 500


@bp.route('/admin/export', methods=['GET'])
@permission_required('i18n.config')
def export_locales():
    """
    Export all translations from DB as JSON for B2B deployments.

    Query Params:
    - format: 'nested' (default) or 'flat'
    - languages: comma-separated list (default: all active)

    Returns:
    {
        "de": {"common": {"loading": "Laden..."}, "nav": {"home": "Startseite"}},
        "en": {"common": {"loading": "Loading..."}, "nav": {"home": "Home"}},
        ...
    }
    """
    from app.database.connection import fetch_all

    output_format = request.args.get('format', 'nested')
    languages_param = request.args.get('languages')

    try:
        # Get active languages or filter by param
        if languages_param:
            lang_codes = [l.strip() for l in languages_param.split(',')]
        else:
            lang_rows = fetch_all(
                "SELECT language_code FROM supported_languages WHERE active = TRUE ORDER BY priority"
            ) or []
            lang_codes = [r['language_code'] for r in lang_rows]

        # Get all keys with translations
        query = """
            SELECT
                k.key_path,
                t.language_code,
                t.value
            FROM i18n_keys k
            LEFT JOIN i18n_translations t ON k.key_id = t.key_id
            WHERE t.language_code = ANY(%s)
            ORDER BY k.key_path, t.language_code
        """
        rows = fetch_all(query, (lang_codes,)) or []

        # Build result structure
        result = {lang: {} for lang in lang_codes}

        for row in rows:
            lang = row['language_code']
            key_path = row['key_path']
            value = row['value']

            if lang not in result:
                continue

            if output_format == 'flat':
                result[lang][key_path] = value
            else:
                # Nested format: "common.loading" -> {"common": {"loading": "..."}}
                parts = key_path.split('.')
                current = result[lang]
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value

        return jsonify({
            'success': True,
            'data': result,
            'meta': {
                'format': output_format,
                'languages': lang_codes,
                'total_keys': len(set(r['key_path'] for r in rows))
            }
        })

    except Exception as e:
        logger.error(f"Error exporting locales: {e}")
        return jsonify({
            'success': False,
            'error': {'code': 'EXPORT_FAILED', 'message': str(e)}
        }), 500


@bp.route('/admin/languages/<language_code>', methods=['DELETE'])
@permission_required('i18n.config')
def delete_language(language_code: str):
    """Delete a language (only if not primary)."""
    from app.database.connection import execute_query, fetch_one

    # Don't allow deleting German (primary language)
    if language_code == 'de':
        return jsonify({
            'success': False,
            'error': {'code': 'FORBIDDEN', 'message': 'Cannot delete primary language'}
        }), 403

    try:
        # Check if language exists
        check = fetch_one(
            "SELECT 1 FROM supported_languages WHERE language_code = %s",
            (language_code,)
        )
        if not check:
            return jsonify({
                'success': False,
                'error': {'code': 'NOT_FOUND', 'message': 'Language not found'}
            }), 404

        # Delete translations first (cascade)
        execute_query(
            "DELETE FROM i18n_translations WHERE language_code = %s",
            (language_code,)
        )

        # Delete the language
        execute_query(
            "DELETE FROM supported_languages WHERE language_code = %s",
            (language_code,)
        )

        I18nService.invalidate_cache()

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Failed to delete language: {e}")
        return jsonify({
            'success': False,
            'error': {'code': 'DELETE_FAILED', 'message': str(e)}
        }), 500


# =============================================================================
# Register Blueprint with API v1
# =============================================================================

from . import api_v1
api_v1.register_blueprint(bp)
