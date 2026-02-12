"""
Admin Translations API — Part 3: Review / Edit / Verify
========================================================
Translation review endpoints for QA after AI bulk translation.

Routes registered on the blueprint from translations.py.
"""

from flask import request, jsonify, g
from app.api.middleware.auth import token_required, admin_required
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query
from app.api.v1.i18n.admin.translations.translations import bp
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Endpoint 1: Paginated review list with source comparison
# ---------------------------------------------------------------------------

@bp.route('/review', methods=['GET'])
@token_required
@admin_required
def get_review_translations():
    """
    Get translations for review (paginated, filterable).

    Query Params:
        language     (required) - target language code
        source_language         - source language for comparison (default: en)
        namespace               - filter by namespace_code
        status                  - 'unverified', 'verified', 'all' (default: all)
        search                  - search key_path or translated_value
        page                    - page number (default: 1)
        per_page                - items per page (default: 50, max 200)
    """
    language = request.args.get('language')
    if not language:
        return jsonify({'success': False, 'error': 'language parameter required'}), 400

    source_language = request.args.get('source_language', 'en')
    namespace = request.args.get('namespace')
    status = request.args.get('status', 'all')
    search = request.args.get('search', '').strip()
    page = max(1, int(request.args.get('page', 1)))
    per_page = min(int(request.args.get('per_page', 50)), 200)
    offset = (page - 1) * per_page

    # Build WHERE conditions shared by count + main query
    conditions = ["k.is_active = TRUE"]
    params = []

    if namespace:
        conditions.append("k.namespace_code = %s")
        params.append(namespace)

    if status == 'verified':
        conditions.append("t.is_verified = TRUE")
    elif status == 'unverified':
        conditions.append("(t.is_verified = FALSE OR t.is_verified IS NULL)")

    if search:
        conditions.append("(k.key_path ILIKE %s OR t.translated_value ILIKE %s)")
        params.extend([f'%{search}%', f'%{search}%'])

    where_sql = " AND ".join(conditions)

    # Count total matching rows
    count_query = f"""
        SELECT COUNT(*) AS total
        FROM translations.i18n_keys k
        JOIN translations.i18n_translations t
            ON t.key_id = k.key_id AND t.language_code = %s
        WHERE {where_sql}
    """
    count_result = fetch_one(count_query, tuple([language] + params))
    total = count_result['total'] if count_result else 0

    # Fetch page with source-language value for side-by-side comparison
    main_query = f"""
        SELECT
            t.translation_id,
            k.key_id,
            k.key_path,
            k.namespace_code,
            src.translated_value  AS source_value,
            t.translated_value,
            t.translation_source,
            t.is_verified,
            t.quality_score,
            t.updated_at
        FROM translations.i18n_keys k
        JOIN translations.i18n_translations t
            ON t.key_id = k.key_id AND t.language_code = %s
        LEFT JOIN translations.i18n_translations src
            ON src.key_id = k.key_id AND src.language_code = %s
        WHERE {where_sql}
        ORDER BY k.namespace_code, k.key_path
        LIMIT %s OFFSET %s
    """
    main_params = [language, source_language] + params + [per_page, offset]
    rows = fetch_all(main_query, tuple(main_params)) or []

    items = []
    for r in rows:
        items.append({
            'translation_id': str(r['translation_id']),
            'key_id': str(r['key_id']),
            'key_path': r['key_path'],
            'namespace_code': r['namespace_code'],
            'source_value': r.get('source_value', ''),
            'translated_value': r['translated_value'],
            'translation_source': r.get('translation_source', ''),
            'is_verified': r.get('is_verified', False),
            'quality_score': r.get('quality_score'),
            'updated_at': r['updated_at'].isoformat() if r.get('updated_at') else None,
        })

    return jsonify({
        'success': True,
        'data': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': max(1, -(-total // per_page)),
    }), 200


# ---------------------------------------------------------------------------
# Endpoint 2: Edit a single translation
# ---------------------------------------------------------------------------

@bp.route('/review/<translation_id>', methods=['PUT'])
@token_required
@admin_required
def edit_translation(translation_id: str):
    """
    Edit a translation value.

    Sets translation_source='manual' and is_verified=true.

    Request Body:
        { "translated_value": "Corrected value" }
    """
    data = request.get_json(silent=True) or {}
    new_value = data.get('translated_value')

    if new_value is None:
        return jsonify({'success': False, 'error': 'translated_value required'}), 400

    result = execute_query("""
        UPDATE translations.i18n_translations
        SET translated_value  = %s,
            translation_source = 'manual',
            is_verified        = TRUE,
            translator_user_id = %s,
            updated_at         = NOW()
        WHERE translation_id = %s
        RETURNING translation_id
    """, (new_value, g.user_id, translation_id))

    if not result:
        return jsonify({'success': False, 'error': 'Translation not found'}), 404

    return jsonify({'success': True, 'translation_id': translation_id}), 200


# ---------------------------------------------------------------------------
# Endpoint 3: Verify a single translation
# ---------------------------------------------------------------------------

@bp.route('/review/<translation_id>/verify', methods=['POST'])
@token_required
@admin_required
def verify_translation(translation_id: str):
    """Mark a single translation as verified."""
    result = execute_query("""
        UPDATE translations.i18n_translations
        SET is_verified = TRUE, updated_at = NOW()
        WHERE translation_id = %s
        RETURNING translation_id
    """, (translation_id,))

    if not result:
        return jsonify({'success': False, 'error': 'Translation not found'}), 404

    return jsonify({'success': True, 'translation_id': translation_id}), 200


# ---------------------------------------------------------------------------
# Endpoint 4: Bulk verify translations
# ---------------------------------------------------------------------------

@bp.route('/review/bulk-verify', methods=['POST'])
@token_required
@admin_required
def bulk_verify_translations():
    """
    Verify multiple translations at once.

    Request Body:
        { "translation_ids": ["uuid1", "uuid2", ...] }
    """
    data = request.get_json(silent=True) or {}
    ids = data.get('translation_ids', [])

    if not ids or not isinstance(ids, list):
        return jsonify({'success': False, 'error': 'translation_ids array required'}), 400

    if len(ids) > 500:
        return jsonify({'success': False, 'error': 'Max 500 translations per request'}), 400

    execute_query("""
        UPDATE translations.i18n_translations
        SET is_verified = TRUE, updated_at = NOW()
        WHERE translation_id = ANY(%s)
    """, (ids,))

    return jsonify({'success': True, 'verified_count': len(ids)}), 200
