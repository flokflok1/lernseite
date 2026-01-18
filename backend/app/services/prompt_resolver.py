"""
Prompt Resolver Service Bridge - LEGACY IMPORT PATH

NOTICE: This file exists for backward compatibility only.
The actual implementation has been moved to app/services/ai/prompts/resolver.py

DEPRECATED IMPORT (old path - still works):
    from app.services.prompt_resolver import PromptResolver

RECOMMENDED IMPORT (new path):
    from app.services.ai.prompts import PromptResolver

This bridge re-exports the PromptResolver class for backward compatibility
with existing code. All new code should use the recommended import path.
"""

# Re-export from the actual location for backward compatibility
from app.services.ai.prompts.resolver import PromptResolver

__all__ = ['PromptResolver']
