"""
LernsystemX KI - AI Editor Prompts

Specialized prompts for the KI-Authoring-Studio wizard steps.

Exports:
- AI_EDITOR_SYSTEM_BASE: Base system prompt
- AI_EDITOR_PROMPT_CODES: List of all prompt codes
- init_ai_editor_prompts: Initialize all 6 wizard step prompts
"""

from ._base import AI_EDITOR_SYSTEM_BASE
from .source import init_source_prompt
from .theory import init_theory_prompt
from .lessons import init_lessons_prompt
from .methods import init_methods_prompt
from .review import init_review_prompt
from .finalize import init_finalize_prompt


# List of all AI Editor prompt codes
AI_EDITOR_PROMPT_CODES = [
    "ai_editor_source",
    "ai_editor_theory",
    "ai_editor_lessons",
    "ai_editor_methods",
    "ai_editor_review",
    "ai_editor_finalize"
]


def init_ai_editor_prompts() -> None:
    """
    Initialize AI Editor prompt templates.

    Registers templates for all 6 wizard steps:
    - ai_editor_source: PDF analysis and didactic perspectives
    - ai_editor_theory: Theory variant generation
    - ai_editor_lessons: Lesson structure generation
    - ai_editor_methods: Method variants per lesson
    - ai_editor_review: Consistency check
    - ai_editor_finalize: Final blueprint generation

    Called during application initialization.
    """
    from flask import current_app
    current_app.logger.info("Initializing AI Editor prompt templates...")

    init_source_prompt()
    init_theory_prompt()
    init_lessons_prompt()
    init_methods_prompt()
    init_review_prompt()
    init_finalize_prompt()

    current_app.logger.info("Registered 6 AI Editor prompt templates")


__all__ = [
    'AI_EDITOR_SYSTEM_BASE',
    'AI_EDITOR_PROMPT_CODES',
    'init_ai_editor_prompts'
]
