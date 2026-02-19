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
        from app.infrastructure.persistence.database.connection import get_connection
        from psycopg.rows import dict_row
        import time

        results = {'keys_created': 0, 'keys_updated': 0, 'translations_set': 0}
        primary_messages = locales.get(primary_lang, {})

        if not primary_messages:
            return jsonify({'success': True, 'data': results})

        t0 = time.monotonic()

        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # 1. Get existing namespaces
                cur.execute("SELECT namespace_code FROM translations.i18n_namespaces")
                existing_ns = {r['namespace_code'] for r in cur.fetchall()}

                # 2. Collect and batch-create missing namespaces
                needed_ns = set()
                key_ns_map = {}  # key_path -> namespace_code
                for key_path in primary_messages:
                    parts = key_path.split('.')
                    ns_code = parts[0] if len(parts) > 1 else 'common'
                    key_ns_map[key_path] = ns_code
                    if ns_code not in existing_ns:
                        needed_ns.add(ns_code)

                if needed_ns:
                    ns_values = []
                    ns_params = []
                    for ns_code in needed_ns:
                        ns_values.append("(%s, %s)")
                        ns_params.extend([ns_code, ns_code.replace('.', ' > ').title()])
                    cur.execute(
                        "INSERT INTO translations.i18n_namespaces (namespace_code, name) "
                        "VALUES " + ", ".join(ns_values) + " ON CONFLICT DO NOTHING",
                        ns_params
                    )

                # 3. COPY keys into temp table, then upsert (fast bulk load)
                cur.execute(
                    "CREATE TEMP TABLE _tmp_keys ("
                    "namespace_code VARCHAR, key_path VARCHAR, default_value TEXT"
                    ") ON COMMIT DROP"
                )

                with cur.copy("COPY _tmp_keys (namespace_code, key_path, default_value) FROM STDIN") as copy:
                    for key_path, value in primary_messages.items():
                        copy.write_row((key_ns_map[key_path], key_path, str(value) if value else ''))

                cur.execute(
                    "INSERT INTO translations.i18n_keys (namespace_code, key_path, default_value) "
                    "SELECT namespace_code, key_path, default_value FROM _tmp_keys "
                    "ON CONFLICT (namespace_code, key_path) DO UPDATE SET "
                    "default_value = EXCLUDED.default_value, updated_at = NOW() "
                    "RETURNING key_id, key_path, (xmax = 0) AS is_new"
                )
                key_rows = cur.fetchall()

                key_id_map = {}
                for row in key_rows:
                    key_id_map[row['key_path']] = row['key_id']
                    if row.get('is_new'):
                        results['keys_created'] += 1
                    else:
                        results['keys_updated'] += 1

                t1 = time.monotonic()
                logger.info(f"Keys upserted in {t1-t0:.1f}s: {len(key_rows)} keys")

                # 4. Disable per-row triggers (they update language_progress
                #    stats on EVERY row — catastrophic for bulk loads)
                cur.execute(
                    "ALTER TABLE translations.i18n_translations "
                    "DISABLE TRIGGER trg_update_language_progress_insert"
                )
                cur.execute(
                    "ALTER TABLE translations.i18n_translations "
                    "DISABLE TRIGGER trg_update_language_progress_update"
                )

                # 5. COPY translations into temp table, then upsert per language
                for lang_code, messages in locales.items():
                    cur.execute(
                        "CREATE TEMP TABLE _tmp_trans ("
                        "key_id UUID, language_code VARCHAR(10), "
                        "translated_value TEXT, translator_user_id VARCHAR"
                        ") ON COMMIT DROP"
                    )

                    row_count = 0
                    with cur.copy("COPY _tmp_trans FROM STDIN") as copy:
                        for key_path, value in messages.items():
                            key_id = key_id_map.get(key_path)
                            if key_id and value:
                                copy.write_row((str(key_id), lang_code, str(value), str(user_id)))
                                row_count += 1

                    if row_count > 0:
                        cur.execute(
                            "INSERT INTO translations.i18n_translations "
                            "(key_id, language_code, translated_value, translator_user_id, translation_source) "
                            "SELECT key_id, language_code, translated_value, "
                            "translator_user_id::uuid, 'imported' FROM _tmp_trans "
                            "ON CONFLICT (key_id, language_code) DO UPDATE SET "
                            "translated_value = EXCLUDED.translated_value, updated_at = NOW()"
                        )
                        results['translations_set'] += row_count

                    cur.execute("DROP TABLE IF EXISTS _tmp_trans")

                # 6. Re-enable triggers
                cur.execute(
                    "ALTER TABLE translations.i18n_translations "
                    "ENABLE TRIGGER trg_update_language_progress_insert"
                )
                cur.execute(
                    "ALTER TABLE translations.i18n_translations "
                    "ENABLE TRIGGER trg_update_language_progress_update"
                )

                # 7. Update language progress stats once (replaces ~9500 trigger calls)
                cur.execute("""
                    UPDATE translations.supported_languages sl SET
                        total_keys = sub.total_keys,
                        translated_keys = sub.translated_keys,
                        completion_percent = CASE
                            WHEN sub.total_keys > 0
                            THEN (sub.translated_keys::DECIMAL / sub.total_keys::DECIMAL) * 100
                            ELSE 0
                        END,
                        updated_at = CURRENT_TIMESTAMP
                    FROM (
                        SELECT
                            sl2.language_code,
                            (SELECT COUNT(DISTINCT key_id) FROM translations.i18n_translations) AS total_keys,
                            COUNT(DISTINCT t.key_id) AS translated_keys
                        FROM translations.supported_languages sl2
                        LEFT JOIN translations.i18n_translations t
                            ON t.language_code = sl2.language_code
                        GROUP BY sl2.language_code
                    ) sub
                    WHERE sl.language_code = sub.language_code
                """)

                t2 = time.monotonic()
                logger.info(f"Translations upserted in {t2-t1:.1f}s, total: {t2-t0:.1f}s")

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
