"""
TTS Service

Provides text-to-speech functionality with:
- Pronunciation corrections from database
- AI-generated pronunciations for unknown words
- Caching of generated audio
"""

import re
import hashlib
from typing import Optional, Dict, Any, List, Tuple
from app.repositories.tts_repository import TTSRepository
from app.services.ai_adapter import AIAdapter
import logging

logger = logging.getLogger(__name__)


class TTSService:
    """Service for Text-to-Speech with intelligent pronunciation."""

    # Fallback pronunciations if DB is not available
    FALLBACK_PRONUNCIATIONS = {
        'de': {
            '€': ' Euro ',
            '$': ' Dollar ',
            '%': ' Prozent ',
            '×': ' mal ',
            '÷': ' geteilt durch ',
            '+': ' plus ',
            '−': ' minus ',
            '=': ' gleich ',
        }
    }

    # Pattern replacements (regex-based)
    PATTERN_REPLACEMENTS = {
        'de': [
            # Numbers with decimals: "35.67" -> "35 Komma 67"
            (r'(\d+)[.,](\d+)', r'\1 Komma \2'),
            # Large numbers: add spaces for better pronunciation
            (r'(\d)(\d{3})(?!\d)', r'\1 \2'),
            # Sentence pauses
            (r'\. ', '. , '),
            (r'! ', '! , '),
            (r'\? ', '? , '),
        ]
    }

    _pronunciation_cache: Dict[str, Dict[str, str]] = {}
    _cache_loaded: bool = False

    @classmethod
    def load_pronunciations(cls, language: str = 'de', force_reload: bool = False) -> Dict[str, str]:
        """Load all pronunciations from database into memory cache."""
        cache_key = language

        if not force_reload and cache_key in cls._pronunciation_cache:
            return cls._pronunciation_cache[cache_key]

        try:
            pronunciations = TTSRepository.get_all_pronunciations(language=language)
            cls._pronunciation_cache[cache_key] = {
                p['original_word'].lower(): p['phonetic_spelling']
                for p in pronunciations
            }
            cls._cache_loaded = True
            logger.info(f"Loaded {len(cls._pronunciation_cache[cache_key])} pronunciations for {language}")
        except Exception as e:
            logger.warning(f"Failed to load pronunciations from DB: {e}")
            cls._pronunciation_cache[cache_key] = {}

        return cls._pronunciation_cache.get(cache_key, {})

    @classmethod
    def preprocess_text(cls, text: str, language: str = 'de') -> str:
        """
        Preprocess text for better TTS pronunciation.

        1. Load pronunciations from database
        2. Apply word replacements
        3. Apply pattern replacements
        4. Request AI for unknown difficult words
        """
        if not text:
            return text

        # Load pronunciations from DB
        pronunciations = cls.load_pronunciations(language)

        # Apply fallback symbol replacements
        processed = text
        for symbol, replacement in cls.FALLBACK_PRONUNCIATIONS.get(language, {}).items():
            processed = processed.replace(symbol, replacement)

        # Apply pattern replacements (regex)
        for pattern, replacement in cls.PATTERN_REPLACEMENTS.get(language, []):
            processed = re.sub(pattern, replacement, processed)

        # Apply word-by-word replacements from DB
        # Sort by length (longest first) to handle compound words correctly
        sorted_words = sorted(pronunciations.keys(), key=len, reverse=True)

        for word in sorted_words:
            phonetic = pronunciations[word]
            # Case-insensitive replacement with word boundaries
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            processed = pattern.sub(phonetic, processed)

        # Find potentially difficult words that aren't in DB
        difficult_words = cls._find_difficult_words(processed, language, pronunciations)
        if difficult_words:
            # Queue them for AI processing (async)
            cls._queue_ai_pronunciation_requests(difficult_words, language)

        # Clean up multiple spaces
        processed = re.sub(r'\s+', ' ', processed).strip()

        return processed

    @classmethod
    def _find_difficult_words(
        cls,
        text: str,
        language: str,
        known_pronunciations: Dict[str, str]
    ) -> List[str]:
        """Find words that might need pronunciation help."""
        difficult_words = []

        # Extract words
        words = re.findall(r'\b[A-Za-zÄÖÜäöüß]{8,}\b', text)  # Words 8+ chars

        for word in words:
            word_lower = word.lower()

            # Skip if already in pronunciations
            if word_lower in known_pronunciations:
                continue

            # Check for compound word indicators
            is_compound = (
                # German compound words often have these patterns
                any(part in word_lower for part in ['preis', 'kosten', 'rechnung', 'kalkulation'])
                or len(word) > 15
                or word[0].isupper()  # Nouns in German
            )

            if is_compound and word_lower not in difficult_words:
                difficult_words.append(word)

        return difficult_words[:10]  # Limit to 10 words per request

    @classmethod
    def _queue_ai_pronunciation_requests(cls, words: List[str], language: str) -> None:
        """Queue words for AI pronunciation generation (non-blocking)."""
        for word in words:
            try:
                # Check if not already in DB or pending
                if not TTSRepository.word_exists(word, language):
                    TTSRepository.add_ai_request(word=word, language=language)
            except Exception as e:
                logger.debug(f"Could not queue AI request for '{word}': {e}")

    @classmethod
    async def generate_pronunciation_with_ai(
        cls,
        word: str,
        language: str = 'de',
        context: Optional[str] = None
    ) -> Optional[str]:
        """
        Use AI to generate phonetic spelling for a word.

        Returns the phonetic spelling or None if failed.
        """
        prompt = f"""Du bist ein Experte für deutsche Aussprache und Text-to-Speech Systeme.

Ich brauche eine phonetische Schreibweise für das Wort "{word}", die von einem TTS-System (Piper mit deutscher Stimme) korrekt ausgesprochen wird.

Regeln:
1. Trenne zusammengesetzte Wörter mit Leerzeichen: "Listeneinkaufspreis" -> "Listen Einkaufs Preis"
2. Bei schwierigen Konsonanten, schreibe sie phonetisch: "Skonto" -> "Skonnto"
3. Bei Fremdwörtern, schreibe sie so wie sie im Deutschen gesprochen werden
4. Halte die Schreibweise einfach und lesbar

{f'Kontext: {context}' if context else ''}

Antworte NUR mit der phonetischen Schreibweise, ohne Erklärung.
"""

        try:
            result = await AIAdapter.generate_content_async(
                prompt=prompt,
                provider='openai',
                model='gpt-4o-mini',
                max_tokens=100,
                temperature=0.3
            )

            if result and result.get('success') and result.get('content'):
                phonetic = result['content'].strip().strip('"\'')

                # Validate: should be similar length, no special characters
                if len(phonetic) >= len(word) * 0.5 and len(phonetic) <= len(word) * 3:
                    return phonetic

        except Exception as e:
            logger.error(f"AI pronunciation generation failed for '{word}': {e}")

        return None

    @classmethod
    async def process_pending_ai_requests(cls, limit: int = 10) -> int:
        """Process pending AI pronunciation requests. Returns count of processed."""
        processed = 0

        try:
            pending = TTSRepository.get_pending_ai_requests(limit=limit)

            for request in pending:
                word = request['word']
                language = request['language']
                context = request.get('context')
                request_id = request['request_id']

                # Generate with AI
                phonetic = await cls.generate_pronunciation_with_ai(word, language, context)

                if phonetic:
                    # Add to pronunciations (not verified)
                    result = TTSRepository.add_pronunciation(
                        original_word=word,
                        phonetic_spelling=phonetic,
                        language=language,
                        source='ai_generated',
                        ai_model='gpt-4o-mini',
                        confidence=0.8
                    )

                    # Update request
                    TTSRepository.update_ai_request(
                        request_id=request_id,
                        status='completed',
                        suggested_spelling=phonetic,
                        pronunciation_id=result['pronunciation_id'] if result else None
                    )
                    processed += 1

                    # Invalidate cache
                    cls._pronunciation_cache.pop(language, None)
                else:
                    TTSRepository.update_ai_request(
                        request_id=request_id,
                        status='failed'
                    )

        except Exception as e:
            logger.error(f"Error processing AI requests: {e}")

        return processed

    @classmethod
    def get_pronunciation(cls, word: str, language: str = 'de') -> Optional[str]:
        """Get pronunciation for a single word."""
        pronunciations = cls.load_pronunciations(language)
        return pronunciations.get(word.lower())

    @classmethod
    def add_pronunciation(
        cls,
        word: str,
        phonetic: str,
        language: str = 'de',
        category: Optional[str] = None,
        word_type: Optional[str] = None
    ) -> bool:
        """Add a new pronunciation (manual entry)."""
        try:
            TTSRepository.add_pronunciation(
                original_word=word,
                phonetic_spelling=phonetic,
                language=language,
                category=category,
                word_type=word_type,
                source='manual'
            )
            # Invalidate cache
            cls._pronunciation_cache.pop(language, None)
            return True
        except Exception as e:
            logger.error(f"Failed to add pronunciation: {e}")
            return False

    @classmethod
    def search_pronunciations(
        cls,
        query: str,
        language: str = 'de',
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search pronunciations."""
        return TTSRepository.search_pronunciations(query, language, limit)

    @classmethod
    def get_stats(cls, language: str = 'de') -> Dict[str, Any]:
        """Get pronunciation statistics."""
        pronunciations = cls.load_pronunciations(language)
        categories = TTSRepository.get_categories(language)

        return {
            'total_pronunciations': len(pronunciations),
            'categories': categories,
            'cache_loaded': cls._cache_loaded
        }
