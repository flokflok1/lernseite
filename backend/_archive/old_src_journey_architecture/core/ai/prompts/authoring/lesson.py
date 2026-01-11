"""
Lesson-Level Authoring Prompts

Prompts for lesson content generation and explanations.
"""

from typing import Dict, List


# ==============================================================================
# QUICK PROMPTS - Lesson Context
# ==============================================================================

QUICK_PROMPTS_LESSON: List[Dict[str, str]] = [
    {
        'label': 'Schritt-für-Schritt',
        'prompt': 'Erkläre den Inhalt dieser Lektion Schritt für Schritt, als wärst du ein geduldiger Tutor.',
        'icon': '👣'
    },
    {
        'label': 'Beispiele hinzufügen',
        'prompt': 'Erstelle 3-4 praktische Beispiele mit konkreten Zahlen und Lösungswegen.',
        'icon': '💡'
    },
    {
        'label': 'Quiz erstellen',
        'prompt': 'Erstelle 5 Verständnisfragen (Multiple Choice) zu dieser Lektion mit Erklärungen.',
        'icon': '❓'
    },
    {
        'label': 'Übungsaufgabe',
        'prompt': 'Erstelle eine Übungsaufgabe zum Selbsttest mit Musterlösung.',
        'icon': '✏️'
    }
]


# ==============================================================================
# SYSTEM PROMPT - Lesson
# ==============================================================================

SYSTEM_PROMPT_LESSON: str = """Du bist ein geduldiger Nachhilfelehrer für Fachinformatiker.
Du hilfst beim Erstellen von Lektions-Inhalten mit Schritt-für-Schritt Erklärungen.

Deine Stärken:
- Komplexe Themen einfach erklären
- Jeden Rechenschritt einzeln zeigen
- Konkrete Beispiele mit echten Zahlen
- Taschenrechner-Eingaben zeigen (welche Taste drücken)
- Schema/Tabellen schrittweise aufbauen

Wenn du strukturierten Content (Schritte, Erklärungen) generierst, gib ihn als JSON aus.
Wenn du nur antwortest/erklärst, nutze normalen Text.

Antworte auf Deutsch. Sei geduldig und ermutigend."""


# ==============================================================================
# USER PROMPT TEMPLATE - Lesson
# ==============================================================================

USER_PROMPT_LESSON: str = """Kontext:
- Kurs: {course_info[title]}
- Kapitel: {chapter_info[title]}
{lesson_info_section}

Datei-Kontext (falls vorhanden):
{file_context}

Bisherige Konversation:
{conversation_history}

Aktuelle Anfrage:
{user_message}

Wenn du Lektions-Erklärungen generierst, nutze diese JSON-Struktur:
```json
{{
    "title": "Lektions-Titel",
    "overview": "Kurze Einführung",
    "steps": [
        {{
            "title": "Schritt-Titel",
            "speech": "Was der Tutor erklärt (2-4 Sätze)",
            "calculator": "Taschenrechner-Eingabe (optional)",
            "result": "Ergebnis (optional)",
            "schema": [
                {{"name": "Zeile", "operator": "=", "value": "Wert", "highlight": false}}
            ],
            "tip": "Merkhilfe (optional)"
        }}
    ],
    "summary": "Zusammenfassung",
    "practiceTask": {{
        "description": "Übungsaufgabe",
        "solution": "Lösung"
    }}
}}
```"""
