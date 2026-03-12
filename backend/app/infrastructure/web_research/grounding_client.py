"""
Gemini Grounding Client — Real Google Search via Gemini API.

Calls Gemini generateContent with google_search tool enabled.
Returns AI summary + real source URLs from grounding_metadata.
Raises WebResearchError on failure (NO silent fallback).
"""

import logging
import os
import time
from typing import Dict, Any, List

import requests
from requests.exceptions import RequestException, Timeout

from app.domain.exceptions.web_research import WebResearchError

logger = logging.getLogger(__name__)

GEMINI_API_URL = (
    'https://generativelanguage.googleapis.com/v1beta/models'
    '/{model}:generateContent'
)
DEFAULT_MODEL = 'gemini-2.0-flash'
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 2
RETRY_BACKOFF = 2


def search_with_grounding(
    query: str,
    language: str = 'de',
    model: str = DEFAULT_MODEL,
    temperature: float = 0.2,
    max_tokens: int = 4000,
) -> Dict[str, Any]:
    """Execute a single Gemini Grounding search.

    Args:
        query: Search query string.
        language: Response language ('de' or 'en').

    Returns:
        Dict with 'text', 'sources', 'grounding_status', token counts.

    Raises:
        WebResearchError: On API failure after retries.
    """
    api_key = _get_api_key()
    url = GEMINI_API_URL.format(model=model) + f'?key={api_key}'

    lang_label = 'Deutsch' if language == 'de' else 'English'
    prompt = (
        f"Beantworte die folgende Frage ausführlich auf {lang_label}. "
        f"Nutze aktuelle Informationen aus dem Internet.\n\n"
        f"Frage: {query}"
    )

    payload = {
        'contents': [{'parts': [{'text': prompt}]}],
        'tools': [{'google_search': {}}],
        'generationConfig': {
            'temperature': temperature,
            'maxOutputTokens': max_tokens,
        },
    }

    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            start = time.time()
            resp = requests.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
            latency_ms = int((time.time() - start) * 1000)

            if resp.status_code == 429:
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF * (attempt + 1))
                    continue
                raise WebResearchError(
                    f'Google API rate limit after {MAX_RETRIES + 1} attempts'
                )

            resp.raise_for_status()
            data = resp.json()
            return _parse_grounding_response(data, latency_ms)

        except WebResearchError:
            raise
        except Timeout:
            last_error = f'Gemini timed out after {DEFAULT_TIMEOUT}s'
        except requests.HTTPError as e:
            status = e.response.status_code if e.response else 0
            body = e.response.text[:200] if e.response else ''
            last_error = f'Gemini API error {status}: {body}'
        except RequestException as e:
            last_error = f'Gemini request failed: {str(e)}'

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_BACKOFF * (attempt + 1))

    raise WebResearchError(last_error or 'Gemini Grounding failed')


def _parse_grounding_response(
    data: Dict[str, Any], latency_ms: int,
) -> Dict[str, Any]:
    """Parse Gemini response with grounding metadata."""
    candidates = data.get('candidates', [])
    if not candidates:
        raise WebResearchError('Gemini returned no candidates')

    candidate = candidates[0]
    parts = candidate.get('content', {}).get('parts', [])

    text = ''.join(p.get('text', '') for p in parts)
    if not text:
        raise WebResearchError('Gemini returned empty text')

    sources = _extract_grounding_sources(candidate)

    usage = data.get('usageMetadata', {})
    input_tokens = usage.get('promptTokenCount', 0)
    output_tokens = usage.get('candidatesTokenCount', 0)

    return {
        'text': text,
        'sources': sources,
        'grounding_status': 'success' if sources else 'partial',
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'latency_ms': latency_ms,
    }


def _extract_grounding_sources(
    candidate: Dict[str, Any],
) -> List[Dict[str, str]]:
    """Extract source URLs from groundingMetadata.groundingChunks."""
    metadata = candidate.get('groundingMetadata', {})
    chunks = metadata.get('groundingChunks', [])

    sources = []
    seen_urls = set()
    for chunk in chunks:
        web = chunk.get('web', {})
        url = web.get('uri', '')
        title = web.get('title', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            sources.append({'url': url, 'title': title})

    return sources


def _get_api_key() -> str:
    """Get Google API key from DB or environment."""
    try:
        from app.infrastructure.persistence.repositories.ai.provider import (
            AIProviderRepository,
        )
        key = AIProviderRepository.get_decrypted_api_key('google')
        if key:
            return key
    except Exception:
        logger.debug("DB API key lookup failed, falling back to env var")

    key = os.getenv('GOOGLE_API_KEY', '')
    if not key:
        raise WebResearchError(
            'Google API key not found. Set GOOGLE_API_KEY or configure in Admin Panel.'
        )
    return key
