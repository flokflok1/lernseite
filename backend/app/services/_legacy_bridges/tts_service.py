"""Backward Compatibility Bridge: tts_service
DEPRECATED: Use 'from app.services.media_cache.tts_service import TTSService' instead
This bridge maintains backward compatibility with old import paths.
"""
from app.services.media_cache.tts_service import TTSService
__all__ = ['TTSService']
