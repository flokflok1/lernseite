"""
LernsystemX TTS API - Core Configuration & Helpers

Configuration, constants, and preprocessing functions for Text-to-Speech.

ISO 27001:2013 compliant - TTS security and caching
"""

import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# OpenAI TTS is our PRIMARY engine - best quality, no GPU needed
logger.info("Using OpenAI TTS as primary TTS engine")

# =============================================================================
# VOICE CONFIGURATION
# =============================================================================

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

# =============================================================================
# LIMITS & CONSTRAINTS
# =============================================================================

# Text length limits per provider
MAX_TEXT_LENGTH = {
    'edge': 10000,
    'openai': 4096,
    'default': 4096
}

# Speed limits
MIN_SPEED = 0.5
MAX_SPEED = 2.0

# =============================================================================
# TTS SERVICE INTEGRATION
# =============================================================================

# Try to import TTS Service for pronunciation
try:
    from app.application.services.media_cache.tts_service import TTSService
    TTS_SERVICE_AVAILABLE = True
except ImportError:
    TTS_SERVICE_AVAILABLE = False
    logger.warning("TTSService not available, using basic preprocessing")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def basic_preprocess(text: str, language: str = 'de') -> str:
    """
    Basic text preprocessing fallback when TTSService is not available.

    Handles German language-specific preprocessing:
    - Symbol replacements (€, $, %, etc.)
    - Abbreviation expansion
    - Compound word separation
    - Decimal number formatting
    - Pause insertion after sentences

    Args:
        text: Input text to preprocess
        language: Language code (default: 'de' for German)

    Returns:
        Preprocessed text suitable for TTS
    """
    if language != 'de':
        return text

    processed = text

    # Basic German replacements
    replacements = {
        '€': ' Euro ',
        '$': ' Dollar ',
        '%': ' Prozent ',
        '×': ' mal ',
        '÷': ' geteilt durch ',
        '+': ' plus ',
        '−': ' minus ',
        '=': ' gleich ',
        # Common compound words
        'Listeneinkaufspreis': 'Listen Einkaufs Preis',
        'Zieleinkaufspreis': 'Ziel Einkaufs Preis',
        'Bareinkaufspreis': 'Bar Einkaufs Preis',
        'Bezugskalkulation': 'Bezugs Kalkulation',
        'Handelskalkulation': 'Handels Kalkulation',
        'Verkaufspreis': 'Verkaufs Preis',
        'Selbstkostenpreis': 'Selbstkosten Preis',
        'Bezugskosten': 'Bezugs Kosten',
        'Lieferantenrabatt': 'Lieferannten Rabbatt',
        'Rabatt': 'Rabbatt',
        'Skonto': 'Skonnto',
        'Kalkulation': 'Kalkullazion',
        'Lieferant': 'Lieferannt',
        # Abbreviations
        'LEP': 'Listen Einkaufs Preis',
        'ZEP': 'Ziel Einkaufs Preis',
        'BEP': 'Bar Einkaufs Preis',
        'VKP': 'Verkaufs Preis',
        'MwSt': 'Mehrwertsteuer',
        'z.B.': 'zum Beispiel',
        'd.h.': 'das heisst',
        'bzw.': 'beziehungsweise',
        'ca.': 'zirka',
        'inkl.': 'inklusive',
        'exkl.': 'exklusive',
        'zzgl.': 'zuzueglich',
        'abzgl.': 'abzueglich',
    }

    # Apply replacements (case-insensitive for words)
    for original, replacement in replacements.items():
        if len(original) > 2:  # Word replacement
            pattern = re.compile(r'\b' + re.escape(original) + r'\b', re.IGNORECASE)
            processed = pattern.sub(replacement, processed)
        else:  # Symbol replacement
            processed = processed.replace(original, replacement)

    # Number with decimals: "35.67" -> "35 Komma 67"
    processed = re.sub(r'(\d+)[.,](\d+)', r'\1 Komma \2', processed)

    # Add pauses after sentences
    processed = re.sub(r'\. ', '. , ', processed)

    # Clean up multiple spaces
    processed = re.sub(r'\s+', ' ', processed).strip()

    return processed


def get_voice_info(voice: str) -> Tuple[str, str, str]:
    """
    Get voice provider and voice_id from voice name.

    Args:
        voice: Voice name (e.g., 'nova', 'echo', 'alloy')

    Returns:
        Tuple of (provider, voice_id, display_name)

    Example:
        >>> get_voice_info('nova')
        ('openai', 'nova', 'Nova')
    """
    # Check OpenAI voices
    if voice in AVAILABLE_VOICES['openai']:
        info = AVAILABLE_VOICES['openai'][voice]
        return ('openai', voice, info['name'])

    # Default to OpenAI Nova
    return ('openai', 'nova', 'Nova')


def preprocess_text(text: str, language: str = 'de') -> str:
    """
    Preprocess text for TTS using service or fallback.

    Attempts to use TTSService if available, falls back to basic_preprocess.

    Args:
        text: Input text to preprocess
        language: Language code (default: 'de' for German)

    Returns:
        Preprocessed text
    """
    if TTS_SERVICE_AVAILABLE:
        try:
            return TTSService.preprocess_text(text, language)
        except Exception as e:
            logger.warning(f"TTS preprocessing failed, using fallback: {e}")

    return basic_preprocess(text, language)


__all__ = [
    'AVAILABLE_VOICES',
    'DEFAULT_TUTOR_VOICE',
    'DEFAULT_PROVIDER',
    'DEFAULT_MODEL',
    'VALID_TTS_MODELS',
    'MAX_TEXT_LENGTH',
    'MIN_SPEED',
    'MAX_SPEED',
    'TTS_SERVICE_AVAILABLE',
    'basic_preprocess',
    'get_voice_info',
    'preprocess_text',
]
