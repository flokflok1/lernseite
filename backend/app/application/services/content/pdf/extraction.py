"""
PDF Text Extraction Module

Core text extraction functionality using PyPDF2 with page-by-page processing.
"""

import io
import logging
from typing import Dict, Any, List

try:
    from PyPDF2 import PdfReader
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

from .exceptions import PDFExtractionError, PDFPasswordProtectedError, PDFCorruptedError

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Handles PDF text extraction with metadata parsing"""

    @staticmethod
    def extract_with_pypdf2(file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract text using PyPDF2

        Args:
            file_content: Raw PDF bytes
            filename: Filename for error messages

        Returns:
            Dict with text, page_count, metadata, structure
        """
        try:
            pdf_file = io.BytesIO(file_content)
            reader = PdfReader(pdf_file)
        except Exception as e:
            if "password" in str(e).lower() or "encrypted" in str(e).lower():
                raise PDFPasswordProtectedError(f"PDF is password protected: {filename}")
            raise PDFCorruptedError(f"Cannot read PDF: {filename} - {str(e)}")

        # Check if encrypted
        if reader.is_encrypted:
            raise PDFPasswordProtectedError(f"PDF is encrypted: {filename}")

        # Extract metadata
        metadata = PDFExtractor._extract_metadata(reader)

        # Extract text from all pages
        pages_text = PDFExtractor._extract_pages(reader)

        # Combine all text
        full_text = '\n\n'.join([p['text'] for p in pages_text if p['text']])

        return {
            'text': full_text,
            'page_count': len(reader.pages),
            'metadata': metadata,
            'pages_text': pages_text
        }

    @staticmethod
    def _extract_metadata(reader) -> Dict[str, str]:
        """
        Extract metadata from PDF

        Args:
            reader: PyPDF2 PdfReader instance

        Returns:
            Dictionary of metadata fields
        """
        metadata = {}
        if reader.metadata:
            metadata = {
                'title': reader.metadata.get('/Title', ''),
                'author': reader.metadata.get('/Author', ''),
                'subject': reader.metadata.get('/Subject', ''),
                'creator': reader.metadata.get('/Creator', ''),
                'producer': reader.metadata.get('/Producer', ''),
                'creation_date': str(reader.metadata.get('/CreationDate', '')),
                'modification_date': str(reader.metadata.get('/ModDate', ''))
            }
            # Clean empty values
            metadata = {k: v for k, v in metadata.items() if v}

        return metadata

    @staticmethod
    def _extract_pages(reader) -> List[Dict[str, Any]]:
        """
        Extract text from all pages

        Args:
            reader: PyPDF2 PdfReader instance

        Returns:
            List of page dictionaries with page number and text
        """
        pages_text = []

        for page_num, page in enumerate(reader.pages):
            try:
                text = page.extract_text() or ''
                pages_text.append({
                    'page': page_num + 1,
                    'text': text
                })
            except Exception as e:
                logger.warning(f"Failed to extract page {page_num + 1}: {str(e)}")
                pages_text.append({
                    'page': page_num + 1,
                    'text': '',
                    'error': str(e)
                })

        return pages_text
