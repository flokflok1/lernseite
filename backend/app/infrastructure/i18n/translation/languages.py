"""
i18n Admin Language Management Endpoints
========================================

Admin endpoints for managing supported languages and exporting translations.

Endpoints:
    GET    /i18n/admin/languages                - Get all languages (admin view)
    POST   /i18n/admin/languages                - Create a new language
    PUT    /i18n/admin/languages/<code>         - Update a language
    DELETE /i18n/admin/languages/<code>         - Delete a language
    GET    /i18n/admin/export                   - Export translations as JSON
"""

from flask import Blueprint, request, jsonify
from app.application.services.i18n_service import I18nService
from app.api.middleware.auth import permission_required
import logging

logger = logging.getLogger(__name__)

i18n_languages_bp = Blueprint('i18n_languages', __name__, url_prefix='/i18n')


@i18n_languages_bp.route('/admin/languages', methods=['GET'])
@permission_required('i18n.view')
def admin_get_languages():
    """
    Get all languages (admin view with more details, includes inactive).

    Returns:
        List of all languages with full metadata
    """
    from app.application.services.i18n.languages import LanguageManager
    languages = LanguageManager.get_all_languages()
    return jsonify({
        'success': True,
        'data': languages
    })


@i18n_languages_bp.route('/admin/languages', methods=['POST'])
@permission_required('i18n.config')
def create_language():
    """
    Create a new language.

    Request Body:
        language_code: ISO language code (required)
        language_name: English name (required)
        native_name: Native name (required)
        flag_svg_code: SVG flag code, e.g. 'de', 'en', 'pl' (required)
        active: Whether language is active, default True (optional)
        rtl: Right-to-left language, default False (optional)
        is_primary: Whether this is primary language, default False (optional)
        priority: Sort priority, default 100 (optional)

    Returns:
        language_code of created language
    """
    from app.infrastructure.persistence.database.connection import execute_query, fetch_one

    data = request.get_json()

    required = ['language_code', 'language_name', 'native_name', 'flag_svg_code']
    for field in required:
        if not data.get(field):
            return jsonify({
                'success': False,
                'error': {'code': 'INVALID_INPUT', 'message': f'{field} is required'}
            }), 400

    try:
        # Check if language already exists
        check = fetch_one(
            "SELECT 1 FROM translations.supported_languages WHERE language_code = %s",
            (data['language_code'],)
        )
        if check:
            return jsonify({
                'success': False,
                'error': {'code': 'DUPLICATE', 'message': 'Language already exists'}
            }), 409

        # Insert new language
        execute_query("""
            INSERT INTO translations.supported_languages (
                language_code, language_name, native_name, flag_svg_code,
                is_active, is_rtl, is_primary, priority
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['language_code'],
            data['language_name'],
            data['native_name'],
            data['flag_svg_code'],
            data.get('active', True),
            data.get('rtl', False),
            data.get('is_primary', False),
            data.get('priority', 100)
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


@i18n_languages_bp.route('/admin/languages/<language_code>', methods=['PUT'])
@permission_required('i18n.config')
def update_language(language_code: str):
    """
    Update a language.

    Args:
        language_code: Language code to update

    Request Body:
        language_name: English name (optional)
        native_name: Native name (optional)
        flag_svg_code: SVG flag code (optional)
        active: Whether language is active (optional)
        rtl: Right-to-left language (optional)
        is_primary: Whether this is primary language (optional)
        priority: Sort priority (optional)

    Returns:
        Success status
    """
    from app.infrastructure.persistence.database.connection import execute_query, fetch_one

    data = request.get_json()

    try:
        # Check if language exists
        check = fetch_one(
            "SELECT 1 FROM translations.supported_languages WHERE language_code = %s",
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
        if 'flag_svg_code' in data:
            updates.append("flag_svg_code = %s")
            params.append(data['flag_svg_code'])
        if 'active' in data:
            updates.append("is_active = %s")
            params.append(data['active'])
        if 'rtl' in data:
            updates.append("is_rtl = %s")
            params.append(data['rtl'])
        primary_changed = False
        if 'is_primary' in data and data['is_primary']:
            # Use LanguageManager to safely toggle primary (unsets others first)
            from app.application.services.i18n.languages import LanguageManager
            primary_changed = LanguageManager.set_primary_language(language_code)
        if 'priority' in data:
            updates.append("priority = %s")
            params.append(data['priority'])

        if not updates and not primary_changed:
            return jsonify({
                'success': False,
                'error': {'code': 'INVALID_INPUT', 'message': 'No fields to update'}
            }), 400

        if updates:
            params.append(language_code)

            execute_query(f"""
                UPDATE translations.supported_languages
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


@i18n_languages_bp.route('/admin/languages/<language_code>', methods=['DELETE'])
@permission_required('i18n.config')
def delete_language(language_code: str):
    """
    Delete a language (only if not primary).

    Args:
        language_code: Language code to delete

    Returns:
        Success status
    """
    from app.infrastructure.persistence.database.connection import execute_query, fetch_one

    # Don't allow deleting the primary language (dynamic check)
    from app.application.services.i18n.languages import LanguageManager
    if language_code == LanguageManager.get_primary_language():
        return jsonify({
            'success': False,
            'error': {'code': 'FORBIDDEN', 'message': 'Cannot delete primary language'}
        }), 403

    try:
        # Check if language exists
        check = fetch_one(
            "SELECT 1 FROM translations.supported_languages WHERE language_code = %s",
            (language_code,)
        )
        if not check:
            return jsonify({
                'success': False,
                'error': {'code': 'NOT_FOUND', 'message': 'Language not found'}
            }), 404

        # Delete translations first (cascade)
        execute_query(
            "DELETE FROM translations.i18n_translations WHERE language_code = %s",
            (language_code,)
        )

        # Delete the language
        execute_query(
            "DELETE FROM translations.supported_languages WHERE language_code = %s",
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


@i18n_languages_bp.route('/admin/export', methods=['GET'])
@permission_required('i18n.config')
def export_locales():
    """
    Export all translations from DB as JSON for B2B deployments.

    Query Params:
        format: 'nested' (default) or 'flat'
        languages: comma-separated list (default: all active)

    Returns:
        Translations organized by language code
    """
    from app.infrastructure.persistence.database.connection import fetch_all

    output_format = request.args.get('format', 'nested')
    languages_param = request.args.get('languages')

    try:
        # Get active languages or filter by param
        if languages_param:
            lang_codes = [l.strip() for l in languages_param.split(',')]
        else:
            lang_rows = fetch_all(
                "SELECT language_code FROM translations.supported_languages WHERE is_active = TRUE ORDER BY priority"
            ) or []
            lang_codes = [r['language_code'] for r in lang_rows]

        # Get all keys with translations
        query = """
            SELECT
                k.key_path,
                t.language_code,
                t.value
            FROM translations.i18n_keys k
            LEFT JOIN translations.i18n_translations t ON k.key_id = t.key_id
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
