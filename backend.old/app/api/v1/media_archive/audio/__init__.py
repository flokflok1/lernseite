"""
LernsystemX Audio API Package

Audio processing and streaming endpoints split for maintainability:
- processing: STT from file upload and base64 data
- streaming: Oral explanation analysis and format info

Structure:
    processing.py  ~257 lines  - /audio/transcribe, /audio/transcribe-base64
    streaming.py   ~203 lines  - /audio/analyze-oral, /audio/supported-formats

Refactored from media/audio.py (460 lines) - 2026-01-08
Per Developer-Guide-KI Section 10.2 (Max 500 lines per file)
"""

from .processing import audio_processing_bp
from .streaming import audio_streaming_bp

__all__ = [
    'audio_processing_bp',
    'audio_streaming_bp',
]
