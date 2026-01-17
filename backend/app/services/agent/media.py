"""
Agent Media Operations - Audio/voice responses and transcription

Handles:
- TTS audio response generation with caching
- User audio transcription
- Voice conversation turns
- Media cost tracking
"""

import logging
from typing import Dict, Any, Optional

from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)


class MediaOperations:
    """
    Manages media-based agent interactions (audio/TTS).
    """

    @staticmethod
    def ask_with_audio(
        course_id: str,
        user_id: str,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        language: str = 'de',
        organization_id: Optional[str] = None,
        voice: str = 'nova',
        speech_speed: float = 1.0,
        ask_func=None  # Injected ask() function to avoid circular imports
    ) -> Dict[str, Any]:
        """
        Ask agent with TTS audio response (Cache-First for both text AND audio).

        This method first gets the text answer (with caching), then gets
        or generates TTS audio for that answer (also with caching).

        Args:
            course_id: Course UUID
            user_id: User UUID
            question: User's question
            context: Optional context
            language: Response language
            organization_id: Optional org UUID
            voice: TTS voice (nova, alloy, echo, fable, onyx, shimmer)
            speech_speed: Speech speed (0.25-4.0)
            ask_func: Injected ask() function

        Returns:
            {
                'answer': str,
                'source': str,
                'tokens_used': int,
                'tokens_saved': int,
                'audio_url': str,
                'audio_from_cache': bool,
                'audio_duration_ms': int,
                'tts_cost_saved': float
            }
        """
        # Import here to avoid circular import
        from app.services.media_cache import MediaCacheService

        # Guard: ask_func is required
        if not ask_func:
            logger.error("ask_func not provided to ask_with_audio")
            return {
                'answer': '',
                'source': 'error',
                'error': 'Internal error: ask_func not provided',
                'tokens_used': 0,
                'tokens_saved': 0,
                'audio_error': 'Failed to process request'
            }

        # First get text answer (with caching)
        result = ask_func(
            course_id=course_id,
            user_id=user_id,
            question=question,
            context=context,
            language=language,
            organization_id=organization_id
        )

        # If error or no answer, return without audio
        if result.get('source') == 'error' or not result.get('answer'):
            return result

        # Get or generate TTS audio (with caching)
        try:
            audio_result = MediaCacheService.get_agent_response_with_audio(
                agent_id=result.get('agent_id', ''),
                text_response=result['answer'],
                voice=voice,
                speed=speech_speed
            )

            # Merge results
            result.update({
                'audio_url': audio_result.get('audio_url'),
                'audio_path': audio_result.get('audio_path'),
                'audio_from_cache': audio_result.get('audio_from_cache', False),
                'audio_duration_ms': audio_result.get('duration_ms', 0),
                'tts_cost': audio_result.get('tts_cost', 0),
                'tts_cost_saved': audio_result.get('tts_saved', 0)
            })

        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            # Return text-only response
            result['audio_error'] = str(e)

        return result

    @staticmethod
    def transcribe_user_audio(
        audio_path: str,
        agent_id: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe user audio input with caching.

        Useful for voice-based questions. The transcript is cached
        so identical audio files don't need re-transcription.

        Args:
            audio_path: Path to audio file
            agent_id: Optional agent UUID for context
            language: Optional language hint

        Returns:
            {
                'text': str,
                'from_cache': bool,
                'language': str,
                'confidence': float
            }
        """
        from app.services.media_cache import MediaCacheService

        try:
            transcript, from_cache = MediaCacheService.get_or_generate_transcript(
                audio_path=audio_path,
                language=language
            )

            return {
                'text': transcript.get('text', ''),
                'from_cache': from_cache,
                'language': transcript.get('language', 'de'),
                'confidence': transcript.get('confidence'),
                'segments': transcript.get('segments', [])
            }

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {
                'text': '',
                'error': str(e),
                'from_cache': False
            }

    @staticmethod
    def voice_conversation_turn(
        course_id: str,
        user_id: str,
        audio_path: str,
        session: Dict[str, Any],
        voice: str = 'nova',
        language: str = 'de',
        ask_with_audio_func=None  # Injected ask_with_audio() function
    ) -> Dict[str, Any]:
        """
        Process a single turn in a voice conversation.

        1. Transcribe user audio (cached)
        2. Get agent text response (cached)
        3. Generate TTS response (cached)

        Args:
            course_id: Course UUID
            user_id: User UUID
            audio_path: Path to user's audio
            session: Session context from start_realtime_session
            voice: TTS voice
            language: Language
            ask_with_audio_func: Injected ask_with_audio() function

        Returns:
            {
                'user_text': str,
                'agent_text': str,
                'agent_audio_url': str,
                'transcription_from_cache': bool,
                'response_from_cache': bool,
                'tts_from_cache': bool,
                'turn_cost': float,
                'turn_saved': float
            }
        """
        turn_cost = 0.0
        turn_saved = 0.0

        # Step 1: Transcribe user audio
        transcript_result = MediaOperations.transcribe_user_audio(
            audio_path=audio_path,
            language=language
        )

        user_text = transcript_result.get('text', '')
        transcription_cached = transcript_result.get('from_cache', False)

        if transcription_cached:
            turn_saved += 0.006  # Estimated Whisper cost per minute
        else:
            turn_cost += 0.006

        # Step 2: Get agent response
        if not ask_with_audio_func:
            logger.error("ask_with_audio_func not provided to voice_conversation_turn")
            return {
                'user_text': user_text,
                'agent_text': '',
                'error': 'Internal error: ask_with_audio_func not provided',
                'turn_cost': turn_cost,
                'turn_saved': turn_saved
            }

        agent_result = ask_with_audio_func(
            course_id=course_id,
            user_id=user_id,
            question=user_text,
            language=language,
            voice=voice
        )

        response_cached = agent_result.get('source') in ['cache_hit', 'knowledge_match']
        tts_cached = agent_result.get('audio_from_cache', False)

        turn_saved += agent_result.get('tokens_saved', 0) * 0.00001  # Rough token cost
        turn_cost += agent_result.get('tokens_used', 0) * 0.00001
        turn_saved += agent_result.get('tts_cost_saved', 0)
        turn_cost += agent_result.get('tts_cost', 0)

        # Update session stats
        session['turns'].append({
            'user_text': user_text,
            'agent_text': agent_result.get('answer'),
            'transcription_cost': 0 if transcription_cached else 0.006,
            'ai_cost': turn_cost,
            'tts_cost': agent_result.get('tts_cost', 0)
        })

        if response_cached or tts_cached or transcription_cached:
            session['cache_hits'] += 1
        else:
            session['cache_misses'] += 1

        session['tokens_saved'] += agent_result.get('tokens_saved', 0)
        session['total_cost'] += turn_cost

        return {
            'user_text': user_text,
            'agent_text': agent_result.get('answer', ''),
            'agent_audio_url': agent_result.get('audio_url'),
            'agent_audio_path': agent_result.get('audio_path'),
            'transcription_from_cache': transcription_cached,
            'response_from_cache': response_cached,
            'tts_from_cache': tts_cached,
            'turn_cost': turn_cost,
            'turn_saved': turn_saved,
            'source': agent_result.get('source')
        }
