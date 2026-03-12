"""
Web Research Service — Gemini Grounding + PDF Integration.

Real Google Search via Gemini Grounding API + IHK PDF content.
Multi-query strategy, source scoring, Redis + DB cache.
NO silent fallback — raises WebResearchError on failure.
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.domain.exceptions.web_research import WebResearchError
from app.infrastructure.web_research.grounding_client import search_with_grounding
from app.infrastructure.web_research.source_scorer import (
    score_sources, compute_average_source_score,
)

logger = logging.getLogger(__name__)

MAX_WORKERS = int(os.getenv('WEB_RESEARCH_MAX_WORKERS', '5'))
CACHE_TTL_SECONDS = int(os.getenv('WEB_RESEARCH_CACHE_TTL', str(7 * 24 * 3600)))

_PROFESSION_LABELS_DE = {
    'FISI': 'Fachinformatiker Systemintegration',
    'FIAE': 'Fachinformatiker Anwendungsentwicklung',
}
_PROFESSION_LABELS_EN = {
    'FISI': 'IT Specialist System Integration',
    'FIAE': 'IT Specialist Application Development',
}


def _exam_type_to_label(exam_type: str, language: str = 'de') -> str:
    """Parse exam_type key into a search-friendly label.

    'IHK_FISI_AP1' → 'IHK Fachinformatiker Systemintegration AP1'
    'IHK_FIAE_AP2' → 'IHK Fachinformatiker Anwendungsentwicklung AP2'
    'CompTIA_A+' → 'CompTIA A+'
    """
    if not exam_type or exam_type == 'Custom':
        return 'IHK Fachinformatiker' if language == 'de' else 'IT specialist'

    labels = _PROFESSION_LABELS_DE if language == 'de' else _PROFESSION_LABELS_EN
    parts = exam_type.split('_')
    result = []
    for part in parts:
        expanded = labels.get(part.upper())
        result.append(expanded if expanded else part)
    return ' '.join(result)


TECH_KEYWORDS = {
    'docker', 'kubernetes', 'python', 'java', 'linux', 'git',
    'sql', 'html', 'css', 'javascript', 'api', 'rest', 'tcp',
    'http', 'dns', 'dhcp', 'cloud', 'devops', 'agile', 'scrum',
    'raid', 'vpn', 'vlan', 'ssh', 'tls', 'ssl', 'oauth',
    'json', 'xml', 'yaml', 'ci', 'cd', 'oop', 'mvc',
}


class WebSearchService:
    """Web research via Gemini Grounding + PDF content with caching."""

    @staticmethod
    def research_position(
        position_id: int, position_title: str,
        objectives: List[str], language: str = 'de',
        region: str = '', exam_type: str = '',
    ) -> Dict[str, Any]:
        """Research a curriculum position via Grounding + PDFs.

        Checks Redis → DB cache → Gemini Grounding + PDF search.
        Raises WebResearchError if Grounding fails completely.
        """
        # 1. Redis cache (region-aware key)
        cached = _check_redis_cache(position_id, language, region)
        if cached:
            logger.info("Redis cache hit for position %d", position_id)
            return cached

        # 2. DB cache
        cached = _check_db_cache(position_id, language)
        if cached:
            logger.info("DB cache hit for position %d", position_id)
            _save_to_redis(position_id, language, cached, region)
            return cached

        # 3. Grounding + PDF
        search_lang = _detect_search_language(position_title)
        queries = _build_queries(
            position_title, objectives, search_lang, region, exam_type,
        )

        logger.info(
            "Research for position %d: %d queries (%s, region=%s, type=%s)",
            position_id, len(queries), search_lang,
            region or 'none', exam_type or 'none',
        )

        grounding_results = _execute_queries_parallel(
            queries, search_lang, region, exam_type,
        )
        pdf_content = _find_pdf_content(position_title)
        merged = _merge_results(grounding_results, pdf_content, queries)

        # 4. Cache
        _save_to_caches(position_id, language, search_lang, queries, merged)

        return merged


def _build_queries(
    position_title: str, objectives: List[str],
    search_lang: str, region: str = '', exam_type: str = '',
) -> List[str]:
    """Build objective-driven queries from position + Lernziele.

    1 overview + 1 Rahmenplan + 1 exam + per-objective queries.
    Uses exam_type for dynamic profession labels (FISI/FIAE/AP1/AP2).
    Region replaces bare 'IHK' → 'IHK Bayern' for specificity.
    """
    queries = []
    label_de = _exam_type_to_label(exam_type, 'de')
    label_en = _exam_type_to_label(exam_type, 'en')

    # Inject region into label: "IHK Fach..." → "IHK Bayern Fach..."
    if region and label_de.upper().startswith('IHK '):
        label_de = f"IHK {region} {label_de[4:]}"
    if region and label_en.upper().startswith('IHK '):
        label_en = f"IHK {region} {label_en[4:]}"

    if search_lang == 'en':
        queries.append(f"{label_en} {position_title} exam preparation")
        for obj in objectives[:5]:
            queries.append(f"{obj} {label_en} explanation examples")
        if not objectives:
            queries.append(f"{label_en} {position_title} exam questions")
    else:
        queries.append(f"{label_de} {position_title} Prüfungsvorbereitung")
        queries.append(f"Rahmenplan {label_de} {position_title}")
        queries.append(
            f"Abschlussprüfung {label_de} {position_title} alte Prüfungen"
        )
        for obj in objectives[:5]:
            queries.append(f"{obj} {label_de} Erklärung Beispiele")

    return queries


def _detect_search_language(position_title: str) -> str:
    """Detect optimal search language based on topic keywords."""
    title_lower = position_title.lower()
    tech_matches = sum(1 for kw in TECH_KEYWORDS if kw in title_lower)
    return 'en' if tech_matches >= 2 else 'de'


def _execute_queries_parallel(
    queries: List[str], language: str,
    region: str = '', exam_type: str = '',
) -> List[Dict[str, Any]]:
    """Execute Grounding queries in parallel via ThreadPoolExecutor."""
    results = []
    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(queries))) as ex:
        futures = {
            ex.submit(search_with_grounding, q, language, region, exam_type): q
            for q in queries
        }
        for future in as_completed(futures):
            query = futures[future]
            try:
                results.append(future.result())
            except WebResearchError:
                logger.warning("Grounding failed for query: %s", query[:80])

    if not results:
        raise WebResearchError('All Grounding queries failed.')

    return results


def _find_pdf_content(position_title: str) -> List[Dict[str, Any]]:
    """Search cached PDFs for relevant content (non-blocking)."""
    try:
        from app.infrastructure.web_research.pdf_scraper import PDFScraperService
        return PDFScraperService.find_relevant_content(position_title)
    except Exception:
        logger.debug("PDF content search failed for: %s", position_title)
        return []


def _merge_results(
    grounding: List[Dict[str, Any]],
    pdf_content: List[Dict[str, Any]],
    queries: List[str],
) -> Dict[str, Any]:
    """Merge Grounding + PDF results into one structured result."""
    texts = [r['text'] for r in grounding if r.get('text')]

    # Add PDF snippets
    for pdf in pdf_content:
        snippet = pdf.get('snippet', '')
        if snippet:
            texts.append(f"[PDF: {pdf.get('source', '')}]\n{snippet}")

    combined_text = '\n\n---\n\n'.join(texts)

    # Collect + dedup sources
    all_sources = []
    seen_urls = set()
    for r in grounding:
        for src in r.get('sources', []):
            url = src.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                src['source_type'] = 'web'
                all_sources.append(src)

    for pdf in pdf_content:
        all_sources.append({
            'url': '',
            'title': pdf.get('source', 'PDF'),
            'source_type': 'pdf',
        })

    scored = score_sources(all_sources)
    avg_score = compute_average_source_score(scored)

    statuses = [r.get('grounding_status', 'failed') for r in grounding]
    if all(s == 'success' for s in statuses):
        overall = 'success'
    elif any(s == 'success' for s in statuses):
        overall = 'partial'
    else:
        overall = 'failed'

    return {
        'summary': combined_text,
        'key_points': [],
        'sources': scored,
        'grounding_status': overall,
        'average_source_score': avg_score,
        'source_count': len(scored),
        'query_count': len(queries),
        'input_tokens': sum(r.get('input_tokens', 0) for r in grounding),
        'output_tokens': sum(r.get('output_tokens', 0) for r in grounding),
        'pdf_sources_count': len(pdf_content),
        'cached': False,
        'generated_at': datetime.now(timezone.utc).isoformat(),
    }


def _check_redis_cache(
    position_id: int, language: str, region: str = '',
) -> Optional[Dict[str, Any]]:
    """Check Redis cache (region-aware key)."""
    try:
        from app.infrastructure.cache.service import CacheService
        parts = ['RESEARCH', 'POS', str(position_id), 'LANG', language]
        if region:
            parts.extend(['REG', region.lower().replace(' ', '_')])
        key = CacheService.make_key(*parts)
        result = CacheService.cache_get(key)
        if result:
            result['cached'] = True
            return result
    except Exception:
        logger.debug("Redis cache lookup failed for position %d", position_id)
    return None


def _check_db_cache(
    position_id: int, language: str,
) -> Optional[Dict[str, Any]]:
    """Check DB cache."""
    try:
        from app.infrastructure.persistence.repositories.web_research import (
            ResearchCacheRepository,
        )
        return ResearchCacheRepository.find_cached(position_id, language)
    except Exception:
        logger.debug("DB cache lookup failed for position %d", position_id)
    return None


def _save_to_redis(
    position_id: int, language: str, data: Dict[str, Any],
    region: str = '',
) -> None:
    """Save to Redis cache (region-aware key)."""
    try:
        from app.infrastructure.cache.service import CacheService
        parts = ['RESEARCH', 'POS', str(position_id), 'LANG', language]
        if region:
            parts.extend(['REG', region.lower().replace(' ', '_')])
        key = CacheService.make_key(*parts)
        CacheService.cache_set(key, data, ttl=CACHE_TTL_SECONDS)
    except Exception:
        logger.debug("Redis cache save failed for position %d", position_id)


def _save_to_caches(
    position_id: int, language: str, search_lang: str,
    queries: List[str], result: Dict[str, Any],
) -> None:
    """Save to Redis + DB caches."""
    _save_to_redis(position_id, language, result)
    try:
        from app.infrastructure.persistence.repositories.web_research import (
            ResearchCacheRepository,
        )
        ResearchCacheRepository.save(
            position_id=position_id,
            language=language,
            summary=result.get('summary', ''),
            key_points=result.get('key_points', []),
            sources=result.get('sources', []),
            grounding_status=result.get('grounding_status', 'failed'),
            queries_used=queries,
            search_language=search_lang,
        )
    except Exception:
        logger.exception("DB cache save failed for position %d", position_id)
