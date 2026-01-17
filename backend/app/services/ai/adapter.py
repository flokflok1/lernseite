"""
LernsystemX AI Adapter - Core AIAdapter Class

Multi-provider AI integration with Factory Pattern.

Features:
- Automatic provider selection based on configuration
- Token counting and cost calculation
- Error handling and retry logic
- Timeout management (<60s)
- Request/response logging

ISO 27001:2013 compliant - API key management and security
"""

import os
import time
from typing import Dict, Any, Optional

from .exceptions import (
    AIProviderError,
    AIQuotaExceededError,
    AIInvalidKeyError,
    AITimeoutError
)
from .config import PROVIDERS, MODELS_USING_COMPLETION_TOKENS
from .providers.openai import OpenAIProvider
from .providers.anthropic import AnthropicProvider
from .providers.google import GoogleProvider
from .providers.cohere import CohereProvider
from .providers.huggingface import HuggingFaceProvider

# Import monitoring (if available)
try:
    from app.monitoring import record_ai_call
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False


class AIAdapter:
    """
    AI Adapter with multi-provider support using Factory Pattern.

    Usage:
        >>> adapter = AIAdapter(provider='openai', model='gpt-4o-mini')
        >>> response = adapter.send_request(
        ...     prompt="Explain polymorphism in Python",
        ...     context="We are at OOP basics",
        ...     language="de"
        ... )
        >>> print(response['output_text'])
        >>> print(response['tokens_used'])
    """

    # Expose configuration as class attributes for backwards compatibility
    PROVIDERS = PROVIDERS
    MODELS_USING_COMPLETION_TOKENS = MODELS_USING_COMPLETION_TOKENS

    def __init__(self, provider: str = 'openai', model: Optional[str] = None, timeout: int = 55):
        """
        Initialize AI Adapter.

        Args:
            provider: AI provider ('openai', 'anthropic', 'google', 'cohere', 'huggingface')
            model: Model name (defaults to first model for provider)
            timeout: Request timeout in seconds (max 55s, API has 60s hard limit)

        Raises:
            ValueError: If provider is invalid or API key is missing
        """
        if provider not in PROVIDERS:
            raise ValueError(f'Invalid provider: {provider}. Must be one of: {", ".join(PROVIDERS.keys())}')

        self.provider = provider
        self.provider_config = PROVIDERS[provider]
        self.timeout = min(timeout, 55)  # Max 55s to stay under 60s API limit

        # Try to get API key from database first, then fallback to environment
        self.api_key = self._get_api_key_from_db(provider)

        if not self.api_key:
            # Fallback to environment variable
            api_key_env = self.provider_config['api_key_env']
            self.api_key = os.getenv(api_key_env)

        if not self.api_key:
            api_key_env = self.provider_config['api_key_env']
            raise AIInvalidKeyError(f'API key not found. Set {api_key_env} environment variable or configure in Admin Panel.')

        # Set model (default to first/cheapest model)
        available_models = list(self.provider_config['models'].keys())
        self.model = model if model else available_models[0]

        if self.model not in self.provider_config['models']:
            raise ValueError(f'Invalid model: {self.model}. Available models: {", ".join(available_models)}')

        # Get pricing
        self.pricing = self.provider_config['models'][self.model]

    @staticmethod
    def _get_api_key_from_db(provider: str) -> Optional[str]:
        """
        Get API key from database (ai_providers table).

        Args:
            provider: Provider name (openai, anthropic, etc.)

        Returns:
            Decrypted API key or None
        """
        try:
            from app.repositories.ai.providers import AIProviderRepository
            return AIProviderRepository.get_decrypted_api_key(provider)
        except Exception:
            # If database is not available, return None to use env fallback
            return None

    def send_request(
        self,
        prompt: str,
        context: Optional[str] = None,
        language: str = 'de',
        temperature: float = 0.7,
        max_tokens: int = 2000,
        conversation_history: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Send AI request to configured provider.

        Args:
            prompt: User's input/question
            context: Additional context about the learning material
            language: Response language ('de', 'en', etc.)
            temperature: Randomness (0.0-1.0, higher = more creative)
            max_tokens: Maximum output tokens
            conversation_history: Previous conversation turns

        Returns:
            {
                'output_text': str,
                'input_tokens': int,
                'output_tokens': int,
                'total_tokens': int,
                'cost_eur': float,
                'latency_ms': int,
                'model': str,
                'provider': str
            }

        Raises:
            AIProviderError: On API errors
            AITimeoutError: On timeout
            AIQuotaExceededError: On quota exceeded
        """
        start_time = time.time()

        # Build request based on provider
        if self.provider == 'openai':
            response_data = OpenAIProvider.send_request(
                self.api_key, self.provider_config['api_url'], self.model,
                prompt, context, language, temperature, max_tokens, conversation_history, self.timeout
            )
        elif self.provider == 'anthropic':
            response_data = AnthropicProvider.send_request(
                self.api_key, self.provider_config['api_url'], self.model,
                prompt, context, language, temperature, max_tokens, conversation_history, self.timeout
            )
        elif self.provider == 'google':
            response_data = GoogleProvider.send_request(
                self.api_key, self.provider_config['api_url'], self.model,
                prompt, context, language, temperature, max_tokens, conversation_history, self.timeout
            )
        elif self.provider == 'cohere':
            response_data = CohereProvider.send_request(
                self.api_key, self.provider_config['api_url'], self.model,
                prompt, context, language, temperature, max_tokens, conversation_history, self.timeout
            )
        elif self.provider == 'huggingface':
            response_data = HuggingFaceProvider.send_request(
                self.api_key, self.provider_config['api_url'], self.model,
                prompt, context, language, temperature, max_tokens, conversation_history, self.timeout
            )
        else:
            raise AIProviderError(f'Provider {self.provider} not implemented')

        return self._format_response(response_data, start_time, 'ai_request')

    def send_messages(
        self,
        messages: list[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Send AI request with pre-formatted messages (Phase 24 - Prompt Templates).

        This method accepts pre-rendered messages from PromptTemplate.render()
        and sends them directly to the AI provider without additional formatting.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
                     Example: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
            temperature: Randomness (0.0-1.0, higher = more creative)
            max_tokens: Maximum output tokens

        Returns:
            {
                'output_text': str,
                'input_tokens': int,
                'output_tokens': int,
                'total_tokens': int,
                'cost_eur': float,
                'latency_ms': int,
                'model': str,
                'provider': str
            }

        Raises:
            AIProviderError: On API errors
            AITimeoutError: On timeout
            AIQuotaExceededError: On quota exceeded
            ValueError: If messages format is invalid

        Usage:
            >>> from app.ai.configuration import get_prompt_template
            >>> template = get_prompt_template("explain_concept")
            >>> messages = template.render({
            ...     "course_title": "Python Basics",
            ...     "lesson_title": "Functions",
            ...     "concept_text": "What is a decorator?",
            ...     "user_level": "intermediate"
            ... })
            >>> adapter = AIAdapter(provider='openai', model='gpt-4o-mini')
            >>> response = adapter.send_messages(messages)
        """
        # Validate messages format
        if not messages or not isinstance(messages, list):
            raise ValueError("Messages must be a non-empty list")

        for msg in messages:
            if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                raise ValueError("Each message must have 'role' and 'content' keys")
            if msg['role'] not in ['system', 'user', 'assistant']:
                raise ValueError(f"Invalid role: {msg['role']}. Must be 'system', 'user', or 'assistant'")

        start_time = time.time()

        # Send to provider based on type
        if self.provider == 'openai':
            response_data = OpenAIProvider.send_messages(
                self.api_key, self.provider_config['api_url'], self.model,
                messages, temperature, max_tokens, self.timeout
            )
        elif self.provider == 'anthropic':
            response_data = AnthropicProvider.send_messages(
                self.api_key, self.provider_config['api_url'], self.model,
                messages, temperature, max_tokens, self.timeout
            )
        elif self.provider == 'google':
            response_data = GoogleProvider.send_messages(
                self.api_key, self.provider_config['api_url'], self.model,
                messages, temperature, max_tokens, self.timeout
            )
        elif self.provider == 'cohere':
            response_data = CohereProvider.send_messages(
                self.api_key, self.provider_config['api_url'], self.model,
                messages, temperature, max_tokens, self.timeout
            )
        elif self.provider == 'huggingface':
            response_data = HuggingFaceProvider.send_messages(
                self.api_key, self.provider_config['api_url'], self.model,
                messages, temperature, max_tokens, self.timeout
            )
        else:
            raise AIProviderError(f'Provider {self.provider} not implemented')

        return self._format_response(response_data, start_time, 'ai_request_template')

    def _format_response(
        self,
        response_data: Dict[str, Any],
        start_time: float,
        method_name: str
    ) -> Dict[str, Any]:
        """
        Format the response with latency, cost, and metadata.

        Args:
            response_data: Raw response from provider
            start_time: Request start time
            method_name: Method name for monitoring

        Returns:
            Formatted response dict
        """
        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)

        # Calculate cost
        cost_eur = self.calculate_cost(response_data['input_tokens'], response_data['output_tokens'])

        # Record AI call metric
        if MONITORING_AVAILABLE:
            total_tokens = response_data['input_tokens'] + response_data['output_tokens']
            record_ai_call(
                method_name=method_name,
                provider=self.provider,
                duration=latency_ms / 1000.0,  # Convert to seconds
                tokens=total_tokens,
                cost=cost_eur,
                success=True
            )

        return {
            'output_text': response_data['output_text'],
            'input_tokens': response_data['input_tokens'],
            'output_tokens': response_data['output_tokens'],
            'total_tokens': response_data['input_tokens'] + response_data['output_tokens'],
            'cost_eur': cost_eur,
            'latency_ms': latency_ms,
            'model': self.model,
            'provider': self.provider
        }

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost in EUR for token usage.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in EUR (rounded to 6 decimals)
        """
        input_cost = (input_tokens / 1000) * self.pricing['input_price']
        output_cost = (output_tokens / 1000) * self.pricing['output_price']
        total_cost = input_cost + output_cost

        return round(total_cost, 6)

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimate token count for text.

        Uses rough approximation: ~4 characters per token for English,
        ~3 characters per token for German (more compound words)

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count
        """
        # Rough estimation: average 3.5 characters per token
        return max(1, len(text) // 4)

    @staticmethod
    def get_available_providers() -> Dict[str, list]:
        """
        Get list of available providers and their models.

        Returns:
            {
                'openai': ['gpt-4o', 'gpt-4o-mini', ...],
                'anthropic': ['claude-3-5-sonnet-20241022', ...],
                ...
            }
        """
        return {
            provider: list(config['models'].keys())
            for provider, config in PROVIDERS.items()
        }

    @staticmethod
    def validate_api_key(provider: str) -> bool:
        """
        Validate that API key exists for provider.

        Args:
            provider: Provider name

        Returns:
            True if API key is set, False otherwise
        """
        if provider not in PROVIDERS:
            return False

        api_key_env = PROVIDERS[provider]['api_key_env']
        return bool(os.getenv(api_key_env))

    def __repr__(self) -> str:
        """String representation."""
        return f'AIAdapter(provider={self.provider}, model={self.model})'
