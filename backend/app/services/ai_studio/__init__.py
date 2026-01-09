"""
AI Studio Service Package

Central service for AI generation in KI-Authoring-Studio.
Handles content generation and session finalization workflows.

Phase D4 - KI-Authoring-Studio
"""

from app.services.ai_studio.service import AiStudioService
from app.services.ai_studio.generation import AiStudioGenerator
from app.services.ai_studio.finalization import AiStudioFinalizer
from app.services.ai_studio.utils import (
    AiStudioServiceError,
    get_prompt_code,
    get_available_steps,
    get_prompt_code_for_step,
    AI_STUDIO_STEP_TO_PROMPT
)

__all__ = [
    'AiStudioService',
    'AiStudioGenerator',
    'AiStudioFinalizer',
    'AiStudioServiceError',
    'get_prompt_code',
    'get_available_steps',
    'get_prompt_code_for_step',
    'AI_STUDIO_STEP_TO_PROMPT'
]


# Convenience function for quick access
def get_ai_studio_service(
    provider: str = "anthropic",
    model: str = "claude-3-5-sonnet-20241022"
) -> AiStudioService:
    """
    Get an AI Studio service instance.

    Args:
        provider: AI provider
        model: Model name

    Returns:
        AiStudioService instance
    """
    return AiStudioService(provider=provider, model=model)
