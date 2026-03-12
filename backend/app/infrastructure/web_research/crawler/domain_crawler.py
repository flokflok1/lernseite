"""Domain crawler orchestrator — BFS crawl + PDF discovery + extraction.

Ties together robots_parser, sitemap_parser, page_crawler, relevance_scorer,
PDFScraperService, and CrawlUrlRepository into an end-to-end domain crawl.
"""

import logging
from collections import deque
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse

from app.infrastructure.web_research.crawler.robots_parser import (
    fetch_robots,
    is_allowed,
)
from app.infrastructure.web_research.crawler.sitemap_parser import (
    discover_from_sitemap,
)
from app.infrastructure.web_research.crawler.page_crawler import crawl_page
from app.infrastructure.web_research.crawler.relevance_scorer import (
    score_link_relevance,
)
from app.infrastructure.web_research.pdf_scraper import PDFScraperService
from app.infrastructure.persistence.repositories.web_research.crawl_url_repository import (
    CrawlUrlRepository,
)
from app.infrastructure.persistence.repositories.web_research.pdf_cache_repository import (
    PDFCacheRepository,
)

logger = logging.getLogger(__name__)

MIN_RELEVANCE_SCORE = 0.3
PROGRESS_INTERVAL_PAGES = 5


def crawl_domain(
    domain_config: dict,
    job_id: str,
    on_progress: Optional[Callable] = None,
) -> dict:
    """Crawl a single domain end-to-end.

    Args:
        domain_config: Dict with keys domain_id, domain_name, base_url,
            url_patterns, rate_limit_seconds, max_pages_per_crawl, max_depth.
        job_id: UUID string for this crawl job.
        on_progress: Optional callback(stats_dict) for progress updates.

    Returns:
        Summary stats dict with pages_crawled, pdfs_discovered,
        pdfs_downloaded, pdfs_new, pdfs_updated, errors_count.
    """
    _validate_config(domain_config)

    base_url = domain_config['base_url'].rstrip('/')
    domain_id = domain_config['domain_id']
    url_patterns = domain_config.get('url_patterns') or []
    rate_limit = domain_config.get('rate_limit_seconds', 1.5)
    max_pages = domain_config.get('max_pages_per_crawl', 100)
    max_depth = domain_config.get('max_depth', 3)

    stats = _init_stats()

    logger.info("Starting crawl for domain %s (%s)", domain_config.get('domain_name', '?'), base_url)

    robots = fetch_robots(base_url)
    sitemap_pdfs = _collect_sitemap_pdfs(base_url, url_patterns, robots)
    crawl_pdfs = _crawl_pages_bfs(
        base_url, robots, url_patterns, rate_limit,
        max_pages, max_depth, on_progress, stats,
    )

    all_pdfs = _merge_pdf_lists(sitemap_pdfs, crawl_pdfs)
    stats['pdfs_discovered'] = len(all_pdfs)
    _report_progress(on_progress, stats, max_pages)

    _process_all_pdfs(all_pdfs, robots, domain_id, job_id, on_progress, stats, max_pages)

    logger.info(
        "Crawl complete for %s: %d pages, %d PDFs discovered, %d downloaded",
        base_url, stats['pages_crawled'], stats['pdfs_discovered'], stats['pdfs_downloaded'],
    )
    return stats


def _validate_config(config: dict) -> None:
    """Raise ValueError if required config keys are missing."""
    required = ('domain_id', 'base_url')
    missing = [k for k in required if not config.get(k)]
    if missing:
        raise ValueError(f"domain_config missing required keys: {missing}")


def _init_stats() -> Dict[str, int]:
    """Return a fresh stats dict with zeroed counters."""
    return {
        'pages_crawled': 0,
        'pdfs_discovered': 0,
        'pdfs_downloaded': 0,
        'pdfs_new': 0,
        'pdfs_updated': 0,
        'errors_count': 0,
    }


def _normalize_url(url: str) -> str:
    """Normalize URL for dedup: strip fragment and trailing slash."""
    parsed = urlparse(url)
    path = parsed.path.rstrip('/')
    return f"{parsed.scheme}://{parsed.netloc}{path}"


def _collect_sitemap_pdfs(
    base_url: str,
    url_patterns: List[str],
    robots: Any,
) -> List[Dict[str, str]]:
    """Discover PDF URLs from sitemap.xml, filtering by robots.txt."""
    sitemap_entries = discover_from_sitemap(base_url, url_patterns or None)
    pdfs = []
    for entry in sitemap_entries:
        if entry.get('url_type') != 'pdf':
            continue
        if not is_allowed(robots, entry['url']):
            logger.debug("Sitemap PDF blocked by robots.txt: %s", entry['url'])
            continue
        pdfs.append({
            'url': entry['url'],
            'text': '',
            'context': f"sitemap:{entry.get('lastmod', '')}",
            'source': 'sitemap',
        })
    logger.info("Sitemap yielded %d PDF URLs", len(pdfs))
    return pdfs


def _crawl_pages_bfs(
    base_url: str,
    robots: Any,
    url_patterns: List[str],
    rate_limit: float,
    max_pages: int,
    max_depth: int,
    on_progress: Optional[Callable],
    stats: Dict[str, int],
) -> List[Dict[str, str]]:
    """BFS crawl of HTML pages, collecting PDF link info dicts.

    Returns list of pdf_info dicts with keys: url, text, context, source.
    """
    queue: deque = deque()
    visited: set = set()
    pdf_links: List[Dict[str, str]] = []

    start_normalized = _normalize_url(base_url)
    queue.append((base_url, 0))
    visited.add(start_normalized)

    while queue and stats['pages_crawled'] < max_pages:
        url, depth = queue.popleft()

        if not is_allowed(robots, url):
            logger.debug("Page blocked by robots.txt: %s", url)
            continue

        result = _crawl_single_page(url, rate_limit)
        stats['pages_crawled'] += 1

        if not result['success']:
            stats['errors_count'] += 1
        else:
            for pdf in result['pdf_links']:
                pdf['source'] = 'page'
                pdf_links.append(pdf)

            if depth < max_depth:
                _enqueue_page_links(result['page_links'], visited, queue, depth)

        if stats['pages_crawled'] % PROGRESS_INTERVAL_PAGES == 0:
            _report_progress(on_progress, stats, max_pages)

    return pdf_links


def _crawl_single_page(url: str, rate_limit: float) -> Dict[str, Any]:
    """Crawl a single page with error handling. Never raises."""
    try:
        return crawl_page(url, rate_limit_seconds=rate_limit)
    except Exception:
        logger.exception("Unexpected error crawling page %s", url)
        return {
            'url': url,
            'pdf_links': [],
            'page_links': [],
            'success': False,
            'error': 'exception',
        }


def _enqueue_page_links(
    page_links: List[str],
    visited: set,
    queue: deque,
    current_depth: int,
) -> None:
    """Add unvisited page links to the BFS queue."""
    for link in page_links:
        normalized = _normalize_url(link)
        if normalized not in visited:
            visited.add(normalized)
            queue.append((link, current_depth + 1))


def _merge_pdf_lists(
    sitemap_pdfs: List[Dict[str, str]],
    crawl_pdfs: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    """Merge PDF lists, deduplicating by normalized URL."""
    seen: set = set()
    merged: List[Dict[str, str]] = []

    for pdf in sitemap_pdfs + crawl_pdfs:
        norm = _normalize_url(pdf['url'])
        if norm not in seen:
            seen.add(norm)
            merged.append(pdf)

    return merged


def _process_all_pdfs(
    all_pdfs: List[Dict[str, str]],
    robots: Any,
    domain_id: str,
    job_id: str,
    on_progress: Optional[Callable],
    stats: Dict[str, int],
    max_pages: int,
) -> None:
    """Process each discovered PDF: score, upsert, download, quality-check."""
    for pdf_info in all_pdfs:
        try:
            _process_single_pdf(pdf_info, robots, domain_id, job_id, stats)
        except Exception:
            logger.exception("Failed to process PDF %s", pdf_info.get('url', '?'))
            stats['errors_count'] += 1

        _report_progress(on_progress, stats, max_pages)


def _process_single_pdf(
    pdf_info: Dict[str, str],
    robots: Any,
    domain_id: str,
    job_id: str,
    stats: Dict[str, int],
) -> None:
    """Score, upsert, download, and quality-check a single PDF URL."""
    url = pdf_info['url']

    if not is_allowed(robots, url):
        logger.debug("PDF blocked by robots.txt: %s", url)
        return

    relevance = score_link_relevance(
        url,
        link_text=pdf_info.get('text', ''),
        surrounding_text=pdf_info.get('context', ''),
    )

    if relevance['score'] < MIN_RELEVANCE_SCORE:
        logger.debug("PDF below relevance threshold (%.2f): %s", relevance['score'], url)
        return

    url_id = CrawlUrlRepository.upsert({
        'domain_id': domain_id,
        'job_id': job_id,
        'url': url,
        'url_type': 'pdf',
        'status': 'discovered',
        'relevance_score': relevance['score'],
        'relevance_reason': relevance['reason'],
    })

    _download_and_update_pdf(url, url_id, stats)


def _download_and_update_pdf(
    url: str,
    url_id: str,
    stats: Dict[str, int],
) -> None:
    """Download PDF via PDFScraperService, resolve cache, update URL record."""
    extraction = PDFScraperService.extract_text_from_url(url)
    if extraction is None:
        logger.warning("PDF download/extraction failed: %s", url)
        stats['errors_count'] += 1
        return

    cache_id = _resolve_cache_id(extraction, url)
    if not cache_id:
        logger.warning("Could not resolve cache_id for PDF: %s", url)
        stats['errors_count'] += 1
        return

    extracted_text = extraction.get('extracted_text', '')
    content_hash = PDFCacheRepository.compute_hash(extracted_text.encode('utf-8'))
    page_count = extraction.get('page_count', 0)
    has_text = len(extracted_text.strip()) > 100

    CrawlUrlRepository.mark_downloaded(
        url_id=url_id,
        pdf_cache_id=cache_id,
        content_hash=content_hash,
        page_count=page_count,
        has_text=has_text,
    )

    stats['pdfs_downloaded'] += 1
    # Cache hit means the PDF existed before — count as updated if re-crawled
    if extraction.get('cache_id'):
        stats['pdfs_updated'] += 1
    else:
        stats['pdfs_new'] += 1

    logger.info("PDF processed: %s (pages=%d, has_text=%s)", url, page_count, has_text)


def _resolve_cache_id(extraction: Dict[str, Any], url: str) -> Optional[str]:
    """Resolve the pdf_cache.cache_id from an extraction result.

    On cache hit, extract_text_from_url returns dict with 'cache_id'.
    On fresh extraction, look up by content hash.
    """
    if extraction.get('cache_id'):
        return extraction['cache_id']

    try:
        text = extraction.get('extracted_text', '')
        content_hash = PDFCacheRepository.compute_hash(text.encode('utf-8'))
        cached = PDFCacheRepository.find_by_hash(content_hash)
        if cached:
            return cached['cache_id']
    except Exception:
        logger.warning("Cache lookup failed for %s", url, exc_info=True)

    # Fall back: look up by file content hash (file bytes, not text)
    return _lookup_cache_by_file_download(url)


def _lookup_cache_by_file_download(url: str) -> Optional[str]:
    """Download file bytes to compute file hash and find cache entry."""
    try:
        import requests
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        file_hash = PDFCacheRepository.compute_hash(resp.content)
        cached = PDFCacheRepository.find_by_hash(file_hash)
        return cached['cache_id'] if cached else None
    except Exception:
        logger.debug("File-hash cache lookup failed for %s", url, exc_info=True)
        return None


def _report_progress(
    on_progress: Optional[Callable],
    stats: Dict[str, int],
    max_pages: int,
) -> None:
    """Call the progress callback with current stats if provided."""
    if on_progress is None:
        return

    progress_pct = min(95, int((stats['pages_crawled'] / max(max_pages, 1)) * 100))

    try:
        on_progress({
            'pages_crawled': stats['pages_crawled'],
            'pdfs_discovered': stats['pdfs_discovered'],
            'pdfs_downloaded': stats['pdfs_downloaded'],
            'progress_pct': progress_pct,
            'status': 'running',
        })
    except Exception:
        logger.warning("Progress callback failed", exc_info=True)
