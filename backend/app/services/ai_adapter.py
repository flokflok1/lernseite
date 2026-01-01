"""
LernsystemX AI Adapter Service

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
"""

import os
import time
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import requests
from requests.exceptions import RequestException, Timeout

# Import monitoring (if available)
try:
    from app.monitoring import record_ai_call
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False


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


class AIAdapter:
    """
    AI Adapter with multi-provider support using Factory Pattern

    Usage:
        >>> adapter = AIAdapter(provider='openai', model='gpt-4o-mini')
        >>> response = adapter.send_request(
        ...     prompt="Erkläre Polymorphismus in Python",
        ...     context="Wir sind bei OOP Grundlagen",
        ...     language="de"
        ... )
        >>> print(response['output_text'])
        >>> print(response['tokens_used'])
    """

    # Provider configurations
    PROVIDERS = {
        'openai': {
            'api_url': 'https://api.openai.com/v1/chat/completions',
            'api_key_env': 'OPENAI_API_KEY',
            'display_name': 'OpenAI',
            'models': {
                # ============================================================
                # GPT-5 Series (2025) - Latest flagship models
                # ============================================================
                'gpt-5.1': {'input_price': 0.005, 'output_price': 0.020, 'max_tokens': 64000, 'context_window': 256000, 'category': 'chat'},
                'gpt-5': {'input_price': 0.004, 'output_price': 0.016, 'max_tokens': 64000, 'context_window': 256000, 'category': 'chat'},
                'gpt-5-mini': {'input_price': 0.001, 'output_price': 0.004, 'max_tokens': 32768, 'context_window': 128000, 'category': 'chat'},
                'gpt-5-nano': {'input_price': 0.0002, 'output_price': 0.0008, 'max_tokens': 16384, 'context_window': 64000, 'category': 'chat'},
                'gpt-5-pro': {'input_price': 0.010, 'output_price': 0.040, 'max_tokens': 128000, 'context_window': 512000, 'category': 'chat'},
                'gpt-5.1-chat-latest': {'input_price': 0.005, 'output_price': 0.020, 'max_tokens': 64000, 'context_window': 256000, 'category': 'chat'},
                'gpt-5-chat-latest': {'input_price': 0.004, 'output_price': 0.016, 'max_tokens': 64000, 'context_window': 256000, 'category': 'chat'},

                # ============================================================
                # GPT-5 Codex Series (2025) - Code generation specialists
                # ============================================================
                'gpt-5.1-codex': {'input_price': 0.006, 'output_price': 0.024, 'max_tokens': 64000, 'context_window': 256000, 'category': 'coding'},
                'gpt-5-codex': {'input_price': 0.005, 'output_price': 0.020, 'max_tokens': 64000, 'context_window': 256000, 'category': 'coding'},
                'gpt-5.1-codex-mini': {'input_price': 0.002, 'output_price': 0.008, 'max_tokens': 32768, 'context_window': 128000, 'category': 'coding'},

                # ============================================================
                # O-Series Reasoning Models (2025) - Deep reasoning capabilities
                # ============================================================
                'o3': {'input_price': 0.010, 'output_price': 0.040, 'max_tokens': 100000, 'context_window': 200000, 'category': 'reasoning'},
                'o3-pro': {'input_price': 0.020, 'output_price': 0.080, 'max_tokens': 100000, 'context_window': 200000, 'category': 'reasoning'},
                'o3-mini': {'input_price': 0.0011, 'output_price': 0.0044, 'max_tokens': 65536, 'context_window': 200000, 'category': 'reasoning'},
                'o3-deep-research': {'input_price': 0.030, 'output_price': 0.120, 'max_tokens': 100000, 'context_window': 200000, 'category': 'reasoning'},
                'o4-mini': {'input_price': 0.0011, 'output_price': 0.0044, 'max_tokens': 100000, 'context_window': 200000, 'category': 'reasoning'},
                'o4-mini-deep-research': {'input_price': 0.010, 'output_price': 0.040, 'max_tokens': 100000, 'context_window': 200000, 'category': 'reasoning'},
                'o1': {'input_price': 0.015, 'output_price': 0.060, 'max_tokens': 100000, 'context_window': 200000, 'category': 'reasoning'},
                'o1-pro': {'input_price': 0.150, 'output_price': 0.600, 'max_tokens': 100000, 'context_window': 200000, 'category': 'reasoning'},
                'o1-mini': {'input_price': 0.003, 'output_price': 0.012, 'max_tokens': 65536, 'context_window': 128000, 'category': 'reasoning'},
                'o1-preview': {'input_price': 0.015, 'output_price': 0.060, 'max_tokens': 32768, 'context_window': 128000, 'category': 'reasoning'},

                # ============================================================
                # GPT-4.1 Series (2025) - Smartest non-reasoning models
                # ============================================================
                'gpt-4.1': {'input_price': 0.002, 'output_price': 0.008, 'max_tokens': 32768, 'context_window': 1000000, 'category': 'chat'},
                'gpt-4.1-mini': {'input_price': 0.0004, 'output_price': 0.0016, 'max_tokens': 32768, 'context_window': 1000000, 'category': 'chat'},
                'gpt-4.1-nano': {'input_price': 0.0001, 'output_price': 0.0004, 'max_tokens': 32768, 'context_window': 1000000, 'category': 'chat'},

                # ============================================================
                # GPT-4o Series (Multimodal - Text, Vision, Audio)
                # ============================================================
                'gpt-4o': {'input_price': 0.0025, 'output_price': 0.010, 'max_tokens': 16384, 'context_window': 128000, 'category': 'chat'},
                'gpt-4o-mini': {'input_price': 0.00015, 'output_price': 0.0006, 'max_tokens': 16384, 'context_window': 128000, 'category': 'chat'},
                'chatgpt-4o-latest': {'input_price': 0.005, 'output_price': 0.015, 'max_tokens': 16384, 'context_window': 128000, 'category': 'chat'},

                # ============================================================
                # Search Preview Models (2025) - Web search integration
                # ============================================================
                'gpt-4o-search-preview': {'input_price': 0.003, 'output_price': 0.012, 'max_tokens': 16384, 'context_window': 128000, 'category': 'search'},
                'gpt-4o-mini-search-preview': {'input_price': 0.0003, 'output_price': 0.0012, 'max_tokens': 16384, 'context_window': 128000, 'category': 'search'},

                # ============================================================
                # Computer Use Models (2025) - Agentic automation
                # ============================================================
                'computer-use-preview': {'input_price': 0.003, 'output_price': 0.012, 'max_tokens': 16384, 'context_window': 128000, 'category': 'agent'},

                # ============================================================
                # Realtime API Models (Voice/Audio in real-time)
                # ============================================================
                'gpt-realtime': {'input_price': 0.005, 'output_price': 0.020, 'max_tokens': 4096, 'context_window': 128000, 'category': 'realtime'},
                'gpt-realtime-mini': {'input_price': 0.001, 'output_price': 0.004, 'max_tokens': 4096, 'context_window': 128000, 'category': 'realtime'},
                'gpt-4o-realtime-preview': {'input_price': 0.005, 'output_price': 0.020, 'max_tokens': 4096, 'context_window': 128000, 'category': 'realtime'},
                'gpt-4o-mini-realtime-preview': {'input_price': 0.0006, 'output_price': 0.0024, 'max_tokens': 4096, 'context_window': 128000, 'category': 'realtime'},

                # ============================================================
                # Audio Models (Transcription, TTS & Speech)
                # ============================================================
                'gpt-audio': {'input_price': 0.008, 'output_price': 0.032, 'max_tokens': 16384, 'context_window': 128000, 'category': 'audio'},
                'gpt-audio-mini': {'input_price': 0.002, 'output_price': 0.008, 'max_tokens': 16384, 'context_window': 128000, 'category': 'audio'},
                'gpt-4o-audio-preview': {'input_price': 0.0025, 'output_price': 0.010, 'max_tokens': 16384, 'context_window': 128000, 'category': 'audio'},
                'gpt-4o-mini-audio-preview': {'input_price': 0.00015, 'output_price': 0.0006, 'max_tokens': 16384, 'context_window': 128000, 'category': 'audio'},
                'gpt-4o-transcribe': {'input_price': 0.006, 'output_price': 0.006, 'max_tokens': 16384, 'context_window': 128000, 'category': 'audio'},
                'gpt-4o-mini-transcribe': {'input_price': 0.003, 'output_price': 0.003, 'max_tokens': 16384, 'context_window': 128000, 'category': 'audio'},
                'gpt-4o-transcribe-diarize': {'input_price': 0.010, 'output_price': 0.010, 'max_tokens': 16384, 'context_window': 128000, 'category': 'audio'},
                'gpt-4o-mini-tts': {'input_price': 0.006, 'output_price': 0.006, 'max_tokens': 0, 'context_window': 4096, 'category': 'audio'},
                'whisper-1': {'input_price': 0.006, 'output_price': 0.006, 'max_tokens': 0, 'context_window': 0, 'category': 'audio'},
                'tts-1': {'input_price': 0.015, 'output_price': 0.015, 'max_tokens': 0, 'context_window': 4096, 'category': 'audio'},
                'tts-1-hd': {'input_price': 0.030, 'output_price': 0.030, 'max_tokens': 0, 'context_window': 4096, 'category': 'audio'},

                # ============================================================
                # Video Models (Sora 2 Series)
                # ============================================================
                'sora-2': {'input_price': 0.0, 'output_price': 0.100, 'max_tokens': 0, 'context_window': 0, 'category': 'video'},
                'sora-2-pro': {'input_price': 0.0, 'output_price': 0.200, 'max_tokens': 0, 'context_window': 0, 'category': 'video'},

                # ============================================================
                # Image Generation (GPT-Image & DALL-E)
                # ============================================================
                'gpt-image-1': {'input_price': 0.0, 'output_price': 0.040, 'max_tokens': 0, 'context_window': 0, 'category': 'image'},
                'gpt-image-1-mini': {'input_price': 0.0, 'output_price': 0.020, 'max_tokens': 0, 'context_window': 0, 'category': 'image'},
                'dall-e-3': {'input_price': 0.0, 'output_price': 0.040, 'max_tokens': 0, 'context_window': 0, 'category': 'image'},
                'dall-e-2': {'input_price': 0.0, 'output_price': 0.020, 'max_tokens': 0, 'context_window': 0, 'category': 'image'},

                # ============================================================
                # GPT-4 Turbo & Legacy GPT-4
                # ============================================================
                'gpt-4-turbo': {'input_price': 0.010, 'output_price': 0.030, 'max_tokens': 4096, 'context_window': 128000, 'category': 'chat'},
                'gpt-4-turbo-preview': {'input_price': 0.010, 'output_price': 0.030, 'max_tokens': 4096, 'context_window': 128000, 'category': 'chat'},
                'gpt-4': {'input_price': 0.030, 'output_price': 0.060, 'max_tokens': 8192, 'context_window': 8192, 'category': 'chat'},
                'gpt-4.5-preview': {'input_price': 0.010, 'output_price': 0.030, 'max_tokens': 16384, 'context_window': 128000, 'category': 'chat'},

                # ============================================================
                # GPT-3.5 Turbo (Legacy, cost-effective)
                # ============================================================
                'gpt-3.5-turbo': {'input_price': 0.0005, 'output_price': 0.0015, 'max_tokens': 4096, 'context_window': 16385, 'category': 'chat'},

                # ============================================================
                # Embeddings Models
                # ============================================================
                'text-embedding-3-large': {'input_price': 0.00013, 'output_price': 0.0, 'max_tokens': 0, 'context_window': 8191, 'category': 'embedding'},
                'text-embedding-3-small': {'input_price': 0.00002, 'output_price': 0.0, 'max_tokens': 0, 'context_window': 8191, 'category': 'embedding'},
                'text-embedding-ada-002': {'input_price': 0.0001, 'output_price': 0.0, 'max_tokens': 0, 'context_window': 8191, 'category': 'embedding'},

                # ============================================================
                # Moderation Models (Free)
                # ============================================================
                'omni-moderation-latest': {'input_price': 0.0, 'output_price': 0.0, 'max_tokens': 0, 'context_window': 0, 'category': 'moderation'},
                'text-moderation-latest': {'input_price': 0.0, 'output_price': 0.0, 'max_tokens': 0, 'context_window': 0, 'category': 'moderation'},
                'text-moderation-stable': {'input_price': 0.0, 'output_price': 0.0, 'max_tokens': 0, 'context_window': 0, 'category': 'moderation'},

                # ============================================================
                # Open-Source / Open-Weight Models (GPT-OSS)
                # ============================================================
                'gpt-oss-120b': {'input_price': 0.003, 'output_price': 0.012, 'max_tokens': 32768, 'context_window': 128000, 'category': 'open-source'},
                'gpt-oss-20b': {'input_price': 0.0005, 'output_price': 0.002, 'max_tokens': 32768, 'context_window': 128000, 'category': 'open-source'},

                # ============================================================
                # Legacy/Deprecated Models
                # ============================================================
                'babbage-002': {'input_price': 0.0004, 'output_price': 0.0004, 'max_tokens': 16384, 'context_window': 16384, 'category': 'legacy'},
                'davinci-002': {'input_price': 0.002, 'output_price': 0.002, 'max_tokens': 16384, 'context_window': 16384, 'category': 'legacy'}
            }
        },
        'anthropic': {
            'api_url': 'https://api.anthropic.com/v1/messages',
            'api_key_env': 'ANTHROPIC_API_KEY',
            'display_name': 'Anthropic',
            'models': {
                'claude-sonnet-4-20250514': {'input_price': 0.003, 'output_price': 0.015, 'max_tokens': 64000, 'context_window': 200000, 'category': 'chat'},
                'claude-3-5-sonnet-20241022': {'input_price': 0.003, 'output_price': 0.015, 'max_tokens': 8192, 'context_window': 200000, 'category': 'chat'},
                'claude-3-5-haiku-20241022': {'input_price': 0.001, 'output_price': 0.005, 'max_tokens': 8192, 'context_window': 200000, 'category': 'chat'},
                'claude-3-opus-20240229': {'input_price': 0.015, 'output_price': 0.075, 'max_tokens': 4096, 'context_window': 200000, 'category': 'chat'},
                'claude-3-haiku-20240307': {'input_price': 0.00025, 'output_price': 0.00125, 'max_tokens': 4096, 'context_window': 200000, 'category': 'chat'}
            }
        },
        'google': {
            'api_url': 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
            'api_key_env': 'GOOGLE_API_KEY',
            'display_name': 'Google',
            'models': {
                'gemini-2.0-flash': {'input_price': 0.0001, 'output_price': 0.0004, 'max_tokens': 8192, 'context_window': 1000000, 'category': 'chat'},
                'gemini-2.0-pro': {'input_price': 0.00125, 'output_price': 0.005, 'max_tokens': 8192, 'context_window': 1000000, 'category': 'chat'},
                'gemini-1.5-pro': {'input_price': 0.00125, 'output_price': 0.005, 'max_tokens': 8192, 'context_window': 2000000, 'category': 'chat'},
                'gemini-1.5-flash': {'input_price': 0.000075, 'output_price': 0.0003, 'max_tokens': 8192, 'context_window': 1000000, 'category': 'chat'},
                'gemini-pro': {'input_price': 0.0005, 'output_price': 0.0015, 'max_tokens': 8192, 'context_window': 32000, 'category': 'chat'}
            }
        },
        'cohere': {
            'api_url': 'https://api.cohere.ai/v1/chat',
            'api_key_env': 'COHERE_API_KEY',
            'display_name': 'Cohere',
            'models': {
                'command-r-plus': {'input_price': 0.003, 'output_price': 0.015, 'max_tokens': 4096, 'context_window': 128000, 'category': 'chat'},
                'command-r': {'input_price': 0.0005, 'output_price': 0.0015, 'max_tokens': 4096, 'context_window': 128000, 'category': 'chat'},
                'command': {'input_price': 0.0015, 'output_price': 0.002, 'max_tokens': 4096, 'context_window': 4096, 'category': 'chat'},
                'command-light': {'input_price': 0.0003, 'output_price': 0.0006, 'max_tokens': 4096, 'context_window': 4096, 'category': 'chat'}
            }
        },
        'huggingface': {
            'api_url': 'https://api-inference.huggingface.co/models/{model}',
            'api_key_env': 'HUGGINGFACE_API_KEY',
            'display_name': 'HuggingFace',
            'models': {
                'meta-llama/Llama-3.2-3B-Instruct': {'input_price': 0.0001, 'output_price': 0.0002, 'max_tokens': 4096, 'context_window': 128000, 'category': 'chat'},
                'meta-llama/Llama-3.1-70B-Instruct': {'input_price': 0.0009, 'output_price': 0.0009, 'max_tokens': 4096, 'context_window': 128000, 'category': 'chat'},
                'mistralai/Mistral-7B-Instruct-v0.3': {'input_price': 0.0001, 'output_price': 0.0002, 'max_tokens': 4096, 'context_window': 32000, 'category': 'chat'},
                'mistralai/Mixtral-8x7B-Instruct-v0.1': {'input_price': 0.0007, 'output_price': 0.0007, 'max_tokens': 4096, 'context_window': 32000, 'category': 'chat'}
            }
        }
    }

    # Models that require max_completion_tokens instead of max_tokens
    # (GPT-5 series, O-series reasoning models, O4 series)
    MODELS_USING_COMPLETION_TOKENS = [
        'gpt-5', 'gpt-5.1', 'gpt-5-mini', 'gpt-5-nano', 'gpt-5-pro',
        'gpt-5.1-chat-latest', 'gpt-5-chat-latest',
        'gpt-5.1-codex', 'gpt-5-codex', 'gpt-5.1-codex-mini',
        'o1', 'o1-pro', 'o1-mini', 'o1-preview',
        'o3', 'o3-pro', 'o3-mini', 'o3-deep-research',
        'o4-mini', 'o4-mini-deep-research'
    ]

    def __init__(self, provider: str = 'openai', model: Optional[str] = None, timeout: int = 55):
        """
        Initialize AI Adapter

        Args:
            provider: AI provider ('openai', 'anthropic', 'google', 'cohere', 'huggingface')
            model: Model name (defaults to cheapest model for provider)
            timeout: Request timeout in seconds (max 55s, API has 60s hard limit)

        Raises:
            ValueError: If provider is invalid or API key is missing
        """
        if provider not in self.PROVIDERS:
            raise ValueError(f'Invalid provider: {provider}. Must be one of: {", ".join(self.PROVIDERS.keys())}')

        self.provider = provider
        self.provider_config = self.PROVIDERS[provider]
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
        Get API key from database (ai_providers table)

        Args:
            provider: Provider name (openai, anthropic, etc.)

        Returns:
            Decrypted API key or None
        """
        try:
            from app.repositories.ai_provider_repository import AIProviderRepository
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
        Send AI request to configured provider

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
            response_data = self._send_openai_request(prompt, context, language, temperature, max_tokens, conversation_history)
        elif self.provider == 'anthropic':
            response_data = self._send_anthropic_request(prompt, context, language, temperature, max_tokens, conversation_history)
        elif self.provider == 'google':
            response_data = self._send_google_request(prompt, context, language, temperature, max_tokens, conversation_history)
        elif self.provider == 'cohere':
            response_data = self._send_cohere_request(prompt, context, language, temperature, max_tokens, conversation_history)
        elif self.provider == 'huggingface':
            response_data = self._send_huggingface_request(prompt, context, language, temperature, max_tokens, conversation_history)
        else:
            raise AIProviderError(f'Provider {self.provider} not implemented')

        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)

        # Calculate cost
        cost_eur = self.calculate_cost(response_data['input_tokens'], response_data['output_tokens'])

        # Record AI call metric
        if MONITORING_AVAILABLE:
            total_tokens = response_data['input_tokens'] + response_data['output_tokens']
            record_ai_call(
                method_name='ai_request',
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
            >>> from app.ki import get_prompt_template
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
            response_data = self._send_openai_messages(messages, temperature, max_tokens)
        elif self.provider == 'anthropic':
            response_data = self._send_anthropic_messages(messages, temperature, max_tokens)
        elif self.provider == 'google':
            response_data = self._send_google_messages(messages, temperature, max_tokens)
        elif self.provider == 'cohere':
            response_data = self._send_cohere_messages(messages, temperature, max_tokens)
        elif self.provider == 'huggingface':
            response_data = self._send_huggingface_messages(messages, temperature, max_tokens)
        else:
            raise AIProviderError(f'Provider {self.provider} not implemented')

        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)

        # Calculate cost
        cost_eur = self.calculate_cost(response_data['input_tokens'], response_data['output_tokens'])

        # Record AI call metric
        if MONITORING_AVAILABLE:
            total_tokens = response_data['input_tokens'] + response_data['output_tokens']
            record_ai_call(
                method_name='ai_request_template',
                provider=self.provider,
                duration=latency_ms / 1000.0,
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

    def _send_openai_messages(
        self,
        messages: list[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Send pre-formatted messages to OpenAI API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature
        }

        # Use max_completion_tokens for newer models, max_tokens for legacy
        if any(self.model.startswith(m) for m in self.MODELS_USING_COMPLETION_TOKENS):
            payload['max_completion_tokens'] = max_tokens
        else:
            payload['max_tokens'] = max_tokens

        try:
            response = requests.post(
                self.provider_config['api_url'],
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            return {
                'output_text': data['choices'][0]['message']['content'],
                'input_tokens': data['usage']['prompt_tokens'],
                'output_tokens': data['usage']['completion_tokens']
            }

        except Timeout:
            raise AITimeoutError(f'OpenAI request timed out after {self.timeout}s')
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise AIQuotaExceededError('OpenAI quota exceeded')
            elif e.response.status_code == 401:
                raise AIInvalidKeyError('Invalid OpenAI API key')
            else:
                raise AIProviderError(f'OpenAI API error: {e.response.text}')
        except RequestException as e:
            raise AIProviderError(f'OpenAI request failed: {str(e)}')

    def _send_anthropic_messages(
        self,
        messages: list[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Send pre-formatted messages to Anthropic API"""
        # Anthropic requires system message separate from messages array
        system_message = None
        conversation_messages = []

        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                conversation_messages.append(msg)

        headers = {
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': self.model,
            'messages': conversation_messages,
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        if system_message:
            payload['system'] = system_message

        try:
            response = requests.post(
                self.provider_config['api_url'],
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            return {
                'output_text': data['content'][0]['text'],
                'input_tokens': data['usage']['input_tokens'],
                'output_tokens': data['usage']['output_tokens']
            }

        except Timeout:
            raise AITimeoutError(f'Anthropic request timed out after {self.timeout}s')
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise AIQuotaExceededError('Anthropic quota exceeded')
            elif e.response.status_code == 401:
                raise AIInvalidKeyError('Invalid Anthropic API key')
            else:
                raise AIProviderError(f'Anthropic API error: {e.response.text}')
        except RequestException as e:
            raise AIProviderError(f'Anthropic request failed: {str(e)}')

    def _send_google_messages(
        self,
        messages: list[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Send pre-formatted messages to Google Gemini API"""
        # Google Gemini uses a different format - convert messages
        system_instruction = None
        conversation_parts = []

        for msg in messages:
            if msg['role'] == 'system':
                system_instruction = msg['content']
            elif msg['role'] == 'user':
                conversation_parts.append({'role': 'user', 'parts': [{'text': msg['content']}]})
            elif msg['role'] == 'assistant':
                conversation_parts.append({'role': 'model', 'parts': [{'text': msg['content']}]})

        api_url = self.provider_config['api_url'].format(model=self.model)
        url_with_key = f"{api_url}?key={self.api_key}"

        payload = {
            'contents': conversation_parts,
            'generationConfig': {
                'temperature': temperature,
                'maxOutputTokens': max_tokens
            }
        }

        if system_instruction:
            payload['systemInstruction'] = {'parts': [{'text': system_instruction}]}

        try:
            response = requests.post(url_with_key, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            output_text = data['candidates'][0]['content']['parts'][0]['text']
            # Google doesn't always return token counts - estimate if needed
            input_tokens = data.get('usageMetadata', {}).get('promptTokenCount', len(' '.join([m['content'] for m in messages])) // 4)
            output_tokens = data.get('usageMetadata', {}).get('candidatesTokenCount', len(output_text) // 4)

            return {
                'output_text': output_text,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens
            }

        except Timeout:
            raise AITimeoutError(f'Google request timed out after {self.timeout}s')
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise AIQuotaExceededError('Google quota exceeded')
            elif e.response.status_code == 401:
                raise AIInvalidKeyError('Invalid Google API key')
            else:
                raise AIProviderError(f'Google API error: {e.response.text}')
        except RequestException as e:
            raise AIProviderError(f'Google request failed: {str(e)}')

    def _send_cohere_messages(
        self,
        messages: list[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Send pre-formatted messages to Cohere API"""
        # Cohere uses chat_history format
        preamble = None
        chat_history = []
        message = None

        for msg in messages:
            if msg['role'] == 'system':
                preamble = msg['content']
            elif msg['role'] == 'user':
                if len(chat_history) > 0 or message is not None:
                    chat_history.append({'role': 'USER', 'message': msg['content']})
                else:
                    message = msg['content']
            elif msg['role'] == 'assistant':
                chat_history.append({'role': 'CHATBOT', 'message': msg['content']})

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': self.model,
            'message': message or "Continue",
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        if preamble:
            payload['preamble'] = preamble
        if chat_history:
            payload['chat_history'] = chat_history

        try:
            response = requests.post(
                self.provider_config['api_url'],
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            return {
                'output_text': data['text'],
                'input_tokens': data.get('meta', {}).get('tokens', {}).get('input_tokens', 0),
                'output_tokens': data.get('meta', {}).get('tokens', {}).get('output_tokens', 0)
            }

        except Timeout:
            raise AITimeoutError(f'Cohere request timed out after {self.timeout}s')
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise AIQuotaExceededError('Cohere quota exceeded')
            elif e.response.status_code == 401:
                raise AIInvalidKeyError('Invalid Cohere API key')
            else:
                raise AIProviderError(f'Cohere API error: {e.response.text}')
        except RequestException as e:
            raise AIProviderError(f'Cohere request failed: {str(e)}')

    def _send_huggingface_messages(
        self,
        messages: list[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Send pre-formatted messages to HuggingFace API"""
        # HuggingFace inference API expects a single prompt - concatenate messages
        prompt_parts = []
        for msg in messages:
            role_prefix = {
                'system': 'System:',
                'user': 'User:',
                'assistant': 'Assistant:'
            }.get(msg['role'], '')
            prompt_parts.append(f"{role_prefix} {msg['content']}")

        full_prompt = "\n\n".join(prompt_parts) + "\n\nAssistant:"

        api_url = self.provider_config['api_url'].format(model=self.model)
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'inputs': full_prompt,
            'parameters': {
                'temperature': temperature,
                'max_new_tokens': max_tokens,
                'return_full_text': False
            }
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            output_text = data[0]['generated_text'] if isinstance(data, list) else data.get('generated_text', '')

            # HuggingFace doesn't provide token counts - estimate
            input_tokens = len(full_prompt) // 4
            output_tokens = len(output_text) // 4

            return {
                'output_text': output_text,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens
            }

        except Timeout:
            raise AITimeoutError(f'HuggingFace request timed out after {self.timeout}s')
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise AIQuotaExceededError('HuggingFace quota exceeded')
            elif e.response.status_code == 401:
                raise AIInvalidKeyError('Invalid HuggingFace API key')
            else:
                raise AIProviderError(f'HuggingFace API error: {e.response.text}')
        except RequestException as e:
            raise AIProviderError(f'HuggingFace request failed: {str(e)}')

    def _send_openai_request(
        self,
        prompt: str,
        context: Optional[str],
        language: str,
        temperature: float,
        max_tokens: int,
        conversation_history: Optional[list]
    ) -> Dict[str, Any]:
        """Send request to OpenAI API"""
        # Build messages
        messages = []

        # System message
        system_content = f"You are an expert AI tutor. Respond in {language}."
        if context:
            system_content += f"\n\nContext: {context}"
        messages.append({"role": "system", "content": system_content})

        # Conversation history
        if conversation_history:
            messages.extend(conversation_history)

        # User prompt
        messages.append({"role": "user", "content": prompt})

        # Prepare request
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature
        }

        # Use max_completion_tokens for newer models, max_tokens for legacy
        if any(self.model.startswith(m) for m in self.MODELS_USING_COMPLETION_TOKENS):
            payload['max_completion_tokens'] = max_tokens
        else:
            payload['max_tokens'] = max_tokens

        try:
            response = requests.post(
                self.provider_config['api_url'],
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            return {
                'output_text': data['choices'][0]['message']['content'],
                'input_tokens': data['usage']['prompt_tokens'],
                'output_tokens': data['usage']['completion_tokens']
            }

        except Timeout:
            raise AITimeoutError(f'OpenAI request timed out after {self.timeout}s')
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise AIQuotaExceededError('OpenAI quota exceeded')
            elif e.response.status_code == 401:
                raise AIInvalidKeyError('Invalid OpenAI API key')
            else:
                raise AIProviderError(f'OpenAI API error: {e.response.text}')
        except Exception as e:
            raise AIProviderError(f'OpenAI request failed: {str(e)}')

    def _send_anthropic_request(
        self,
        prompt: str,
        context: Optional[str],
        language: str,
        temperature: float,
        max_tokens: int,
        conversation_history: Optional[list]
    ) -> Dict[str, Any]:
        """Send request to Anthropic API"""
        # Build messages
        messages = []

        # Conversation history
        if conversation_history:
            messages.extend(conversation_history)

        # User prompt with context
        user_content = prompt
        if context:
            user_content = f"Context: {context}\n\n{prompt}"

        messages.append({"role": "user", "content": user_content})

        # System message
        system_message = f"You are an expert AI tutor. Respond in {language}."

        headers = {
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': self.model,
            'messages': messages,
            'system': system_message,
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        try:
            response = requests.post(
                self.provider_config['api_url'],
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            return {
                'output_text': data['content'][0]['text'],
                'input_tokens': data['usage']['input_tokens'],
                'output_tokens': data['usage']['output_tokens']
            }

        except Timeout:
            raise AITimeoutError(f'Anthropic request timed out after {self.timeout}s')
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise AIQuotaExceededError('Anthropic quota exceeded')
            elif e.response.status_code == 401:
                raise AIInvalidKeyError('Invalid Anthropic API key')
            else:
                raise AIProviderError(f'Anthropic API error: {e.response.text}')
        except Exception as e:
            raise AIProviderError(f'Anthropic request failed: {str(e)}')

    def _send_google_request(
        self,
        prompt: str,
        context: Optional[str],
        language: str,
        temperature: float,
        max_tokens: int,
        conversation_history: Optional[list]
    ) -> Dict[str, Any]:
        """Send request to Google Gemini API"""
        # Build prompt
        full_prompt = f"You are an expert AI tutor. Respond in {language}.\n\n"
        if context:
            full_prompt += f"Context: {context}\n\n"
        full_prompt += prompt

        # Format API URL
        api_url = self.provider_config['api_url'].format(model=self.model)
        api_url += f"?key={self.api_key}"

        payload = {
            'contents': [{
                'parts': [{'text': full_prompt}]
            }],
            'generationConfig': {
                'temperature': temperature,
                'maxOutputTokens': max_tokens
            }
        }

        try:
            response = requests.post(
                api_url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            output_text = data['candidates'][0]['content']['parts'][0]['text']

            # Estimate tokens (Google doesn't always provide exact counts)
            input_tokens = self.estimate_tokens(full_prompt)
            output_tokens = self.estimate_tokens(output_text)

            return {
                'output_text': output_text,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens
            }

        except Timeout:
            raise AITimeoutError(f'Google request timed out after {self.timeout}s')
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise AIQuotaExceededError('Google quota exceeded')
            elif e.response.status_code == 401:
                raise AIInvalidKeyError('Invalid Google API key')
            else:
                raise AIProviderError(f'Google API error: {e.response.text}')
        except Exception as e:
            raise AIProviderError(f'Google request failed: {str(e)}')

    def _send_cohere_request(
        self,
        prompt: str,
        context: Optional[str],
        language: str,
        temperature: float,
        max_tokens: int,
        conversation_history: Optional[list]
    ) -> Dict[str, Any]:
        """Send request to Cohere API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        # Build message
        message = prompt
        preamble = f"You are an expert AI tutor. Respond in {language}."
        if context:
            preamble += f"\n\nContext: {context}"

        payload = {
            'model': self.model,
            'message': message,
            'preamble': preamble,
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        try:
            response = requests.post(
                self.provider_config['api_url'],
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            output_text = data['text']

            # Estimate tokens
            input_tokens = self.estimate_tokens(preamble + message)
            output_tokens = self.estimate_tokens(output_text)

            return {
                'output_text': output_text,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens
            }

        except Timeout:
            raise AITimeoutError(f'Cohere request timed out after {self.timeout}s')
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise AIQuotaExceededError('Cohere quota exceeded')
            elif e.response.status_code == 401:
                raise AIInvalidKeyError('Invalid Cohere API key')
            else:
                raise AIProviderError(f'Cohere API error: {e.response.text}')
        except Exception as e:
            raise AIProviderError(f'Cohere request failed: {str(e)}')

    def _send_huggingface_request(
        self,
        prompt: str,
        context: Optional[str],
        language: str,
        temperature: float,
        max_tokens: int,
        conversation_history: Optional[list]
    ) -> Dict[str, Any]:
        """Send request to HuggingFace Inference API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        # Build prompt
        full_prompt = f"You are an expert AI tutor. Respond in {language}.\n\n"
        if context:
            full_prompt += f"Context: {context}\n\n"
        full_prompt += f"User: {prompt}\nAssistant:"

        # Format API URL
        api_url = self.provider_config['api_url'].format(model=self.model)

        payload = {
            'inputs': full_prompt,
            'parameters': {
                'temperature': temperature,
                'max_new_tokens': max_tokens,
                'return_full_text': False
            }
        }

        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            output_text = data[0]['generated_text'] if isinstance(data, list) else data['generated_text']

            # Estimate tokens
            input_tokens = self.estimate_tokens(full_prompt)
            output_tokens = self.estimate_tokens(output_text)

            return {
                'output_text': output_text,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens
            }

        except Timeout:
            raise AITimeoutError(f'HuggingFace request timed out after {self.timeout}s')
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise AIQuotaExceededError('HuggingFace quota exceeded')
            elif e.response.status_code == 401:
                raise AIInvalidKeyError('Invalid HuggingFace API key')
            else:
                raise AIProviderError(f'HuggingFace API error: {e.response.text}')
        except Exception as e:
            raise AIProviderError(f'HuggingFace request failed: {str(e)}')

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost in EUR for token usage

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
        Estimate token count for text

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
        Get list of available providers and their models

        Returns:
            {
                'openai': ['gpt-4o', 'gpt-4o-mini', ...],
                'anthropic': ['claude-3-5-sonnet-20241022', ...],
                ...
            }
        """
        return {
            provider: list(config['models'].keys())
            for provider, config in AIAdapter.PROVIDERS.items()
        }

    @staticmethod
    def validate_api_key(provider: str) -> bool:
        """
        Validate that API key exists for provider

        Args:
            provider: Provider name

        Returns:
            True if API key is set, False otherwise
        """
        if provider not in AIAdapter.PROVIDERS:
            return False

        api_key_env = AIAdapter.PROVIDERS[provider]['api_key_env']
        return bool(os.getenv(api_key_env))

    def __repr__(self) -> str:
        """String representation"""
        return f'AIAdapter(provider={self.provider}, model={self.model})'

    # =========================================================================
    # Static convenience methods for common operations
    # =========================================================================

    @staticmethod
    def chat_completion(
        messages: list,
        system_prompt: str = None,
        model: str = 'gpt-4o-mini',
        max_tokens: int = 1000,
        temperature: float = 0.7,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Convenience static method for chat completions.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt
            model: Model name (default: gpt-4o-mini)
            max_tokens: Maximum output tokens
            temperature: Randomness (0.0-1.0)
            user_id: Optional user ID for logging

        Returns:
            {
                'content': str,        # The response text
                'usage': {
                    'input_tokens': int,
                    'output_tokens': int,
                    'total_tokens': int
                }
            }
        """
        # Determine provider from model name
        provider = 'openai'
        if model.startswith('claude'):
            provider = 'anthropic'
        elif model.startswith('gemini'):
            provider = 'google'

        adapter = AIAdapter(provider=provider, model=model)

        # Prepare messages
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({'role': 'system', 'content': system_prompt})

        for msg in messages:
            formatted_messages.append({
                'role': msg.get('role', 'user'),
                'content': msg.get('content', '')
            })

        # Send request
        result = adapter.send_messages(
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return {
            'content': result.get('output_text', ''),
            'usage': {
                'input_tokens': result.get('input_tokens', 0),
                'output_tokens': result.get('output_tokens', 0),
                'total_tokens': result.get('total_tokens', 0)
            }
        }

    @staticmethod
    def text_to_speech(
        text: str,
        voice: str = 'alloy',
        model: str = 'tts-1',
        speed: float = 1.0
    ) -> bytes:
        """
        Generate speech audio from text using OpenAI TTS.

        Args:
            text: Text to convert to speech
            voice: Voice ID (alloy, echo, fable, onyx, nova, shimmer)
            model: TTS model (tts-1 or tts-1-hd)
            speed: Speech speed (0.25 to 4.0)

        Returns:
            MP3 audio data as bytes
        """
        import logging
        logger = logging.getLogger(__name__)

        # Use the same method as the main AIAdapter class to get API key
        logger.info(f"TTS: Attempting to get OpenAI API key from database...")
        api_key = AIAdapter._get_api_key_from_db('openai')

        if api_key:
            logger.info(f"TTS: Got API key from DB (length: {len(api_key)}, starts with: {api_key[:10]}...)")
        else:
            logger.warning("TTS: No API key found in database, trying environment variable...")
            # Fallback to environment variable
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                logger.info(f"TTS: Got API key from env (length: {len(api_key)})")

        if not api_key:
            logger.error("TTS: No OpenAI API key configured!")
            raise AIProviderError('OpenAI API key not configured. Set OPENAI_API_KEY or configure in Admin Panel.')

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': model,
            'input': text,
            'voice': voice,
            'speed': speed,
            'response_format': 'mp3'
        }

        try:
            response = requests.post(
                'https://api.openai.com/v1/audio/speech',
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.content

        except Timeout:
            raise AITimeoutError('TTS request timed out')
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise AIQuotaExceededError('OpenAI quota exceeded')
            elif e.response.status_code == 401:
                raise AIInvalidKeyError('Invalid OpenAI API key')
            else:
                raise AIProviderError(f'TTS API error: {e.response.text}')
        except RequestException as e:
            raise AIProviderError(f'TTS request failed: {str(e)}')

    @staticmethod
    def transcribe_audio(
        audio_path: str,
        language: str = None,
        prompt: str = None,
        model: str = 'whisper-1'
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text using OpenAI Whisper.

        Args:
            audio_path: Path to the audio file
            language: Optional language code (e.g., 'de', 'en')
            prompt: Optional context prompt to improve accuracy
            model: Whisper model (default: whisper-1)

        Returns:
            {
                'text': str,           # Transcribed text
                'language': str,       # Detected language
                'duration': float,     # Audio duration in seconds
                'segments': list       # Detailed segments with timestamps
            }
        """
        # Use the same method as the main AIAdapter class to get API key
        api_key = AIAdapter._get_api_key_from_db('openai')

        if not api_key:
            # Fallback to environment variable
            api_key = os.getenv('OPENAI_API_KEY')

        if not api_key:
            raise AIProviderError('OpenAI API key not configured. Set OPENAI_API_KEY or configure in Admin Panel.')

        headers = {
            'Authorization': f'Bearer {api_key}'
        }

        # Prepare form data
        with open(audio_path, 'rb') as audio_file:
            files = {
                'file': audio_file,
                'model': (None, model)
            }

            data = {}
            if language:
                data['language'] = language
            if prompt:
                data['prompt'] = prompt
            # Request verbose JSON for segments and duration
            data['response_format'] = 'verbose_json'

            try:
                response = requests.post(
                    'https://api.openai.com/v1/audio/transcriptions',
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=120  # 2 minutes for long audio
                )
                response.raise_for_status()

                result = response.json()
                return {
                    'text': result.get('text', ''),
                    'language': result.get('language', language or 'unknown'),
                    'duration': result.get('duration', 0),
                    'segments': result.get('segments', [])
                }

            except Timeout:
                raise AITimeoutError('Transcription request timed out')
            except requests.HTTPError as e:
                if e.response.status_code == 429:
                    raise AIQuotaExceededError('OpenAI quota exceeded')
                elif e.response.status_code == 401:
                    raise AIInvalidKeyError('Invalid OpenAI API key')
                else:
                    raise AIProviderError(f'Transcription API error: {e.response.text}')
            except RequestException as e:
                raise AIProviderError(f'Transcription request failed: {str(e)}')
