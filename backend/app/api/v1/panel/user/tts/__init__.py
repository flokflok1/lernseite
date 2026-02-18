"""User TTS API — Text-to-speech features."""

from .synthesis import synthesis_bp
from . import synthesis_part2 as _synthesis_part2  # noqa: F401 — registers routes on synthesis_bp
from .pronunciations import pronunciations_bp
from .audio import audio_bp

__all__ = ['synthesis_bp', 'pronunciations_bp', 'audio_bp']
