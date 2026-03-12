"""Web Research Crawler — Infrastructure modules for domain crawling."""

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
    check_pdf_quality,
)
from app.infrastructure.web_research.crawler.domain_crawler import crawl_domain
