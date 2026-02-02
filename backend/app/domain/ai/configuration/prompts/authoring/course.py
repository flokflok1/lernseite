"""
Course-Level Authoring Prompts

Prompts for course builder and course-level content generation.
"""

from typing import Dict, List
import json


# ==============================================================================
# QUICK PROMPTS - Course Builder Context
# ==============================================================================

QUICK_PROMPTS_COURSE_BUILDER: List[Dict[str, str]] = [
    {
        'label': 'Struktur vorschlagen',
        'prompt': 'Analysiere das Kursmaterial und schlage eine passende Kapitelstruktur vor.',
        'icon': '📋',
        'mode': 'structure'
    },
    {
        'label': '3 Kapitel erstellen',
        'prompt': 'Erstelle 3 Kapitel mit je 3-5 Lektionen basierend auf dem Kursmaterial.',
        'icon': '📚',
        'mode': 'structure'
    },
    {
        'label': 'Taschenrechner-Tutorial',
        'prompt': 'Erstelle ein Taschenrechner-Tutorial für das aktuelle Thema mit Casio fx-991.',
        'icon': '🧮',
        'mode': 'calculator'
    },
    {
        'label': 'Prüfung generieren',
        'prompt': 'Generiere IHK-Stil Prüfungsfragen basierend auf den vorhandenen Kapiteln.',
        'icon': '🎓',
        'mode': 'exam'
    },
    {
        'label': 'Flashcards erstellen',
        'prompt': 'Erstelle Karteikarten für die wichtigsten Begriffe und Definitionen.',
        'icon': '🗂️',
        'mode': 'method'
    },
    {
        'label': 'Quiz hinzufügen',
        'prompt': 'Füge Verständnis-Quizzes zu allen Lektionen hinzu.',
        'icon': '❓',
        'mode': 'method'
    }
]


# ==============================================================================
# SYSTEM PROMPT - Course Builder
# ==============================================================================

SYSTEM_PROMPT_COURSE_BUILDER: str = """Du bist ein erfahrener Kurs-Architekt für ein KI-Lern-Management-System.
Du hilfst beim strukturierten Aufbau von Kursen durch Chat-basierte Interaktion.

Deine Aufgaben:
- Kursstrukturen (Kapitel, Lektionen, Lernmethoden) planen und erstellen
- Basierend auf hochgeladenen Dokumenten (PDFs, Skripten) passende Inhalte extrahieren
- Prüfungsrelevante Themen identifizieren und strukturieren
- IHK-konforme Lernpfade entwickeln

Du kannst folgende Operationen durchführen:
- add_chapter: Neues Kapitel hinzufügen
- update_chapter: Kapitel aktualisieren
- delete_chapter: Kapitel entfernen
- add_lesson: Neue Lektion zu einem Kapitel hinzufügen
- update_lesson: Lektion aktualisieren
- delete_lesson: Lektion entfernen
- add_method: Neue Lernmethode zu einer Lektion hinzufügen
- update_method: Lernmethode aktualisieren
- delete_method: Lernmethode entfernen

Verfügbare Lernmethoden-Typen:
- calculator_tutorial (LM01): Taschenrechner-Tutorial mit Schritt-für-Schritt Anleitung
- tool_tutorial (LM09): Software/Tool-Anleitung (z.B. CLI, IDE)
- step_by_step (LM01): Prozess-Anleitung mit Schema-Aufbau
- theory (LM00): Strukturierte Theorie mit Konzepten
- quiz (LM22): Multiple-Choice Verständnisfragen
- flashcards (LM13): Lernkarten für Begriffe
- exercise (LM08): Praktische Übungsaufgabe
- exam (LM19): IHK-Stil Prüfungssimulation

Wenn du Strukturänderungen vornimmst, antworte IMMER mit einem JSON-Block:
```json
{
    "message": "Kurze Erklärung was du gemacht hast",
    "operations": [
        {
            "type": "add_chapter|update_chapter|delete_chapter|add_lesson|update_lesson|delete_lesson|add_method|update_method|delete_method",
            "data": {...}
        }
    ]
}
```

Wenn du nur antwortest/erklärst ohne Änderungen, nutze normalen Text.

Antworte auf Deutsch. Sei strukturiert und effizient."""


# ==============================================================================
# USER PROMPT TEMPLATE - Course Builder
# ==============================================================================

USER_PROMPT_COURSE_BUILDER: str = """Kontext:
- Kurs: {course_info[title]}
- Kurs-Beschreibung: {course_info[description]}
- Aktueller Modus: {mode}

Aktuelle Draft-Struktur:
{draft_structure}

Datei-Kontext (falls vorhanden):
{file_context}

Bisherige Konversation (letzte 5 Nachrichten):
{conversation_history}

Benutzer-Nachricht:
{user_message}

Wenn du Änderungen an der Kursstruktur vornimmst, antworte mit JSON wie im System-Prompt beschrieben.
Wenn du nur erklärst oder Fragen beantwortest, antworte mit normalem Text."""


# ==============================================================================
# HELPER FUNCTION
# ==============================================================================

def format_course_builder_prompt(
    course_info: Dict,
    draft_structure: Dict,
    mode: str = "auto",
    file_context: str = "",
    conversation_history: str = "",
    user_message: str = ""
) -> str:
    """
    Format user prompt for course builder context.

    Args:
        course_info: Course information dict with title and description
        draft_structure: Current draft structure (chapters, lessons, methods)
        mode: Current mode (structure, lesson, method, exam, calculator, auto)
        file_context: Extracted text from uploaded files
        conversation_history: Last 5 messages formatted
        user_message: Current user message

    Returns:
        Formatted prompt string
    """
    # Safe course info
    safe_course = {
        'title': course_info.get('title', 'Unbenannter Kurs') if course_info else 'Unbenannter Kurs',
        'description': course_info.get('description', 'Keine Beschreibung') if course_info else 'Keine Beschreibung'
    }

    # Format draft structure as readable JSON
    structure_text = "Keine Struktur vorhanden."
    if draft_structure and draft_structure.get('chapters'):
        try:
            structure_text = json.dumps(draft_structure, ensure_ascii=False, indent=2)
        except Exception:
            structure_text = str(draft_structure)

    # Mode descriptions
    mode_labels = {
        'auto': 'Automatisch (basierend auf Kontext)',
        'structure': 'Struktur-Modus (Kapitel und Lektionen)',
        'lesson': 'Lektions-Modus (Inhalte generieren)',
        'method': 'Methoden-Modus (Lernmethoden hinzufügen)',
        'exam': 'Prüfungs-Modus (IHK-Aufgaben)',
        'calculator': 'Taschenrechner-Modus (Tutorials)'
    }
    mode_text = mode_labels.get(mode, mode)

    return USER_PROMPT_COURSE_BUILDER.format(
        course_info=safe_course,
        mode=mode_text,
        draft_structure=structure_text,
        file_context=file_context or "Keine Dateien hochgeladen.",
        conversation_history=conversation_history or "Keine vorherigen Nachrichten.",
        user_message=user_message
    )
