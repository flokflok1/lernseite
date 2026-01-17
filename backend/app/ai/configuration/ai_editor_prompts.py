"""
LernsystemX KI - AI Editor Prompts (Wrapper)

Bridge module for backward compatibility.
All functionality has been moved to app/ki/prompts/ai_editor/.

This module re-exports the AI Editor prompts for use in app/__init__.py.
"""

from app.ai.configuration.prompts.ai_editor import (
    AI_EDITOR_SYSTEM_BASE,
    AI_EDITOR_PROMPT_CODES,
    init_ai_editor_prompts
)

__all__ = [
    'AI_EDITOR_SYSTEM_BASE',
    'AI_EDITOR_PROMPT_CODES',
    'init_ai_editor_prompts'
]
