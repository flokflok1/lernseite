"""
LernsystemX Chapter Theory Generation Package

KI-powered theory generation split for maintainability:
- core: Main generation endpoint and logic
- templates: Style-specific prompt templates

Structure:
    core.py       ~210 lines  - /chapters/<id>/theory/generate endpoint
    templates.py  ~237 lines  - Prompt templates for 5 styles

Refactored from chapter_theory/generation.py (447 lines) - 2026-01-08
Per Developer-Guide-KI Section 10.2 (Max 500 lines per file)
"""

from .core import chapter_theory_gen_bp, generate_theory_content, parse_json_response
from .templates import get_theory_prompts

__all__ = [
    'chapter_theory_gen_bp',
    'generate_theory_content',
    'parse_json_response',
    'get_theory_prompts',
]
