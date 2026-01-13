"""
TTS Helper Functions.

Shared utility functions for text preprocessing and voice lookup.
"""

import re
import logging
from typing import Tuple

from .config import AVAILABLE_VOICES

logger = logging.getLogger(__name__)

# Try to import TTS Service for pronunciation
try:
    from app.services.tts_service import TTSService
    TTS_SERVICE_AVAILABLE = True
except ImportError:
    TTS_SERVICE_AVAILABLE = False
    logger.warning("TTSService not available, using basic preprocessing")


def basic_preprocess(text: str, language: str = 'de') -> str:
    """
    Basic text preprocessing fallback when TTSService is not available.

    Args:
        text: Raw text to preprocess
        language: Language code (default: 'de')

    Returns:
        Preprocessed text optimized for TTS
    """
    if language != 'de':
        return text

    processed = text

    # Basic German replacements
    replacements = {
        '\u20ac': ' Euro ',
        '$': ' Dollar ',
        '%': ' Prozent ',
        '\u00d7': ' mal ',
        '\u00f7': ' geteilt durch ',
        '+': ' plus ',
        '\u2212': ' minus ',
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
        voice: Voice identifier string

    Returns:
        Tuple of (provider, voice_id, display_name)
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

    Args:
        text: Raw text to preprocess
        language: Language code

    Returns:
        Preprocessed text
    """
    if TTS_SERVICE_AVAILABLE:
        try:
            return TTSService.preprocess_text(text, language)
        except Exception as e:
            logger.warning(f"TTS preprocessing failed, using fallback: {e}")

    return basic_preprocess(text, language)
