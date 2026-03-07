"""
LernsystemX AI Adapter Package

Multi-provider AI integration with Factory Pattern.
Supported providers: OpenAI, Anthropic, Google, Cohere, HuggingFace.
Model data and pricing are managed in the database (Single Source of Truth).

Features:
- Automatic provider selection based on configuration
- Token counting and cost calculation
- Error handling and retry logic
- Timeout management (<60s)
- Request/response logging

Usage:
    >>> from app.application.services.ai import AIAdapter
    >>> adapter = AIAdapter()  # Uses default provider/model from DB
    >>> response = adapter.send_request(
    ...     prompt="Explain polymorphism in Python",
    ...     context="We are at OOP basics",
    ...     language="de"
    ... )
    >>> print(response['output_text'])

    # Static convenience methods
    >>> from app.application.services.ai import chat_completion, text_to_speech
    >>> result = chat_completion(messages=[...])
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
from app.infrastructure.ai.config import (
    MODELS_USING_COMPLETION_TOKENS,
    DEFAULT_TTS_MODEL,
    DEFAULT_WHISPER_MODEL,
)

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
from .plan.plan_service import PlanService
from .plan.plan_service_part2 import PlanWizardService

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
