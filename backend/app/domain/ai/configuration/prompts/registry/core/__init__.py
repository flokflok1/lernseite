"""
Prompt Registry Core

Provides core registry and retrieval functions for prompt templates.
"""

# Registry
from app.domain.ai.configuration.prompts.registry.core.registry import (
    PROMPT_REGISTRY,
    PromptRegistryError,
    register_prompt
)

# Retrieval
from app.domain.ai.configuration.prompts.registry.core.retrieval import (
    get_prompt_template,
    get_prompt_with_style,
    list_all_prompts,
    get_prompts_by_role,
    get_prompt_for_lm_id,
    get_prompts_by_group
)

__all__ = [
    # Registry
    'PROMPT_REGISTRY',
    'PromptRegistryError',
    'register_prompt',

    # Retrieval
    'get_prompt_template',
    'get_prompt_with_style',
    'list_all_prompts',
    'get_prompts_by_role',
    'get_prompt_for_lm_id',
    'get_prompts_by_group'
]
