"""
LernsystemX AI Adapter - OpenAI Provider

OpenAI-specific request handling for GPT models.
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
from ..config import MODELS_USING_COMPLETION_TOKENS


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

        from ..config import MODELS_USING_COMPLETION_TOKENS

        payload = {
            'model': model,
            'messages': messages,
            'tools': tools,
            'temperature': temperature
        }

        if any(model.startswith(m) for m in MODELS_USING_COMPLETION_TOKENS):
            payload['max_completion_tokens'] = max_tokens
        else:
            payload['max_tokens'] = max_tokens

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
            if e.response.status_code == 429:
                raise AIQuotaExceededError('OpenAI quota exceeded')
            elif e.response.status_code == 401:
                raise AIInvalidKeyError('Invalid OpenAI API key')
            else:
                raise AIProviderError(f'OpenAI API error: {e.response.text}')
        except RequestException as e:
            raise AIProviderError(f'OpenAI request failed: {str(e)}')

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

        # Use max_completion_tokens for newer models, max_tokens for legacy
        if any(model.startswith(m) for m in MODELS_USING_COMPLETION_TOKENS):
            payload['max_completion_tokens'] = max_tokens
        else:
            payload['max_tokens'] = max_tokens

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
            if e.response.status_code == 429:
                raise AIQuotaExceededError('OpenAI quota exceeded')
            elif e.response.status_code == 401:
                raise AIInvalidKeyError('Invalid OpenAI API key')
            else:
                raise AIProviderError(f'OpenAI API error: {e.response.text}')
        except RequestException as e:
            raise AIProviderError(f'OpenAI request failed: {str(e)}')
