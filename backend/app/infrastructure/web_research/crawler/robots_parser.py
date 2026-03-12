"""robots.txt compliance checker."""

import logging
from urllib.robotparser import RobotFileParser
from typing import Optional

import requests

logger = logging.getLogger(__name__)

USER_AGENT = 'LernsystemX-Crawler/1.0'
FETCH_TIMEOUT = 10


def fetch_robots(base_url: str) -> Optional[RobotFileParser]:
    """Fetch and parse robots.txt for a domain. Returns None on failure."""
    robots_url = f"{base_url.rstrip('/')}/robots.txt"
    try:
        resp = requests.get(robots_url, timeout=FETCH_TIMEOUT, headers={
            'User-Agent': USER_AGENT,
        })
        if resp.status_code == 200:
            parser = RobotFileParser()
            parser.parse(resp.text.splitlines())
            return parser
        logger.info("No robots.txt at %s (status %d)", robots_url, resp.status_code)
        return None
    except Exception:
        logger.warning("Failed to fetch robots.txt from %s", robots_url, exc_info=True)
        return None


def is_allowed(parser: Optional[RobotFileParser], url: str) -> bool:
    """Check if URL is allowed by robots.txt. Allows all if no parser."""
    if parser is None:
        return True
    return parser.can_fetch(USER_AGENT, url)
