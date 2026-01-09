"""
LernsystemX AI Adapter - HuggingFace Provider

HuggingFace-specific request handling for open-source models.
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


class HuggingFaceProvider:
    """HuggingFace provider implementation for open-source models."""

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
        Send request to HuggingFace Inference API.

        Args:
            api_key: HuggingFace API key
            api_url: API endpoint URL template
            model: Model name (e.g., 'meta-llama/Llama-3.2-3B-Instruct')
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
        # Build prompt
        full_prompt = f"You are an expert AI tutor. Respond in {language}.\n\n"
        if context:
            full_prompt += f"Context: {context}\n\n"
        full_prompt += f"User: {prompt}\nAssistant:"

        return HuggingFaceProvider._execute_request(
            api_key, api_url, model, full_prompt, temperature, max_tokens, timeout
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
        Send pre-formatted messages to HuggingFace API.

        Args:
            api_key: HuggingFace API key
            api_url: API endpoint URL template
            model: Model name
            messages: List of message dicts with 'role' and 'content'
            temperature: Randomness (0.0-1.0)
            max_tokens: Maximum output tokens
            timeout: Request timeout in seconds

        Returns:
            Dict with output_text, input_tokens, output_tokens
        """
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

        return HuggingFaceProvider._execute_request(
            api_key, api_url, model, full_prompt, temperature, max_tokens, timeout
        )

    @staticmethod
    def _execute_request(
        api_key: str,
        api_url: str,
        model: str,
        full_prompt: str,
        temperature: float,
        max_tokens: int,
        timeout: int
    ) -> Dict[str, Any]:
        """
        Execute the actual HuggingFace API request.

        Args:
            api_key: HuggingFace API key
            api_url: API endpoint URL template
            model: Model name
            full_prompt: Complete prompt text
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
        # Format API URL
        formatted_url = api_url.format(model=model)

        headers = {
            'Authorization': f'Bearer {api_key}',
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
            response = requests.post(
                formatted_url,
                headers=headers,
                json=payload,
                timeout=timeout
            )
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
            raise AITimeoutError(f'HuggingFace request timed out after {timeout}s')
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise AIQuotaExceededError('HuggingFace quota exceeded')
            elif e.response.status_code == 401:
                raise AIInvalidKeyError('Invalid HuggingFace API key')
            else:
                raise AIProviderError(f'HuggingFace API error: {e.response.text}')
        except RequestException as e:
            raise AIProviderError(f'HuggingFace request failed: {str(e)}')
