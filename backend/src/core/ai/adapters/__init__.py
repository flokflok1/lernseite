"""
LernsystemX AI Adapter Package

Multi-provider AI integration with Factory Pattern:
- OpenAI (GPT-4o, GPT-4o-mini)
- Anthropic (Claude 3.5 Sonnet, Claude 3 Haiku)
- Google (Gemini Pro, Gemini Flash)
- Cohere (Command, Command Light)
- HuggingFace (Open-source models)

Features:
- Automatic provider selection based on configuration
- Token counting and cost calculation
- Error handling and retry logic
- Timeout management (<60s)
- Request/response logging

ISO 27001:2013 compliant - API key management and security

Usage:
    >>> from app.services.ai import AIAdapter
    >>> adapter = AIAdapter(provider='openai', model='gpt-4o-mini')
    >>> response = adapter.send_request(
    ...     prompt="Explain polymorphism in Python",
    ...     context="We are at OOP basics",
    ...     language="de"
    ... )
    >>> print(response['output_text'])

    # Static convenience methods
    >>> from app.services.ai import chat_completion, text_to_speech
    >>> result = chat_completion(messages=[...], model='gpt-4o-mini')
"""

# Core adapter class
from .adapter import AIAdapter

# Exception classes
from .exceptions import (
    AIProviderError,
    AIQuotaExceededError,
    AIInvalidKeyError,
    AITimeoutError
)

# Configuration
from .config import PROVIDERS, MODELS_USING_COMPLETION_TOKENS

# Static convenience methods
from .static import (
    chat_completion,
    text_to_speech,
    transcribe_audio
)

# Provider implementations (for advanced usage)
from .providers import (
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
