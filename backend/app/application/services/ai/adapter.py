"""
Bridge module - AIAdapter moved to app.infrastructure.ai.adapter

This re-export ensures backward compatibility for existing imports:
    from app.application.services.ai.adapter import AIAdapter
"""

from app.infrastructure.ai.adapter import AIAdapter  # noqa: F401
from app.infrastructure.ai.exceptions import (  # noqa: F401
    AIProviderError,
    AIQuotaExceededError,
    AIInvalidKeyError,
    AITimeoutError,
)
