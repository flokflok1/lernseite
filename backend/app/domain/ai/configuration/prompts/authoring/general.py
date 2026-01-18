"""
General Authoring Prompts

General prompts, task prompts, and shared helper functions.
"""

from typing import Dict, List, Optional


# ==============================================================================
# QUICK PROMPTS - Task Context
# ==============================================================================

QUICK_PROMPTS_TASK: List[Dict[str, str]] = [
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
]


# ==============================================================================
# QUICK PROMPTS - General Context
# ==============================================================================

QUICK_PROMPTS_GENERAL: List[Dict[str, str]] = [
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
]


# ==============================================================================
# SYSTEM PROMPTS - Task & General
# ==============================================================================

SYSTEM_PROMPT_TASK: str = """Du bist ein IHK-Prüfer und erstellst prüfungsnahe Aufgaben für Fachinformatiker.

Deine Aufgaben:
- Realistische Aufgabenstellungen wie in der IHK-Prüfung
- Klare Formulierungen ohne Mehrdeutigkeiten
- Musterlösungen mit allen Rechenschritten
- Punkteverteilung angeben
- Typische Fehler vorwegnehmen

Wenn du Aufgaben generierst, gib sie als JSON aus.
Wenn du nur antwortest/erklärst, nutze normalen Text.

Antworte auf Deutsch. Sei präzise."""


SYSTEM_PROMPT_GENERAL: str = """Du bist ein hilfreicher Assistent für die Erstellung von Lern-Inhalten.
Du unterstützt bei der Erstellung von Kursen, Kapiteln, Lektionen und Aufgaben.

Antworte auf Deutsch. Sei präzise und hilfreich."""


# ==============================================================================
# USER PROMPT TEMPLATES - Task & General
# ==============================================================================

USER_PROMPT_TASK: str = """Kontext:
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
```"""


USER_PROMPT_GENERAL: str = """Kontext:
- Kurs: {course_info[title]}

Datei-Kontext (falls vorhanden):
{file_context}

Bisherige Konversation:
{conversation_history}

Aktuelle Anfrage:
{user_message}"""


# ==============================================================================
# BACKWARD COMPATIBILITY - QUICK_PROMPTS DICT
# ==============================================================================

def _build_quick_prompts_dict() -> Dict[str, List[Dict[str, str]]]:
    """Build unified QUICK_PROMPTS dict for backward compatibility."""
    from .chapter import QUICK_PROMPTS_CHAPTER
    from .lesson import QUICK_PROMPTS_LESSON
    from .method import QUICK_PROMPTS_LEARNING_METHOD
    from .course import QUICK_PROMPTS_COURSE_BUILDER

    return {
        'chapter': QUICK_PROMPTS_CHAPTER,
        'lesson': QUICK_PROMPTS_LESSON,
        'task': QUICK_PROMPTS_TASK,
        'learning_method': QUICK_PROMPTS_LEARNING_METHOD,
        'general': QUICK_PROMPTS_GENERAL,
        'course_builder': QUICK_PROMPTS_COURSE_BUILDER
    }


# Lazy-loaded for backward compatibility
QUICK_PROMPTS: Dict[str, List[Dict[str, str]]] = _build_quick_prompts_dict()


def _build_system_prompts_dict() -> Dict[str, str]:
    """Build unified SYSTEM_PROMPTS dict for backward compatibility."""
    from .chapter import SYSTEM_PROMPT_CHAPTER
    from .lesson import SYSTEM_PROMPT_LESSON
    from .method import SYSTEM_PROMPT_LEARNING_METHOD
    from .course import SYSTEM_PROMPT_COURSE_BUILDER

    return {
        'chapter': SYSTEM_PROMPT_CHAPTER,
        'lesson': SYSTEM_PROMPT_LESSON,
        'task': SYSTEM_PROMPT_TASK,
        'learning_method': SYSTEM_PROMPT_LEARNING_METHOD,
        'general': SYSTEM_PROMPT_GENERAL,
        'course_builder': SYSTEM_PROMPT_COURSE_BUILDER
    }


def _build_user_prompts_dict() -> Dict[str, str]:
    """Build unified USER_PROMPTS dict for backward compatibility."""
    from .chapter import USER_PROMPT_CHAPTER
    from .lesson import USER_PROMPT_LESSON
    from .method import USER_PROMPT_LEARNING_METHOD
    from .course import USER_PROMPT_COURSE_BUILDER

    return {
        'chapter': USER_PROMPT_CHAPTER,
        'lesson': USER_PROMPT_LESSON,
        'task': USER_PROMPT_TASK,
        'learning_method': USER_PROMPT_LEARNING_METHOD,
        'general': USER_PROMPT_GENERAL,
        'course_builder': USER_PROMPT_COURSE_BUILDER
    }


# Backward compatibility dicts
SYSTEM_PROMPTS: Dict[str, str] = _build_system_prompts_dict()
USER_PROMPTS: Dict[str, str] = _build_user_prompts_dict()


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
    from .chapter import SYSTEM_PROMPT_CHAPTER, USER_PROMPT_CHAPTER
    from .lesson import SYSTEM_PROMPT_LESSON, USER_PROMPT_LESSON
    from .method import SYSTEM_PROMPT_LEARNING_METHOD, USER_PROMPT_LEARNING_METHOD
    from .course import SYSTEM_PROMPT_COURSE_BUILDER, USER_PROMPT_COURSE_BUILDER

    SYSTEM_PROMPTS = {
        'chapter': SYSTEM_PROMPT_CHAPTER,
        'lesson': SYSTEM_PROMPT_LESSON,
        'task': SYSTEM_PROMPT_TASK,
        'learning_method': SYSTEM_PROMPT_LEARNING_METHOD,
        'general': SYSTEM_PROMPT_GENERAL,
        'course_builder': SYSTEM_PROMPT_COURSE_BUILDER
    }

    USER_PROMPTS = {
        'chapter': USER_PROMPT_CHAPTER,
        'lesson': USER_PROMPT_LESSON,
        'task': USER_PROMPT_TASK,
        'learning_method': USER_PROMPT_LEARNING_METHOD,
        'general': USER_PROMPT_GENERAL,
        'course_builder': USER_PROMPT_COURSE_BUILDER
    }

    if prompt_type == 'system':
        return SYSTEM_PROMPTS.get(context_type, SYSTEM_PROMPTS['general'])
    elif prompt_type == 'user':
        return USER_PROMPTS.get(context_type, USER_PROMPTS['general'])
    else:
        raise ValueError(f"Unknown prompt type: {prompt_type}")


def get_quick_prompts(context_type: str) -> List[Dict[str, str]]:
    """Get quick prompts for a context type."""
    from .chapter import QUICK_PROMPTS_CHAPTER
    from .lesson import QUICK_PROMPTS_LESSON
    from .method import QUICK_PROMPTS_LEARNING_METHOD
    from .course import QUICK_PROMPTS_COURSE_BUILDER

    QUICK_PROMPTS = {
        'chapter': QUICK_PROMPTS_CHAPTER,
        'lesson': QUICK_PROMPTS_LESSON,
        'task': QUICK_PROMPTS_TASK,
        'learning_method': QUICK_PROMPTS_LEARNING_METHOD,
        'general': QUICK_PROMPTS_GENERAL,
        'course_builder': QUICK_PROMPTS_COURSE_BUILDER
    }

    return QUICK_PROMPTS.get(context_type, QUICK_PROMPTS_GENERAL)


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
    from .chapter import USER_PROMPT_CHAPTER
    from .lesson import USER_PROMPT_LESSON
    from .method import USER_PROMPT_LEARNING_METHOD

    USER_PROMPTS = {
        'chapter': USER_PROMPT_CHAPTER,
        'lesson': USER_PROMPT_LESSON,
        'task': USER_PROMPT_TASK,
        'learning_method': USER_PROMPT_LEARNING_METHOD,
        'general': USER_PROMPT_GENERAL
    }

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
