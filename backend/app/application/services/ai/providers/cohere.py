"""
LernsystemX AI Adapter - Cohere Provider

Cohere-specific request handling for Command models.
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


class CohereProvider:
    """Cohere provider implementation for Command models."""

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
        Send request to Cohere API.

        Args:
            api_key: Cohere API key
            api_url: API endpoint URL
            model: Model name (e.g., 'command-r-plus')
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
        # Build message
        preamble = f"You are an expert AI tutor. Respond in {language}."
        if context:
            preamble += f"\n\nContext: {context}"

        return CohereProvider._execute_request(
            api_key, api_url, model, prompt, preamble, None, temperature, max_tokens, timeout
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
        Send pre-formatted messages to Cohere API.

        Args:
            api_key: Cohere API key
            api_url: API endpoint URL
            model: Model name
            messages: List of message dicts with 'role' and 'content'
            temperature: Randomness (0.0-1.0)
            max_tokens: Maximum output tokens
            timeout: Request timeout in seconds

        Returns:
            Dict with output_text, input_tokens, output_tokens
        """
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

        return CohereProvider._execute_request(
            api_key, api_url, model, message or "Continue", preamble, chat_history, temperature, max_tokens, timeout
        )

    @staticmethod
    def _execute_request(
        api_key: str,
        api_url: str,
        model: str,
        message: str,
        preamble: Optional[str],
        chat_history: Optional[List[Dict[str, str]]],
        temperature: float,
        max_tokens: int,
        timeout: int
    ) -> Dict[str, Any]:
        """
        Execute the actual Cohere API request.

        Args:
            api_key: Cohere API key
            api_url: API endpoint URL
            model: Model name
            message: Current user message
            preamble: System preamble
            chat_history: Previous conversation turns
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
            'message': message,
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        if preamble:
            payload['preamble'] = preamble
        if chat_history:
            payload['chat_history'] = chat_history

        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()
            data = response.json()

            output_text = data['text']

            # Get token counts from response or estimate
            input_tokens = data.get('meta', {}).get('tokens', {}).get('input_tokens', 0)
            output_tokens = data.get('meta', {}).get('tokens', {}).get('output_tokens', 0)

            # Estimate if not provided
            if input_tokens == 0:
                input_tokens = len((preamble or '') + message) // 4
            if output_tokens == 0:
                output_tokens = len(output_text) // 4

            return {
                'output_text': output_text,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens
            }

        except Timeout:
            raise AITimeoutError(f'Cohere request timed out after {timeout}s')
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise AIQuotaExceededError('Cohere quota exceeded')
            elif e.response.status_code == 401:
                raise AIInvalidKeyError('Invalid Cohere API key')
            else:
                raise AIProviderError(f'Cohere API error: {e.response.text}')
        except RequestException as e:
            raise AIProviderError(f'Cohere request failed: {str(e)}')
