"""
LernsystemX KI - Prompt Registry Retrieval

Functions for retrieving prompt templates from registry or database.
"""

from typing import List, Optional
from flask import current_app

from app.domain.ai.configuration.prompt_models import PromptTemplate
from app.domain.ports.core.registry import repos
from .registry import PROMPT_REGISTRY, PromptRegistryError
from ..storage.db_override import DB_OVERRIDE_ENABLED, db_record_to_template


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
            db_template = repos.prompt_templates.find_by_code(code)

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
            db_template = repos.prompt_templates.find_by_category_and_style(category, style)

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
    Get prompt template for a specific learning method ID.

    DB-Driven (v2.0.0+): Fetches prompt_template from database learning_method_types table.

    Legacy Fallback: If database lookup fails, checks PROMPT_REGISTRY code-based registry.

    Args:
        lm_id: Learning method ID (0-11 for Content-LMs, extensible via database)

    Returns:
        PromptTemplate instance or None if no prompt defined

    Examples:
        template = get_prompt_for_lm_id(0)   # LM00 = Tiefgehende Erklärung
        if template:
            messages = template.render(context)
    """
    # Try database first (DB-driven approach)
    try:
        method_data = repos.lm_catalog.get_by_type(method_type=lm_id)

        if method_data and method_data.get('prompt_template'):
            prompt_key = method_data.get('prompt_template')

            if prompt_key in PROMPT_REGISTRY:
                return PROMPT_REGISTRY[prompt_key]
            else:
                current_app.logger.debug(
                    f"Prompt template '{prompt_key}' for LM{lm_id:02d} not in registry"
                )
                return None
    except Exception as e:
        current_app.logger.debug(f"DB lookup failed for LM{lm_id:02d}: {e}")

    # Fallback: No prompt defined for this LM
    return None


def get_prompts_by_group(group: str) -> List[PromptTemplate]:
    """
    Get all prompts for learning methods in a specific group.

    DB-Driven (v2.0.0+): Fetches all LMs from database for the given group_code.

    Args:
        group: Group code ('A' | 'B' | 'C')

    Returns:
        List of PromptTemplate instances for that group

    Examples:
        theory_prompts = get_prompts_by_group('A')  # Explaining group
        practice_prompts = get_prompts_by_group('B') # Practice group
        exam_prompts = get_prompts_by_group('C')     # Assessment group
    """
    # Validate group code against database (not hardcoded!)
    group_upper = group.upper()
    group_data = repos.lm_groups.find_by_code(group_upper)
    if not group_data:
        current_app.logger.warning(f"Invalid learning method group: {group} (not found in database)")
        return []

    try:
        # Get all LMs for this group from database
        catalog = repos.lm_catalog.get_full_catalog(use_cache=True)

        if not catalog or 'learning_methods' not in catalog:
            return []

        templates = []

        # Filter methods by group and find their prompts
        for method in catalog['learning_methods']:
            if method.get('group_code') == group.upper():
                prompt_template = method.get('prompt_template')

                if prompt_template and prompt_template in PROMPT_REGISTRY:
                    templates.append(PROMPT_REGISTRY[prompt_template])

        return templates

    except Exception as e:
        current_app.logger.error(f"Error fetching prompts for group {group}: {e}")
        return []
