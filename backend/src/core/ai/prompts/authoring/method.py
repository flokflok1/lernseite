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

Die 33 Lernmethoden (LM00-LM32) umfassen:
- Gruppe A (LM00-LM07): Erklärende Methoden (Deep Explanation, Step-by-Step, etc.)
- Gruppe B (LM08-LM17): Übungen (Whiteboard Tasks, Sandbox, Flashcards, etc.)
- Gruppe C (LM18-LM25): Prüfungsorientiert (Free Text, IHK-Tasks, Time Limit, etc.)
- Gruppe D (LM26-LM32): Pro/Gamification (Adaptive, Quest/XP, etc.)

Erstelle Content, der zur jeweiligen Methode passt.
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
