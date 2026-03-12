"""
Domain Service: IHK Exam Question Styles

Defines the standard question formats used in IHK exams.
Pure domain logic — no infrastructure imports.
"""
from typing import Dict, List


# IHK question format definitions
QUESTION_STYLES = {
    'multiple_choice': {
        'name': 'Multiple Choice',
        'description': 'Wählen Sie die richtige(n) Antwort(en)',
        'answer_format': 'options',
        'typical_points': [1, 2, 3],
    },
    'assignment': {
        'name': 'Zuordnungsaufgabe',
        'description': 'Ordnen Sie die Begriffe den Definitionen zu',
        'answer_format': 'mapping',
        'typical_points': [2, 4, 6],
    },
    'calculation': {
        'name': 'Berechnungsaufgabe',
        'description': 'Berechnen Sie das Ergebnis',
        'answer_format': 'numeric',
        'typical_points': [3, 5, 8],
    },
    'free_text': {
        'name': 'Freitextaufgabe',
        'description': 'Erläutern/Beschreiben/Begründen Sie',
        'answer_format': 'text',
        'typical_points': [3, 5, 10],
    },
    'situation': {
        'name': 'Situationsaufgabe',
        'description': 'Analysieren Sie die Ausgangssituation und beantworten Sie die Fragen',
        'answer_format': 'structured',
        'typical_points': [5, 10, 15],
    },
}

DIFFICULTY_LEVELS = {
    'leicht': {
        'label': 'Leicht',
        'description': 'Grundwissen abfragen (kennen)',
        'competency': 'kennen',
    },
    'mittel': {
        'label': 'Mittel',
        'description': 'Wissen anwenden (anwenden)',
        'competency': 'anwenden',
    },
    'schwer': {
        'label': 'Schwer',
        'description': 'Transferaufgabe (beherrschen)',
        'competency': 'beherrschen',
    },
}


def get_style_names() -> List[str]:
    """Return all available question style keys."""
    return list(QUESTION_STYLES.keys())


def get_difficulty_levels() -> List[str]:
    """Return all difficulty level keys."""
    return list(DIFFICULTY_LEVELS.keys())


def build_generation_context(
    style: str, difficulty: str,
) -> Dict:
    """Build context for AI prompt based on style + difficulty."""
    s = QUESTION_STYLES.get(style, QUESTION_STYLES['multiple_choice'])
    d = DIFFICULTY_LEVELS.get(difficulty, DIFFICULTY_LEVELS['mittel'])
    return {
        'style_name': s['name'],
        'style_description': s['description'],
        'answer_format': s['answer_format'],
        'points_range': s['typical_points'],
        'difficulty_label': d['label'],
        'difficulty_description': d['description'],
        'competency_level': d['competency'],
    }
