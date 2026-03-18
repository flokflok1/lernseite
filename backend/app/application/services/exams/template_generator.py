"""Template Generator — detects and generates missing solution templates.

Scans question texts for references to solution templates (Loesungsvorlagen)
and generates HTML templates for any that are missing from the exam anlagen.
"""
import re
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

_TEMPLATE_PATTERNS = [
    r'[Ll](?:ö|oe)sungsvorlage\s+(\d+)',
    r'[Vv]orlage\s+(\d+)',
    r'[Ll](?:ö|oe)sungsblatt\s+(\d+)',
]

# AI prompt labels keyed by language — used to build the generation prompt.
_LABELS = {
    'de': {
        'intro': 'Erstelle eine HTML-Vorlage fuer eine IHK-Klausur.',
        'scenario': 'Szenario',
        'task': 'Die Aufgabenstellung',
        'template': 'Vorlage Nr.',
        'body': (
            'Die Vorlage soll eine leere Tabelle oder ein Formular sein, '
            'das ausgefuellt wird. Passende Spalten/Zeilen basierend '
            'auf der Beschreibung. Sauberes HTML mit <table>.'
        ),
        'css': "CSS-Klasse: 'template-generated'.",
        'rule': 'Antworte NUR mit dem HTML-Code.',
    },
    'en': {
        'intro': 'Create an HTML solution template for an IHK exam.',
        'scenario': 'Scenario',
        'task': 'The task',
        'template': 'Template No.',
        'body': (
            'The template should be an empty table or form to be filled in. '
            'Appropriate columns/rows based on the description. '
            'Clean HTML with <table>.'
        ),
        'css': "CSS class: 'template-generated'.",
        'rule': 'Reply ONLY with the HTML code.',
    },
}


def find_missing_templates(
    questions: List[Dict],
    existing_numbers: set,
) -> List[Dict]:
    """Find template references that don't have a matching Anlage.

    Args:
        questions: List of question record dicts with question_text etc.
        existing_numbers: Set of Anlage numbers already present.

    Returns:
        List of dicts with number, question_text, scenario_title.
    """
    missing: Dict[int, Dict] = {}
    for q in questions:
        text = ' '.join(filter(None, [
            q.get('question_text', ''),
            q.get('scenario_text', ''),
        ]))
        for pattern in _TEMPLATE_PATTERNS:
            for match in re.finditer(pattern, text):
                num = int(match.group(1))
                if num not in existing_numbers and num not in missing:
                    missing[num] = {
                        'number': num,
                        'question_text': q.get('question_text', '')[:500],
                        'scenario_title': q.get('scenario_title', ''),
                    }
    return list(missing.values())


def generate_template_html(
    number: int,
    question_text: str,
    scenario_title: str,
    language: str = 'de',
) -> Optional[str]:
    """Generate HTML for a missing solution template using AI.

    Args:
        number: Template number (e.g. 1).
        question_text: The question referencing this template.
        scenario_title: Title of the scenario (context).
        language: Prompt language ('de', 'en').

    Returns:
        HTML string or None on failure.
    """
    prompt = _build_prompt(number, question_text, scenario_title, language)

    try:
        from app.infrastructure.ai.adapter import AIAdapter
        adapter = AIAdapter()
        response = adapter.send_request(
            prompt=prompt, language=language,
            temperature=0.3, max_tokens=2000,
        )
        html = response.get('output_text', '')
        html = _extract_html_block(html)
        return html if html and html.strip() else None
    except Exception:
        logger.exception("Failed to generate template %d", number)
        return None


def _build_prompt(
    number: int,
    question_text: str,
    scenario_title: str,
    language: str,
) -> str:
    """Build the AI prompt from language-specific label templates."""
    lb = _LABELS.get(language, _LABELS['de'])
    parts = [
        lb['intro'],
        '',
        f"{lb['scenario']}: {scenario_title}",
        f"{lb['task']}: {question_text}",
        f"{lb['template']} {number}",
        '',
        lb['body'],
        lb['css'],
        '',
        lb['rule'],
    ]
    return '\n'.join(parts)


def _extract_html_block(text: str) -> str:
    """Extract HTML from a markdown code block if present."""
    if '```html' in text:
        return text.split('```html')[1].split('```')[0].strip()
    if '```' in text:
        return text.split('```')[1].split('```')[0].strip()
    return text
