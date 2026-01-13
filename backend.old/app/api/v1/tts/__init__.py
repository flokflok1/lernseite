"""
LernsystemX TTS API Package.

Text-to-Speech endpoints with caching, voice management, and pronunciation rules.
Refactored from monolithic tts.py (993 lines) into focused modules.

Modules:
    - config: Constants, voices, default settings (~45 LOC)
    - helpers: Text preprocessing, voice lookup utilities (~137 LOC)
    - synthesis: /tts/speak, /tts/audio/<id>, /tts/speak-stream (~328 LOC)
    - voices: /tts/voices (~114 LOC)
    - scripts: /tts/tutor-script (~157 LOC)
    - tutor: /tutor/knowledge, /tutor/course/<id>/context, /tutor/chapter/<id>/context (~188 LOC)
    - pronunciation: /tts/pronunciations (GET/POST), /tts/pronunciations/ai (~206 LOC)

Route Registration:
    Blueprint registration is handled by the bridge module (../tts.py).
    Do NOT register blueprints here to avoid double registration.

Refactored: 2026-01-07 per Developer-Guide-KI Section 10
"""

from .synthesis import tts_synthesis_bp
from .voices import tts_voices_bp
from .scripts import tts_scripts_bp
from .tutor import tts_tutor_bp
from .pronunciation import tts_pronunciation_bp

# All blueprints in this package
# NOTE: Registration is done in ../tts.py (bridge module)
ALL_BLUEPRINTS = [
    tts_synthesis_bp,
    tts_voices_bp,
    tts_scripts_bp,
    tts_tutor_bp,
    tts_pronunciation_bp,
]

# Re-export config for convenience
from .config import (
    AVAILABLE_VOICES,
    DEFAULT_TUTOR_VOICE,
    DEFAULT_PROVIDER,
    DEFAULT_MODEL,
    VALID_TTS_MODELS,
)

# Export all blueprints and config for direct import
__all__ = [
    'tts_synthesis_bp',
    'tts_voices_bp',
    'tts_scripts_bp',
    'tts_tutor_bp',
    'tts_pronunciation_bp',
    'ALL_BLUEPRINTS',
    'AVAILABLE_VOICES',
    'DEFAULT_TUTOR_VOICE',
    'DEFAULT_PROVIDER',
    'DEFAULT_MODEL',
    'VALID_TTS_MODELS',
]
