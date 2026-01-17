"""TTS Module - Text-to-Speech and Audio Services"""

from app.api.v1.tts.pronunciations import pronunciations_bp
from app.api.v1.tts.synthesis import synthesis_bp
from app.api.v1.tts.audio import audio_bp

__all__ = ['pronunciations_bp', 'synthesis_bp', 'audio_bp']
