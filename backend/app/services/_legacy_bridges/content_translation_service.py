"""Backward Compatibility Bridge: content_translation_service
DEPRECATED: Use 'from app.services.content.translation import ContentTranslationService' instead
This bridge maintains backward compatibility with old import paths.
"""
from app.services.content.translation import ContentTranslationService
__all__ = ['ContentTranslationService']
