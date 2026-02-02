"""
PDF Service Package

LernSystemX PDF Analysis Service with text extraction, structure analysis,
metadata extraction, and AI-optimized content preparation.

Modules:
    - exceptions: Custom exception classes
    - extraction: PDF text extraction (PyPDF2)
    - analysis: Structure analysis and content processing
    - validation: PDF validation and integrity checking
    - bridge: Unified public API (PDFService class)

Usage:
    from app.application.services.pdf import PDFService, PDFExtractionError

    try:
        result = PDFService.extract_text(file_bytes, "document.pdf")
        print(result['extracted_text'])
    except PDFExtractionError as e:
        print(f"Error: {e}")
"""

from .exceptions import (
    PDFExtractionError,
    PDFPasswordProtectedError,
    PDFCorruptedError
)
from .extraction import PDFExtractor
from .analysis import PDFAnalyzer
from .validation import PDFValidator
from .bridge import PDFService

__all__ = [
    'PDFService',
    'PDFExtractor',
    'PDFAnalyzer',
    'PDFValidator',
    'PDFExtractionError',
    'PDFPasswordProtectedError',
    'PDFCorruptedError'
]

__version__ = '2.0.0'
__doc__ = """
PDF Service Package - Phase D4 KI-Authoring-Studio

Refactored from monolithic pdf_service.py (656 LOC) into modular package:
- extraction.py: 107 LOC
- analysis.py: 253 LOC
- validation.py: 105 LOC
- bridge.py: 172 LOC
- exceptions.py: 20 LOC

Total: 657 LOC split into 5 specialized modules for maintainability and testing.
"""
