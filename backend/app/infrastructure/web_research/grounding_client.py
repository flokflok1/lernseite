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
    query: str, language: str = 'de',
    region: str = '', exam_type: str = '',
    model: str = DEFAULT_MODEL,
    temperature: float = 0.2, max_tokens: int = 4000,
) -> Dict[str, Any]:
    """Execute a single Gemini Grounding search.

    Args:
        query: Search query string.
        language: Response language ('de' or 'en').
        region: Federal state (e.g. 'Bayern') for IHK context.
        exam_type: Exam type key (e.g. 'FI_AP1') for specificity.

    Returns:
        Dict with 'text', 'sources', 'grounding_status', token counts.

    Raises:
        WebResearchError: On API failure after retries.
    """
    api_key = _get_api_key()
    url = GEMINI_API_URL.format(model=model) + f'?key={api_key}'

    lang_label = 'Deutsch' if language == 'de' else 'English'
    prompt = _build_grounding_prompt(
        query, language, lang_label, region, exam_type,
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


def _build_grounding_prompt(
    query: str, language: str, lang_label: str,
    region: str = '', exam_type: str = '',
) -> str:
    """Build an exam-focused prompt for Gemini Grounding.

    Dynamically adapts to exam_type (FISI/FIAE/AP1/AP2/CompTIA)
    and region (Bayern/Sachsen/etc.) for targeted results.
    """
    # Build exam context from exam_type
    exam_label = _resolve_exam_label(exam_type, language)
    region_ctx = _resolve_region_context(region, language)

    if language == 'de':
        return (
            f"Du bist ein Experte für Prüfungsvorbereitung im Bereich "
            f"{exam_label}. Beantworte die folgende Frage ausführlich auf "
            f"{lang_label}. Fokussiere dich auf prüfungsrelevante Inhalte, "
            "konkrete Definitionen und praktische Beispiele die in einer "
            f"Abschlussprüfung vorkommen können.{region_ctx} "
            "Nutze aktuelle Informationen aus dem Internet.\n\n"
            f"Frage: {query}"
        )
    return (
        f"You are an exam preparation expert for {exam_label}. "
        f"Answer the following question in detail in {lang_label}. "
        "Focus on exam-relevant content, concrete definitions, and "
        f"practical examples suitable for this certification.{region_ctx} "
        "Use current information from the internet.\n\n"
        f"Question: {query}"
    )


def _resolve_exam_label(exam_type: str, language: str) -> str:
    """Convert exam_type key to human-readable prompt label."""
    if not exam_type or exam_type == 'Custom':
        if language == 'de':
            return 'IHK Fachinformatik'
        return 'IT specialist certification'

    labels_de = {
        'FISI': 'Fachinformatiker Systemintegration',
        'FIAE': 'Fachinformatiker Anwendungsentwicklung',
    }
    labels_en = {
        'FISI': 'IT Specialist System Integration',
        'FIAE': 'IT Specialist Application Development',
    }
    labels = labels_de if language == 'de' else labels_en
    parts = exam_type.split('_')
    result = []
    for part in parts:
        expanded = labels.get(part.upper())
        result.append(expanded if expanded else part)
    return ' '.join(result)


def _resolve_region_context(region: str, language: str) -> str:
    """Build region context string for prompt injection."""
    if not region:
        return ''
    if language == 'de':
        return (
            f" Berücksichtige den regionalen Kontext der IHK {region}. "
            f"Suche nach Rahmenlehrplänen, alten Prüfungen und "
            f"regionalen Besonderheiten für {region}."
        )
    return (
        f" Consider the regional context of IHK {region}. "
        f"Search for curriculum frameworks and past exams from {region}."
    )


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
