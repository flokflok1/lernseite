"""Backward Compatibility Bridge: tts_service
DEPRECATED: Use 'from app.application.services.media_cache.tts_service import TTSService' instead
This bridge maintains backward compatibility with old import paths.
"""
from app.application.services.media_cache.tts_service import TTSService
__all__ = ['TTSService']
