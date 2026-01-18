"""
Backward Compatibility Bridge: prompt_resolver

DEPRECATED: Use 'from app.application.services.ai.prompts.resolver import PromptResolver' instead
This bridge maintains backward compatibility with old import paths.
"""

from app.application.services.ai.prompts.resolver import PromptResolver

__all__ = ['PromptResolver']
