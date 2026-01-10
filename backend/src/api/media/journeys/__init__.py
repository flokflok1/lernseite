"""
Media Domain - Journeys Layer

Journeys organize routes by user type/flow:
- public: Media capabilities info (formats, voices) - 2 endpoints
- user: Audio STT + TTS synthesis - 13 endpoints

Total: 15 endpoints

Architecture: Journey-Based DDD
"""

from src.api.media.journeys.public.api.routes import (
    media_info_bp,
)
from src.api.media.journeys.user.api.routes import (
    audio_stt_bp,
    audio_analysis_bp,
    tts_synthesis_bp,
    tts_scripts_bp,
    tts_tutor_bp,
    tts_pronunciation_bp,
)

ALL_JOURNEY_BLUEPRINTS = [
    # Public Journey (2 endpoints)
    media_info_bp,
    # User Journey (13 endpoints)
    audio_stt_bp,
    audio_analysis_bp,
    tts_synthesis_bp,
    tts_scripts_bp,
    tts_tutor_bp,
    tts_pronunciation_bp,
]

__all__ = ['ALL_JOURNEY_BLUEPRINTS']
