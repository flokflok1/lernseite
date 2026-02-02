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
- PromptRegistryError: Exception class
"""

from .core import PROMPT_REGISTRY, register_prompt, PromptRegistryError
from .retrieval import (
    get_prompt_template,
    get_prompt_for_lm_id,
    get_prompt_with_style,
    list_all_prompts,
    get_prompts_by_role,
    get_prompts_by_group
)
from .initialization import init_default_prompts, clear_registry
from .db_override import DB_OVERRIDE_ENABLED

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
