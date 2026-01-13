"""
LernsystemX Media API Package

Media processing endpoints:
- audio: STT processing and oral explanation analysis
- tts: Text-to-Speech generation (existing package - NOT CHANGED)

Structure:
    audio/processing.py  ~257 lines  - /audio/transcribe, /audio/transcribe-base64
    audio/streaming.py   ~203 lines  - /audio/analyze-oral, /audio/supported-formats
    tts/                 (existing)   - TTS endpoints

Route Registration:
    All routes are registered on api_v1 blueprint.
    Final URLs: /api/v1/audio/..., /api/v1/tts/...

Refactored: 2026-01-08 per Developer-Guide-KI Section 10
Original: media/audio.py (460 LOC) → audio/ package (2 modules, 460 LOC)
"""

from .audio import audio_processing_bp, audio_streaming_bp

# All blueprints in this package
ALL_BLUEPRINTS = [
    audio_processing_bp,
    audio_streaming_bp,
]

# Register all sub-blueprints on api_v1 (nested blueprint pattern)
# This is executed when the package is imported from app/api/__init__.py
from app.api import api_v1

for bp in ALL_BLUEPRINTS:
    api_v1.register_blueprint(bp)


# Import TTS module (existing - not changed)
from . import tts

# Export all blueprints for direct import
__all__ = [
    'audio_processing_bp',
    'audio_streaming_bp',
    'ALL_BLUEPRINTS',
    'tts',
]
