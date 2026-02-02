"""i18n Module - Internationalization and Translation"""

from app.api.v1.i18n.admin import admin_bp
from app.api.v1.i18n.public import public_bp
from app.api.v1.i18n.translation_api import bp as translation_bp

__all__ = ['admin_bp', 'public_bp', 'translation_bp']
