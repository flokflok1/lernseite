"""
PDF Validation Module

Validates PDF files for structure, encryption, and basic readability.
"""

import io
import logging
from typing import Tuple, Optional

try:
    from PyPDF2 import PdfReader
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

from .exceptions import PDFPasswordProtectedError, PDFCorruptedError

logger = logging.getLogger(__name__)


class PDFValidator:
    """PDF validation and integrity checking"""

    @staticmethod
    def validate_pdf(file_content: bytes) -> Tuple[bool, Optional[str]]:
        """
        Validate if file is a valid PDF

        Args:
            file_content: Raw file bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check magic bytes
        if not file_content.startswith(b'%PDF'):
            return False, "File is not a valid PDF (missing PDF header)"

        # Try to parse
        try:
            pdf_file = io.BytesIO(file_content)
            reader = PdfReader(pdf_file)

            if reader.is_encrypted:
                return False, "PDF is password protected"

            # Try to read at least one page
            if len(reader.pages) == 0:
                return False, "PDF has no pages"

            return True, None

        except Exception as e:
            return False, f"PDF parsing error: {str(e)}"

    @staticmethod
    def get_page_count(file_content: bytes) -> int:
        """
        Get page count quickly

        Args:
            file_content: Raw PDF bytes

        Returns:
            Number of pages, or 0 on error
        """
        try:
            pdf_file = io.BytesIO(file_content)
            reader = PdfReader(pdf_file)
            return len(reader.pages)
        except Exception:
            return 0

    @staticmethod
    def get_text_preview(file_content: bytes, max_chars: int = 5000) -> str:
        """
        Get a quick text preview without full analysis

        Args:
            file_content: Raw PDF bytes
            max_chars: Maximum characters to return

        Returns:
            Preview text
        """
        try:
            pdf_file = io.BytesIO(file_content)
            reader = PdfReader(pdf_file)

            if reader.is_encrypted:
                return "[PDF ist passwortgeschützt]"

            text = ""
            for page in reader.pages:
                page_text = page.extract_text() or ''
                text += page_text + "\n"
                if len(text) >= max_chars:
                    break

            return text[:max_chars]

        except Exception as e:
            return f"[Fehler beim Lesen: {str(e)}]"

    @staticmethod
    def check_encryption(file_content: bytes) -> bool:
        """
        Check if PDF is encrypted

        Args:
            file_content: Raw PDF bytes

        Returns:
            True if encrypted, False otherwise
        """
        try:
            pdf_file = io.BytesIO(file_content)
            reader = PdfReader(pdf_file)
            return reader.is_encrypted
        except Exception:
            return False
