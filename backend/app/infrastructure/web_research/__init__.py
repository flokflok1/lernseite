"""Web Research Infrastructure Package."""
from app.infrastructure.web_research.search_service import WebSearchService
from app.infrastructure.web_research.source_scorer import score_source, score_sources
from app.infrastructure.web_research.grounding_client import search_with_grounding
from app.infrastructure.web_research.pdf_scraper import PDFScraperService

__all__ = [
    'WebSearchService', 'PDFScraperService',
    'score_source', 'score_sources', 'search_with_grounding',
]
