"""
Curriculum Mapping Helpers

Helper functions for AI-powered question-to-curriculum mapping:
- JSON extraction from AI responses
- Compound code building (A.1.a format)
- Objective reference building for AI prompts
- Specialization detection and section filtering
- Mapping prompt construction

Split from curriculum_service.py per G01 (max 500 LOC).
"""

import re
from typing import Dict, List


# ── Specialization detection & section filtering ──────────────

_SPECIALIZATION_MAP = {
    'FISI': 'Fachinformatiker Systemintegration',
    'FIAE': 'Fachinformatiker Anwendungsentwicklung',
    'FIDP': 'Fachinformatiker Daten- und Prozessanalyse',
    'FIKA': 'Fachinformatiker Digitale Vernetzung',
}


def detect_specialization(exam_type_key: str) -> str:
    """Extract specialization abbreviation from exam type key.

    E.g. 'FI_AP1' → 'FISI', 'FI_AP2_FIAE' → 'FIAE'.
    """
    for abbr in _SPECIALIZATION_MAP:
        if abbr in exam_type_key.upper():
            return abbr
    return ''


def filter_sections_for_specialization(
    sections: List[Dict], specialization: str,
) -> set:
    """Return section codes that apply to the given specialization.

    Uses the applies_to field from curriculum_sections.
    If specialization is unknown, returns all sections.
    """
    full_name = _SPECIALIZATION_MAP.get(specialization)
    if not full_name:
        return {s.get('section_number', '') for s in sections}

    allowed = set()
    for s in sections:
        applies_to = s.get('applies_to') or []
        if full_name in applies_to or not applies_to:
            allowed.add(s.get('section_number', ''))
    return allowed


# ── JSON extraction ───────────────────────────────────────────

def extract_json_object(text: str) -> str:
    """Extract JSON array or object from AI output.

    AI models often add explanatory text before/after the JSON.
    Handles both [...] arrays and {...} objects.
    """
    text = text.strip()
    # Remove markdown code fences first
    text = re.sub(r'^```(?:json)?\s*\n?', '', text)
    text = re.sub(r'\n?```\s*$', '', text)
    text = text.strip()

    # Prefer array extraction (auto-map returns arrays)
    arr_start = text.find('[')
    arr_end = text.rfind(']')
    if arr_start != -1 and arr_end != -1 and arr_end > arr_start:
        return text[arr_start:arr_end + 1]

    # Fallback: extract single object
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]

    return text


# ── Compound codes & objective reference ──────────────────────

def build_compound_code(obj: Dict) -> str:
    """Build unique compound code like A.1.a from objective hierarchy."""
    return (
        f"{obj.get('section_code', '?')}"
        f".{obj.get('position_code', '?')}"
        f".{obj['objective_code']}"
    )


def build_objective_reference(objectives: List[Dict]) -> str:
    """Build a compact text reference of objectives for AI prompts."""
    lines = []
    for obj in objectives:
        code = build_compound_code(obj)
        desc = obj.get('description', '')
        if isinstance(desc, dict):
            desc = desc.get('de', '') or next(iter(desc.values()), '')
        lines.append(f"{code}: {str(desc)[:120]}")
    return "\n".join(lines)


# ── Prompt construction ──────────────────────────────────────

def build_mapping_prompt(
    obj_reference: str,
    questions_text: str,
    specialization: str = None,
) -> str:
    """Build the AI prompt for question-to-objective mapping.

    Includes IHK exam structure context and part-specific guidance
    for accurate mapping.
    """
    spec_label = _SPECIALIZATION_MAP.get(specialization, 'IT-Berufe')

    return (
        f"You are an expert at mapping IHK {spec_label} exam questions "
        "to Ausbildungsrahmenplan curriculum objectives.\n\n"
        "IMPORTANT CONTEXT about IHK exam structure:\n"
        "- GA1 (Ganzheitliche Aufgabe 1): General IT questions — "
        "projects, business processes, planning. "
        "Map primarily to Section A (fachrichtungsübergreifend).\n"
        "- GA2 (Ganzheitliche Aufgabe 2): Specialization-specific "
        "technical questions. "
        "Map to the specialization section (e.g. C for FISI).\n"
        "- WK (Wirtschafts- und Sozialkunde): Law, contracts, labor "
        "law, economics, social insurance. "
        "Map PRIMARILY to Section F (Berufsbildung, Arbeits- und "
        "Tarifrecht, betriebliche Mitbestimmung).\n"
        "- Questions without a Part label: treat as GA1/GA2 mix.\n\n"
        "MAPPING RULES:\n"
        "- Each question's Part (GA1/GA2/WK) is shown after 'Part:'\n"
        "- WK questions about contracts, law, rights, insurance → "
        "Section F (NOT Section A)\n"
        "- Programming/HTML/CSS/UML questions → A.10 (Programmieren "
        "von Softwarelösungen), NOT Section B\n"
        "- Networking/server/infrastructure questions → Section C "
        "(for FISI)\n"
        "- A.1 is ONLY for project planning and work organization, "
        "NOT a catch-all\n"
        "- Set confidence realistically: 0.9+ only for clear matches, "
        "0.6-0.8 for uncertain ones\n\n"
        "Available curriculum objectives (code: description):\n"
        f"{obj_reference}\n\n"
        "Questions to map:\n"
        f"{questions_text}\n\n"
        "Respond with ONLY a JSON array, no other text:\n"
        '[{"question_id": "uuid-here", "objective_code": "A.1.a", '
        '"confidence": 0.85}]\n\n'
        "Rules:\n"
        "- objective_code MUST be one of the codes listed above\n"
        "- confidence: 0.0-1.0 (be realistic, not always 0.95)\n"
        "- Each question gets exactly one objective"
    )
