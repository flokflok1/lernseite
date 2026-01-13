"""
LernsystemX KI - AI Studio Prompts (Wrapper)

Bridge module for backward compatibility.
All functionality has been moved to app/ki/prompts/ai_studio/.

This module re-exports the AI Studio prompts for use in app/__init__.py.
"""

from app.ki.prompts.ai_studio import (
    AI_STUDIO_SYSTEM_BASE,
    AI_STUDIO_PROMPT_CODES,
    init_ai_studio_prompts
)

__all__ = [
    'AI_STUDIO_SYSTEM_BASE',
    'AI_STUDIO_PROMPT_CODES',
    'init_ai_studio_prompts'
]
