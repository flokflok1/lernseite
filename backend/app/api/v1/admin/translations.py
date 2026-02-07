"""
Admin Translations API
======================

Deterministic helper endpoints for translation management.

Endpoints:
    POST /api/v1/admin/translations/supported-languages/draft
        - Suggest language metadata from a code or name input
        - Fully deterministic (no AI, no DB writes)
"""

from flask import Blueprint, request, jsonify
from app.api.middleware.auth import token_required, admin_required
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('admin_translations', __name__, url_prefix='/admin/translations')

# ---------------------------------------------------------------------------
# Hardcoded language map (~30 common languages)
# ---------------------------------------------------------------------------
_KNOWN_RTL = frozenset({'ar', 'he', 'fa', 'ur', 'ps', 'sd', 'yi', 'ku'})

_LANGUAGE_MAP = {
    'af': ('Afrikaans', 'Afrikaans', 'za', 100),
    'ar': ('Arabic', '\u0627\u0644\u0639\u0631\u0628\u064a\u0629', 'sa', 100),
    'bg': ('Bulgarian', '\u0411\u044a\u043b\u0433\u0430\u0440\u0441\u043a\u0438', 'bg', 100),
    'cs': ('Czech', '\u010ce\u0161tina', 'cz', 100),
    'da': ('Danish', 'Dansk', 'dk', 100),
    'de': ('German', 'Deutsch', 'de', 10),
    'el': ('Greek', '\u0395\u03bb\u03bb\u03b7\u03bd\u03b9\u03ba\u03ac', 'gr', 100),
    'en': ('English', 'English', 'gb', 20),
    'es': ('Spanish', 'Espa\u00f1ol', 'es', 100),
    'et': ('Estonian', 'Eesti', 'ee', 100),
    'fa': ('Persian', '\u0641\u0627\u0631\u0633\u06cc', 'ir', 100),
    'fi': ('Finnish', 'Suomi', 'fi', 100),
    'fr': ('French', 'Fran\u00e7ais', 'fr', 100),
    'he': ('Hebrew', '\u05e2\u05d1\u05e8\u05d9\u05ea', 'il', 100),
    'hi': ('Hindi', '\u0939\u093f\u0928\u094d\u0926\u0940', 'in', 100),
    'hr': ('Croatian', 'Hrvatski', 'hr', 100),
    'hu': ('Hungarian', 'Magyar', 'hu', 100),
    'id': ('Indonesian', 'Bahasa Indonesia', 'id', 100),
    'it': ('Italian', 'Italiano', 'it', 100),
    'ja': ('Japanese', '\u65e5\u672c\u8a9e', 'jp', 100),
    'ko': ('Korean', '\ud55c\uad6d\uc5b4', 'kr', 100),
    'lt': ('Lithuanian', 'Lietuvi\u0173', 'lt', 100),
    'lv': ('Latvian', 'Latvie\u0161u', 'lv', 100),
    'nl': ('Dutch', 'Nederlands', 'nl', 100),
    'no': ('Norwegian', 'Norsk', 'no', 100),
    'pl': ('Polish', 'Polski', 'pl', 30),
    'pt': ('Portuguese', 'Portugu\u00eas', 'pt', 100),
    'ro': ('Romanian', 'Rom\u00e2n\u0103', 'ro', 100),
    'ru': ('Russian', '\u0420\u0443\u0441\u0441\u043a\u0438\u0439', 'ru', 100),
    'sk': ('Slovak', 'Sloven\u010dina', 'sk', 100),
    'sl': ('Slovenian', 'Sloven\u0161\u010dina', 'si', 100),
    'sv': ('Swedish', 'Svenska', 'se', 100),
    'th': ('Thai', '\u0e44\u0e17\u0e22', 'th', 100),
    'tr': ('Turkish', 'T\u00fcrk\u00e7e', 'tr', 100),
    'uk': ('Ukrainian', '\u0423\u043a\u0440\u0430\u0457\u043d\u0441\u044c\u043a\u0430', 'ua', 100),
    'vi': ('Vietnamese', 'Ti\u1ebfng Vi\u1ec7t', 'vn', 100),
    'zh': ('Chinese', '\u4e2d\u6587', 'cn', 100),
}

# Reverse lookup: English name (lowercase) -> code
_NAME_TO_CODE = {}
for _code, (_eng, _native, _flag, _prio) in _LANGUAGE_MAP.items():
    _NAME_TO_CODE[_eng.lower()] = _code
    _NAME_TO_CODE[_native.lower()] = _code


def _resolve_input(raw: str) -> dict:
    """
    Resolve free-text input to a language draft.

    Lookup order:
    1. Exact code match (lowercased)
    2. English / native name match (case-insensitive)
    3. Unknown -> return skeleton with empty strings

    Always succeeds (never raises).
    """
    normalised = raw.strip().lower()

    # 1. Direct code match
    if normalised in _LANGUAGE_MAP:
        eng, native, flag, prio = _LANGUAGE_MAP[normalised]
        return {
            'code': normalised,
            'name': eng,
            'native_name': native,
            'flag_svg_code': flag,
            'is_rtl': normalised in _KNOWN_RTL,
            'priority': prio,
        }

    # 2. Name match
    if normalised in _NAME_TO_CODE:
        code = _NAME_TO_CODE[normalised]
        eng, native, flag, prio = _LANGUAGE_MAP[code]
        return {
            'code': code,
            'name': eng,
            'native_name': native,
            'flag_svg_code': flag,
            'is_rtl': code in _KNOWN_RTL,
            'priority': prio,
        }

    # 3. Unknown input
    return {
        'code': normalised,
        'name': '',
        'native_name': '',
        'flag_svg_code': normalised,
        'is_rtl': normalised in _KNOWN_RTL,
        'priority': 100,
    }


@bp.route('/supported-languages/draft', methods=['POST'])
@token_required
@admin_required
def draft_language():
    """
    Suggest language metadata from a code or name.

    Fully deterministic, no AI calls, no DB writes.
    Always returns 200.

    Request Body:
        input: str  (e.g. "BG", "fr", "Japanese")

    Returns:
        { code, name, native_name, flag_svg_code, is_rtl, priority }
    """
    data = request.get_json(silent=True) or {}
    raw_input = data.get('input', '')

    if not raw_input or not isinstance(raw_input, str):
        return jsonify({
            'success': True,
            'data': {
                'code': '',
                'name': '',
                'native_name': '',
                'flag_svg_code': '',
                'is_rtl': False,
                'priority': 100,
            }
        }), 200

    draft = _resolve_input(raw_input)

    return jsonify({
        'success': True,
        'data': draft,
    }), 200
