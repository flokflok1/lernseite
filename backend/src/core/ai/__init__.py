"""
AI Core Module

Central AI system with multi-provider support, pipeline modules, and agent intelligence.

Structure:
- adapters/: AI Adapter with multi-provider support (OpenAI, Anthropic, Google, Cohere, HuggingFace)
- providers/: Provider-specific implementations
- agent/: Agent Intelligence with cross-course knowledge pool
- pipeline/: AI Pipeline with 13 modules
  - parsers/: PDF, Math parsers
  - generators/: Content, Module, Theory, Quiz, Exam, Method generators
  - validators/: Content validators
  - optimizers/: Content optimizers
  - analyzers/: Whiteboard, Image analyzers
- prompts/: Prompt templates (AI Studio, Authoring)
- slots/: Capability slots and requirements
- mappings/: Learning Method and System Features mappings

Usage:
    from src.core.ai import AIAdapter

    adapter = AIAdapter(provider='anthropic', model='claude-3-7-sonnet-20250219')
    response = adapter.send_request(
        prompt="Explain polymorphism in Python",
        context="We are at OOP basics",
        language="de"
    )
"""

# Main AI Adapter
from src.core.ai.adapters.adapter import AIAdapter
from src.core.ai.adapters.exceptions import (
    AIProviderError,
    AIQuotaExceededError,
    AIInvalidKeyError,
    AITimeoutError
)
from src.core.ai.adapters.config import PROVIDERS, MODELS_USING_COMPLETION_TOKENS

# Providers
from src.core.ai.providers.openai import OpenAIProvider
from src.core.ai.providers.anthropic import AnthropicProvider
from src.core.ai.providers.google import GoogleProvider
from src.core.ai.providers.cohere import CohereProvider
from src.core.ai.providers.huggingface import HuggingFaceProvider

__all__ = [
    # Core Adapter
    'AIAdapter',

    # Exceptions
    'AIProviderError',
    'AIQuotaExceededError',
    'AIInvalidKeyError',
    'AITimeoutError',

    # Configuration
    'PROVIDERS',
    'MODELS_USING_COMPLETION_TOKENS',

    # Providers
    'OpenAIProvider',
    'AnthropicProvider',
    'GoogleProvider',
    'CohereProvider',
    'HuggingFaceProvider'
]
