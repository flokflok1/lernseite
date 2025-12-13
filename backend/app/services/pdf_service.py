"""
LernsystemX PDF Analysis Service

PDF text extraction and structure analysis for KI-Authoring-Studio:
- Text extraction (PyPDF2)
- Structure analysis (headings, sections, key topics)
- Metadata extraction
- PDF caching

Phase D4 - KI-Authoring-Studio - ISO 27001:2013 compliant
"""

import io
import re
import hashlib
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

# PDF Libraries
try:
    from PyPDF2 import PdfReader
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

from app.repositories.ai_studio_repository import PDFCacheRepository

logger = logging.getLogger(__name__)


class PDFExtractionError(Exception):
    """Base exception for PDF extraction errors"""
    pass


class PDFPasswordProtectedError(PDFExtractionError):
    """Raised when PDF is password protected"""
    pass


class PDFCorruptedError(PDFExtractionError):
    """Raised when PDF is corrupted or unreadable"""
    pass


class PDFService:
    """
    PDF Analysis Service

    Features:
    - Text extraction from PDF files
    - Structure analysis (headings, paragraphs, lists)
    - Metadata extraction (title, author, page count)
    - Caching of extraction results
    - Key topic detection

    Usage:
        >>> result = PDFService.extract_text(file_content, "document.pdf")
        >>> print(result['text'])
        >>> print(result['page_count'])
        >>> print(result['structure'])
    """

    # Heading patterns for structure detection
    HEADING_PATTERNS = [
        # German patterns
        (r'^(?:Kapitel|Abschnitt|Teil)\s*\d+[\.:]\s*(.+)$', 1),
        (r'^(\d+(?:\.\d+)*)\s+(.+)$', 2),  # Numbered headings like "1.2.3 Title"
        (r'^([A-Z][A-ZÄÖÜ\s]{2,})$', 1),  # ALL CAPS headings
        # Common patterns
        (r'^(?:Chapter|Section|Part)\s*\d+[\.:]\s*(.+)$', 1),
        (r'^(?:Einleitung|Einführung|Zusammenfassung|Fazit|Schluss)$', 0),
        (r'^(?:Introduction|Summary|Conclusion)$', 0),
    ]

    # Keywords for topic detection (German educational context)
    TOPIC_KEYWORDS = [
        'Definition', 'Beispiel', 'Übung', 'Aufgabe', 'Lösung',
        'Merke', 'Hinweis', 'Wichtig', 'Achtung', 'Tipp',
        'Formel', 'Regel', 'Gesetz', 'Theorem', 'Satz',
        'Zusammenfassung', 'Fazit', 'Schlussfolgerung',
        'Lernziel', 'Ziel', 'Inhalt', 'Überblick'
    ]

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
            Dict with:
            - file_hash: SHA-256 hash
            - original_filename: str
            - file_size_bytes: int
            - page_count: int
            - extracted_text: str
            - extracted_metadata: dict
            - structure_analysis: dict
            - processing_time_ms: int
            - from_cache: bool

        Raises:
            PDFExtractionError: If extraction fails
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

        # Extract using PyPDF2
        if not PYPDF2_AVAILABLE:
            raise PDFExtractionError("PyPDF2 is not installed")

        try:
            result = cls._extract_with_pypdf2(file_content, filename)
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
            'page_count': result['page_count'],
            'extracted_text': result['text'],
            'extracted_metadata': result['metadata'],
            'structure_analysis': result['structure'],
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
                    'page_count': result['page_count'],
                    'extracted_text': result['text'],
                    'extracted_metadata': result['metadata'],
                    'structure_analysis': result['structure'],
                    'extraction_method': 'pypdf2',
                    'processing_time_ms': processing_time
                })
                logger.info(f"PDF cached: {filename} (hash: {file_hash[:8]}...)")
            except Exception as e:
                logger.warning(f"Failed to cache PDF: {str(e)}")

        return extraction_result

    @classmethod
    def _extract_with_pypdf2(cls, file_content: bytes, filename: str) -> Dict[str, Any]:
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

        # Extract text from all pages
        pages_text = []
        page_count = len(reader.pages)

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

        # Combine all text
        full_text = '\n\n'.join([p['text'] for p in pages_text if p['text']])

        # Analyze structure
        structure = cls._analyze_structure(full_text, pages_text)

        return {
            'text': full_text,
            'page_count': page_count,
            'metadata': metadata,
            'structure': structure
        }

    @classmethod
    def _analyze_structure(cls, full_text: str, pages_text: List[Dict]) -> Dict[str, Any]:
        """
        Analyze document structure

        Args:
            full_text: Complete extracted text
            pages_text: Text per page

        Returns:
            Structure analysis with headings, sections, topics
        """
        structure = {
            'headings': [],
            'sections': [],
            'key_topics': [],
            'word_count': 0,
            'paragraph_count': 0,
            'estimated_reading_time_min': 0
        }

        if not full_text:
            return structure

        # Word count
        words = full_text.split()
        structure['word_count'] = len(words)

        # Paragraph count (double newlines or single newlines with empty lines)
        paragraphs = re.split(r'\n\s*\n', full_text)
        structure['paragraph_count'] = len([p for p in paragraphs if p.strip()])

        # Estimated reading time (avg 200 words/min for educational content)
        structure['estimated_reading_time_min'] = max(1, round(len(words) / 200))

        # Detect headings
        lines = full_text.split('\n')
        headings = []
        current_section = None

        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Check heading patterns
            heading_match = cls._detect_heading(line)
            if heading_match:
                heading = {
                    'text': heading_match,
                    'line': line_num + 1,
                    'level': cls._estimate_heading_level(line)
                }
                headings.append(heading)

                # Track sections
                if heading['level'] <= 2:
                    if current_section:
                        structure['sections'].append(current_section)
                    current_section = {
                        'title': heading_match,
                        'start_line': line_num + 1,
                        'headings': []
                    }
                elif current_section:
                    current_section['headings'].append(heading)

        # Add last section
        if current_section:
            structure['sections'].append(current_section)

        structure['headings'] = headings

        # Detect key topics
        key_topics = []
        for keyword in cls.TOPIC_KEYWORDS:
            pattern = rf'\b{keyword}\b'
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            if matches:
                key_topics.append({
                    'topic': keyword,
                    'count': len(matches)
                })

        # Sort by frequency
        key_topics.sort(key=lambda x: x['count'], reverse=True)
        structure['key_topics'] = key_topics[:20]  # Top 20

        return structure

    @classmethod
    def _detect_heading(cls, line: str) -> Optional[str]:
        """
        Detect if a line is a heading

        Args:
            line: Text line to check

        Returns:
            Heading text or None
        """
        line = line.strip()

        # Skip very long lines (unlikely to be headings)
        if len(line) > 200:
            return None

        # Skip lines that look like body text
        if line.endswith(',') or line.endswith(';'):
            return None

        # Check patterns
        for pattern, group in cls.HEADING_PATTERNS:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                if group == 0:
                    return line
                try:
                    return match.group(group).strip()
                except IndexError:
                    return line

        # Short lines that might be headings (title case or ends with colon)
        if len(line) < 100:
            # Title case check
            words = line.split()
            if len(words) <= 10 and words:
                # Check if most words are capitalized
                capitalized = sum(1 for w in words if w[0].isupper())
                if capitalized >= len(words) * 0.7:
                    # But not all lowercase with first letter caps (normal sentence)
                    if not all(w[1:].islower() for w in words if len(w) > 1):
                        return line

            # Ends with colon
            if line.endswith(':') and len(line) < 80:
                return line.rstrip(':')

        return None

    @classmethod
    def _estimate_heading_level(cls, line: str) -> int:
        """
        Estimate heading level (1-6)

        Args:
            line: Heading text

        Returns:
            Level 1-6 (1 = main heading)
        """
        line = line.strip()

        # Check for numbered patterns
        match = re.match(r'^(\d+(?:\.\d+)*)', line)
        if match:
            number = match.group(1)
            dots = number.count('.')
            return min(dots + 1, 6)

        # All caps = level 1
        if line.isupper() and len(line) > 3:
            return 1

        # Keywords for level 1
        if re.match(r'^(?:Kapitel|Chapter|Teil|Part)\s*\d+', line, re.IGNORECASE):
            return 1

        # Keywords for level 2
        if re.match(r'^(?:Abschnitt|Section)\s*\d+', line, re.IGNORECASE):
            return 2

        # Short lines are likely higher level
        if len(line) < 30:
            return 2

        return 3

    @classmethod
    def get_text_preview(cls, file_content: bytes, max_chars: int = 5000) -> str:
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

    @classmethod
    def get_page_count(cls, file_content: bytes) -> int:
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

    @classmethod
    def validate_pdf(cls, file_content: bytes) -> Tuple[bool, Optional[str]]:
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

    @classmethod
    def extract_for_ai(cls, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract and prepare PDF content for AI processing

        Returns structured data optimized for AI prompts

        Args:
            file_content: Raw PDF bytes
            filename: Original filename

        Returns:
            Dict with:
            - summary: Brief document summary
            - main_text: Cleaned text for AI
            - structure: Document structure
            - metadata: PDF metadata
            - recommendations: AI processing recommendations
        """
        # Full extraction
        result = cls.extract_text(file_content, filename)

        # Clean text for AI (remove excessive whitespace, page numbers, etc.)
        text = result['extracted_text']
        cleaned_text = cls._clean_text_for_ai(text)

        # Generate recommendations
        structure = result['structure_analysis']
        recommendations = cls._generate_recommendations(structure, len(cleaned_text))

        return {
            'file_hash': result['file_hash'],
            'filename': filename,
            'page_count': result['page_count'],
            'summary': cls._generate_summary(structure, result['extracted_metadata']),
            'main_text': cleaned_text,
            'structure': structure,
            'metadata': result['extracted_metadata'],
            'recommendations': recommendations,
            'word_count': structure.get('word_count', 0),
            'estimated_reading_time': structure.get('estimated_reading_time_min', 0)
        }

    @classmethod
    def _clean_text_for_ai(cls, text: str) -> str:
        """Clean text for AI processing"""
        if not text:
            return ""

        # Remove page numbers (common patterns)
        text = re.sub(r'\n\s*-?\s*\d+\s*-?\s*\n', '\n', text)
        text = re.sub(r'\nSeite\s+\d+\s*(von\s+\d+)?\n', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'\nPage\s+\d+\s*(of\s+\d+)?\n', '\n', text, flags=re.IGNORECASE)

        # Remove excessive whitespace
        text = re.sub(r'\n{4,}', '\n\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)

        # Remove common header/footer patterns
        text = re.sub(r'\n.*?©.*?\n', '\n', text)
        text = re.sub(r'\n.*?Copyright.*?\n', '\n', text, flags=re.IGNORECASE)

        return text.strip()

    @classmethod
    def _generate_summary(cls, structure: Dict, metadata: Dict) -> str:
        """Generate a brief document summary"""
        parts = []

        if metadata.get('title'):
            parts.append(f"Titel: {metadata['title']}")

        if structure.get('page_count'):
            parts.append(f"Seiten: {structure.get('page_count', 'unbekannt')}")

        word_count = structure.get('word_count', 0)
        if word_count:
            parts.append(f"Wörter: {word_count:,}")

        if structure.get('sections'):
            parts.append(f"Abschnitte: {len(structure['sections'])}")

        if structure.get('headings'):
            parts.append(f"Überschriften: {len(structure['headings'])}")

        reading_time = structure.get('estimated_reading_time_min', 0)
        if reading_time:
            parts.append(f"Lesezeit: ~{reading_time} Min.")

        return " | ".join(parts) if parts else "Keine Zusammenfassung verfügbar"

    @classmethod
    def _generate_recommendations(cls, structure: Dict, text_length: int) -> Dict[str, Any]:
        """Generate AI processing recommendations"""
        recommendations = {
            'suggested_chapters': 1,
            'suggested_lessons_per_chapter': 3,
            'complexity_level': 'intermediate',
            'suitable_methods': [],
            'notes': []
        }

        word_count = structure.get('word_count', 0)
        sections = structure.get('sections', [])
        headings = structure.get('headings', [])

        # Suggest chapters based on content
        if len(sections) >= 3:
            recommendations['suggested_chapters'] = min(len(sections), 10)
            recommendations['notes'].append(f"Dokument hat {len(sections)} erkennbare Abschnitte")
        elif word_count > 5000:
            recommendations['suggested_chapters'] = max(1, word_count // 2000)
            recommendations['notes'].append("Kapitelaufteilung basierend auf Textlänge empfohlen")

        # Complexity estimation
        avg_word_length = sum(len(w) for w in structure.get('key_topics', [])) / max(1, len(structure.get('key_topics', [])))
        if word_count > 10000 or len(headings) > 20:
            recommendations['complexity_level'] = 'advanced'
        elif word_count < 2000:
            recommendations['complexity_level'] = 'beginner'

        # Suitable learning methods
        key_topics = [t['topic'] for t in structure.get('key_topics', [])]

        if any(t in key_topics for t in ['Definition', 'Regel', 'Formel']):
            recommendations['suitable_methods'].extend([1, 2, 4])  # Karteikarten, Lückentext, Quiz
            recommendations['notes'].append("Enthält Definitionen - Karteikarten empfohlen")

        if any(t in key_topics for t in ['Beispiel', 'Übung', 'Aufgabe']):
            recommendations['suitable_methods'].extend([8, 9])  # Praxis-orientiert
            recommendations['notes'].append("Enthält Übungen - praktische Methoden empfohlen")

        if any(t in key_topics for t in ['Zusammenfassung', 'Überblick']):
            recommendations['suitable_methods'].extend([0, 3])  # Textlektion, Lernkarten

        # Default methods if none detected
        if not recommendations['suitable_methods']:
            recommendations['suitable_methods'] = [0, 1, 4]  # Standard: Text, Karten, Quiz

        # Remove duplicates
        recommendations['suitable_methods'] = list(set(recommendations['suitable_methods']))

        return recommendations
