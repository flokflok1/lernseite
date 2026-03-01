"""
LernsystemX AI Adapter - Anthropic Provider

Anthropic-specific request handling for Claude models.
"""

from typing import Dict, Any, Optional, List
import requests
from requests.exceptions import RequestException, Timeout

from ..exceptions import (
    AIProviderError,
    AIQuotaExceededError,
    AIInvalidKeyError,
    AITimeoutError
)


class AnthropicProvider:
    """Anthropic provider implementation for Claude models."""

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
        Send request to Anthropic API.

        Args:
            api_key: Anthropic API key
            api_url: API endpoint URL
            model: Model name (e.g., 'claude-3-5-sonnet-20241022')
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

        return AnthropicProvider._execute_request(
            api_key, api_url, model, messages, system_message, temperature, max_tokens, timeout
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
        Send pre-formatted messages to Anthropic API.

        Args:
            api_key: Anthropic API key
            api_url: API endpoint URL
            model: Model name
            messages: List of message dicts with 'role' and 'content'
            temperature: Randomness (0.0-1.0)
            max_tokens: Maximum output tokens
            timeout: Request timeout in seconds

        Returns:
            Dict with output_text, input_tokens, output_tokens
        """
        # Anthropic requires system message separate from messages array
        system_message = None
        conversation_messages = []

        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                conversation_messages.append(msg)

        return AnthropicProvider._execute_request(
            api_key, api_url, model, conversation_messages, system_message, temperature, max_tokens, timeout
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
        Send messages with tool definitions to Anthropic API.

        Returns dict with 'content' key containing content blocks
        (text + tool_use) for normalization by tool_formatters.
        """
        headers = {
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json'
        }

        system_message = None
        conversation_messages = []
        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                conversation_messages.append(msg)

        payload = {
            'model': model,
            'messages': conversation_messages,
            'tools': tools,
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        if system_message:
            payload['system'] = system_message

        try:
            response = requests.post(
                api_url, headers=headers, json=payload, timeout=timeout
            )
            response.raise_for_status()
            data = response.json()

            return {
                'content': data['content'],
                'input_tokens': data['usage']['input_tokens'],
                'output_tokens': data['usage']['output_tokens']
            }

        except Timeout:
            raise AITimeoutError(f'Anthropic request timed out after {timeout}s')
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise AIQuotaExceededError('Anthropic quota exceeded')
            elif e.response.status_code == 401:
                raise AIInvalidKeyError('Invalid Anthropic API key')
            else:
                raise AIProviderError(f'Anthropic API error: {e.response.text}')
        except RequestException as e:
            raise AIProviderError(f'Anthropic request failed: {str(e)}')

    @staticmethod
    def _execute_request(
        api_key: str,
        api_url: str,
        model: str,
        messages: List[Dict[str, str]],
        system_message: Optional[str],
        temperature: float,
        max_tokens: int,
        timeout: int
    ) -> Dict[str, Any]:
        """
        Execute the actual Anthropic API request.

        Args:
            api_key: Anthropic API key
            api_url: API endpoint URL
            model: Model name
            messages: List of message dicts
            system_message: Optional system message
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
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        if system_message:
            payload['system'] = system_message

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
                'output_text': data['content'][0]['text'],
                'input_tokens': data['usage']['input_tokens'],
                'output_tokens': data['usage']['output_tokens']
            }

        except Timeout:
            raise AITimeoutError(f'Anthropic request timed out after {timeout}s')
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise AIQuotaExceededError('Anthropic quota exceeded')
            elif e.response.status_code == 401:
                raise AIInvalidKeyError('Invalid Anthropic API key')
            else:
                raise AIProviderError(f'Anthropic API error: {e.response.text}')
        except RequestException as e:
            raise AIProviderError(f'Anthropic request failed: {str(e)}')
