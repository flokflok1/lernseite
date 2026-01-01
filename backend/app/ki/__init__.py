"""
LernsystemX KI - Prompt System

Central prompt management system for all AI-related functionality.

Phase 24 - Developer Guide / KI-Prompts
"""

from app.ki.prompt_models import (
    PromptMessage,
    PromptVariable,
    PromptTemplate,
    PromptContext
)

from app.ki.prompt_registry import (
    PROMPT_REGISTRY,
    DB_OVERRIDE_ENABLED,
    register_prompt,
    get_prompt_template,
    get_prompt_with_style,
    list_all_prompts,
    init_default_prompts
)

__all__ = [
    'PromptMessage',
    'PromptVariable',
    'PromptTemplate',
    'PromptContext',
    'PROMPT_REGISTRY',
    'DB_OVERRIDE_ENABLED',
    'register_prompt',
    'get_prompt_template',
    'get_prompt_with_style',
    'list_all_prompts',
    'init_default_prompts'
]
