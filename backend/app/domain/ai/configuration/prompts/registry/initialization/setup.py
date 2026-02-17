"""
LernsystemX KI - Prompt Registry Initialization

Default prompt templates initialization for standard learning methods.
"""

import logging

from app.domain.ai.configuration.prompt_models import PromptTemplate, PromptMessage, PromptVariable

logger = logging.getLogger(__name__)
from ..core.registry import PROMPT_REGISTRY, register_prompt


def init_default_prompts() -> None:
    """
    Initialize default prompt templates for standard learning methods.

    Registers templates for:
    - explain_concept: Explain concepts with examples
    - flashcards: Generate flashcard Q&A pairs
    - quiz_generator: Create multiple-choice quizzes
    - socratic_tutor: Socratic dialogue learning
    - summarize_lesson: Summarize lesson content
    - translation_assistant: Translate educational content

    Called during application initialization.
    """
    logger.info("Initializing default prompt templates...")

    # ========================================================================
    # 1. EXPLAIN CONCEPT
    # ========================================================================
    explain_concept = PromptTemplate(
        code="explain_concept",
        title="Konzept Erklärung",
        description=(
            "Erklärt ein Konzept schrittweise mit verständlichen Beispielen. "
            "Passt sich an das Wissenslevel des Lernenden an."
        ),
        version=1,
        tags=["learning", "explanation", "concept", "beginner-friendly"],
        messages=[
            PromptMessage(
                role="system",
                content=(
                    "Du bist ein erfahrener KI-Tutor für {{course_title}}. "
                    "Dein Ziel ist es, Konzepte klar, verständlich und präzise zu erklären. "
                    "Nutze Beispiele und Analogien, um komplexe Themen zugänglich zu machen. "
                    "Passe deine Erklärung an das Wissenslevel '{{user_level}}' an."
                )
            ),
            PromptMessage(
                role="user",
                content=(
                    "Erkläre folgendes Konzept aus der Lektion '{{lesson_title}}':\n\n"
                    "{{concept_text}}\n\n"
                    "Strukturiere deine Erklärung so:\n"
                    "1. Kurze Definition\n"
                    "2. Wichtigste Merkmale\n"
                    "3. Praktische Beispiele\n"
                    "4. Häufige Missverständnisse (falls relevant)"
                )
            )
        ],
        variables=[
            PromptVariable(
                name="course_title",
                description="Titel des Kurses",
                required=True
            ),
            PromptVariable(
                name="lesson_title",
                description="Titel der aktuellen Lektion",
                required=True
            ),
            PromptVariable(
                name="concept_text",
                description="Der zu erklärende Konzepttext oder Begriff",
                required=True
            ),
            PromptVariable(
                name="user_level",
                description="Wissenslevel des Lernenden (beginner/intermediate/advanced)",
                required=False,
                default="intermediate"
            )
        ],
        model="claude-3-sonnet-20240229",
        max_tokens=2000,
        temperature=0.7,
        language_mode="target",
        allowed_roles=["student", "teacher", "admin"],
        created_by="system"
    )
    register_prompt(explain_concept)

    # ========================================================================
    # 2. FLASHCARDS
    # ========================================================================
    flashcards = PromptTemplate(
        code="flashcards",
        title="Karteikarten Generator",
        description=(
            "Generiert Frage-Antwort-Paare (Flashcards) aus Lektionsinhalten. "
            "Fokussiert auf wichtige Konzepte, Definitionen und Zusammenhänge."
        ),
        version=1,
        tags=["learning", "flashcards", "memorization", "quiz"],
        messages=[
            PromptMessage(
                role="system",
                content=(
                    "Du bist ein KI-Assistent spezialisiert auf die Erstellung von Lernkarten (Flashcards) "
                    "für den Kurs '{{course_title}}'. "
                    "Erstelle präzise Fragen und klare, prägnante Antworten. "
                    "Fokussiere auf zentrale Konzepte, Definitionen und wichtige Zusammenhänge."
                )
            ),
            PromptMessage(
                role="user",
                content=(
                    "Erstelle {{num_flashcards}} Flashcards basierend auf folgendem Lektionsinhalt:\n\n"
                    "Lektion: {{lesson_title}}\n\n"
                    "Inhalt:\n{{lesson_content}}\n\n"
                    "Ausgabeformat (JSON):\n"
                    "{\n"
                    '  "flashcards": [\n'
                    "    {\n"
                    '      "question": "Frage hier",\n'
                    '      "answer": "Antwort hier",\n'
                    '      "difficulty": "easy|medium|hard"\n'
                    "    }\n"
                    "  ]\n"
                    "}"
                )
            )
        ],
        variables=[
            PromptVariable(
                name="course_title",
                description="Titel des Kurses",
                required=True
            ),
            PromptVariable(
                name="lesson_title",
                description="Titel der Lektion",
                required=True
            ),
            PromptVariable(
                name="lesson_content",
                description="Vollständiger Lektionsinhalt",
                required=True
            ),
            PromptVariable(
                name="num_flashcards",
                description="Anzahl der zu erstellenden Flashcards",
                required=False,
                default="10"
            )
        ],
        model="gpt-4-turbo",
        max_tokens=2500,
        temperature=0.8,
        language_mode="target",
        allowed_roles=["student", "teacher", "admin"],
        created_by="system"
    )
    register_prompt(flashcards)

    # ========================================================================
    # 3. QUIZ GENERATOR
    # ========================================================================
    quiz_generator = PromptTemplate(
        code="quiz_generator",
        title="Quiz Generator (Multiple Choice)",
        description=(
            "Erstellt Multiple-Choice-Quizfragen mit 4 Antwortmöglichkeiten. "
            "Jede Frage enthält eine korrekte Antwort und eine Erklärung."
        ),
        version=1,
        tags=["learning", "quiz", "multiple-choice", "assessment"],
        messages=[
            PromptMessage(
                role="system",
                content=(
                    "Du bist ein KI-Modul zur Erstellung von Multiple-Choice-Quizfragen "
                    "für den Kurs '{{course_title}}'. "
                    "Erstelle faire, eindeutige Fragen mit einer korrekten und drei plausiblen "
                    "falschen Antworten. Vermeide Tricks oder mehrdeutige Formulierungen."
                )
            ),
            PromptMessage(
                role="user",
                content=(
                    "Erstelle {{num_questions}} Multiple-Choice-Fragen basierend auf:\n\n"
                    "Lektion: {{lesson_title}}\n\n"
                    "Inhalt:\n{{lesson_content}}\n\n"
                    "Ausgabeformat (JSON):\n"
                    "{\n"
                    '  "questions": [\n'
                    "    {\n"
                    '      "question": "Fragestellung",\n'
                    '      "answers": ["Option A", "Option B", "Option C", "Option D"],\n'
                    '      "correct_index": 0,\n'
                    '      "explanation": "Begründung der korrekten Antwort",\n'
                    '      "difficulty": "easy|medium|hard"\n'
                    "    }\n"
                    "  ]\n"
                    "}"
                )
            )
        ],
        variables=[
            PromptVariable(
                name="course_title",
                description="Titel des Kurses",
                required=True
            ),
            PromptVariable(
                name="lesson_title",
                description="Titel der Lektion",
                required=True
            ),
            PromptVariable(
                name="lesson_content",
                description="Lektionsinhalt für Quiz-Erstellung",
                required=True
            ),
            PromptVariable(
                name="num_questions",
                description="Anzahl der Multiple-Choice-Fragen",
                required=False,
                default="5"
            )
        ],
        model="gpt-4-turbo",
        max_tokens=3000,
        temperature=0.7,
        language_mode="target",
        allowed_roles=["teacher", "admin"],
        created_by="system"
    )
    register_prompt(quiz_generator)

    # ========================================================================
    # 4. SOCRATIC TUTOR
    # ========================================================================
    socratic_tutor = PromptTemplate(
        code="socratic_tutor",
        title="Sokratischer Dialog Tutor",
        description=(
            "Führt einen sokratischen Dialog, bei dem der Lernende durch gezielte "
            "Rückfragen zum selbstständigen Denken angeregt wird."
        ),
        version=1,
        tags=["learning", "socratic", "dialogue", "critical-thinking"],
        messages=[
            PromptMessage(
                role="system",
                content=(
                    "Du bist ein sokratischer KI-Tutor für '{{course_title}}'. "
                    "Dein Ziel ist es, den Lernenden durch gezielte Fragen zum eigenständigen "
                    "Nachdenken anzuregen, anstatt direkte Antworten zu geben. "
                    "Stelle offene Fragen, die zum kritischen Denken anregen. "
                    "Gib Hinweise, wenn der Lernende feststeckt, aber vermeide es, "
                    "die Lösung direkt preiszugeben."
                )
            ),
            PromptMessage(
                role="user",
                content=(
                    "Thema der aktuellen Lektion: {{lesson_title}}\n\n"
                    "Lernender fragt: {{student_question}}\n\n"
                    "Führe einen sokratischen Dialog, um den Lernenden zur Lösung zu führen."
                )
            )
        ],
        variables=[
            PromptVariable(
                name="course_title",
                description="Titel des Kurses",
                required=True
            ),
            PromptVariable(
                name="lesson_title",
                description="Aktuelles Lektionsthema",
                required=True
            ),
            PromptVariable(
                name="student_question",
                description="Frage oder Problem des Lernenden",
                required=True
            )
        ],
        model="claude-3-sonnet-20240229",
        max_tokens=1500,
        temperature=0.8,
        language_mode="target",
        allowed_roles=["student", "teacher", "admin"],
        created_by="system"
    )
    register_prompt(socratic_tutor)

    # ========================================================================
    # 5. SUMMARIZE LESSON
    # ========================================================================
    summarize_lesson = PromptTemplate(
        code="summarize_lesson",
        title="Lektions-Zusammenfassung",
        description=(
            "Erstellt strukturierte Zusammenfassungen von Lektionsinhalten. "
            "Hebt Kernpunkte, wichtige Konzepte und Zusammenhänge hervor."
        ),
        version=1,
        tags=["learning", "summary", "overview", "key-concepts"],
        messages=[
            PromptMessage(
                role="system",
                content=(
                    "Du bist ein KI-Assistent für das Erstellen prägnanter Zusammenfassungen "
                    "im Kurs '{{course_title}}'. "
                    "Identifiziere die wichtigsten Konzepte, Definitionen und Zusammenhänge. "
                    "Strukturiere die Zusammenfassung klar und übersichtlich."
                )
            ),
            PromptMessage(
                role="user",
                content=(
                    "Erstelle eine {{summary_length}} Zusammenfassung für:\n\n"
                    "Lektion: {{lesson_title}}\n\n"
                    "Inhalt:\n{{lesson_content}}\n\n"
                    "Strukturiere die Zusammenfassung so:\n"
                    "1. Kernaussage (1-2 Sätze)\n"
                    "2. Wichtigste Konzepte (Bullet Points)\n"
                    "3. Zentrale Zusammenhänge\n"
                    "4. Praxis-Relevanz (falls zutreffend)"
                )
            )
        ],
        variables=[
            PromptVariable(
                name="course_title",
                description="Titel des Kurses",
                required=True
            ),
            PromptVariable(
                name="lesson_title",
                description="Titel der Lektion",
                required=True
            ),
            PromptVariable(
                name="lesson_content",
                description="Vollständiger Lektionsinhalt",
                required=True
            ),
            PromptVariable(
                name="summary_length",
                description="Länge der Zusammenfassung (kurz/mittel/ausführlich)",
                required=False,
                default="mittel"
            )
        ],
        model="gpt-4-turbo",
        max_tokens=1500,
        temperature=0.6,
        language_mode="target",
        allowed_roles=["student", "teacher", "admin"],
        created_by="system"
    )
    register_prompt(summarize_lesson)

    # ========================================================================
    # 6. TRANSLATION ASSISTANT
    # ========================================================================
    translation_assistant = PromptTemplate(
        code="translation_assistant",
        title="Übersetzungs-Assistent",
        description=(
            "Übersetzt Lerninhalte unter Berücksichtigung fachlicher Terminologie. "
            "Erhält Kontext und Fachbegriffe für präzise Übersetzungen."
        ),
        version=1,
        tags=["translation", "i18n", "localization", "content"],
        messages=[
            PromptMessage(
                role="system",
                content=(
                    "Du bist ein spezialisierter Übersetzungs-Assistent für Bildungsinhalte. "
                    "Übersetze präzise unter Berücksichtigung fachlicher Terminologie. "
                    "Bewahre die pädagogische Struktur und Intention des Originaltextes."
                )
            ),
            PromptMessage(
                role="user",
                content=(
                    "Übersetze folgenden Text:\n\n"
                    "Von: {{source_language}}\n"
                    "Nach: {{target_language}}\n\n"
                    "Kontext: {{course_title}} - {{lesson_title}}\n\n"
                    "Text:\n{{content_to_translate}}\n\n"
                    "Beachte fachspezifische Terminologie und pädagogische Klarheit."
                )
            )
        ],
        variables=[
            PromptVariable(
                name="source_language",
                description="Quellsprache (z.B. 'Deutsch', 'English')",
                required=True
            ),
            PromptVariable(
                name="target_language",
                description="Zielsprache (z.B. 'Englisch', 'Français')",
                required=True
            ),
            PromptVariable(
                name="course_title",
                description="Kurstitel für Kontext",
                required=True
            ),
            PromptVariable(
                name="lesson_title",
                description="Lektionstitel für Kontext",
                required=True
            ),
            PromptVariable(
                name="content_to_translate",
                description="Zu übersetzender Inhalt",
                required=True
            )
        ],
        model="gpt-4-turbo",
        max_tokens=3000,
        temperature=0.3,
        language_mode="mixed",
        allowed_roles=["teacher", "admin"],
        created_by="system"
    )
    register_prompt(translation_assistant)

    logger.info(
        f"Registered {len(PROMPT_REGISTRY)} default prompt templates"
    )


def clear_registry() -> None:
    """
    Clear all registered prompts.

    Warning: Only use in testing or during re-initialization.
    """
    PROMPT_REGISTRY.clear()
    logger.warning("Cleared prompt registry")
