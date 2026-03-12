"""
IHK PDF Scraper — Download and extract text from IHK PDFs.

Uses PyMuPDF (fitz) for PDF text extraction.
Stores results in storage.pdf_cache for reuse.
"""

import logging
import time
from typing import Dict, Any, List, Optional

import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

# Known IHK PDF sources — URLs or URL patterns
KNOWN_PDF_SOURCES: List[Dict[str, str]] = [
    {
        'name': 'BIBB Rahmenlehrplan Fachinformatiker',
        'url': 'https://www.bibb.de/dokumente/pdf/Fachinformatiker_RL.pdf',
        'domain': 'bibb.de',
    },
]

DOWNLOAD_TIMEOUT = 30  # seconds
MAX_PDF_SIZE_MB = 50


class PDFScraperService:
    """Download and extract text from IHK-related PDFs."""

    @staticmethod
    def extract_text_from_url(url: str) -> Optional[Dict[str, Any]]:
        """Download PDF from URL and extract text.

        Checks pdf_cache first (dedup by hash).
        Returns dict with extracted_text, page_count, etc.
        Returns None if download or extraction fails.
        """
        from app.infrastructure.persistence.repositories.web_research.pdf_cache_repository import (
            PDFCacheRepository,
        )

        try:
            # Download PDF
            start = time.time()
            resp = requests.get(url, timeout=DOWNLOAD_TIMEOUT, stream=True)
            resp.raise_for_status()

            content = resp.content
            size_mb = len(content) / (1024 * 1024)
            if size_mb > MAX_PDF_SIZE_MB:
                logger.warning("PDF too large (%.1f MB): %s", size_mb, url)
                return None

            # Check cache by hash
            file_hash = PDFCacheRepository.compute_hash(content)
            cached = PDFCacheRepository.find_by_hash(file_hash)
            if cached:
                logger.info("PDF cache hit for %s", url)
                return cached

            # Extract text with PyMuPDF
            extracted = _extract_with_pymupdf(content)
            if not extracted:
                return None

            processing_ms = int((time.time() - start) * 1000)
            filename = url.split('/')[-1] or 'unknown.pdf'

            # Save to cache
            PDFCacheRepository.save(
                file_hash=file_hash,
                filename=filename,
                extracted_text=extracted['text'],
                page_count=extracted['page_count'],
                file_size_bytes=len(content),
                processing_time_ms=processing_ms,
                structure=extracted.get('structure'),
            )

            logger.info(
                "Extracted PDF: %s (%d pages, %.1f MB, %dms)",
                filename, extracted['page_count'], size_mb, processing_ms,
            )
            return {
                'extracted_text': extracted['text'],
                'page_count': extracted['page_count'],
                'structure_analysis': extracted.get('structure', {}),
            }

        except RequestException:
            logger.warning("Failed to download PDF: %s", url)
            return None
        except Exception:
            logger.exception("PDF extraction failed: %s", url)
            return None

    @staticmethod
    def find_relevant_content(
        position_title: str,
        max_results: int = 2,
    ) -> List[Dict[str, Any]]:
        """Search cached PDFs for content relevant to a position."""
        from app.infrastructure.persistence.repositories.web_research.pdf_cache_repository import (
            PDFCacheRepository,
        )

        keywords = position_title.lower().split()
        if not keywords:
            return []

        try:
            rows = PDFCacheRepository.search_by_keywords(keywords, max_results)

            results = []
            for row in rows:
                text = row[1] or ''
                snippet = _extract_relevant_snippet(text, keywords)
                if snippet:
                    results.append({
                        'source': f'PDF: {row[0]}',
                        'snippet': snippet,
                        'structure': row[2] or {},
                    })
            return results

        except Exception:
            logger.debug("PDF content search failed for: %s", position_title)
            return []


def _extract_with_pymupdf(content: bytes) -> Optional[Dict[str, Any]]:
    """Extract text from PDF bytes using PyMuPDF (fitz)."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=content, filetype="pdf")
        pages_text = []
        headings = []

        for page_num, page in enumerate(doc):
            text = page.get_text()
            pages_text.append(text)

            # Simple heading extraction (lines in upper case or short bold lines)
            for line in text.split('\n'):
                stripped = line.strip()
                if stripped and len(stripped) < 100 and stripped.isupper():
                    headings.append({
                        'text': stripped,
                        'page': page_num + 1,
                    })

        full_text = '\n\n'.join(pages_text)
        doc.close()

        return {
            'text': full_text,
            'page_count': len(pages_text),
            'structure': {'headings': headings[:50]},
        }

    except Exception:
        logger.exception("PyMuPDF extraction failed")
        return None


def _extract_relevant_snippet(
    text: str, keywords: List[str], context_chars: int = 500,
) -> str:
    """Extract a text snippet around the first keyword match."""
    text_lower = text.lower()
    for kw in keywords:
        pos = text_lower.find(kw)
        if pos >= 0:
            start = max(0, pos - context_chars // 2)
            end = min(len(text), pos + context_chars // 2)
            snippet = text[start:end].strip()
            return f"...{snippet}..."
    return ''
