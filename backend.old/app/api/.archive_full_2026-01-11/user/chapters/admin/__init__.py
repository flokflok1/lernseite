"""
LernsystemX Chapter Theory Admin Package

Admin-only operations for chapter theory management.

Packages:
    - generation: KI-powered theory generation
    - management: CRUD operations (admin-level)
    - media: Audio TTS generation and management

DDD Refactored: 2026-01-08
Per Developer-Guide-KI DDD Pattern and ISO/IEC 26515
"""

from .generation import chapter_theory_gen_bp, generate_theory_content, parse_json_response, get_theory_prompts
from .management import chapter_theory_admin_management_bp
from .media import chapter_theory_audio_bp, generate_theory_audio

__all__ = [
    # Generation
    'chapter_theory_gen_bp',
    'generate_theory_content',
    'parse_json_response',
    'get_theory_prompts',
    # Management
    'chapter_theory_admin_management_bp',
    # Media
    'chapter_theory_audio_bp',
    'generate_theory_audio',
]
