"""
LernsystemX AI Adapter - OpenAI Provider

OpenAI-specific request handling for GPT models.

Token-Parameter:
* OpenAI's "Reasoning"-Modelle (gpt-5*, o-Serie, …) brauchen
  ``max_completion_tokens`` statt ``max_tokens``. Welche das sind, wird
  per **lazy auto-discovery** gelernt:
  - DB-Flag ``ai_models.capabilities.requires_completion_tokens`` wird
    als Wahrheit angesehen.
  - Wenn unbekannt → erst ``max_tokens`` probieren. Liefert OpenAI den
    typischen 400-Error mit dem Hinweis ``max_completion_tokens``,
    persistieren wir das Flag und retryen mit der korrekten Variante.
  - Folge-Requests gehen direkt mit der gespeicherten Capability raus.
* Keine hardcoded Modell-Liste mehr.
"""

import logging
from typing import Dict, Any, Optional, List
import requests
from requests.exceptions import RequestException, Timeout

from ..exceptions import (
    AIProviderError,
    AIQuotaExceededError,
    AIInvalidKeyError,
    AITimeoutError
)
from ..model_capabilities import (
    requires_completion_tokens,
    mark_requires_completion_tokens,
)

logger = logging.getLogger(__name__)


def _completion_tokens_signal(error_text: str) -> bool:
    """True wenn OpenAI explizit auf ``max_completion_tokens`` hinweist."""
    if not error_text:
        return False
    needle = 'max_completion_tokens'
    return needle in error_text


def _add_token_param(payload: dict, model: str, max_tokens: int) -> str:
    """Setzt den richtigen Token-Parameter ins Payload — gibt verwendeten
    Schlüsselnamen zurück (für Retry-Logik)."""
    flag = requires_completion_tokens(model, provider_name='openai')
    if flag is True:
        payload['max_completion_tokens'] = max_tokens
        return 'max_completion_tokens'
    payload['max_tokens'] = max_tokens
    return 'max_tokens'


class OpenAIProvider:
    """OpenAI provider implementation for GPT models."""

    @staticmethod
    def send_request(
        api_key: str,
        api_url: str,
        model: str,
        prompt: str,
        context: Optional[str],
        language: str,
        temperature: float,
        max_tokens: int,
        conversation_history: Optional[list],
        timeout: int
    ) -> Dict[str, Any]:
        """
        Send request to OpenAI API.

        Args:
            api_key: OpenAI API key
            api_url: API endpoint URL
            model: Model name (e.g., 'gpt-4o-mini')
            prompt: User's input/question
            context: Additional context about the learning material
            language: Response language ('de', 'en', etc.)
            temperature: Randomness (0.0-1.0)
            max_tokens: Maximum output tokens
            conversation_history: Previous conversation turns
            timeout: Request timeout in seconds

        Returns:
            Dict with output_text, input_tokens, output_tokens
        """
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

        return OpenAIProvider._execute_request(
            api_key, api_url, model, messages, temperature, max_tokens, timeout
        )

    @staticmethod
    def send_messages(
        api_key: str,
        api_url: str,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        timeout: int
    ) -> Dict[str, Any]:
        """
        Send pre-formatted messages to OpenAI API.

        Args:
            api_key: OpenAI API key
            api_url: API endpoint URL
            model: Model name
            messages: List of message dicts with 'role' and 'content'
            temperature: Randomness (0.0-1.0)
            max_tokens: Maximum output tokens
            timeout: Request timeout in seconds

        Returns:
            Dict with output_text, input_tokens, output_tokens
        """
        return OpenAIProvider._execute_request(
            api_key, api_url, model, messages, temperature, max_tokens, timeout
        )

    @staticmethod
    def send_messages_with_tools(
        api_key: str,
        api_url: str,
        model: str,
        messages: List[Dict[str, str]],
        tools: List[Dict],
        temperature: float,
        max_tokens: int,
        timeout: int
    ) -> Dict[str, Any]:
        """
        Send messages with tool definitions to OpenAI API.

        Returns dict with 'message' key containing the full message object
        (content + tool_calls) for normalization by tool_formatters.
        """
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': model,
            'messages': messages,
            'tools': tools,
            'temperature': temperature
        }

        used_token_param: Optional[str] = None
        if max_tokens is not None and max_tokens > 0:
            used_token_param = _add_token_param(payload, model, max_tokens)

        for attempt in range(2):
            try:
                response = requests.post(
                    api_url, headers=headers, json=payload, timeout=timeout
                )
                response.raise_for_status()
                data = response.json()

                message = data['choices'][0]['message']
                return {
                    'message': message,
                    'input_tokens': data['usage']['prompt_tokens'],
                    'output_tokens': data['usage']['completion_tokens']
                }

            except Timeout:
                raise AITimeoutError(f'OpenAI request timed out after {timeout}s')
            except requests.HTTPError as e:
                error_text = e.response.text if e.response is not None else ''
                if (
                    attempt == 0
                    and used_token_param == 'max_tokens'
                    and e.response is not None and e.response.status_code == 400
                    and _completion_tokens_signal(error_text)
                ):
                    logger.info(
                        'OpenAI (tools) verlangt max_completion_tokens für %s — '
                        'Capability wird persistiert und Request retried.',
                        model,
                    )
                    mark_requires_completion_tokens(model, True, provider_name='openai')
                    payload.pop('max_tokens', None)
                    payload['max_completion_tokens'] = max_tokens
                    used_token_param = 'max_completion_tokens'
                    continue

                if e.response is not None and e.response.status_code == 429:
                    raise AIQuotaExceededError('OpenAI quota exceeded')
                if e.response is not None and e.response.status_code == 401:
                    raise AIInvalidKeyError('Invalid OpenAI API key')
                raise AIProviderError(f'OpenAI API error: {error_text}')
            except RequestException as e:
                raise AIProviderError(f'OpenAI request failed: {str(e)}')

        raise AIProviderError('OpenAI request failed after retry')

    @staticmethod
    def _execute_request(
        api_key: str,
        api_url: str,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        timeout: int
    ) -> Dict[str, Any]:
        """
        Execute the actual OpenAI API request.

        Args:
            api_key: OpenAI API key
            api_url: API endpoint URL
            model: Model name
            messages: List of message dicts
            temperature: Randomness (0.0-1.0)
            max_tokens: Maximum output tokens
            timeout: Request timeout in seconds

        Returns:
            Dict with output_text, input_tokens, output_tokens

        Raises:
            AITimeoutError: On timeout
            AIQuotaExceededError: On quota exceeded
            AIInvalidKeyError: On invalid API key
            AIProviderError: On other API errors
        """
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': model,
            'messages': messages,
            'temperature': temperature
        }

        used_token_param: Optional[str] = None
        if max_tokens is not None and max_tokens > 0:
            used_token_param = _add_token_param(payload, model, max_tokens)

        for attempt in range(2):
            try:
                response = requests.post(
                    api_url,
                    headers=headers,
                    json=payload,
                    timeout=timeout
                )
                response.raise_for_status()
                data = response.json()

                return {
                    'output_text': data['choices'][0]['message']['content'],
                    'input_tokens': data['usage']['prompt_tokens'],
                    'output_tokens': data['usage']['completion_tokens']
                }

            except Timeout:
                raise AITimeoutError(f'OpenAI request timed out after {timeout}s')
            except requests.HTTPError as e:
                error_text = e.response.text if e.response is not None else ''
                # Lazy-Discovery: OpenAI signalisiert dass max_completion_tokens
                # gebraucht wird → Flag persistieren + einmal retry.
                if (
                    attempt == 0
                    and used_token_param == 'max_tokens'
                    and e.response is not None and e.response.status_code == 400
                    and _completion_tokens_signal(error_text)
                ):
                    logger.info(
                        'OpenAI verlangt max_completion_tokens für %s — '
                        'Capability wird persistiert und Request retried.',
                        model,
                    )
                    mark_requires_completion_tokens(model, True, provider_name='openai')
                    payload.pop('max_tokens', None)
                    payload['max_completion_tokens'] = max_tokens
                    used_token_param = 'max_completion_tokens'
                    continue

                if e.response is not None and e.response.status_code == 429:
                    raise AIQuotaExceededError('OpenAI quota exceeded')
                if e.response is not None and e.response.status_code == 401:
                    raise AIInvalidKeyError('Invalid OpenAI API key')
                raise AIProviderError(f'OpenAI API error: {error_text}')
            except RequestException as e:
                raise AIProviderError(f'OpenAI request failed: {str(e)}')

        # Sollte unerreichbar sein (Loop liefert immer entweder return oder raise)
        raise AIProviderError('OpenAI request failed after retry')
