"""
TTS Configuration and Constants.

Centralized configuration for TTS voices, models, and defaults.
"""

import logging

logger = logging.getLogger(__name__)

# OpenAI TTS is our PRIMARY engine - best quality, no GPU needed
logger.info("Using OpenAI TTS as primary TTS engine")

# Available voices - OpenAI TTS (best quality)
AVAILABLE_VOICES = {
    'openai': {
        # OpenAI TTS-1 voices
        'alloy': {'name': 'Alloy', 'gender': 'neutral', 'style': 'balanced', 'model': 'tts-1'},
        'echo': {'name': 'Echo', 'gender': 'male', 'style': 'warm', 'model': 'tts-1'},
        'fable': {'name': 'Fable', 'gender': 'neutral', 'style': 'expressive', 'model': 'tts-1'},
        'onyx': {'name': 'Onyx', 'gender': 'male', 'style': 'deep', 'model': 'tts-1'},
        'nova': {'name': 'Nova', 'gender': 'female', 'style': 'friendly', 'model': 'tts-1'},
        'shimmer': {'name': 'Shimmer', 'gender': 'female', 'style': 'soft', 'model': 'tts-1'},
    }
}

# Default tutor voice (OpenAI Nova - friendly female voice)
DEFAULT_TUTOR_VOICE = 'nova'
DEFAULT_PROVIDER = 'openai'
DEFAULT_MODEL = 'tts-1'  # or 'tts-1-hd' for higher quality

# Valid OpenAI TTS models
VALID_TTS_MODELS = ['tts-1', 'tts-1-hd']

# Text length limits per provider
MAX_TEXT_LENGTH = {
    'edge': 10000,
    'openai': 4096,
    'default': 4096
}

# Speed limits
MIN_SPEED = 0.5
MAX_SPEED = 2.0
