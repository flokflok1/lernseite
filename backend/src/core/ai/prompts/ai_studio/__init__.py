"""
LernsystemX KI - AI Studio Prompts

Specialized prompts for the KI-Authoring-Studio wizard steps.

Exports:
- AI_STUDIO_SYSTEM_BASE: Base system prompt
- AI_STUDIO_PROMPT_CODES: List of all prompt codes
- init_ai_studio_prompts: Initialize all 6 wizard step prompts
"""

from ._base import AI_STUDIO_SYSTEM_BASE
from .source import init_source_prompt
from .theory import init_theory_prompt
from .lessons import init_lessons_prompt
from .methods import init_methods_prompt
from .review import init_review_prompt
from .finalize import init_finalize_prompt


# List of all AI Studio prompt codes
AI_STUDIO_PROMPT_CODES = [
    "ai_studio_source",
    "ai_studio_theory",
    "ai_studio_lessons",
    "ai_studio_methods",
    "ai_studio_review",
    "ai_studio_finalize"
]


def init_ai_studio_prompts() -> None:
    """
    Initialize AI Studio prompt templates.

    Registers templates for all 6 wizard steps:
    - ai_studio_source: PDF analysis and didactic perspectives
    - ai_studio_theory: Theory variant generation
    - ai_studio_lessons: Lesson structure generation
    - ai_studio_methods: Method variants per lesson
    - ai_studio_review: Consistency check
    - ai_studio_finalize: Final blueprint generation

    Called during application initialization.
    """
    from flask import current_app
    current_app.logger.info("Initializing AI Studio prompt templates...")

    init_source_prompt()
    init_theory_prompt()
    init_lessons_prompt()
    init_methods_prompt()
    init_review_prompt()
    init_finalize_prompt()

    current_app.logger.info("Registered 6 AI Studio prompt templates")


__all__ = [
    'AI_STUDIO_SYSTEM_BASE',
    'AI_STUDIO_PROMPT_CODES',
    'init_ai_studio_prompts'
]
