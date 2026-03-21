"""
Tool-Definitionen für AI Editor Course Authoring.

Provider-agnostische Schemas — beschreiben WAS die KI tun kann.
Die Konvertierung ins Provider-Format (OpenAI/Anthropic/Google)
passiert in infrastructure/ai/tool_formatters.py.

Jedes Tool entspricht einer Authoring-Operation mit JSON Schema
für required/optional Felder.
"""

from typing import Dict, List


# ============================================================================
# Kapitel-Tools
# ============================================================================

TOOL_ADD_CHAPTER: Dict = {
    "name": "add_chapter",
    "description": (
        "Erstellt ein neues Kapitel im Kurs. "
        "Verwende eine temporäre ID für Referenzen in nachfolgenden Operationen."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "Temporäre ID (z.B. 'ch-001') für Referenzen"
            },
            "title": {
                "type": "string",
                "description": "Kapitel-Titel"
            },
            "description": {
                "type": "string",
                "description": "Kurze Beschreibung des Kapitelinhalts"
            }
        },
        "required": ["title"]
    }
}

TOOL_UPDATE_CHAPTER: Dict = {
    "name": "update_chapter",
    "description": "Aktualisiert ein bestehendes Kapitel (Titel und/oder Beschreibung).",
    "parameters": {
        "type": "object",
        "properties": {
            "chapter_id": {
                "type": "string",
                "description": "ID des zu ändernden Kapitels (aus aktueller Struktur)"
            },
            "title": {"type": "string"},
            "description": {"type": "string"}
        },
        "required": ["chapter_id"]
    }
}

TOOL_DELETE_CHAPTER: Dict = {
    "name": "delete_chapter",
    "description": "Löscht ein Kapitel und alle enthaltenen Lektionen/Methoden.",
    "parameters": {
        "type": "object",
        "properties": {
            "chapter_id": {
                "type": "string",
                "description": "ID des zu löschenden Kapitels"
            }
        },
        "required": ["chapter_id"]
    }
}

# ============================================================================
# Lektions-Tools
# ============================================================================

TOOL_ADD_LESSON: Dict = {
    "name": "add_lesson",
    "description": (
        "Erstellt eine neue Lektion in einem Kapitel. "
        "content.content_html MUSS vollständigen HTML-Inhalt enthalten."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "chapter_id": {
                "type": "string",
                "description": "ID des Kapitels, in dem die Lektion erstellt wird"
            },
            "id": {
                "type": "string",
                "description": "Temporäre ID (z.B. 'ls-001')"
            },
            "title": {
                "type": "string",
                "description": "Lektions-Titel"
            },
            "type": {
                "type": "string",
                "enum": ["text"],
                "description": "Lektions-Typ (aktuell nur 'text')"
            },
            "content": {
                "type": "object",
                "description": "Lektions-Inhalt mit Theorieblatt",
                "properties": {
                    "content_html": {
                        "type": "string",
                        "description": "Vollständiger HTML-Inhalt der Lektion"
                    }
                },
                "required": ["content_html"]
            }
        },
        "required": ["chapter_id", "title", "content"]
    }
}

TOOL_UPDATE_LESSON: Dict = {
    "name": "update_lesson",
    "description": (
        "Aktualisiert eine bestehende Lektion. "
        "content.content_html ist PFLICHT — immer den vollständigen Theorieblatt-Inhalt liefern. "
        "Das Theorieblatt ist die Hauptzusammenfassung, die der Lernende sieht."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "lesson_id": {
                "type": "string",
                "description": "ID der zu ändernden Lektion (aus aktueller Struktur)"
            },
            "title": {"type": "string"},
            "type": {
                "type": "string",
                "enum": ["text"]
            },
            "content": {
                "type": "object",
                "description": "Neuer Lektions-Inhalt",
                "properties": {
                    "content_html": {
                        "type": "string",
                        "description": "Vollständiger HTML-Inhalt des Theorieblatts"
                    }
                },
                "required": ["content_html"]
            }
        },
        "required": ["lesson_id", "content"]
    }
}

TOOL_DELETE_LESSON: Dict = {
    "name": "delete_lesson",
    "description": "Löscht eine Lektion und alle zugehörigen Methoden.",
    "parameters": {
        "type": "object",
        "properties": {
            "lesson_id": {
                "type": "string",
                "description": "ID der zu löschenden Lektion"
            }
        },
        "required": ["lesson_id"]
    }
}

# ============================================================================
# Methoden-Tools
# ============================================================================

VALID_METHOD_TYPES = [
    "theory", "step_by_step", "interactive",
    "quiz", "flashcards", "exercise",
    "exam", "calculator_tutorial", "tool_tutorial",
    "video", "drag_and_drop", "cloze",
]

TOOL_ADD_METHOD: Dict = {
    "name": "add_method",
    "description": (
        "Fügt eine Lernmethode zu einer Lektion hinzu. "
        "content muss vollständige Daten enthalten (keine Platzhalter). "
        "Beispiel Quiz: content.questions mit Fragen+Optionen+Antworten. "
        "Beispiel Theorie: content.text mit Erklärungstext. "
        "Beispiel Flashcards: content.cards mit front/back Paaren."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "lesson_id": {
                "type": "string",
                "description": "ID der Lektion"
            },
            "id": {
                "type": "string",
                "description": "Temporäre ID (z.B. 'mt-001')"
            },
            "type": {
                "type": "string",
                "enum": VALID_METHOD_TYPES,
                "description": "Lernmethoden-Typ"
            },
            "title": {
                "type": "string",
                "description": "Titel der Lernmethode"
            },
            "content": {
                "type": "object",
                "description": "Methoden-Inhalt (Schema variiert je nach Typ)"
            },
            "solution": {
                "type": "object",
                "description": (
                    "Lösung/Musterlösung für Übungsaufgaben. "
                    "Für exercise: {modelAnswer: string, keyPoints: string[]}. "
                    "Für quiz: nicht nötig (correct-Index reicht)."
                )
            }
        },
        "required": ["lesson_id", "type", "title", "content"]
    }
}

TOOL_UPDATE_METHOD: Dict = {
    "name": "update_method",
    "description": "Aktualisiert eine bestehende Lernmethode.",
    "parameters": {
        "type": "object",
        "properties": {
            "method_id": {
                "type": "string",
                "description": "ID der zu ändernden Methode (aus aktueller Struktur)"
            },
            "type": {
                "type": "string",
                "enum": VALID_METHOD_TYPES
            },
            "title": {"type": "string"},
            "content": {
                "type": "object",
                "description": "Neuer Methoden-Inhalt"
            },
            "solution": {
                "type": "object",
                "description": "Neue Lösung/Musterlösung (optional)"
            }
        },
        "required": ["method_id"]
    }
}

TOOL_DELETE_METHOD: Dict = {
    "name": "delete_method",
    "description": "Löscht eine Lernmethode aus einer Lektion.",
    "parameters": {
        "type": "object",
        "properties": {
            "method_id": {
                "type": "string",
                "description": "ID der zu löschenden Methode"
            }
        },
        "required": ["method_id"]
    }
}

# ============================================================================
# Sortierungs-Tools
# ============================================================================

TOOL_REORDER_CHAPTERS: Dict = {
    "name": "reorder_chapters",
    "description": "Ändert die Reihenfolge der Kapitel im Kurs.",
    "parameters": {
        "type": "object",
        "properties": {
            "order": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Kapitel-IDs in neuer Reihenfolge"
            }
        },
        "required": ["order"]
    }
}

TOOL_REORDER_LESSONS: Dict = {
    "name": "reorder_lessons",
    "description": "Ändert die Reihenfolge der Lektionen in einem Kapitel.",
    "parameters": {
        "type": "object",
        "properties": {
            "chapter_id": {
                "type": "string",
                "description": "ID des Kapitels"
            },
            "order": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Lektions-IDs in neuer Reihenfolge"
            }
        },
        "required": ["chapter_id", "order"]
    }
}

# ============================================================================
# Gesamtliste aller Authoring-Tools
# ============================================================================

AUTHORING_TOOLS: List[Dict] = [
    TOOL_ADD_CHAPTER,
    TOOL_UPDATE_CHAPTER,
    TOOL_DELETE_CHAPTER,
    TOOL_ADD_LESSON,
    TOOL_UPDATE_LESSON,
    TOOL_DELETE_LESSON,
    TOOL_ADD_METHOD,
    TOOL_UPDATE_METHOD,
    TOOL_DELETE_METHOD,
    TOOL_REORDER_CHAPTERS,
    TOOL_REORDER_LESSONS,
]

# Tool-Namen Set für schnelle Lookups
TOOL_NAMES = {t["name"] for t in AUTHORING_TOOLS}
