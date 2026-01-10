"""
Media Domain - User Journey Routes

User-authenticated media routes for audio and TTS.

Routes:
- audio_stt.py: transcribe, transcribe-base64 (2 endpoints)
- audio_analysis.py: analyze-oral (1 endpoint)
- tts_synthesis.py: speak, audio/<id>, speak-stream (3 endpoints)
- tts_scripts.py: tutor-script (1 endpoint)
- tts_tutor.py: knowledge, course/chapter context (3 endpoints)
- tts_pronunciation.py: pronunciations CRUD + AI (3 endpoints)

Total: 13 user endpoints
"""

from .audio_stt import audio_stt_bp
from .audio_analysis import audio_analysis_bp
from .tts_synthesis import tts_synthesis_bp
from .tts_scripts import tts_scripts_bp
from .tts_tutor import tts_tutor_bp
from .tts_pronunciation import tts_pronunciation_bp

__all__ = [
    'audio_stt_bp',
    'audio_analysis_bp',
    'tts_synthesis_bp',
    'tts_scripts_bp',
    'tts_tutor_bp',
    'tts_pronunciation_bp',
]
