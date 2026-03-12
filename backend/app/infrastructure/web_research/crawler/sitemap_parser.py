"""Sitemap XML parser for URL discovery."""

import fnmatch
import logging
import xml.etree.ElementTree as ET
from typing import Optional

import requests

logger = logging.getLogger(__name__)

USER_AGENT = 'LernsystemX-Crawler/1.0'
FETCH_TIMEOUT = 15
SITEMAP_NS = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}


def discover_from_sitemap(
    base_url: str,
    url_patterns: Optional[list[str]] = None,
) -> list[dict]:
    """Fetch and parse sitemap.xml, returning discovered URLs.

    Args:
        base_url: Domain root, e.g. ``https://example.com``.
        url_patterns: Optional wildcard patterns (fnmatch) to filter URLs.
            Example: ``['*/fachinformatiker/*']``.

    Returns:
        List of dicts with keys ``url``, ``lastmod`` (str | None),
        ``url_type`` (``'page'`` or ``'pdf'``).
    """
    sitemap_url = f"{base_url.rstrip('/')}/sitemap.xml"
    try:
        resp = requests.get(sitemap_url, timeout=FETCH_TIMEOUT, headers={
            'User-Agent': USER_AGENT,
        })
        if resp.status_code != 200:
            logger.info(
                "No sitemap.xml at %s (status %d)", sitemap_url, resp.status_code,
            )
            return []
        return _parse_sitemap_xml(resp.text, url_patterns)
    except Exception:
        logger.warning(
            "Failed to fetch sitemap.xml from %s", sitemap_url, exc_info=True,
        )
        return []


def _parse_sitemap_xml(
    xml_text: str,
    url_patterns: Optional[list[str]] = None,
) -> list[dict]:
    """Parse sitemap XML content, handling both index and urlset formats."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        logger.warning("Malformed sitemap XML", exc_info=True)
        return []

    tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag

    if tag == 'sitemapindex':
        return _parse_sitemap_index(root, url_patterns)

    if tag == 'urlset':
        return _parse_urlset(root, url_patterns)

    logger.warning("Unexpected sitemap root element: %s", tag)
    return []


def _parse_sitemap_index(
    root: ET.Element,
    url_patterns: Optional[list[str]] = None,
) -> list[dict]:
    """Handle sitemapindex by fetching each nested sitemap."""
    results: list[dict] = []
    for sitemap_el in root.findall('sm:sitemap', SITEMAP_NS):
        loc_el = sitemap_el.find('sm:loc', SITEMAP_NS)
        if loc_el is not None and loc_el.text:
            sub_results = _fetch_sub_sitemap(loc_el.text.strip(), url_patterns)
            results.extend(sub_results)
    return results


def _parse_urlset(
    root: ET.Element,
    url_patterns: Optional[list[str]] = None,
) -> list[dict]:
    """Extract URL entries from a urlset element."""
    results: list[dict] = []
    for url_el in root.findall('sm:url', SITEMAP_NS):
        loc_el = url_el.find('sm:loc', SITEMAP_NS)
        if loc_el is None or not loc_el.text:
            continue

        url = loc_el.text.strip()
        if not _matches_patterns(url, url_patterns):
            continue

        lastmod_el = url_el.find('sm:lastmod', SITEMAP_NS)
        lastmod = lastmod_el.text.strip() if lastmod_el is not None and lastmod_el.text else None

        url_type = 'pdf' if url.lower().endswith('.pdf') else 'page'
        results.append({'url': url, 'lastmod': lastmod, 'url_type': url_type})
    return results


def _fetch_sub_sitemap(
    url: str,
    url_patterns: Optional[list[str]] = None,
) -> list[dict]:
    """Fetch and parse a nested sitemap referenced from a sitemap index."""
    try:
        resp = requests.get(url, timeout=FETCH_TIMEOUT, headers={
            'User-Agent': USER_AGENT,
        })
        if resp.status_code != 200:
            logger.info("Sub-sitemap %s returned status %d", url, resp.status_code)
            return []
        return _parse_sitemap_xml(resp.text, url_patterns)
    except Exception:
        logger.warning("Failed to fetch sub-sitemap %s", url, exc_info=True)
        return []


def _matches_patterns(url: str, patterns: Optional[list[str]]) -> bool:
    """Check if a URL matches any of the given fnmatch wildcard patterns."""
    if not patterns:
        return True
    return any(fnmatch.fnmatch(url, pattern) for pattern in patterns)
