"""
LernsystemX AI Adapter - Exception Classes

Custom exceptions for AI provider error handling.
"""


class AIProviderError(Exception):
    """Base exception for AI provider errors"""
    pass


class AIQuotaExceededError(AIProviderError):
    """Raised when API quota is exceeded"""
    pass


class AIInvalidKeyError(AIProviderError):
    """Raised when API key is invalid"""
    pass


class AITimeoutError(AIProviderError):
    """Raised when request times out"""
    pass
