"""User TTS API — Text-to-speech features."""

from .user.synthesis import synthesis_bp
from .user import synthesis_part2 as _synthesis_part2  # noqa: F401 — registers routes on synthesis_bp
from .user.pronunciations import pronunciations_bp
from .user.audio import audio_bp

__all__ = ['synthesis_bp', 'pronunciations_bp', 'audio_bp']
