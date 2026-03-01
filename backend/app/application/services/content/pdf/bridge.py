"""
PDF Service Bridge Module

Unified public API that orchestrates extraction, validation, and analysis.
Maintains backward compatibility with the original PDFService interface.
"""

import hashlib
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

try:
    from PyPDF2 import PdfReader
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

from app.infrastructure.persistence.repositories.ai.config.editor import PDFCacheRepository
from .exceptions import PDFExtractionError
from .extraction import PDFExtractor
from .analysis import PDFAnalyzer
from .validation import PDFValidator

logger = logging.getLogger(__name__)


class PDFService:
    """
    PDF Analysis Service (Bridge)

    Unified API that coordinates extraction, validation, and analysis.

    Features:
    - Text extraction from PDF files
    - Structure analysis (headings, paragraphs, lists)
    - Metadata extraction (title, author, page count)
    - Caching of extraction results
    - Key topic detection
    - AI-optimized content preparation

    Usage:
        >>> result = PDFService.extract_text(file_content, "document.pdf")
        >>> print(result['extracted_text'])
        >>> print(result['structure_analysis'])
    """

    @classmethod
    def extract_text(
        cls,
        file_content: bytes,
        filename: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Extract text and metadata from PDF

        Args:
            file_content: Raw PDF file bytes
            filename: Original filename
            use_cache: Whether to use/store cache

        Returns:
            Dict with file_hash, page_count, extracted_text, extracted_metadata,
            structure_analysis, processing_time_ms, from_cache
        """
        start_time = datetime.utcnow()

        # Calculate file hash
        file_hash = hashlib.sha256(file_content).hexdigest()

        # Check cache
        if use_cache:
            cached = PDFCacheRepository.get_by_hash(file_hash)
            if cached:
                logger.info(f"PDF cache hit for {filename} (hash: {file_hash[:8]}...)")
                return {
                    'file_hash': file_hash,
                    'original_filename': cached['original_filename'],
                    'file_size_bytes': cached['file_size_bytes'],
                    'page_count': cached['page_count'],
                    'extracted_text': cached['extracted_text'],
                    'extracted_metadata': cached.get('extracted_metadata', {}),
                    'structure_analysis': cached.get('structure_analysis', {}),
                    'processing_time_ms': 0,
                    'from_cache': True
                }

        # Validate PyPDF2 availability
        if not PYPDF2_AVAILABLE:
            raise PDFExtractionError("PyPDF2 is not installed")

        try:
            # Extract using PyPDF2
            extraction = PDFExtractor.extract_with_pypdf2(file_content, filename)

            # Analyze structure
            structure = PDFAnalyzer.analyze_structure(
                extraction['text'],
                extraction.get('pages_text', [])
            )
        except Exception as e:
            logger.error(f"PDF extraction failed for {filename}: {str(e)}")
            raise PDFExtractionError(f"Failed to extract PDF: {str(e)}")

        # Calculate processing time
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Build result
        extraction_result = {
            'file_hash': file_hash,
            'original_filename': filename,
            'file_size_bytes': len(file_content),
            'page_count': extraction['page_count'],
            'extracted_text': extraction['text'],
            'extracted_metadata': extraction['metadata'],
            'structure_analysis': structure,
            'processing_time_ms': processing_time,
            'from_cache': False
        }

        # Store in cache
        if use_cache:
            try:
                PDFCacheRepository.create_cache({
                    'file_hash': file_hash,
                    'original_filename': filename,
                    'file_size_bytes': len(file_content),
                    'page_count': extraction['page_count'],
                    'extracted_text': extraction['text'],
                    'extracted_metadata': extraction['metadata'],
                    'structure_analysis': structure,
                    'extraction_method': 'pypdf2',
                    'processing_time_ms': processing_time
                })
                logger.info(f"PDF cached: {filename} (hash: {file_hash[:8]}...)")
            except Exception as e:
                logger.warning(f"Failed to cache PDF: {str(e)}")

        return extraction_result

    @classmethod
    def extract_for_ai(cls, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract and prepare PDF content for AI processing

        Returns structured data optimized for AI prompts

        Args:
            file_content: Raw PDF bytes
            filename: Original filename

        Returns:
            Dict with summary, main_text, structure, metadata, recommendations
        """
        # Full extraction
        result = cls.extract_text(file_content, filename)

        # Clean text for AI (remove excessive whitespace, page numbers, etc.)
        text = result['extracted_text']
        cleaned_text = PDFAnalyzer.clean_text_for_ai(text)

        # Generate recommendations
        structure = result['structure_analysis']
        recommendations = PDFAnalyzer.generate_recommendations(structure, len(cleaned_text))

        return {
            'file_hash': result['file_hash'],
            'filename': filename,
            'page_count': result['page_count'],
            'summary': PDFAnalyzer.generate_summary(structure, result['extracted_metadata']),
            'main_text': cleaned_text,
            'structure': structure,
            'metadata': result['extracted_metadata'],
            'recommendations': recommendations,
            'word_count': structure.get('word_count', 0),
            'estimated_reading_time': structure.get('estimated_reading_time_min', 0)
        }

    # Proxy to validation module
    @staticmethod
    def validate_pdf(file_content: bytes) -> Tuple[bool, Optional[str]]:
        """Validate if file is a valid PDF"""
        return PDFValidator.validate_pdf(file_content)

    @staticmethod
    def get_page_count(file_content: bytes) -> int:
        """Get page count quickly"""
        return PDFValidator.get_page_count(file_content)

    @staticmethod
    def get_text_preview(file_content: bytes, max_chars: int = 5000) -> str:
        """Get a quick text preview without full analysis"""
        return PDFValidator.get_text_preview(file_content, max_chars)
