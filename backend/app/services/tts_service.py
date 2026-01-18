"""
Text-to-Speech Service Bridge - LEGACY IMPORT PATH

NOTICE: This file exists for backward compatibility only.
The actual implementation has been moved to app/services/media_cache/tts_service.py

DEPRECATED IMPORT (old path - still works):
    from app.services.tts_service import TTSService

RECOMMENDED IMPORT (new path):
    from app.services.media_cache.tts_service import TTSService

This bridge re-exports the TTSService class for backward compatibility
with existing code. All new code should use the recommended import path.
"""

# Re-export from the actual location for backward compatibility
from app.services.media_cache.tts_service import TTSService

__all__ = ['TTSService']
