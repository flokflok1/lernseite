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

import logging
import os
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

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
    from app.infrastructure.monitoring import record_ai_call
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False


class AIAdapter:
    """AI Adapter with multi-provider support using Factory Pattern."""

    # Expose configuration as class attributes for backwards compatibility
    PROVIDERS = PROVIDERS
    MODELS_USING_COMPLETION_TOKENS = MODELS_USING_COMPLETION_TOKENS

    def __init__(self, provider: str = 'openai', model: Optional[str] = None, timeout: int = 55):
        """
        Initialize AI Adapter.

        Args:
            provider: AI provider ('openai', 'anthropic', 'google', 'cohere', 'huggingface')
            model: Model name (defaults to default model from DB)
            timeout: Request timeout in seconds (default 55s, max 300s)

        Raises:
            ValueError: If provider is invalid or API key is missing
        """
        if provider not in PROVIDERS:
            raise ValueError(f'Invalid provider: {provider}. Must be one of: {", ".join(PROVIDERS.keys())}')

        self.provider = provider
        self.provider_config = PROVIDERS[provider]
        self.timeout = min(timeout, 300)

        # Try to get API key from database first, then fallback to environment
        self.api_key = self._get_api_key_from_db(provider)

        if not self.api_key:
            api_key_env = self.provider_config['api_key_env']
            self.api_key = os.getenv(api_key_env)

        if not self.api_key:
            api_key_env = self.provider_config['api_key_env']
            raise AIInvalidKeyError(f'API key not found. Set {api_key_env} or configure in Admin Panel.')

        # Model from DB (Single Source of Truth)
        if model:
            self.model = model
        else:
            self.model = self._get_default_model(provider)

        # Pricing from DB
        self.pricing = self._get_model_pricing(provider, self.model)

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
            from app.infrastructure.persistence.repositories.ai.config.providers import AIProviderRepository
            return AIProviderRepository.get_decrypted_api_key(provider)
        except Exception:
            logger.warning("Could not fetch API key for '%s' from DB, using env fallback", provider)
            return None

    @staticmethod
    def _get_default_model(provider: str) -> str:
        """Get default model for provider from DB."""
        try:
            from app.infrastructure.persistence.repositories.ai_models.query import AIModelsQueryRepository
            models = AIModelsQueryRepository.get_by_provider(provider)
            if models:
                default = next((m for m in models if m.get('is_default')), None)
                return default['model_name'] if default else models[0]['model_name']
        except Exception:
            logger.warning("Failed to fetch default model for provider '%s' from DB", provider)
        raise ValueError(
            f'No models configured for provider "{provider}". '
            f'Sync models in Admin Panel first.'
        )

    @staticmethod
    def _get_model_pricing(provider: str, model: str) -> dict:
        """Get model pricing and limits from DB."""
        try:
            from app.infrastructure.persistence.repositories.ai_models.query import AIModelsQueryRepository
            info = AIModelsQueryRepository.get_by_name(model, provider)
            if info:
                return {
                    'input_price': float(info.get('input_price_per_1k', 0) or 0),
                    'output_price': float(info.get('output_price_per_1k', 0) or 0),
                    'max_tokens': info.get('max_output_tokens') or 0,
                    'context_window': info.get('context_window') or 0,
                    'category': info.get('category', 'chat'),
                }
        except Exception:
            logger.warning("Failed to fetch pricing for model '%s' (provider '%s') from DB", model, provider)
        # Model not in DB — return zero pricing (no error, just no cost tracking)
        return {
            'input_price': 0.0,
            'output_price': 0.0,
            'max_tokens': 16000,
            'context_window': 128000,
            'category': 'chat',
        }

    @staticmethod
    def detect_provider(model: str) -> str:
        """Detect provider from model name prefix."""
        model_lower = model.lower()
        if model_lower.startswith('claude'):
            return 'anthropic'
        if model_lower.startswith('gemini'):
            return 'google'
        if model_lower.startswith('command'):
            return 'cohere'
        return 'openai'

    def _resolve_max_tokens(self, max_tokens: Optional[int]) -> int:
        """Resolve max_tokens: use model's actual limit if not explicitly set."""
        if max_tokens is not None:
            return max_tokens
        return self.pricing.get('max_tokens', 16000)

    def send_request(
        self,
        prompt: str,
        context: Optional[str] = None,
        language: str = 'de',
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        conversation_history: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Send AI request to configured provider.

        Args:
            prompt: User's input/question
            context: Additional context about the learning material
            language: Response language ('de', 'en', etc.)
            temperature: Randomness (0.0-1.0, higher = more creative)
            max_tokens: Maximum output tokens (None = use model's limit)
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
        max_tokens = self._resolve_max_tokens(max_tokens)
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
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send AI request with pre-formatted messages.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Randomness (0.0-1.0)
            max_tokens: Maximum output tokens

        Returns:
            Same format as send_request()
        """
        # Validate messages format
        if not messages or not isinstance(messages, list):
            raise ValueError("Messages must be a non-empty list")

        for msg in messages:
            if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                raise ValueError("Each message must have 'role' and 'content' keys")
            if msg['role'] not in ['system', 'user', 'assistant']:
                raise ValueError(f"Invalid role: {msg['role']}. Must be 'system', 'user', or 'assistant'")

        max_tokens = self._resolve_max_tokens(max_tokens)
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

    def send_messages_with_tools(
        self,
        messages: list[Dict[str, str]],
        tools: list[Dict],
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """
        Send messages with tool definitions for structured AI responses.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Provider-agnostic tool definitions
            temperature: Randomness (0.0-1.0)
            max_tokens: Maximum output tokens

        Returns:
            Same as send_request() plus 'tool_calls' list
        """
        from .tool_formatters import (
            to_openai_tools, to_anthropic_tools, to_google_tools,
            normalize_tool_calls
        )

        start_time = time.time()

        # Convert tools to provider-specific format and call
        if self.provider == 'openai':
            provider_tools = to_openai_tools(tools)
            raw = OpenAIProvider.send_messages_with_tools(
                self.api_key, self.provider_config['api_url'], self.model,
                messages, provider_tools, temperature, max_tokens, self.timeout
            )
        elif self.provider == 'anthropic':
            provider_tools = to_anthropic_tools(tools)
            raw = AnthropicProvider.send_messages_with_tools(
                self.api_key, self.provider_config['api_url'], self.model,
                messages, provider_tools, temperature, max_tokens, self.timeout
            )
        elif self.provider == 'google':
            provider_tools = to_google_tools(tools)
            raw = GoogleProvider.send_messages_with_tools(
                self.api_key, self.provider_config['api_url'], self.model,
                messages, provider_tools, temperature, max_tokens, self.timeout
            )
        else:
            # Fallback: Provider without tool calling support
            # Call regular send_messages, return empty tool_calls
            result = self.send_messages(messages, temperature, max_tokens)
            result['tool_calls'] = []
            return result

        # Normalize response to unified format
        output_text, tool_calls = normalize_tool_calls(self.provider, raw)

        # Calculate cost and latency
        latency_ms = int((time.time() - start_time) * 1000)
        input_tokens = raw.get('input_tokens', 0)
        output_tokens = raw.get('output_tokens', 0)
        cost_eur = self.calculate_cost(input_tokens, output_tokens)

        if MONITORING_AVAILABLE:
            total_tokens = input_tokens + output_tokens
            record_ai_call(
                method_name='ai_request_tools',
                provider=self.provider,
                duration=latency_ms / 1000.0,
                tokens=total_tokens,
                cost=cost_eur,
                success=True
            )

        return {
            'output_text': output_text,
            'tool_calls': tool_calls,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': input_tokens + output_tokens,
            'cost_eur': cost_eur,
            'latency_ms': latency_ms,
            'model': self.model,
            'provider': self.provider
        }

    def _format_response(
        self,
        response_data: Dict[str, Any],
        start_time: float,
        method_name: str
    ) -> Dict[str, Any]:
        """Format the response with latency, cost, and metadata."""
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
        Get list of available providers and their models from DB.

        Returns:
            {
                'openai': ['gpt-4o', 'gpt-4o-mini', ...],
                'anthropic': ['claude-3-5-sonnet-20241022', ...],
                ...
            }
        """
        try:
            from app.infrastructure.persistence.repositories.ai_models.query import AIModelsQueryRepository
            result = {}
            for provider in PROVIDERS:
                models = AIModelsQueryRepository.get_by_provider(provider)
                result[provider] = [m['model_name'] for m in models]
            return result
        except Exception:
            logger.warning("Failed to fetch available providers from DB")
            return {p: [] for p in PROVIDERS}

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
