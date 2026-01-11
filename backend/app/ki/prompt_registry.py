"""
LernsystemX KI - Prompt Registry (Wrapper)

Bridge module for backward compatibility.
All functionality has been moved to app/ki/prompts/registry/.

This module re-exports the registry for use in app/__init__.py.
"""

from app.ki.prompts.registry import (
    PROMPT_REGISTRY,
    register_prompt,
    PromptRegistryError,
    get_prompt_template,
    get_prompt_for_lm_id,
    get_prompt_with_style,
    list_all_prompts,
    get_prompts_by_role,
    get_prompts_by_group,
    init_default_prompts,
    clear_registry,
    DB_OVERRIDE_ENABLED
)

__all__ = [
    'PROMPT_REGISTRY',
    'register_prompt',
    'PromptRegistryError',
    'get_prompt_template',
    'get_prompt_for_lm_id',
    'get_prompt_with_style',
    'list_all_prompts',
    'get_prompts_by_role',
    'get_prompts_by_group',
    'init_default_prompts',
    'clear_registry',
    'DB_OVERRIDE_ENABLED'
]
