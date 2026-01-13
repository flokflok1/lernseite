"""
AI Studio Utilities

Constants and helper functions for AI Studio service.
"""

from typing import Dict, Optional, List


# ==============================================================================
# STEP TO PROMPT MAPPING
# Maps content_type/step to prompt codes in the prompt registry
# ==============================================================================

AI_STUDIO_STEP_TO_PROMPT: Dict[str, str] = {
    # VariantType values -> prompt codes
    "theory": "ai_studio_theory",
    "lesson": "ai_studio_lessons",
    "method": "ai_studio_methods",
    "quiz": "ai_studio_methods",  # Quiz uses methods prompt for now
    "summary": "ai_studio_review",
    "full_chapter": "ai_studio_finalize",

    # Additional step mappings
    "source": "ai_studio_source",
    "review": "ai_studio_review",
    "finalize": "ai_studio_finalize",
}


class AiStudioServiceError(Exception):
    """Base exception for AI Studio service errors"""
    pass


def get_prompt_code(step: str) -> str:
    """
    Get the prompt code for a given step.

    Args:
        step: Step name (e.g., "theory", "lessons", "methods")

    Returns:
        Prompt code from AI_STUDIO_STEP_TO_PROMPT

    Raises:
        AiStudioServiceError: If step not found in mapping
    """
    if step not in AI_STUDIO_STEP_TO_PROMPT:
        raise AiStudioServiceError(
            f"Unknown step: {step}. "
            f"Valid steps: {', '.join(AI_STUDIO_STEP_TO_PROMPT.keys())}"
        )
    return AI_STUDIO_STEP_TO_PROMPT[step]


def get_available_steps() -> List[str]:
    """Get list of all available generation steps."""
    return list(AI_STUDIO_STEP_TO_PROMPT.keys())


def get_prompt_code_for_step(step: str) -> Optional[str]:
    """Get prompt code for a step without raising an error."""
    return AI_STUDIO_STEP_TO_PROMPT.get(step)
