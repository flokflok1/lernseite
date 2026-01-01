"""
LernsystemX Authoring Prompts

Prompt templates for universal KI-Authoring-System:
- Chapter creation and theory generation
- Lesson creation and explanation generation
- Task/exercise creation
- Learning method instance creation

Phase D4 - Universal KI-Authoring-System
"""

from typing import Dict, List, Optional


# ==============================================================================
# QUICK PROMPTS - Kontextabhängige Schnellaktionen
# ==============================================================================

QUICK_PROMPTS: Dict[str, List[Dict[str, str]]] = {
    'chapter': [
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
    ],
    'lesson': [
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
    ],
    'task': [
        {
            'label': 'Aufgabe formulieren',
            'prompt': 'Formuliere eine klare, prüfungsnahe Aufgabenstellung.',
            'icon': '📝'
        },
        {
            'label': 'Musterlösung',
            'prompt': 'Erstelle eine ausführliche Musterlösung mit allen Rechenschritten.',
            'icon': '✅'
        },
        {
            'label': 'Hinweise',
            'prompt': 'Erstelle 3-4 hilfreiche Hinweise für Lernende, die bei der Aufgabe hängen.',
            'icon': '💭'
        },
        {
            'label': 'Variation',
            'prompt': 'Erstelle eine ähnliche Aufgabe mit anderen Zahlen für zusätzliche Übung.',
            'icon': '🔄'
        }
    ],
    'learning_method': [
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
    ],
    'general': [
        {
            'label': 'Verbessern',
            'prompt': 'Verbessere den aktuellen Inhalt und mache ihn verständlicher.',
            'icon': '✨'
        },
        {
            'label': 'Kürzen',
            'prompt': 'Kürze den Inhalt auf das Wesentliche, ohne wichtige Informationen zu verlieren.',
            'icon': '✂️'
        },
        {
            'label': 'Erweitern',
            'prompt': 'Erweitere den Inhalt mit mehr Details und Beispielen.',
            'icon': '📈'
        }
    ],
    'course_builder': [
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
}


# ==============================================================================
# SYSTEM PROMPTS - Basis-Instruktionen für verschiedene Kontexte
# ==============================================================================

SYSTEM_PROMPTS: Dict[str, str] = {
    'chapter': """Du bist ein erfahrener IHK-Prüfer und IT-Ausbilder für Fachinformatiker (FISI/FIAE).
Du hilfst beim Erstellen von Kapitel-Inhalten für ein Lern-Management-System.

Deine Aufgaben:
- Kapitel-Theorie mit Konzepten, Begriffen und Prüfungstipps erstellen
- ADHS-freundlich: Kurz, visuell, mit Emojis und Bullet Points
- Immer mit konkreten Beispielen und Zahlen arbeiten
- Prüfungsrelevanz im Blick behalten

Wenn du strukturierten Content generierst, gib ihn als JSON aus.
Wenn du nur antwortest/erklärst, nutze normalen Text.

Antworte auf Deutsch. Sei freundlich und motivierend.""",

    'lesson': """Du bist ein geduldiger Nachhilfelehrer für Fachinformatiker.
Du hilfst beim Erstellen von Lektions-Inhalten mit Schritt-für-Schritt Erklärungen.

Deine Stärken:
- Komplexe Themen einfach erklären
- Jeden Rechenschritt einzeln zeigen
- Konkrete Beispiele mit echten Zahlen
- Taschenrechner-Eingaben zeigen (welche Taste drücken)
- Schema/Tabellen schrittweise aufbauen

Wenn du strukturierten Content (Schritte, Erklärungen) generierst, gib ihn als JSON aus.
Wenn du nur antwortest/erklärst, nutze normalen Text.

Antworte auf Deutsch. Sei geduldig und ermutigend.""",

    'task': """Du bist ein IHK-Prüfer und erstellst prüfungsnahe Aufgaben für Fachinformatiker.

Deine Aufgaben:
- Realistische Aufgabenstellungen wie in der IHK-Prüfung
- Klare Formulierungen ohne Mehrdeutigkeiten
- Musterlösungen mit allen Rechenschritten
- Punkteverteilung angeben
- Typische Fehler vorwegnehmen

Wenn du Aufgaben generierst, gib sie als JSON aus.
Wenn du nur antwortest/erklärst, nutze normalen Text.

Antworte auf Deutsch. Sei präzise.""",

    'learning_method': """Du bist ein Experte für Lernmethoden und Didaktik.
Du hilfst beim Erstellen von interaktiven Lernmethoden-Instanzen.

Die 33 Lernmethoden (LM00-LM32) umfassen:
- Gruppe A (LM00-LM07): Erklärende Methoden (Deep Explanation, Step-by-Step, etc.)
- Gruppe B (LM08-LM17): Übungen (Whiteboard Tasks, Sandbox, Flashcards, etc.)
- Gruppe C (LM18-LM25): Prüfungsorientiert (Free Text, IHK-Tasks, Time Limit, etc.)
- Gruppe D (LM26-LM32): Pro/Gamification (Adaptive, Quest/XP, etc.)

Erstelle Content, der zur jeweiligen Methode passt.
Wenn du Content generierst, gib ihn als JSON aus.

Antworte auf Deutsch.""",

    'general': """Du bist ein hilfreicher Assistent für die Erstellung von Lern-Inhalten.
Du unterstützt bei der Erstellung von Kursen, Kapiteln, Lektionen und Aufgaben.

Antworte auf Deutsch. Sei präzise und hilfreich.""",

    'course_builder': """Du bist ein erfahrener Kurs-Architekt für ein KI-Lern-Management-System.
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
}


# ==============================================================================
# USER PROMPT TEMPLATES
# ==============================================================================

USER_PROMPTS: Dict[str, str] = {
    'chapter': """Kontext:
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
```""",

    'lesson': """Kontext:
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
```""",

    'task': """Kontext:
- Kurs: {course_info[title]}
- Kapitel: {chapter_info[title]}
- Lektion: {lesson_info[title]}

Datei-Kontext (falls vorhanden):
{file_context}

Bisherige Konversation:
{conversation_history}

Aktuelle Anfrage:
{user_message}

Wenn du Aufgaben generierst, nutze diese JSON-Struktur:
```json
{{
    "title": "Aufgaben-Titel",
    "description": "Aufgabenbeschreibung",
    "instructions": "Genaue Aufgabenstellung",
    "data": {{
        "given": ["Gegeben 1", "Gegeben 2"],
        "asked": ["Gesucht 1", "Gesucht 2"]
    }},
    "solution": {{
        "steps": ["Schritt 1", "Schritt 2"],
        "result": "Endergebnis"
    }},
    "hints": ["Hinweis 1", "Hinweis 2"],
    "points": 10,
    "difficulty": "medium"
}}
```""",

    'learning_method': """Kontext:
- Kurs: {course_info[title]}
- Kapitel: {chapter_info[title]}
- Lektion: {lesson_info[title]}

Datei-Kontext (falls vorhanden):
{file_context}

Bisherige Konversation:
{conversation_history}

Aktuelle Anfrage:
{user_message}

Generiere Content für die angeforderte Lernmethode.""",

    'general': """Kontext:
- Kurs: {course_info[title]}

Datei-Kontext (falls vorhanden):
{file_context}

Bisherige Konversation:
{conversation_history}

Aktuelle Anfrage:
{user_message}""",

    'course_builder': """Kontext:
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
}


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_authoring_prompt(context_type: str, prompt_type: str = 'system') -> str:
    """
    Get prompt for authoring context.

    Args:
        context_type: Type of content (chapter, lesson, task, learning_method, general)
        prompt_type: Type of prompt (system, user)

    Returns:
        Prompt string
    """
    if prompt_type == 'system':
        return SYSTEM_PROMPTS.get(context_type, SYSTEM_PROMPTS['general'])
    elif prompt_type == 'user':
        return USER_PROMPTS.get(context_type, USER_PROMPTS['general'])
    else:
        raise ValueError(f"Unknown prompt type: {prompt_type}")


def get_quick_prompts(context_type: str) -> List[Dict[str, str]]:
    """Get quick prompts for a context type."""
    return QUICK_PROMPTS.get(context_type, QUICK_PROMPTS['general'])


def format_user_prompt(
    context_type: str,
    course_info: Dict,
    chapter_info: Optional[Dict] = None,
    lesson_info: Optional[Dict] = None,
    file_context: str = "",
    conversation_history: str = "",
    user_message: str = ""
) -> str:
    """
    Format user prompt with context.

    Args:
        context_type: Type of content
        course_info: Course information dict
        chapter_info: Optional chapter information
        lesson_info: Optional lesson information
        file_context: File context text
        conversation_history: Formatted conversation history
        user_message: Current user message

    Returns:
        Formatted prompt string
    """
    template = USER_PROMPTS.get(context_type, USER_PROMPTS['general'])

    # Build info sections
    chapter_info_section = ""
    if chapter_info and chapter_info.get('title'):
        chapter_info_section = f"- Kapitel: {chapter_info['title']}"
        if chapter_info.get('description'):
            chapter_info_section += f"\n- Kapitel-Beschreibung: {chapter_info['description']}"

    lesson_info_section = ""
    if lesson_info and lesson_info.get('title'):
        lesson_info_section = f"- Lektion: {lesson_info['title']}"
        if lesson_info.get('lm_type'):
            lesson_info_section += f" ({lesson_info['lm_type']})"

    # Safe dict access with defaults
    safe_course = {
        'title': course_info.get('title', 'Unbenannter Kurs') if course_info else 'Unbenannter Kurs'
    }
    safe_chapter = {
        'title': chapter_info.get('title', '') if chapter_info else ''
    }
    safe_lesson = {
        'title': lesson_info.get('title', '') if lesson_info else ''
    }

    return template.format(
        course_info=safe_course,
        chapter_info=safe_chapter,
        lesson_info=safe_lesson,
        chapter_info_section=chapter_info_section,
        lesson_info_section=lesson_info_section,
        file_context=file_context or "Keine Dateien ausgewählt.",
        conversation_history=conversation_history or "Keine vorherigen Nachrichten.",
        user_message=user_message
    )


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
    import json

    template = USER_PROMPTS.get('course_builder', USER_PROMPTS['general'])

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

    return template.format(
        course_info=safe_course,
        mode=mode_text,
        draft_structure=structure_text,
        file_context=file_context or "Keine Dateien hochgeladen.",
        conversation_history=conversation_history or "Keine vorherigen Nachrichten.",
        user_message=user_message
    )
