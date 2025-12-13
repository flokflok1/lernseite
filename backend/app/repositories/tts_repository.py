"""
TTS Pronunciation Repository

Handles database operations for TTS pronunciation data.
"""

from typing import Optional, List, Dict, Any
from app.repositories.base_repository import BaseRepository


class TTSRepository(BaseRepository):
    """Repository for TTS pronunciation operations."""

    @staticmethod
    def get_all_pronunciations(language: str = 'de', verified_only: bool = True) -> List[Dict[str, Any]]:
        """Get all pronunciation rules for a language."""
        query = """
            SELECT
                pronunciation_id,
                original_word,
                phonetic_spelling,
                language,
                category,
                word_type,
                source,
                verified,
                usage_count
            FROM tts_pronunciations
            WHERE language = %s
        """
        params = [language]

        if verified_only:
            query += " AND verified = true"

        query += " ORDER BY usage_count DESC, original_word"

        return TTSRepository.fetch_all(query, tuple(params)) or []

    @staticmethod
    def get_pronunciation(word: str, language: str = 'de') -> Optional[Dict[str, Any]]:
        """Get pronunciation for a specific word."""
        query = """
            SELECT
                pronunciation_id,
                original_word,
                phonetic_spelling,
                language,
                category,
                word_type
            FROM tts_pronunciations
            WHERE LOWER(original_word) = LOWER(%s)
              AND language = %s
        """
        result = TTSRepository.fetch_one(query, (word, language))

        # Update usage stats
        if result:
            TTSRepository.increment_usage(word, language)

        return result

    @staticmethod
    def get_pronunciations_bulk(words: List[str], language: str = 'de') -> Dict[str, str]:
        """Get pronunciations for multiple words at once."""
        if not words:
            return {}

        # Create placeholders for IN clause
        placeholders = ','.join(['LOWER(%s)' for _ in words])
        query = f"""
            SELECT original_word, phonetic_spelling
            FROM tts_pronunciations
            WHERE LOWER(original_word) IN ({placeholders})
              AND language = %s
              AND verified = true
        """
        params = [w.lower() for w in words] + [language]

        results = TTSRepository.fetch_all(query, tuple(params)) or []

        # Convert to dict (lowercase keys for easy lookup)
        return {r['original_word'].lower(): r['phonetic_spelling'] for r in results}

    @staticmethod
    def increment_usage(word: str, language: str = 'de') -> None:
        """Increment usage count for a word."""
        query = """
            UPDATE tts_pronunciations
            SET usage_count = usage_count + 1,
                last_used_at = CURRENT_TIMESTAMP
            WHERE LOWER(original_word) = LOWER(%s)
              AND language = %s
        """
        TTSRepository.execute(query, (word, language))

    @staticmethod
    def add_pronunciation(
        original_word: str,
        phonetic_spelling: str,
        language: str = 'de',
        category: Optional[str] = None,
        word_type: Optional[str] = None,
        source: str = 'manual',
        ai_model: Optional[str] = None,
        confidence: float = 1.0,
        created_by: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Add a new pronunciation rule."""
        query = """
            INSERT INTO tts_pronunciations (
                original_word, phonetic_spelling, language, category,
                word_type, source, ai_model, confidence, verified, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (original_word, language) DO UPDATE SET
                phonetic_spelling = EXCLUDED.phonetic_spelling,
                category = COALESCE(EXCLUDED.category, tts_pronunciations.category),
                word_type = COALESCE(EXCLUDED.word_type, tts_pronunciations.word_type),
                updated_at = CURRENT_TIMESTAMP
            RETURNING pronunciation_id, original_word, phonetic_spelling
        """
        # AI-generated entries are not verified by default
        verified = source == 'manual'

        return TTSRepository.fetch_one(query, (
            original_word, phonetic_spelling, language, category,
            word_type, source, ai_model, confidence, verified, created_by
        ))

    @staticmethod
    def add_ai_request(
        word: str,
        language: str = 'de',
        context: Optional[str] = None,
        requested_by: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Log an AI pronunciation request."""
        query = """
            INSERT INTO tts_ai_requests (word, language, context, requested_by)
            VALUES (%s, %s, %s, %s)
            RETURNING request_id
        """
        return TTSRepository.fetch_one(query, (word, language, context, requested_by))

    @staticmethod
    def update_ai_request(
        request_id: str,
        status: str,
        ai_response: Optional[Dict] = None,
        suggested_spelling: Optional[str] = None,
        pronunciation_id: Optional[str] = None
    ) -> None:
        """Update an AI request with results."""
        import json
        query = """
            UPDATE tts_ai_requests
            SET status = %s,
                ai_response = %s,
                suggested_spelling = %s,
                pronunciation_id = %s,
                processed_at = CURRENT_TIMESTAMP
            WHERE request_id = %s
        """
        TTSRepository.execute(query, (
            status,
            json.dumps(ai_response) if ai_response else None,
            suggested_spelling,
            pronunciation_id,
            request_id
        ))

    @staticmethod
    def get_pending_ai_requests(limit: int = 10) -> List[Dict[str, Any]]:
        """Get pending AI requests for processing."""
        query = """
            SELECT request_id, word, language, context
            FROM tts_ai_requests
            WHERE status = 'pending'
            ORDER BY created_at
            LIMIT %s
        """
        return TTSRepository.fetch_all(query, (limit,)) or []

    @staticmethod
    def word_exists(word: str, language: str = 'de') -> bool:
        """Check if a word already has a pronunciation entry."""
        query = """
            SELECT 1 FROM tts_pronunciations
            WHERE LOWER(original_word) = LOWER(%s) AND language = %s
        """
        return TTSRepository.fetch_one(query, (word, language)) is not None

    @staticmethod
    def get_categories(language: str = 'de') -> List[str]:
        """Get all categories for a language."""
        query = """
            SELECT DISTINCT category
            FROM tts_pronunciations
            WHERE language = %s AND category IS NOT NULL
            ORDER BY category
        """
        results = TTSRepository.fetch_all(query, (language,)) or []
        return [r['category'] for r in results]

    @staticmethod
    def search_pronunciations(
        search_term: str,
        language: str = 'de',
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search pronunciations by word."""
        query = """
            SELECT
                pronunciation_id,
                original_word,
                phonetic_spelling,
                category,
                word_type,
                verified
            FROM tts_pronunciations
            WHERE language = %s
              AND (
                  LOWER(original_word) LIKE LOWER(%s)
                  OR LOWER(phonetic_spelling) LIKE LOWER(%s)
              )
            ORDER BY
                CASE WHEN LOWER(original_word) = LOWER(%s) THEN 0 ELSE 1 END,
                usage_count DESC
            LIMIT %s
        """
        search_pattern = f'%{search_term}%'
        return TTSRepository.fetch_all(query, (
            language, search_pattern, search_pattern, search_term, limit
        )) or []
