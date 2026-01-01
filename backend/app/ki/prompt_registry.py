"""
LernsystemX KI - Prompt Registry

Central registry for managing prompt templates across 19 Content-Lernmethoden.

Content-LMs (Gruppen A-C):
- A: LM00, LM01, LM02, LM03, LM06 (Erklaerend)
- B: LM08, LM12, LM13, LM14, LM15, LM17 (Praxis)
- C: LM18-LM25 (Pruefung)

Features:
- Code-based default prompts (in PROMPT_REGISTRY)
- Database override capability (admins can customize prompts via UI)
- Fallback hierarchy: DB Override > Code Default

Functions:
- register_prompt: Register a new prompt template
- get_prompt_template: Retrieve a template by code (checks DB first, then code)
- get_prompt_for_lm_id: Retrieve a template by LM-ID
- list_all_prompts: Get all registered templates
- init_default_prompts: Initialize standard learning method prompts
- get_prompt_with_style: Get template for category+style (theory, adhs, etc.)

Referenz: 02_Lernmethoden.md, 02a_System-Features.md
"""

from typing import Dict, List, Optional
from datetime import datetime
from flask import current_app

from app.ki.prompt_models import (
    PromptTemplate,
    PromptMessage,
    PromptVariable
)


# Global prompt registry (code-based defaults)
PROMPT_REGISTRY: Dict[str, PromptTemplate] = {}

# Enable/disable DB override lookup (can be disabled for performance in tests)
DB_OVERRIDE_ENABLED: bool = True


class PromptRegistryError(Exception):
    """Exception raised for prompt registry errors"""
    pass


def register_prompt(template: PromptTemplate, overwrite: bool = False) -> None:
    """
    Register a prompt template in the global registry.

    Args:
        template: PromptTemplate instance to register
        overwrite: If True, allows overwriting existing template

    Raises:
        PromptRegistryError: If template code already exists and overwrite=False

    Examples:
        custom_template = PromptTemplate(
            code="my_custom_method",
            title="My Custom Learning Method",
            ...
        )
        register_prompt(custom_template)
    """
    if template.code in PROMPT_REGISTRY and not overwrite:
        raise PromptRegistryError(
            f"Prompt template '{template.code}' already exists. "
            f"Use overwrite=True to replace it."
        )

    # Set timestamps if not already set
    if template.created_at is None:
        template.created_at = datetime.utcnow()
    template.updated_at = datetime.utcnow()

    PROMPT_REGISTRY[template.code] = template

    current_app.logger.info(
        f"Registered prompt template: {template.code} (v{template.version})"
    )


def get_prompt_template(code: str, check_db: bool = True) -> PromptTemplate:
    """
    Retrieve a prompt template by its code.

    Lookup order:
    1. Database (if DB_OVERRIDE_ENABLED and check_db=True)
    2. Code-based registry (PROMPT_REGISTRY)

    Args:
        code: Unique template identifier (e.g., 'explain_concept')
        check_db: Whether to check database for override (default True)

    Returns:
        PromptTemplate instance

    Raises:
        PromptRegistryError: If template not found in either location

    Examples:
        template = get_prompt_template("explain_concept")
        messages = template.render(context)
    """
    # Try database first (if enabled)
    if DB_OVERRIDE_ENABLED and check_db:
        try:
            from app.repositories.prompt_template_repository import PromptTemplateRepository
            db_template = PromptTemplateRepository.find_by_code(code)

            if db_template:
                # Convert DB record to PromptTemplate
                return _db_record_to_template(db_template)
        except Exception as e:
            # DB lookup failed, fall back to code registry
            current_app.logger.debug(f"DB lookup failed for prompt '{code}': {e}")

    # Fall back to code-based registry
    if code not in PROMPT_REGISTRY:
        raise PromptRegistryError(
            f"Prompt template '{code}' not found in registry. "
            f"Available: {', '.join(PROMPT_REGISTRY.keys())}"
        )

    return PROMPT_REGISTRY[code]


def get_prompt_with_style(category: str, style: str = 'standard') -> Optional[PromptTemplate]:
    """
    Get a prompt template for a specific category and style.

    This is the preferred method for getting prompts with style variants
    (e.g., 'theory' + 'adhs', 'theory' + 'detailed').

    Args:
        category: Template category ('theory', 'lesson', 'quiz', etc.)
        style: Style variant ('standard', 'adhs', 'short', 'detailed', 'exam_focus')

    Returns:
        PromptTemplate instance or None if not found

    Examples:
        # Get ADHS-friendly theory sheet template
        template = get_prompt_with_style('theory', 'adhs')

        # Get default (standard) quiz template
        template = get_prompt_with_style('quiz')
    """
    # Try database first
    if DB_OVERRIDE_ENABLED:
        try:
            from app.repositories.prompt_template_repository import PromptTemplateRepository
            db_template = PromptTemplateRepository.find_by_category_and_style(category, style)

            if db_template:
                return _db_record_to_template(db_template)
        except Exception as e:
            current_app.logger.debug(f"DB lookup failed for {category}/{style}: {e}")

    # Fall back to code - try to find matching template
    # Convention: code = f"{category}_{style}" or f"{category}_sheet_{style}"
    possible_codes = [
        f"{category}_{style}",
        f"{category}_sheet_{style}",
        f"{category}_{style}_template",
    ]

    for code in possible_codes:
        if code in PROMPT_REGISTRY:
            return PROMPT_REGISTRY[code]

    # If style not found, try standard
    if style != 'standard':
        return get_prompt_with_style(category, 'standard')

    return None


def _db_record_to_template(record: Dict) -> PromptTemplate:
    """
    Convert a database record to a PromptTemplate instance.

    The DB stores system_prompt and user_prompt_template separately,
    while PromptTemplate uses a messages list.

    Args:
        record: Database record dict

    Returns:
        PromptTemplate instance
    """
    import json

    # Build messages list from DB fields
    messages = []

    if record.get('system_prompt'):
        messages.append(PromptMessage(
            role='system',
            content=record['system_prompt']
        ))

    if record.get('user_prompt_template'):
        messages.append(PromptMessage(
            role='user',
            content=record['user_prompt_template']
        ))

    # Parse variables from JSONB
    variables_data = record.get('variables', [])
    if isinstance(variables_data, str):
        variables_data = json.loads(variables_data)

    variables = []
    for var in variables_data:
        variables.append(PromptVariable(
            name=var.get('name'),
            description=var.get('description', ''),
            required=var.get('required', True),
            default=var.get('default')
        ))

    # Build tags from category/style
    tags = [record.get('category', ''), record.get('style', '')]
    if record.get('tts_enabled'):
        tags.append('tts')

    return PromptTemplate(
        code=record['code'],
        title=record.get('title', record['code']),
        description=record.get('description', ''),
        version=record.get('version', 1),
        tags=tags,
        messages=messages,
        variables=variables,
        model=record.get('model'),
        max_tokens=record.get('max_tokens'),
        temperature=float(record.get('temperature', 0.7)),
        language_mode='target',
        allowed_roles=[],
        created_at=record.get('created_at'),
        updated_at=record.get('updated_at'),
        created_by=str(record.get('created_by')) if record.get('created_by') else 'system'
    )


def list_all_prompts(tags: Optional[List[str]] = None) -> List[PromptTemplate]:
    """
    List all registered prompt templates.

    Args:
        tags: Optional list of tags to filter by

    Returns:
        List of PromptTemplate instances

    Examples:
        all_prompts = list_all_prompts()
        learning_prompts = list_all_prompts(tags=["learning"])
    """
    templates = list(PROMPT_REGISTRY.values())

    if tags:
        templates = [
            t for t in templates
            if any(tag in t.tags for tag in tags)
        ]

    return sorted(templates, key=lambda t: t.code)


def get_prompts_by_role(role: str) -> List[PromptTemplate]:
    """
    Get all prompts accessible by a specific role.

    Args:
        role: Role identifier (e.g., 'student', 'teacher', 'admin')

    Returns:
        List of accessible PromptTemplate instances
    """
    return [
        t for t in PROMPT_REGISTRY.values()
        if not t.allowed_roles or role in t.allowed_roles
    ]


def get_prompt_for_lm_id(lm_id: int) -> Optional[PromptTemplate]:
    """
    Get prompt template for a specific learning method ID (LM00-LM31).

    Uses the learning_method_mapping to find the appropriate prompt_key
    and returns the corresponding template.

    Args:
        lm_id: Learning method ID (0-31)

    Returns:
        PromptTemplate instance or None if no prompt defined

    Examples:
        template = get_prompt_for_lm_id(13)  # LM13 = Flashcards
        if template:
            messages = template.render(context)
    """
    from app.ki.learning_method_mapping import get_prompt_key_for_lm_id

    prompt_key = get_prompt_key_for_lm_id(lm_id)

    if not prompt_key:
        current_app.logger.warning(
            f"No prompt_key found for LM{lm_id:02d}"
        )
        return None

    if prompt_key not in PROMPT_REGISTRY:
        current_app.logger.warning(
            f"Prompt template '{prompt_key}' for LM{lm_id:02d} not in registry"
        )
        return None

    return PROMPT_REGISTRY[prompt_key]


def get_prompts_by_group(group: str) -> List[PromptTemplate]:
    """
    Get all prompts for learning methods in a specific group.

    Args:
        group: Group code ('A', 'B', 'C', 'D')

    Returns:
        List of PromptTemplate instances for that group
    """
    from app.ki.learning_method_mapping import get_methods_by_group, LearningMethodGroup

    try:
        group_enum = LearningMethodGroup(group)
    except ValueError:
        return []

    methods = get_methods_by_group(group_enum)
    templates = []

    for method in methods:
        if method.prompt_key in PROMPT_REGISTRY:
            templates.append(PROMPT_REGISTRY[method.prompt_key])

    return templates


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
    current_app.logger.info("Initializing default prompt templates...")

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

    current_app.logger.info(
        f"Registered {len(PROMPT_REGISTRY)} default prompt templates"
    )


def clear_registry() -> None:
    """
    Clear all registered prompts.

    Warning: Only use in testing or during re-initialization.
    """
    PROMPT_REGISTRY.clear()
    current_app.logger.warning("Cleared prompt registry")
