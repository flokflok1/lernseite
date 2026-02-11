"""
LernsystemX KI - Prompt Registry

Central registry for managing prompt templates across Content-Lernmethoden.

Exports:
- PROMPT_REGISTRY: Global registry dict
- register_prompt: Register new templates
- get_prompt_template: Retrieve template by code
- get_prompt_for_lm_id: Retrieve template by LM-ID
- get_prompt_with_style: Get template for category+style
- list_all_prompts: Get all registered templates
- init_default_prompts: Initialize standard prompts
- DB_OVERRIDE_ENABLED: DB override flag
- db_record_to_template: Convert DB record to template
- PromptRegistryError: Exception class
"""

# Registry and retrieval (from core/)
from app.domain.ai.configuration.prompts.registry.core import (
    PROMPT_REGISTRY,
    PromptRegistryError,
    register_prompt,
    get_prompt_template,
    get_prompt_for_lm_id,
    get_prompt_with_style,
    list_all_prompts,
    get_prompts_by_role,
    get_prompts_by_group
)

# Initialization (from initialization/)
from app.domain.ai.configuration.prompts.registry.initialization import (
    init_default_prompts,
    clear_registry
)

# Storage utilities (from storage/)
from app.domain.ai.configuration.prompts.registry.storage import (
    DB_OVERRIDE_ENABLED,
    db_record_to_template
)

__all__ = [
    # Registry
    'PROMPT_REGISTRY',
    'PromptRegistryError',
    'register_prompt',

    # Retrieval
    'get_prompt_template',
    'get_prompt_for_lm_id',
    'get_prompt_with_style',
    'list_all_prompts',
    'get_prompts_by_role',
    'get_prompts_by_group',

    # Initialization
    'init_default_prompts',
    'clear_registry',

    # Storage
    'DB_OVERRIDE_ENABLED',
    'db_record_to_template'
]
