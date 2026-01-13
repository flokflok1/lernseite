"""
Media Cache Service - Backward Compatibility Bridge

DEPRECATED: Use app.services.media_cache instead

This file is kept for backward compatibility only.
All imports are re-exported from the media_cache package.

Migration Guide:
    Before: from app.services.media_cache_service import MediaCacheService
    After:  from app.services.media_cache import MediaCacheService

    The API is identical - just update the import statement.
"""

import warnings
from app.services.media_cache import (
    MediaCacheService,
    MediaCacheRepository,
    TTSCacheService,
    TranscriptCacheService,
    SessionCacheService,
)

__all__ = [
    'MediaCacheService',
    'MediaCacheRepository',
    'TTSCacheService',
    'TranscriptCacheService',
    'SessionCacheService',
]

# Emit deprecation warning when imported
warnings.warn(
    "Importing from app.services.media_cache_service is deprecated. "
    "Use app.services.media_cache instead.",
    DeprecationWarning,
    stacklevel=2
)
