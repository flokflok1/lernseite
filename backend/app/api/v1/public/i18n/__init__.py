"""
i18n Public API Module

Public i18n endpoints:
- Language Management: GET/POST/PUT/DELETE /i18n/admin/languages
- Translation Keys: GET/POST /i18n/admin/keys
- Public Bundles: GET /i18n/bundle/<language_code>
- Language Progress: GET /i18n/languages/<language_code>/progress
"""

from .keys import i18n_keys_bp
from .languages import i18n_languages_bp
from .public import i18n_public_bp

__all__ = ['i18n_keys_bp', 'i18n_languages_bp', 'i18n_public_bp']
