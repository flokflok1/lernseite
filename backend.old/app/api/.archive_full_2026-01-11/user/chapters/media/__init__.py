"""
LernsystemX Chapter Theory Media Package

Audio generation and serving for chapter theory content.

Structure:
    audio.py  ~240 lines  - /chapter-theory/<id>/audio endpoint, TTS generation

Reorganized from chapter_theory/audio.py - 2026-01-08
Per Developer-Guide-KI Section 10.2 (Max 500 lines per file)
"""

from .audio import chapter_theory_audio_bp, generate_theory_audio

__all__ = [
    'chapter_theory_audio_bp',
    'generate_theory_audio',
]
