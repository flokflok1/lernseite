"""
AI Editor Utilities

Constants and helper functions for AI Editor service.
"""

from typing import Dict, Optional, List


# ==============================================================================
# STEP TO PROMPT MAPPING
# Maps content_type/step to prompt codes in the prompt registry
# ==============================================================================

AI_EDITOR_STEP_TO_PROMPT: Dict[str, str] = {
    # VariantType values -> prompt codes
    "theory": "ai_editor_theory",
    "lesson": "ai_editor_lessons",
    "method": "ai_editor_methods",
    "quiz": "ai_editor_methods",  # Quiz uses methods prompt for now
    "summary": "ai_editor_review",
    "full_chapter": "ai_editor_finalize",

    # Additional step mappings
    "source": "ai_editor_source",
    "review": "ai_editor_review",
    "finalize": "ai_editor_finalize",
}


class AiEditorServiceError(Exception):
    """Base exception for AI Editor service errors"""
    pass


def get_prompt_code(step: str) -> str:
    """
    Get the prompt code for a given step.

    Args:
        step: Step name (e.g., "theory", "lessons", "methods")

    Returns:
        Prompt code from AI_EDITOR_STEP_TO_PROMPT

    Raises:
        AiEditorServiceError: If step not found in mapping
    """
    if step not in AI_EDITOR_STEP_TO_PROMPT:
        raise AiEditorServiceError(
            f"Unknown step: {step}. "
            f"Valid steps: {', '.join(AI_EDITOR_STEP_TO_PROMPT.keys())}"
        )
    return AI_EDITOR_STEP_TO_PROMPT[step]


def get_available_steps() -> List[str]:
    """Get list of all available generation steps."""
    return list(AI_EDITOR_STEP_TO_PROMPT.keys())


def get_prompt_code_for_step(step: str) -> Optional[str]:
    """Get prompt code for a step without raising an error."""
    return AI_EDITOR_STEP_TO_PROMPT.get(step)
