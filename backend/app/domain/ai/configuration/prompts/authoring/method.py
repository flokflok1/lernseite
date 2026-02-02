"""
Learning Method-Level Authoring Prompts

Prompts for learning method instance content generation.
"""

from typing import Dict, List


# ==============================================================================
# QUICK PROMPTS - Learning Method Context
# ==============================================================================

QUICK_PROMPTS_LEARNING_METHOD: List[Dict[str, str]] = [
    {
        'label': 'Content generieren',
        'prompt': 'Generiere den vollständigen Content für diese Lernmethode.',
        'icon': '🎓'
    },
    {
        'label': 'Interaktiv machen',
        'prompt': 'Füge interaktive Elemente hinzu (Klick-Aktionen, Drag&Drop, etc.).',
        'icon': '🖱️'
    },
    {
        'label': 'Schwierigkeit anpassen',
        'prompt': 'Erstelle drei Schwierigkeitsstufen: Anfänger, Fortgeschritten, Profi.',
        'icon': '📊'
    }
]


# ==============================================================================
# SYSTEM PROMPT - Learning Method
# ==============================================================================

SYSTEM_PROMPT_LEARNING_METHOD: str = """Du bist ein Experte für Lernmethoden und Didaktik.
Du hilfst beim Erstellen von interaktiven Lernmethoden-Instanzen.

Die Lernmethoden sind in der Datenbank definiert und werden zur Laufzeit geladen.
Es gibt mehrere Gruppen von Lernmethoden:
- Gruppe A: Erklärende Methoden (für Verständnis & Wissensaufbau)
- Gruppe B: Praxis-Methoden (für Anwenden & Trainieren)
- Gruppe C: Prüfungs-Methoden (für Kompetenznachweis & Bewertung)

Erstelle Content, der zur jeweiligen Methode passt.
Passe den Content an die spezifischen Anforderungen der Lernmethode an.
Wenn du Content generierst, gib ihn als JSON aus.

Antworte auf Deutsch."""


# ==============================================================================
# USER PROMPT TEMPLATE - Learning Method
# ==============================================================================

USER_PROMPT_LEARNING_METHOD: str = """Kontext:
- Kurs: {course_info[title]}
- Kapitel: {chapter_info[title]}
- Lektion: {lesson_info[title]}

Datei-Kontext (falls vorhanden):
{file_context}

Bisherige Konversation:
{conversation_history}

Aktuelle Anfrage:
{user_message}

Generiere Content für die angeforderte Lernmethode."""
