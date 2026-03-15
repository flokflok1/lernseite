"""Question processing helpers for course generation.

Handles filtering, chunking, JSON serialisation, LM data building and lesson
title generation.
"""
import logging
import re
import uuid
from collections import OrderedDict
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.domain.services.lm_content_mapper import LMContentMapper, get_lm_label

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_QUESTIONS_PER_LESSON = 10

# Patterns in question_text that indicate the student needs an external file
# (Excel spreadsheet, PDF Anlage, etc.) which isn't available in the course.
_FILE_REF_RE = re.compile(
    r'\.xlsx?\b|'
    r'(?:Öffnen|in|aus)\s+(?:Sie\s+)?(?:der\s+|die\s+)?Datei\b|'
    r'Tabellenblatt\s*[„"«»\'"]',
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def filter_usable_questions(questions: List[Dict]) -> List[Dict]:
    """Remove questions that reference external files the student doesn't have.

    Questions like "Öffnen Sie die Datei Kundenumsätze.xls" are unsolvable
    without the actual file.  Questions that give all data inline are kept.
    """
    usable = [q for q in questions if not _requires_external_file(q)]
    skipped = len(questions) - len(usable)
    if skipped:
        logger.info(
            "Filtered %d/%d questions referencing external files",
            skipped, len(questions),
        )
    return usable


def _requires_external_file(question: Dict) -> bool:
    """Check if question_text references files the student can't access."""
    text = question.get('question_text', '')
    return bool(_FILE_REF_RE.search(text))


# ---------------------------------------------------------------------------
# Chunking / splitting
# ---------------------------------------------------------------------------

def split_questions_into_chunks(
    questions: List[Dict],
    max_per_chunk: int = MAX_QUESTIONS_PER_LESSON,
) -> List[List[Dict]]:
    """Split questions into chunks, grouping by scenario_title.

    Questions sharing a scenario stay together.  If a scenario group
    exceeds *max_per_chunk* it becomes its own chunk.
    """
    groups: OrderedDict = OrderedDict()
    for q in questions:
        key = q.get('scenario_title') or id(q)
        groups.setdefault(key, []).append(q)

    chunks: List[List[Dict]] = []
    current: List[Dict] = []

    for group_qs in groups.values():
        if len(current) + len(group_qs) > max_per_chunk and current:
            chunks.append(current)
            current = []
        current.extend(group_qs)

    if current:
        chunks.append(current)

    return chunks if chunks else [questions] if questions else []


# ---------------------------------------------------------------------------
# Lesson title generation
# ---------------------------------------------------------------------------

def lm_lesson_title(
    chunk: List[Dict],
    lm_type: int,
    chunk_idx: int,
    total_chunks: int,
    language: str = 'de',
) -> str:
    """Build a lesson title from scenario titles in the chunk."""
    scenarios = list(dict.fromkeys(
        (q.get('scenario_title', '') for q in chunk if q.get('scenario_title')),
    ))

    if scenarios:
        parts = [s[:50] for s in scenarios[:2]]
        title = ', '.join(parts)
        if len(scenarios) > 2:
            title += f' (+{len(scenarios) - 2})'
    else:
        title = get_lm_label(lm_type, language)

    if total_chunks > 1:
        title = f'{title} ({chunk_idx + 1}/{total_chunks})'

    return title


# ---------------------------------------------------------------------------
# Scenario grouping
# ---------------------------------------------------------------------------

def group_questions_by_scenario(questions: List[Dict]) -> List[tuple]:
    """Group questions by scenario_title, preserving order. Ungrouped last."""
    groups: OrderedDict = OrderedDict()
    ungrouped: List[Dict] = []
    for q in questions:
        key = q.get('scenario_title') or ''
        if key:
            groups.setdefault(key, []).append(q)
        else:
            ungrouped.append(q)
    result = [(t, qs) for t, qs in groups.items()]
    if ungrouped:
        result.append((f"General ({len(ungrouped)} items)", ungrouped))
    return result


# ---------------------------------------------------------------------------
# Anlage (appendix) extraction from raw PDF text
# ---------------------------------------------------------------------------

# Matches headers like "Anlage 1 zu IT 1.3", "Anlage 2: zu Aufgabe 1", etc.
_ANLAGE_HEADER_RE = re.compile(
    r'(?:^|\n)\s*(Anlage\s*(\d+)\s*[:\s]*(?:zu|Vorgabeblatt)[^\n]*)',
    re.IGNORECASE,
)

# Matches references in question_text like "Anlage 1", "Anlagen 1 und 2"
_ANLAGE_REF_RE = re.compile(
    r'Anlage[n]?\s*(\d+)(?:\s*(?:und|,|bis)\s*(\d+))?',
    re.IGNORECASE,
)


def extract_anlagen_from_raw_text(raw_text: str) -> Dict[int, str]:
    """Parse Anlage sections from raw PDF text into {number: content} dict.

    IHK exam PDFs have Anlagen (appendices) at the end with tables, prices,
    diagrams etc. that are essential for solving calculation/case questions.
    """
    if not raw_text:
        return {}

    # Find all Anlage header positions
    headers = []
    for match in _ANLAGE_HEADER_RE.finditer(raw_text):
        num = int(match.group(2))
        start = match.start()
        header_text = match.group(1).strip()
        headers.append((num, start, header_text))

    if not headers:
        return {}

    # Deduplicate — keep first occurrence of each Anlage number
    seen = set()
    unique_headers = []
    for num, start, header in headers:
        if num not in seen:
            seen.add(num)
            unique_headers.append((num, start, header))
    headers = unique_headers

    # Extract content between consecutive headers
    anlagen: Dict[int, str] = {}
    for i, (num, start, header) in enumerate(headers):
        if i + 1 < len(headers):
            end = headers[i + 1][1]
        else:
            end = len(raw_text)
        content = raw_text[start:end].strip()
        # Limit to 5000 chars per Anlage to avoid bloating scenario_text
        if len(content) > 5000:
            content = content[:5000] + '\n[... gekürzt]'
        anlagen[num] = content

    logger.info("Extracted %d Anlagen from raw text", len(anlagen))
    return anlagen


def find_anlage_references(text: str) -> List[int]:
    """Find Anlage numbers referenced in a text string.

    Handles: "Anlage 1", "Anlagen 1 und 2", "Anlage 3, 4", "Anlage 1 bis 5"
    """
    refs = set()
    for match in _ANLAGE_REF_RE.finditer(text):
        first = int(match.group(1))
        refs.add(first)
        if match.group(2):
            second = int(match.group(2))
            # "Anlage 1 bis 5" → range, "Anlage 1 und 2" → pair
            if 'bis' in match.group(0).lower():
                refs.update(range(first, second + 1))
            else:
                refs.add(second)
    return sorted(refs)


def enrich_scenario_with_anlagen(
    scenario_text: str,
    question_text: str,
    anlagen: Dict[int, str],
) -> str:
    """Append referenced Anlage content to scenario_text if not already present.

    Scans question_text for "Anlage N" references, checks whether the Anlage
    content is already in scenario_text, and appends missing ones.
    """
    if not anlagen:
        return scenario_text

    refs = find_anlage_references(question_text)
    if not refs:
        return scenario_text

    additions = []
    for num in refs:
        content = anlagen.get(num)
        if not content:
            continue
        # Skip if already present (check first 80 chars of the Anlage content)
        check_snippet = content[:80].strip()
        if check_snippet and check_snippet in (scenario_text or ''):
            continue
        additions.append(content)

    if additions:
        result = (scenario_text or '').rstrip()
        for addition in additions:
            result += f'\n\n{addition}'
        return result

    return scenario_text


# ---------------------------------------------------------------------------
# JSON serialisation
# ---------------------------------------------------------------------------

def make_json_safe(obj):
    """Convert psycopg3 types (UUID, Decimal, datetime) for json.dumps."""
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_json_safe(item) for item in obj]
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj


# ---------------------------------------------------------------------------
# LM data building
# ---------------------------------------------------------------------------

# LM type -> LMContentMapper method name (static content from exam data)
LM_MAPPER: Dict[int, str] = {
    5: 'map_to_math_interactive',
    6: 'map_to_flashcards',
    7: 'map_to_drag_drop',
    8: 'map_to_cloze',
    10: 'map_to_ihk_tasks',
    11: 'map_to_multi_step',
}


def build_static_lm_data(lm_type: int, questions: List[Dict]) -> Optional[Dict[str, Any]]:
    """Build JSONB data for a static LM type via LMContentMapper."""
    mapper = LM_MAPPER.get(lm_type)
    if not mapper:
        return None
    map_fn = getattr(LMContentMapper, mapper, None)
    if not map_fn:
        return None
    data = map_fn(questions)
    if not data:
        return None
    # Skip if content dict exists but all values are empty lists
    items_key = next(iter(data), None)
    if items_key is not None and len(data.get(items_key, [])) == 0:
        return None
    return data
