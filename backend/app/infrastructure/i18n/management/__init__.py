"""
i18n Management Package
=======================

Admin endpoints for managing translation keys and user suggestions.
"""

from .keys import i18n_keys_bp
from .suggestions import i18n_suggestions_bp

__all__ = ['i18n_keys_bp', 'i18n_suggestions_bp']
