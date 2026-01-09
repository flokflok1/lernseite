"""
DEPRECATED: Authoring Service Bridge

This module is deprecated. Use the authoring package instead:
  from app.services.authoring import AuthoringService, get_authoring_service

This file is kept for backward compatibility during migration.
All actual implementation has been moved to app.services.authoring package.
"""

import warnings

# Issue deprecation warning on import
warnings.warn(
    "Importing from app.services.authoring_service is deprecated. "
    "Use app.services.authoring instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from new location
from app.services.authoring import (  # noqa: F401
    AuthoringService,
    AuthoringServiceError,
    get_authoring_service,
    SessionManager,
    ChatProcessor,
    PreviewGenerator,
    ContentSaver
)

__all__ = [
    'AuthoringService',
    'AuthoringServiceError',
    'get_authoring_service',
    'SessionManager',
    'ChatProcessor',
    'PreviewGenerator',
    'ContentSaver'
]
