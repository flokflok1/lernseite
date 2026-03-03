"""
ExamArchive Service

Application service for importing real IHK exam PDFs into the archive.
Handles folder scanning, filename parsing, PDF text extraction, and DB import.

Filename conventions handled:
  GA1_FIA_Sommer2024.PDF          → part=GA1, profession=FISI, season=sommer, year=2024
  GA2_Winter2019_Loesung.PDF      → part=GA2, season=winter, year=2019, is_solution=True
  WK_Sommer2018.pdf               → part=WK
  2022 AP1 AUFGABEN.pdf           → year=2022 (season from parent folder)
  AP 1 Aufgaben Sommer 2024.pdf   → season=sommer, year=2024
  W2023_AP1_Aufgaben und Lösungen.pdf → season=winter, year=2023
  AP2_Wiso_Sommer2021_Loesung.PDF → part=WK, is_solution=True
"""

import os
import re
import logging
from typing import Optional, List, Dict, Any

from app.application.services.content.pdf.bridge import PDFService
from app.infrastructure.persistence.repositories.exams.core import (
    ExamRepository
)

logger = logging.getLogger(__name__)

# Profession alias mapping
PROFESSION_ALIASES = {
    'fia': 'FISI',
    'fisi': 'FISI',
    'fiae': 'FIAE',
    'fae': 'FIAE',
}

# Part detection patterns (order matters — more specific first)
# Using (?:^|[\s_\-]) instead of \b because _ is a word char
PART_PATTERNS = [
    (r'(?:^|[\s_\-(])ga1(?:[\s_\-.]|$)', 'GA1'),
    (r'(?:^|[\s_\-(])ga2(?:[\s_\-.]|$)', 'GA2'),
    (r'(?:^|[\s_\-(])itsk(?:[\s_\-.]|$)', 'GA2'),
    (r'(?:^|[\s_\-(])wk(?:[\s_\-.]|$)', 'WK'),
    (r'(?:^|[\s_\-(])wiso(?:[\s_\-.]|$)', 'WK'),
    (r'ap2[\s_\-]?wiso', 'WK'),
    (r'(?:^|[\s_\-(])asp(?:[\s_\-.]|$)', 'GA1'),
]

# Solution markers (ö, oe, o variants + plural forms)
SOLUTION_MARKERS = re.compile(
    r'l(?:ö|oe|o)sung(?:en)?', re.IGNORECASE
)


def _parse_season_year_from_folder(folder_name: str) -> Dict[str, Any]:
    """
    Extract season and year from parent folder name.

    Examples:
        "Sommer 2024" → {"season": "sommer", "year": 2024}
        "Winter 2023-2024" → {"season": "winter", "year": 2023}
    """
    result: Dict[str, Any] = {}
    lower = folder_name.lower()

    if 'sommer' in lower or 'summer' in lower:
        result['season'] = 'sommer'
    elif 'winter' in lower:
        result['season'] = 'winter'

    # Extract year (first 4-digit number)
    year_match = re.search(r'(\d{4})', folder_name)
    if year_match:
        result['year'] = int(year_match.group(1))

    return result


def _parse_filename(filename: str, parent_folder: str) -> Dict[str, Any]:
    """
    Parse an exam PDF filename to extract metadata.

    Args:
        filename: The PDF filename (e.g. "GA1_FIA_Sommer2024.PDF")
        parent_folder: Parent folder name (e.g. "Sommer 2024")

    Returns:
        Dict with keys: part, season, year, profession, is_solution,
                        region, semester
    """
    stem = os.path.splitext(filename)[0]
    lower = stem.lower()

    meta: Dict[str, Any] = {
        'part': None,
        'season': None,
        'year': None,
        'profession': 'FISI',
        'region': 'bw',
        'is_solution': False,
    }

    # --- Solution detection ---
    meta['is_solution'] = bool(SOLUTION_MARKERS.search(lower))

    # --- Part detection ---
    for pattern, part_value in PART_PATTERNS:
        if re.search(pattern, lower):
            meta['part'] = part_value
            break

    # --- Season detection from filename ---
    if 'sommer' in lower or 'summer' in lower:
        meta['season'] = 'sommer'
    elif 'winter' in lower:
        meta['season'] = 'winter'
    elif lower.startswith('w') and re.match(r'^w\d{4}', lower):
        meta['season'] = 'winter'

    # --- Year detection from filename ---
    year_match = re.search(r'(\d{4})', stem)
    if year_match:
        meta['year'] = int(year_match.group(1))

    # --- Profession detection ---
    for alias, profession in PROFESSION_ALIASES.items():
        if re.search(rf'\b{alias}\b', lower):
            meta['profession'] = profession
            break

    # --- Fallback from parent folder ---
    folder_info = _parse_season_year_from_folder(parent_folder)
    if meta['season'] is None and 'season' in folder_info:
        meta['season'] = folder_info['season']
    if meta['year'] is None and 'year' in folder_info:
        meta['year'] = folder_info['year']

    # --- Build semester label ---
    if meta['season'] and meta['year']:
        season_label = (
            'Sommer' if meta['season'] == 'sommer' else 'Winter'
        )
        meta['semester'] = f"{season_label} {meta['year']}"
    else:
        meta['semester'] = None

    return meta


class ExamArchiveService:
    """
    Service for scanning folders of real IHK exam PDFs and importing
    them into the exam archive database.
    """

    @staticmethod
    def scan_folder(folder_path: str) -> List[Dict]:
        """
        Walk a folder tree, find all PDFs, parse filenames, and
        match task PDFs with their solution counterparts.

        Args:
            folder_path: Absolute path to the root exam folder

        Returns:
            List of dicts, each representing one exam paper with keys:
            filename, filepath, parent_folder, meta, solution_filepath
        """
        papers: Dict[str, Dict] = {}  # key = task identity
        solutions: Dict[str, Dict] = {}  # key = task identity

        for dirpath, _dirs, files in os.walk(folder_path):
            parent = os.path.basename(dirpath)
            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                if ext != '.pdf':
                    continue
                # Skip macOS resource fork files
                if fname.startswith('._'):
                    continue

                filepath = os.path.join(dirpath, fname)
                meta = _parse_filename(fname, parent)

                entry = {
                    'filename': fname,
                    'filepath': filepath,
                    'parent_folder': parent,
                    'meta': meta,
                }

                # Build identity key for matching
                identity = _build_identity_key(meta)

                if meta['is_solution']:
                    solutions[identity] = entry
                else:
                    papers[identity] = entry

        # Match solutions to papers
        result = []
        for key, paper in papers.items():
            paper['solution_filepath'] = None
            if key in solutions:
                paper['solution_filepath'] = (
                    solutions[key]['filepath']
                )
            result.append(paper)

        # Include unmatched solutions as standalone entries
        for key, sol in solutions.items():
            if key not in papers:
                sol['solution_filepath'] = sol['filepath']
                sol['meta']['is_solution'] = False
                result.append(sol)

        return result

    @staticmethod
    def import_paper(paper: Dict) -> Optional[str]:
        """
        Import a single exam paper into the database.

        Extracts PDF text, creates DB record via ExamRepository.
        Skips duplicates (checks pdf_path).

        Args:
            paper: Dict from scan_folder() with filepath, meta, etc.

        Returns:
            exam_id if created, None if skipped (duplicate)
        """
        filepath = paper['filepath']
        meta = paper['meta']

        # Duplicate check
        existing = ExamRepository.find_by_pdf_path(filepath)
        if existing:
            logger.info("Skipping duplicate: %s", filepath)
            return None

        # Extract text from task PDF
        raw_text = _extract_pdf_text(filepath)

        # Extract solution text if available
        solution_text = None
        solution_path = paper.get('solution_filepath')
        if solution_path and solution_path != filepath:
            solution_text = _extract_pdf_text(solution_path)

        # Build title
        title = _build_exam_title(meta, paper.get('filename', ''))

        # Build settings JSONB
        settings = {}
        if solution_text:
            settings['solution_text'] = solution_text

        exam_data = {
            'exam_type': 'real',
            'title': title,
            'description': f"Importiert aus: {paper.get('filename', '')}",
            'duration_minutes': 90,
            'passing_score': 50,
            'total_points': 100,
            'semester': meta.get('semester'),
            'year': meta.get('year'),
            'season': meta.get('season'),
            'part': meta.get('part'),
            'region': meta.get('region', 'bw'),
            'profession': meta.get('profession', 'FISI'),
            'pdf_path': filepath,
            'solution_pdf_path': solution_path,
            'analysis_status': 'pending',
            'raw_text': raw_text,
            'settings': settings if settings else None,
        }

        # Remove None values to let DB defaults apply
        exam_data = {k: v for k, v in exam_data.items() if v is not None}

        result = ExamRepository.create_exam(exam_data)
        if result:
            logger.info(
                "Imported exam: %s (id=%s)",
                title, result.get('exam_id')
            )
            return result.get('exam_id')

        logger.error("Failed to create exam record for: %s", filepath)
        return None

    @classmethod
    def import_folder(cls, folder_path: str) -> Dict[str, Any]:
        """
        Scan and import all exam PDFs from a folder.

        Args:
            folder_path: Absolute path to root exam folder

        Returns:
            Summary dict with imported, skipped, errors counts
        """
        papers = cls.scan_folder(folder_path)
        summary = {
            'total_found': len(papers),
            'imported': 0,
            'skipped': 0,
            'errors': 0,
            'details': [],
        }

        for paper in papers:
            try:
                exam_id = cls.import_paper(paper)
                if exam_id:
                    summary['imported'] += 1
                    summary['details'].append({
                        'file': paper['filename'],
                        'status': 'imported',
                        'exam_id': exam_id,
                    })
                else:
                    summary['skipped'] += 1
                    summary['details'].append({
                        'file': paper['filename'],
                        'status': 'skipped',
                    })
            except Exception as e:
                logger.error(
                    "Error importing %s: %s",
                    paper.get('filename', '?'), e
                )
                summary['errors'] += 1
                summary['details'].append({
                    'file': paper.get('filename', '?'),
                    'status': 'error',
                    'error': str(e),
                })

        logger.info(
            "Import complete: %d imported, %d skipped, %d errors",
            summary['imported'], summary['skipped'], summary['errors']
        )
        return summary


def _build_identity_key(meta: Dict) -> str:
    """Build a key for matching task PDFs with their solutions."""
    parts = [
        str(meta.get('year', '')),
        str(meta.get('season', '')),
        str(meta.get('part', '')),
    ]
    return '|'.join(parts).lower()


def _extract_pdf_text(filepath: str) -> Optional[str]:
    """
    Read a PDF file and extract its text content.

    Args:
        filepath: Absolute path to the PDF

    Returns:
        Extracted text or None on failure
    """
    try:
        with open(filepath, 'rb') as f:
            file_bytes = f.read()

        result = PDFService.extract_text(
            file_bytes, os.path.basename(filepath), use_cache=False
        )
        return result.get('extracted_text')
    except Exception as e:
        logger.warning("PDF extraction failed for %s: %s", filepath, e)
        return None


def _build_exam_title(meta: Dict, filename: str) -> str:
    """Build a human-readable exam title from metadata."""
    parts = ['IHK AP1']

    if meta.get('part'):
        parts.append(meta['part'])

    if meta.get('profession') and meta['profession'] != 'FISI':
        parts.append(meta['profession'])
    elif meta.get('profession'):
        parts.append('FISI')

    if meta.get('semester'):
        parts.append(meta['semester'])
    elif meta.get('year'):
        parts.append(str(meta['year']))

    if len(parts) <= 1:
        return f"IHK AP1 - {filename}"

    return ' '.join(parts)
