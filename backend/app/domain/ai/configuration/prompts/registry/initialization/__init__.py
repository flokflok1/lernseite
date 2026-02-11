"""
Prompt Registry Initialization

Provides initialization and setup functions for the prompt registry.
"""

from app.domain.ai.configuration.prompts.registry.initialization.setup import (
    init_default_prompts,
    clear_registry
)

__all__ = [
    'init_default_prompts',
    'clear_registry'
]
