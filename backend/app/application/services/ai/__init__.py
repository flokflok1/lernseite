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
    >>> from app.application.services.ai import AIAdapter
    >>> adapter = AIAdapter(provider='openai', model='gpt-4o-mini')
    >>> response = adapter.send_request(
    ...     prompt="Explain polymorphism in Python",
    ...     context="We are at OOP basics",
    ...     language="de"
    ... )
    >>> print(response['output_text'])

    # Static convenience methods
    >>> from app.application.services.ai import chat_completion, text_to_speech
    >>> result = chat_completion(messages=[...], model='gpt-4o-mini')
"""

# Core adapter class (moved to infrastructure layer, bridge in ./adapter.py)
from .adapter import AIAdapter

# Exception classes (moved to infrastructure layer)
from app.infrastructure.ai.exceptions import (
    AIProviderError,
    AIQuotaExceededError,
    AIInvalidKeyError,
    AITimeoutError
)

# Configuration (moved to infrastructure layer)
from app.infrastructure.ai.config import PROVIDERS, MODELS_USING_COMPLETION_TOKENS

# Static convenience methods
from .static import (
    chat_completion,
    text_to_speech,
    transcribe_audio
)

# Context detection
from .context.detector import (
    get_exam_context_sync
)

# Plan services
from .plan_service import PlanService
from .plan_service_part2 import PlanWizardService

# Provider implementations (moved to infrastructure layer)
from app.infrastructure.ai.providers import (  # noqa: F401
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

    # Context detection
    'get_exam_context_sync',

    # Providers
    'OpenAIProvider',
    'AnthropicProvider',
    'GoogleProvider',
    'CohereProvider',
    'HuggingFaceProvider',

    # Plan services
    'PlanService',
    'PlanWizardService',

    # NOTE: AIJobService, PromptResolver, ExamContextDetector are available via:
    # - Direct imports: from app.application.services.ai.job_service import AIJobService
    # - Or bridge files: from app.application.services.ai.job_service import AIJobService
    # They are not re-exported here to avoid circular import issues
]
