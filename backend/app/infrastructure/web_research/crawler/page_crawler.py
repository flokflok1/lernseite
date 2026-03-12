"""HTML page crawler — Extract links from web pages using BeautifulSoup4."""

import logging
import time
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

USER_AGENT = 'LernsystemX-Crawler/1.0'
PAGE_TIMEOUT = 15
MAX_PAGE_SIZE_MB = 10
MAX_PAGE_LINKS = 500


def crawl_page(
    url: str,
    rate_limit_seconds: float = 1.5,
) -> Dict[str, Any]:
    """Crawl a single HTML page and extract links.

    Applies rate limiting, fetches the page, parses HTML with
    BeautifulSoup, and extracts PDF links and same-domain page links.

    Args:
        url: The URL to crawl.
        rate_limit_seconds: Sleep duration before the request for polite crawling.

    Returns:
        Dict with keys: url, title, pdf_links, page_links, success, error.
    """
    time.sleep(rate_limit_seconds)

    try:
        resp = _fetch_page(url)
        if resp is None:
            return _error_result(url, 'Failed to fetch page')

        content_error = _validate_response(resp)
        if content_error:
            return _error_result(url, content_error)

        soup = BeautifulSoup(resp.text, 'lxml')
        title = _extract_title(soup)
        base_domain = urlparse(url).netloc.lower()

        pdf_links = _extract_pdf_links(soup, url)
        page_links = _extract_page_links(soup, url, base_domain)

        return {
            'url': url,
            'title': title,
            'pdf_links': pdf_links,
            'page_links': page_links,
            'success': True,
            'error': None,
        }

    except requests.RequestException as exc:
        logger.warning("Request failed for %s: %s", url, exc)
        return _error_result(url, f'Request error: {exc}')
    except Exception:
        logger.exception("Unexpected error crawling %s", url)
        return _error_result(url, 'Unexpected crawl error')


def _fetch_page(url: str) -> Optional[requests.Response]:
    """Fetch an HTML page with appropriate headers and timeout."""
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml',
    }
    resp = requests.get(url, timeout=PAGE_TIMEOUT, headers=headers)
    resp.raise_for_status()
    return resp


def _validate_response(resp: requests.Response) -> Optional[str]:
    """Validate response content type and size. Returns error string or None."""
    content_type = resp.headers.get('Content-Type', '')
    if 'text/html' not in content_type and 'application/xhtml' not in content_type:
        return f'Not HTML content: {content_type}'

    content_length = resp.headers.get('Content-Length')
    if content_length and int(content_length) > MAX_PAGE_SIZE_MB * 1024 * 1024:
        return f'Page too large: {content_length} bytes'

    if len(resp.content) > MAX_PAGE_SIZE_MB * 1024 * 1024:
        return f'Page content too large: {len(resp.content)} bytes'

    return None


def _extract_title(soup: BeautifulSoup) -> str:
    """Extract page title from <title> tag."""
    title_tag = soup.find('title')
    if title_tag and title_tag.string:
        return title_tag.string.strip()[:300]
    return ''


def _extract_pdf_links(
    soup: BeautifulSoup,
    base_url: str,
) -> List[Dict[str, str]]:
    """Extract all PDF links from the page with text and surrounding context."""
    pdf_links: List[Dict[str, str]] = []
    seen_urls: Set[str] = set()

    for anchor in soup.find_all('a', href=True):
        href = anchor['href'].strip()
        absolute_url = urljoin(base_url, href)

        if not absolute_url.lower().endswith('.pdf'):
            continue
        if absolute_url in seen_urls:
            continue
        seen_urls.add(absolute_url)

        link_text = anchor.get_text(strip=True)[:200]
        context = _get_surrounding_context(anchor)

        pdf_links.append({
            'url': absolute_url,
            'text': link_text,
            'context': context,
        })

    return pdf_links


def _extract_page_links(
    soup: BeautifulSoup,
    base_url: str,
    base_domain: str,
) -> List[str]:
    """Extract same-domain page links (non-PDF), deduped, max MAX_PAGE_LINKS."""
    page_links: List[str] = []
    seen_urls: Set[str] = set()

    for anchor in soup.find_all('a', href=True):
        href = anchor['href'].strip()
        absolute_url = urljoin(base_url, href)

        if not _is_valid_page_link(absolute_url, base_domain):
            continue

        normalized = _normalize_url(absolute_url)
        if normalized in seen_urls:
            continue
        seen_urls.add(normalized)

        page_links.append(absolute_url)
        if len(page_links) >= MAX_PAGE_LINKS:
            break

    return page_links


def _get_surrounding_context(anchor) -> str:
    """Get surrounding text context from the link's parent element."""
    parent = anchor.parent
    if parent:
        parent_text = parent.get_text(strip=True)
        return parent_text[:200]
    return ''


def _is_valid_page_link(url: str, base_domain: str) -> bool:
    """Check if a URL is a valid same-domain, non-PDF page link."""
    parsed = urlparse(url)

    if parsed.scheme not in ('http', 'https'):
        return False

    if parsed.netloc.lower() != base_domain:
        return False

    if url.lower().endswith('.pdf'):
        return False

    # Skip common non-content paths
    skip_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.svg', '.css', '.js',
                       '.zip', '.tar', '.gz', '.exe', '.dmg')
    if any(url.lower().endswith(ext) for ext in skip_extensions):
        return False

    return True


def _normalize_url(url: str) -> str:
    """Normalize URL for dedup (strip fragment, trailing slash)."""
    parsed = urlparse(url)
    path = parsed.path.rstrip('/')
    return f"{parsed.scheme}://{parsed.netloc}{path}"


def _error_result(url: str, error: str) -> Dict[str, Any]:
    """Build an error result dict."""
    return {
        'url': url,
        'title': '',
        'pdf_links': [],
        'page_links': [],
        'success': False,
        'error': error,
    }
