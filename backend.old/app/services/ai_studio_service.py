"""
AI Studio Service Bridge

DEPRECATED: This module is maintained for backward compatibility.
Use `app.services.ai_studio` package directly.

This bridge imports all public APIs from the refactored package
to ensure existing imports continue to work.

Example:
    # Old style (still works)
    from app.services.ai_studio_service import AiStudioService, get_ai_studio_service

    # New style (preferred)
    from app.services.ai_studio import AiStudioService, get_ai_studio_service
"""

# Re-export all public APIs from the refactored package
from app.services.ai_studio import (
    AiStudioService,
    AiStudioGenerator,
    AiStudioFinalizer,
    AiStudioServiceError,
    get_prompt_code,
    get_available_steps,
    get_prompt_code_for_step,
    get_ai_studio_service,
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
    'get_ai_studio_service',
    'AI_STUDIO_STEP_TO_PROMPT'
]
