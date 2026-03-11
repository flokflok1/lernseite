"""
Source URL scoring by domain authority.

Scores Gemini Grounding source URLs based on domain whitelist.
IHK-related domains score highest, random blogs score 1.0x.
"""

import logging
from typing import Dict, Any, List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Domain authority scores — higher = more trusted for IHK content
DOMAIN_SCORES: Dict[str, float] = {
    # Official IHK sources
    'ihk.de': 1.5,
    # IT reference
    'it-handbuch.de': 1.4,
    # Community
    'fachinformatiker.de': 1.3,
    # Official government / legal
    'bundesregierung.de': 1.3,
    'gesetze-im-internet.de': 1.3,
    'bibb.de': 1.3,
    'bmbf.de': 1.3,
    # Academic
    'edu': 1.2,
    'ac.': 1.2,
    # General reference
    'wikipedia.org': 1.1,
    'wikibooks.org': 1.1,
}

DEFAULT_SCORE = 1.0


def score_source(url: str) -> float:
    """Score a source URL by domain authority."""
    try:
        domain = urlparse(url).netloc.lower()
    except Exception:
        return DEFAULT_SCORE

    for pattern, score in DOMAIN_SCORES.items():
        if pattern in domain:
            return score

    return DEFAULT_SCORE


def score_sources(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Score a list of source dicts, adding domain_score field."""
    for source in sources:
        url = source.get('url', '')
        source['domain_score'] = score_source(url)
    return sources


def compute_average_source_score(sources: List[Dict[str, Any]]) -> float:
    """Compute weighted average source score."""
    if not sources:
        return 0.0
    total = sum(s.get('domain_score', DEFAULT_SCORE) for s in sources)
    return round(total / len(sources), 2)
