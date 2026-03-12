"""Relevance scoring for IHK/Fachinformatiker content."""

import logging
from typing import Dict, Any, List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Keywords that indicate IHK/Fachinformatiker relevance (weighted)
HIGH_RELEVANCE_KEYWORDS: List[str] = [
    'fachinformatiker', 'ihk', 'abschlussprüfung', 'ap1', 'ap2',
    'rahmenlehrplan', 'ausbildungsrahmenplan',
]

MEDIUM_RELEVANCE_KEYWORDS: List[str] = [
    'prüfung', 'ausbildung', 'it-berufe', 'systemintegration',
    'anwendungsentwicklung', 'lehrplan', 'berufsbildung',
    'handlungssituation', 'prüfungsaufgabe',
]

LOW_RELEVANCE_KEYWORDS: List[str] = [
    'informatik', 'netzwerk', 'datenbank', 'programmierung',
    'it-sicherheit', 'virtualisierung', 'cloud', 'sql',
]

# URL path segments that boost relevance
URL_BONUS_PATTERNS: List[str] = [
    'fachinformatiker', 'pruefung', 'prüfung', 'ihk',
    'ausbildung', 'abschlusspruefung',
]


def score_link_relevance(
    url: str,
    link_text: str = '',
    surrounding_text: str = '',
) -> Dict[str, Any]:
    """Score relevance of a link to IHK/Fachinformatiker content.

    Combines keyword matching across the URL, link text, and surrounding
    page text to produce a 0.0-1.0 relevance score.

    Args:
        url: The URL to evaluate.
        link_text: Anchor text of the link.
        surrounding_text: Context text from around the link on the page.

    Returns:
        Dict with 'score' (float 0.0-1.0) and 'reason' (str).
    """
    searchable = f"{url} {link_text} {surrounding_text}".lower()

    score = 0.0
    matched_keywords: List[str] = []

    score, matched_keywords = _score_keywords(searchable, score, matched_keywords)
    score = _apply_url_bonus(url, score, matched_keywords)
    score = _apply_pdf_filename_bonus(url, score, matched_keywords)

    score = min(score, 1.0)
    reason = _build_reason(score, matched_keywords)

    return {'score': round(score, 3), 'reason': reason}


def _score_keywords(
    searchable: str,
    score: float,
    matched: List[str],
) -> tuple:
    """Check all keyword tiers and accumulate score."""
    high_score = 0.0
    for kw in HIGH_RELEVANCE_KEYWORDS:
        if kw in searchable:
            high_score += 0.25
            matched.append(f'HIGH:{kw}')
    score += min(high_score, 0.75)

    medium_score = 0.0
    for kw in MEDIUM_RELEVANCE_KEYWORDS:
        if kw in searchable:
            medium_score += 0.15
            matched.append(f'MED:{kw}')
    score += min(medium_score, 0.45)

    low_score = 0.0
    for kw in LOW_RELEVANCE_KEYWORDS:
        if kw in searchable:
            low_score += 0.05
            matched.append(f'LOW:{kw}')
    score += min(low_score, 0.15)

    return score, matched


def _apply_url_bonus(
    url: str,
    score: float,
    matched: List[str],
) -> float:
    """Add bonus for relevant URL path segments."""
    path = urlparse(url).path.lower()
    for pattern in URL_BONUS_PATTERNS:
        if pattern in path:
            score += 0.2
            matched.append(f'URL_PATH:{pattern}')
            break  # Only one URL bonus
    return score


def _apply_pdf_filename_bonus(
    url: str,
    score: float,
    matched: List[str],
) -> float:
    """Add bonus for PDF filenames containing IHK-related terms."""
    if not url.lower().endswith('.pdf'):
        return score

    filename = urlparse(url).path.split('/')[-1].lower()
    pdf_bonus_terms = ['ihk', 'fachinformatiker', 'pruefung', 'rahmenlehrplan']

    for term in pdf_bonus_terms:
        if term in filename:
            score += 0.15
            matched.append(f'PDF_NAME:{term}')
            break  # Only one PDF bonus
    return score


def _build_reason(score: float, matched: List[str]) -> str:
    """Build a human-readable reason string."""
    if not matched:
        return 'No IHK-relevant keywords found'

    keyword_summary = ', '.join(matched[:10])
    if len(matched) > 10:
        keyword_summary += f' (+{len(matched) - 10} more)'

    return f'Matched: {keyword_summary}'


def check_pdf_quality(content_bytes: bytes) -> Dict[str, Any]:
    """Check if a PDF has extractable text or is scan-only.

    Analyzes the PDF content to determine whether it contains
    machine-readable text or is primarily scanned images.

    Args:
        content_bytes: Raw PDF file bytes.

    Returns:
        Dict with 'has_text' (bool), 'page_count' (int), 'text_ratio' (float).
    """
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=content_bytes, filetype="pdf")
        page_count = doc.page_count
        total_text = _extract_all_text(doc)
        doc.close()

        text_length = len(total_text.strip())
        has_text = text_length > 100

        # Estimate text ratio: chars per page (rough heuristic)
        chars_per_page = text_length / max(page_count, 1)
        # A typical text page has ~2000-3000 chars; ratio relative to 2000
        text_ratio = min(chars_per_page / 2000.0, 1.0)

        return {
            'has_text': has_text,
            'page_count': page_count,
            'text_ratio': round(text_ratio, 3),
        }

    except ImportError:
        logger.error("PyMuPDF (fitz) not installed — cannot check PDF quality")
        return {'has_text': False, 'page_count': 0, 'text_ratio': 0.0}
    except Exception:
        logger.exception("PDF quality check failed")
        return {'has_text': False, 'page_count': 0, 'text_ratio': 0.0}


def _extract_all_text(doc) -> str:
    """Extract concatenated text from all pages of a PyMuPDF document."""
    pages_text = []
    for page in doc:
        pages_text.append(page.get_text())
    return '\n'.join(pages_text)
