"""
Chapter-Level Authoring Prompts

Prompts for chapter theory generation and chapter management.
"""

from typing import Dict, List


# ==============================================================================
# QUICK PROMPTS - Chapter Context
# ==============================================================================

QUICK_PROMPTS_CHAPTER: List[Dict[str, str]] = [
    {
        'label': 'Theorie generieren',
        'prompt': 'Generiere eine umfassende Theorie-Erklärung für dieses Kapitel mit allen wichtigen Konzepten, Begriffen und Prüfungstipps.',
        'icon': '📚'
    },
    {
        'label': 'Zusammenfassung',
        'prompt': 'Erstelle eine kompakte Zusammenfassung der wichtigsten Punkte dieses Kapitels.',
        'icon': '📋'
    },
    {
        'label': 'Lernziele definieren',
        'prompt': 'Definiere 4-6 klare, messbare Lernziele für dieses Kapitel.',
        'icon': '🎯'
    },
    {
        'label': 'Lektionen planen',
        'prompt': 'Schlage eine sinnvolle Lektionsstruktur für dieses Kapitel vor mit Titeln und kurzen Beschreibungen.',
        'icon': '📝'
    }
]


# ==============================================================================
# SYSTEM PROMPT - Chapter
# ==============================================================================

SYSTEM_PROMPT_CHAPTER: str = """Du bist ein erfahrener IHK-Prüfer und IT-Ausbilder für Fachinformatiker (FISI/FIAE).
Du hilfst beim Erstellen von Kapitel-Inhalten für ein Lern-Management-System.

Deine Aufgaben:
- Kapitel-Theorie mit Konzepten, Begriffen und Prüfungstipps erstellen
- ADHS-freundlich: Kurz, visuell, mit Emojis und Bullet Points
- Immer mit konkreten Beispielen und Zahlen arbeiten
- Prüfungsrelevanz im Blick behalten

Wenn du strukturierten Content generierst, gib ihn als JSON aus.
Wenn du nur antwortest/erklärst, nutze normalen Text.

Antworte auf Deutsch. Sei freundlich und motivierend."""


# ==============================================================================
# USER PROMPT TEMPLATE - Chapter
# ==============================================================================

USER_PROMPT_CHAPTER: str = """Kontext:
- Kurs: {course_info[title]}
{chapter_info_section}

Datei-Kontext (falls vorhanden):
{file_context}

Bisherige Konversation:
{conversation_history}

Aktuelle Anfrage:
{user_message}

Wenn du Kapitel-Theorie generierst, nutze diese JSON-Struktur:
```json
{{
    "title": "Kapitel-Titel",
    "overview": "Übersicht in 2-3 Sätzen",
    "learningGoals": ["Lernziel 1", "Lernziel 2", ...],
    "concepts": [
        {{
            "title": "Konzept-Name",
            "emoji": "passendes Emoji",
            "oneLiner": "Ein-Satz-Erklärung",
            "description": "Ausführlichere Erklärung",
            "formula": "Formel falls relevant",
            "example": "Konkretes Zahlenbeispiel"
        }}
    ],
    "terms": [
        {{
            "term": "Fachbegriff",
            "simple": "Einfache Erklärung",
            "example": "Beispiel"
        }}
    ],
    "examTips": ["Prüfungstipp 1", ...],
    "commonMistakes": ["Häufiger Fehler 1", ...]
}}
```"""
