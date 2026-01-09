"""
LernsystemX AI Adapter - Provider Modules

Sub-package containing provider-specific implementations for:
- OpenAI (GPT-4o, GPT-4o-mini, etc.)
- Anthropic (Claude 3.5 Sonnet, Claude 3 Haiku)
- Google (Gemini Pro, Gemini Flash)
- Cohere (Command, Command Light)
- HuggingFace (Open-source models)
"""

from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .google import GoogleProvider
from .cohere import CohereProvider
from .huggingface import HuggingFaceProvider

__all__ = [
    'OpenAIProvider',
    'AnthropicProvider',
    'GoogleProvider',
    'CohereProvider',
    'HuggingFaceProvider'
]
