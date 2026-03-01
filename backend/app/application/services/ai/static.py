"""
LernsystemX AI Adapter - Static Convenience Methods

Static utility methods for common AI operations:
- chat_completion: Generic chat completion
- text_to_speech: TTS using OpenAI
- transcribe_audio: Audio transcription using Whisper
"""

import os
import logging
from typing import Dict, Any, Optional

import requests
from requests.exceptions import RequestException, Timeout

from app.infrastructure.ai.exceptions import (
    AIProviderError,
    AIQuotaExceededError,
    AIInvalidKeyError,
    AITimeoutError
)
from app.infrastructure.ai.config import PROVIDERS

logger = logging.getLogger(__name__)


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
        # If database is not available, return None to use env fallback
        return None


def _get_openai_key() -> str:
    """
    Get OpenAI API key from database or environment.

    Returns:
        OpenAI API key

    Raises:
        AIProviderError: If no API key is configured
    """
    api_key = _get_api_key_from_db('openai')

    if not api_key:
        api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        raise AIProviderError('OpenAI API key not configured. Set OPENAI_API_KEY or configure in Admin Panel.')

    return api_key


def chat_completion(
    messages: list,
    system_prompt: str = None,
    model: str = 'gpt-4o-mini',
    max_tokens: Optional[int] = None,
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
    # Import here to avoid circular imports
    from .adapter import AIAdapter

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

    Raises:
        AITimeoutError: On timeout
        AIQuotaExceededError: On quota exceeded
        AIInvalidKeyError: On invalid API key
        AIProviderError: On other API errors
    """
    logger.info("TTS: Attempting to get OpenAI API key from database...")
    api_key = _get_api_key_from_db('openai')

    if api_key:
        logger.info(f"TTS: Got API key from DB (length: {len(api_key)}, starts with: {api_key[:10]}...)")
    else:
        logger.warning("TTS: No API key found in database, trying environment variable...")
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

    Raises:
        AITimeoutError: On timeout
        AIQuotaExceededError: On quota exceeded
        AIInvalidKeyError: On invalid API key
        AIProviderError: On other API errors
    """
    api_key = _get_api_key_from_db('openai')

    if not api_key:
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
