"""
PDF Structure Analysis Module

Analyzes document structure, headings, sections, and content patterns.
"""

import re
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class PDFAnalyzer:
    """Analyzes PDF structure, headings, and content patterns"""

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
    def analyze_structure(
        cls,
        full_text: str,
        pages_text: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Analyze document structure

        Args:
            full_text: Complete extracted text
            pages_text: Text per page (optional)

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

        # Detect headings and sections
        structure['headings'], structure['sections'] = cls._extract_headings_and_sections(full_text)

        # Detect key topics
        structure['key_topics'] = cls._extract_key_topics(full_text)

        return structure

    @classmethod
    def _extract_headings_and_sections(cls, full_text: str) -> tuple:
        """
        Extract headings and organize into sections

        Args:
            full_text: Complete text

        Returns:
            Tuple of (headings list, sections list)
        """
        lines = full_text.split('\n')
        headings = []
        sections = []
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
                        sections.append(current_section)
                    current_section = {
                        'title': heading_match,
                        'start_line': line_num + 1,
                        'headings': []
                    }
                elif current_section:
                    current_section['headings'].append(heading)

        # Add last section
        if current_section:
            sections.append(current_section)

        return headings, sections

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
    def _extract_key_topics(cls, full_text: str) -> List[Dict[str, Any]]:
        """
        Detect key topics from content

        Args:
            full_text: Complete text

        Returns:
            List of topics with occurrence counts
        """
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
        return key_topics[:20]  # Top 20

    @staticmethod
    def clean_text_for_ai(text: str) -> str:
        """
        Clean text for AI processing

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text optimized for AI
        """
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

    @staticmethod
    def generate_summary(structure: Dict, metadata: Dict) -> str:
        """
        Generate a brief document summary

        Args:
            structure: Structure analysis dict
            metadata: PDF metadata dict

        Returns:
            Summary string
        """
        parts = []

        if metadata.get('title'):
            parts.append(f"Titel: {metadata['title']}")

        if structure.get('word_count'):
            parts.append(f"Wörter: {structure['word_count']:,}")

        if structure.get('sections'):
            parts.append(f"Abschnitte: {len(structure['sections'])}")

        if structure.get('headings'):
            parts.append(f"Überschriften: {len(structure['headings'])}")

        reading_time = structure.get('estimated_reading_time_min', 0)
        if reading_time:
            parts.append(f"Lesezeit: ~{reading_time} Min.")

        return " | ".join(parts) if parts else "Keine Zusammenfassung verfügbar"

    @staticmethod
    def generate_recommendations(structure: Dict, text_length: int) -> Dict[str, Any]:
        """
        Generate AI processing recommendations

        Args:
            structure: Structure analysis
            text_length: Length of cleaned text

        Returns:
            Recommendations dict
        """
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
        if word_count > 10000 or len(headings) > 20:
            recommendations['complexity_level'] = 'advanced'
        elif word_count < 2000:
            recommendations['complexity_level'] = 'beginner'

        # Suitable learning methods
        key_topics = [t['topic'] for t in structure.get('key_topics', [])]

        if any(t in key_topics for t in ['Definition', 'Regel', 'Formel']):
            recommendations['suitable_methods'].extend([1, 2, 4])
            recommendations['notes'].append("Enthält Definitionen - Karteikarten empfohlen")

        if any(t in key_topics for t in ['Beispiel', 'Übung', 'Aufgabe']):
            recommendations['suitable_methods'].extend([8, 9])
            recommendations['notes'].append("Enthält Übungen - praktische Methoden empfohlen")

        if any(t in key_topics for t in ['Zusammenfassung', 'Überblick']):
            recommendations['suitable_methods'].extend([0, 3])

        # Default methods if none detected
        if not recommendations['suitable_methods']:
            recommendations['suitable_methods'] = [0, 1, 4]

        # Remove duplicates and sort
        recommendations['suitable_methods'] = sorted(list(set(recommendations['suitable_methods'])))

        return recommendations
