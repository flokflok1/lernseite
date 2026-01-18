"""
Backward Compatibility Bridge: ai_adapter

DEPRECATED: Use 'from app.services.ai.adapter import AIAdapter' instead

This bridge maintains backward compatibility with old import paths across the codebase.
The actual implementation is in app.services.ai.adapter and app.services.ai.exceptions.
"""

# Bridge exports for adapter
from app.services.ai.adapter import AIAdapter

# Bridge exports for exceptions
from app.services.ai.exceptions import (
    AIProviderError,
    AIQuotaExceededError,
    AIInvalidKeyError,
    AITimeoutError,
)

__all__ = [
    'AIAdapter',
    'AIProviderError',
    'AIQuotaExceededError',
    'AIInvalidKeyError',
    'AITimeoutError',
]
