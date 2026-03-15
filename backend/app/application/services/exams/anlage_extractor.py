"""Anlage Extractor — parses exam raw_text into structured appendix documents.

Extracts Anlage sections from IHK exam PDFs and classifies each as:
- offer: Business letter/Angebot (Briefkopf, Preistabelle, Konditionen)
- api_reference: Function/API reference table
- info_document: Informational text (Schutzziele, Richtlinien)
- table: Standalone data table
- generic: Unclassified text block
"""
import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def extract_anlagen(raw_text: str) -> List[Dict]:
    """Extract all Anlage sections from exam raw_text.

    Returns list of structured Anlage dicts with type classification.
    """
    if not raw_text:
        return []

    sections = _split_into_sections(raw_text)
    anlagen = []

    for number, text in sections:
        anlage_type = _classify_type(text)
        data = _parse_by_type(text, anlage_type)
        title = _extract_title(text, number, anlage_type)

        anlagen.append({
            'number': number,
            'title': title,
            'type': anlage_type,
            'raw_text': text.strip(),
            'data': data,
        })

    logger.info("Extracted %d Anlagen from raw_text", len(anlagen))
    return anlagen


def _split_into_sections(raw_text: str) -> List[tuple]:
    """Split raw_text into (number, text) tuples per Anlage."""
    pattern = r'(?:^|\n)\s*Anlage\s+(\d+)\s*\n'
    matches = list(re.finditer(pattern, raw_text))

    if not matches:
        return []

    sections = []
    for i, match in enumerate(matches):
        number = int(match.group(1))
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)
        text = raw_text[start:end].strip()
        # Stop at "Vorgabeblatt" sections
        vorgabe = re.search(r'\n\s*Vorgabeblatt\s+\d', text)
        if vorgabe:
            text = text[:vorgabe.start()].strip()
        sections.append((number, text))

    return sections


def _classify_type(text: str) -> str:
    """Classify Anlage type based on content heuristics."""
    lower = text.lower()

    # Offer/Angebot detection
    offer_signals = ['angebot', 'gesamtpreis', 'einzelpreis', 'gesamtsumme',
                     'gesamtbetrag', 'menge', 'ust.', 'skonto', 'rabatt',
                     'mit freundlichen grüßen', 'sehr geehrte']
    if sum(1 for s in offer_signals if s in lower) >= 3:
        return 'offer'

    # API reference detection
    api_signals = ['()', 'return', 'gibt den', 'gibt die', 'löscht',
                   'function', 'parameter']
    if sum(1 for s in api_signals if s in lower) >= 2:
        return 'api_reference'

    # Info document detection
    if len(text) > 500 and ('hinsichtlich' in lower or 'klassifikation' in lower
                            or 'anforderungen' in lower):
        return 'info_document'

    return 'generic'


def _extract_title(text: str, number: int, anlage_type: str) -> str:
    """Extract a meaningful title for the Anlage."""
    # Try to find company name for offers
    if anlage_type == 'offer':
        for line in text.split('\n')[:5]:
            line = line.strip()
            if line and len(line) > 3 and not line.startswith('Anlage'):
                if any(w in line for w in ['AG', 'GmbH', 'KG', 'OHG', 'e.V.']):
                    return f"Angebot {line}"
                if 'angebot' in line.lower():
                    return line
        return f"Anlage {number} — Angebot"

    if anlage_type == 'api_reference':
        return f"Anlage {number} — Funktionsreferenz"

    if anlage_type == 'info_document':
        first_line = text.split('\n')[0].strip()
        if first_line and len(first_line) < 80:
            return f"Anlage {number} — {first_line}"
        return f"Anlage {number} — Informationsblatt"

    return f"Anlage {number}"


def _parse_by_type(text: str, anlage_type: str) -> Dict:
    """Parse Anlage text into structured data based on type."""
    if anlage_type == 'offer':
        return _parse_offer(text)
    if anlage_type == 'api_reference':
        return _parse_api_reference(text)
    if anlage_type == 'info_document':
        return _parse_info_document(text)
    return {'content': text.strip()}


def _parse_offer(text: str) -> Dict:
    """Parse a business offer/Angebot into structured data."""
    lines = text.split('\n')
    result: Dict = {
        'company': '', 'address': '', 'recipient': {},
        'document_number': '', 'positions': [],
        'conditions': [], 'body_text': '', 'signer': '',
    }

    # Extract company name (usually in first few non-empty lines)
    for line in lines[:8]:
        line = line.strip()
        if line and any(w in line for w in ['AG', 'GmbH', 'KG', 'OHG']):
            if not result['company'] or len(line) < len(result['company']):
                result['company'] = line
            break

    # Extract document/customer numbers
    for line in lines:
        nr_match = re.search(
            r'(?:Angebots?[-\s]*(?:Nr\.?|nr\.?)|Nr\.)\s*:?\s*(\d+)', line,
        )
        if nr_match:
            result['document_number'] = nr_match.group(1)
        kd_match = re.search(
            r'Kunden?[-\s]*(?:Nr\.?|nr\.?)\s*:?\s*(\d+)', line,
        )
        if kd_match:
            result['customer_number'] = kd_match.group(1)

    # Extract prices/totals
    total_match = re.search(
        r'(?:Gesamt(?:summe|betrag|preis)\s*(?:brutto)?)\s*[:\s]*'
        r'([\d.,]+)\s*(?:€|EUR)',
        text,
    )
    if total_match:
        result['grand_total'] = total_match.group(1)

    # Extract conditions (Skonto, Rabatt, Lieferzeit)
    for line in lines:
        lower = line.lower().strip()
        if any(w in lower for w in ['skonto', 'rabatt', 'lieferung',
                                     'lieferzeit', 'zahlung']):
            if line.strip():
                result['conditions'].append(line.strip())

    # Signer
    gruss_idx = None
    for i, line in enumerate(lines):
        if 'freundlichen grüßen' in line.lower():
            gruss_idx = i
            break
    if gruss_idx and gruss_idx + 2 < len(lines):
        for line in lines[gruss_idx + 1:gruss_idx + 4]:
            name = line.strip()
            if name and len(name) > 2 and not name.startswith(('–', '-', '_')):
                result['signer'] = name
                break

    # Full body text for rendering
    result['body_text'] = text.strip()

    return result


def _parse_api_reference(text: str) -> Dict:
    """Parse API/function reference into structured list."""
    functions = []
    lines = text.split('\n')

    current_name = None
    current_desc = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_name:
                functions.append({
                    'name': current_name,
                    'description': ' '.join(current_desc).strip(),
                })
                current_name = None
                current_desc = []
            continue

        # Detect function signature (contains parentheses)
        func_match = re.match(r'^(\w+\([^)]*\))\s*(.*)', stripped)
        if func_match:
            if current_name:
                functions.append({
                    'name': current_name,
                    'description': ' '.join(current_desc).strip(),
                })
            current_name = func_match.group(1)
            current_desc = [func_match.group(2)] if func_match.group(2) else []
        elif current_name:
            current_desc.append(stripped)

    if current_name:
        functions.append({
            'name': current_name,
            'description': ' '.join(current_desc).strip(),
        })

    return {'functions': functions}


def _parse_info_document(text: str) -> Dict:
    """Parse info document preserving sections."""
    return {'content': text.strip()}
