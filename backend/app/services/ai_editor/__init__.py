"""
AI Editor Service Package

Central service for AI generation in KI-Authoring-Studio.
Handles content generation and session finalization workflows.

Phase D4 - KI-Authoring-Studio
"""

from app.services.ai_editor.service import AiEditorService
from app.services.ai_editor.generation import AiEditorGenerator
from app.services.ai_editor.finalization import AiEditorFinalizer
from app.services.ai_editor.utils import (
    AiEditorServiceError,
    get_prompt_code,
    get_available_steps,
    get_prompt_code_for_step,
    AI_EDITOR_STEP_TO_PROMPT
)

__all__ = [
    'AiEditorService',
    'AiEditorGenerator',
    'AiEditorFinalizer',
    'AiEditorServiceError',
    'get_prompt_code',
    'get_available_steps',
    'get_prompt_code_for_step',
    'AI_EDITOR_STEP_TO_PROMPT'
]


# Convenience function for quick access
def get_ai_editor_service(
    provider: str = "anthropic",
    model: str = "claude-3-5-sonnet-20241022"
) -> AiEditorService:
    """
    Get an AI Editor service instance.

    Args:
        provider: AI provider
        model: Model name

    Returns:
        AiEditorService instance
    """
    return AiEditorService(provider=provider, model=model)
