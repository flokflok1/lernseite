"""
LernsystemX AI Adapter - Google Provider

Google-specific request handling for Gemini models.
Supports multipart content (text + images) via inline_data.
"""

import re
from typing import Dict, Any, Optional, List
import requests
from requests.exceptions import RequestException, Timeout

from ..exceptions import (
    AIProviderError,
    AIQuotaExceededError,
    AIInvalidKeyError,
    AITimeoutError
)


class GoogleProvider:
    """Google provider implementation for Gemini models."""

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
        Send request to Google Gemini API.

        Args:
            api_key: Google API key
            api_url: API endpoint URL template
            model: Model name (e.g., 'gemini-1.5-pro')
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
        full_prompt += prompt

        # Format API URL
        formatted_url = api_url.format(model=model)
        url_with_key = f"{formatted_url}?key={api_key}"

        payload = {
            'contents': [{
                'parts': [{'text': full_prompt}]
            }],
            'generationConfig': {
                'temperature': temperature,
                'maxOutputTokens': max_tokens
            }
        }

        return GoogleProvider._execute_request(url_with_key, payload, full_prompt, timeout)

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
        Send pre-formatted messages to Google Gemini API.

        Args:
            api_key: Google API key
            api_url: API endpoint URL template
            model: Model name
            messages: List of message dicts with 'role' and 'content'
            temperature: Randomness (0.0-1.0)
            max_tokens: Maximum output tokens
            timeout: Request timeout in seconds

        Returns:
            Dict with output_text, input_tokens, output_tokens
        """
        # Google Gemini uses a different format - convert messages
        system_instruction = None
        conversation_parts = []

        for msg in messages:
            role = msg['role']
            content = msg['content']

            if role == 'system':
                # System content is always a string
                system_instruction = content if isinstance(content, str) else str(content)
            elif role in ('user', 'assistant'):
                gemini_role = 'user' if role == 'user' else 'model'
                parts = GoogleProvider._convert_content_to_parts(content)
                conversation_parts.append({'role': gemini_role, 'parts': parts})

        formatted_url = api_url.format(model=model)
        url_with_key = f"{formatted_url}?key={api_key}"

        payload = {
            'contents': conversation_parts,
            'generationConfig': {
                'temperature': temperature,
                'maxOutputTokens': max_tokens
            }
        }

        if system_instruction:
            payload['systemInstruction'] = {'parts': [{'text': system_instruction}]}

        # Create combined text for token estimation
        combined_text = GoogleProvider._extract_text_for_estimation(messages)

        return GoogleProvider._execute_request(url_with_key, payload, combined_text, timeout)

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
        Send messages with tool definitions to Google Gemini API.

        Returns dict with 'parts' key containing the response parts
        (text + functionCall) for normalization by tool_formatters.
        """
        system_instruction = None
        conversation_parts = []

        for msg in messages:
            role = msg['role']
            content = msg['content']

            if role == 'system':
                system_instruction = content if isinstance(content, str) else str(content)
            elif role == 'user':
                parts = GoogleProvider._convert_content_to_parts(content)
                conversation_parts.append({'role': 'user', 'parts': parts})
            elif role == 'assistant':
                parts = GoogleProvider._convert_content_to_parts(content)
                conversation_parts.append({'role': 'model', 'parts': parts})

        formatted_url = api_url.format(model=model)
        url_with_key = f"{formatted_url}?key={api_key}"

        payload = {
            'contents': conversation_parts,
            'tools': tools,
            'generationConfig': {
                'temperature': temperature,
                'maxOutputTokens': max_tokens
            }
        }

        if system_instruction:
            payload['systemInstruction'] = {
                'parts': [{'text': system_instruction}]
            }

        combined_text = GoogleProvider._extract_text_for_estimation(messages)

        try:
            response = requests.post(
                url_with_key, json=payload, timeout=timeout
            )
            response.raise_for_status()
            data = response.json()

            parts = data['candidates'][0]['content']['parts']
            input_tokens = data.get('usageMetadata', {}).get(
                'promptTokenCount', len(combined_text) // 4
            )
            output_tokens = data.get('usageMetadata', {}).get(
                'candidatesTokenCount', 100
            )

            return {
                'parts': parts,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens
            }

        except Timeout:
            raise AITimeoutError(f'Google request timed out after {timeout}s')
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise AIQuotaExceededError('Google quota exceeded')
            elif e.response.status_code == 401:
                raise AIInvalidKeyError('Invalid Google API key')
            else:
                raise AIProviderError(f'Google API error: {e.response.text}')
        except RequestException as e:
            raise AIProviderError(f'Google request failed: {str(e)}')

    @staticmethod
    def _convert_content_to_parts(content) -> List[Dict[str, Any]]:
        """
        Convert OpenAI-style message content to Gemini parts format.

        Handles both string content and multipart content (list with
        text and image_url entries).

        OpenAI format:
            [{"type": "text", "text": "..."}, {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}]
        Gemini format:
            [{"text": "..."}, {"inline_data": {"mime_type": "image/jpeg", "data": "..."}}]
        """
        if isinstance(content, str):
            return [{'text': content}]

        parts = []
        for item in content:
            if item.get('type') == 'text':
                parts.append({'text': item['text']})
            elif item.get('type') == 'image_url':
                url = item['image_url']['url']
                # Parse data URI: data:image/jpeg;base64,<data>
                match = re.match(r'data:image/(\w+);base64,(.+)', url, re.DOTALL)
                if match:
                    mime_sub = match.group(1)
                    b64_data = match.group(2)
                    parts.append({
                        'inline_data': {
                            'mime_type': f'image/{mime_sub}',
                            'data': b64_data,
                        }
                    })
        return parts or [{'text': str(content)}]

    @staticmethod
    def _extract_text_for_estimation(messages: list) -> str:
        """Extract text portions from messages for token estimation."""
        texts = []
        for msg in messages:
            content = msg.get('content', '')
            if isinstance(content, str):
                texts.append(content)
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        texts.append(item['text'])
        return ' '.join(texts)

    @staticmethod
    def _execute_request(
        url: str,
        payload: Dict[str, Any],
        input_text: str,
        timeout: int
    ) -> Dict[str, Any]:
        """
        Execute the actual Google API request.

        Args:
            url: Complete API URL with key
            payload: Request payload
            input_text: Input text for token estimation
            timeout: Request timeout in seconds

        Returns:
            Dict with output_text, input_tokens, output_tokens

        Raises:
            AITimeoutError: On timeout
            AIQuotaExceededError: On quota exceeded
            AIInvalidKeyError: On invalid API key
            AIProviderError: On other API errors
        """
        try:
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            data = response.json()

            output_text = data['candidates'][0]['content']['parts'][0]['text']

            # Google doesn't always return token counts - estimate if needed
            input_tokens = data.get('usageMetadata', {}).get('promptTokenCount', len(input_text) // 4)
            output_tokens = data.get('usageMetadata', {}).get('candidatesTokenCount', len(output_text) // 4)

            return {
                'output_text': output_text,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens
            }

        except Timeout:
            raise AITimeoutError(f'Google request timed out after {timeout}s')
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise AIQuotaExceededError('Google quota exceeded')
            elif e.response.status_code == 401:
                raise AIInvalidKeyError('Invalid Google API key')
            else:
                raise AIProviderError(f'Google API error: {e.response.text}')
        except RequestException as e:
            raise AIProviderError(f'Google request failed: {str(e)}')
