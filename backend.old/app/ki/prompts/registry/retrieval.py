"""
LernsystemX KI - Prompt Registry Retrieval

Functions for retrieving prompt templates from registry or database.
"""

from typing import List, Optional
from flask import current_app

from app.ki.prompt_models import PromptTemplate
from .core import PROMPT_REGISTRY, PromptRegistryError
from .db_override import DB_OVERRIDE_ENABLED, db_record_to_template


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
            from app.repositories.prompts.templates import PromptTemplateRepository
            db_template = PromptTemplateRepository.find_by_code(code)

            if db_template:
                # Convert DB record to PromptTemplate
                return db_record_to_template(db_template)
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
            from app.repositories.prompts.templates import PromptTemplateRepository
            db_template = PromptTemplateRepository.find_by_category_and_style(category, style)

            if db_template:
                return db_record_to_template(db_template)
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
