"""
LernsystemX AI Adapter Service - Bridge Module

This module re-exports all components from the refactored ai/ package
to maintain backward compatibility with existing imports:

    from app.services.ai_adapter import AIAdapter

The actual implementation is now in app/services/ai/

Package structure:
    app/services/ai/
    ├── __init__.py         - Package init with re-exports
    ├── exceptions.py       - Exception classes
    ├── config.py           - PROVIDERS dict and model configs
    ├── adapter.py          - Core AIAdapter class
    ├── static.py           - Static convenience methods
    └── providers/
        ├── __init__.py     - Provider sub-package
        ├── openai.py       - OpenAI implementation
        ├── anthropic.py    - Anthropic implementation
        ├── google.py       - Google implementation
        ├── cohere.py       - Cohere implementation
        └── huggingface.py  - HuggingFace implementation

ISO 27001:2013 compliant - API key management and security
"""

# Re-export everything from the ai package for backward compatibility
from app.services.ai import (
    # Core
    AIAdapter,

    # Exceptions
    AIProviderError,
    AIQuotaExceededError,
    AIInvalidKeyError,
    AITimeoutError,

    # Configuration
    PROVIDERS,
    MODELS_USING_COMPLETION_TOKENS,

    # Static methods
    chat_completion,
    text_to_speech,
    transcribe_audio,

    # Providers
    OpenAIProvider,
    AnthropicProvider,
    GoogleProvider,
    CohereProvider,
    HuggingFaceProvider
)

__all__ = [
    # Core
    'AIAdapter',

    # Exceptions
    'AIProviderError',
    'AIQuotaExceededError',
    'AIInvalidKeyError',
    'AITimeoutError',

    # Configuration
    'PROVIDERS',
    'MODELS_USING_COMPLETION_TOKENS',

    # Static methods
    'chat_completion',
    'text_to_speech',
    'transcribe_audio',

    # Providers
    'OpenAIProvider',
    'AnthropicProvider',
    'GoogleProvider',
    'CohereProvider',
    'HuggingFaceProvider'
]
