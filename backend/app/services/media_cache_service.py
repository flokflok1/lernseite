"""
LernsystemX Media Cache Service

Intelligent caching for AI-generated media:
- TTS Audio (Text-to-Speech responses)
- Video Explanations (Avatar/Animation)
- Transcripts (Whisper/Deepgram)
- Realtime Session Recordings

Cost Savings Example:
- TTS: $0.015/1000 chars
- 1000 users asking "Was ist OOP?" = 1000 TTS generations = $15
- With cache: 1 TTS generation = $0.015 -> 99.9% savings

ISO 9001:2015 compliant - Media caching layer
"""

import os
import hashlib
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta

from app.services.cache_service import CacheService
from app.services.ai_adapter import AIAdapter
from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)

# Default TTLs
TTS_CACHE_TTL = 30 * 24 * 3600      # 30 days
TRANSCRIPT_CACHE_TTL = 90 * 24 * 3600  # 90 days (transcripts rarely change)
VIDEO_CACHE_TTL = 60 * 24 * 3600    # 60 days

# Storage paths
MEDIA_BASE_PATH = os.getenv('MEDIA_CACHE_PATH', 'storage/media_cache')


class MediaCacheRepository(BaseRepository):
    """Repository for media cache database operations"""

    @staticmethod
    def get_tts_cache(
        text_hash: str,
        voice_id: str,
        voice_provider: str = 'openai',
        speed: float = 1.0
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached TTS audio

        Args:
            text_hash: SHA256 hash of text
            voice_id: Voice identifier
            voice_provider: TTS provider
            speed: Speech speed

        Returns:
            Cache entry or None
        """
        query = """
            SELECT
                amc.media_id,
                amc.storage_path,
                amc.file_size_bytes,
                amc.mime_type,
                amc.duration_ms,
                atc.tts_id,
                atc.text_content,
                atc.voice_id
            FROM agent_tts_cache atc
            JOIN agent_media_cache amc ON atc.media_id = amc.media_id
            WHERE atc.text_hash = %s
              AND atc.voice_id = %s
              AND atc.voice_provider = %s
              AND atc.speech_speed = %s
              AND amc.status = 'ready'
              AND (amc.expires_at IS NULL OR amc.expires_at > NOW())
        """
        result = MediaCacheRepository.fetch_one(query, (
            text_hash, voice_id, voice_provider, speed
        ))

        if result:
            # Update access stats
            MediaCacheRepository.execute("""
                UPDATE agent_media_cache
                SET access_count = access_count + 1, last_accessed_at = NOW()
                WHERE media_id = %s
            """, (result['media_id'],))

        return result

    @staticmethod
    def create_tts_cache(
        agent_id: Optional[str],
        text: str,
        voice_id: str,
        voice_provider: str,
        speed: float,
        storage_path: str,
        file_size: int,
        duration_ms: int,
        cost: float
    ) -> Dict[str, Any]:
        """Create TTS cache entry"""
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        content_hash = hashlib.sha256(f"{text}:{voice_id}:{speed}".encode()).hexdigest()

        # Create media cache entry
        media_query = """
            INSERT INTO agent_media_cache (
                agent_id, content_hash, media_type, source_type,
                source_text, storage_path, file_size_bytes,
                mime_type, duration_ms, generation_model, generation_cost,
                expires_at
            ) VALUES (
                %s, %s, 'tts_audio', 'answer_text',
                %s, %s, %s,
                'audio/mpeg', %s, %s, %s,
                NOW() + INTERVAL '%s seconds'
            )
            RETURNING media_id
        """
        media_result = MediaCacheRepository.fetch_one(media_query, (
            agent_id, content_hash, text, storage_path, file_size,
            duration_ms, f"{voice_provider}/{voice_id}", cost, TTS_CACHE_TTL
        ))

        # Create TTS-specific entry
        tts_query = """
            INSERT INTO agent_tts_cache (
                media_id, text_hash, text_content, text_language,
                char_count, voice_id, voice_provider, speech_speed,
                total_cost
            ) VALUES (
                %s, %s, %s, 'de', %s, %s, %s, %s, %s
            )
            RETURNING *
        """
        return MediaCacheRepository.fetch_one(tts_query, (
            media_result['media_id'], text_hash, text, len(text),
            voice_id, voice_provider, speed, cost
        ))

    @staticmethod
    def get_transcript_cache(file_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get cached transcript

        Args:
            file_hash: SHA256 hash of audio file

        Returns:
            Transcript data or None
        """
        query = """
            SELECT
                atc.transcript_id,
                atc.transcript_text,
                atc.segments,
                atc.word_timestamps,
                atc.confidence_score,
                atc.transcript_language,
                amc.media_id,
                amc.access_count
            FROM agent_transcript_cache atc
            LEFT JOIN agent_media_cache amc ON atc.media_id = amc.media_id
            WHERE atc.source_file_hash = %s
        """
        result = MediaCacheRepository.fetch_one(query, (file_hash,))

        if result and result.get('media_id'):
            MediaCacheRepository.execute("""
                UPDATE agent_media_cache
                SET access_count = access_count + 1, last_accessed_at = NOW()
                WHERE media_id = %s
            """, (result['media_id'],))

        return result

    @staticmethod
    def create_transcript_cache(
        file_hash: str,
        file_path: str,
        duration_ms: int,
        transcript_text: str,
        segments: list,
        language: str,
        model: str,
        cost: float,
        confidence: float = None
    ) -> Dict[str, Any]:
        """Create transcript cache entry"""

        # Create media cache entry first
        media_query = """
            INSERT INTO agent_media_cache (
                content_hash, media_type, source_type,
                storage_path, duration_ms, generation_model,
                generation_cost, expires_at, never_expire
            ) VALUES (
                %s, 'transcript', 'audio_file',
                %s, %s, %s, %s,
                NOW() + INTERVAL '%s seconds', TRUE
            )
            RETURNING media_id
        """
        media_result = MediaCacheRepository.fetch_one(media_query, (
            file_hash, file_path, duration_ms, model, cost, TRANSCRIPT_CACHE_TTL
        ))

        # Create transcript entry
        transcript_query = """
            INSERT INTO agent_transcript_cache (
                media_id, source_file_hash, source_file_path,
                source_duration_ms, transcript_text, transcript_language,
                segments, confidence_score, model_used, total_cost
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s
            )
            RETURNING *
        """
        import json
        return MediaCacheRepository.fetch_one(transcript_query, (
            media_result['media_id'], file_hash, file_path,
            duration_ms, transcript_text, language,
            json.dumps(segments), confidence, model, cost
        ))

    @staticmethod
    def get_media_stats(agent_id: str) -> Dict[str, Any]:
        """Get media cache statistics for an agent"""
        query = """
            SELECT * FROM v_agent_media_stats
            WHERE agent_id = %s
        """
        return MediaCacheRepository.fetch_one(query, (agent_id,))

    @staticmethod
    def log_realtime_session(
        agent_id: str,
        user_id: str,
        session_type: str,
        duration_ms: int,
        stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Log a realtime session"""
        query = """
            INSERT INTO agent_realtime_sessions (
                agent_id, user_id, session_type,
                ended_at, duration_ms,
                total_turns, user_audio_duration_ms, agent_audio_duration_ms,
                transcription_cost, tts_cost, ai_cost, total_cost,
                responses_from_cache, responses_generated, tokens_saved
            ) VALUES (
                %s, %s, %s,
                NOW(), %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s
            )
            RETURNING *
        """
        return MediaCacheRepository.fetch_one(query, (
            agent_id, user_id, session_type,
            duration_ms,
            stats.get('total_turns', 0),
            stats.get('user_audio_ms', 0),
            stats.get('agent_audio_ms', 0),
            stats.get('transcription_cost', 0),
            stats.get('tts_cost', 0),
            stats.get('ai_cost', 0),
            stats.get('total_cost', 0),
            stats.get('cache_hits', 0),
            stats.get('cache_misses', 0),
            stats.get('tokens_saved', 0)
        ))


class MediaCacheService:
    """
    Media Cache Service for TTS, Transcripts, and Video

    Usage:
        >>> # TTS with caching
        >>> audio_path, from_cache = MediaCacheService.get_or_generate_tts(
        ...     text="Polymorphismus bedeutet...",
        ...     voice='nova',
        ...     agent_id='uuid'
        ... )
        >>> print(f"From cache: {from_cache}")

        >>> # Transcript with caching
        >>> transcript = MediaCacheService.get_or_generate_transcript(
        ...     audio_path='/path/to/audio.mp3'
        ... )
    """

    # Voice mappings
    VOICES = {
        'openai': ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'],
        'elevenlabs': ['rachel', 'domi', 'bella', 'antoni', 'elli', 'josh'],
    }

    # =========================================================================
    # TTS Caching
    # =========================================================================

    @staticmethod
    def get_or_generate_tts(
        text: str,
        voice: str = 'nova',
        voice_provider: str = 'openai',
        speed: float = 1.0,
        agent_id: Optional[str] = None
    ) -> Tuple[str, bool, Dict[str, Any]]:
        """
        Get TTS audio from cache or generate new

        Args:
            text: Text to convert to speech
            voice: Voice ID
            voice_provider: TTS provider
            speed: Speech speed (0.25-4.0)
            agent_id: Optional agent UUID

        Returns:
            Tuple of (audio_path, from_cache, metadata)
        """
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        # Check Redis cache first (for hot data)
        redis_key = CacheService.make_key('TTS', text_hash[:16], voice, str(speed))
        cached_path = CacheService.cache_get(redis_key)

        if cached_path and os.path.exists(cached_path):
            logger.info(f"TTS Redis cache hit: {redis_key}")
            return cached_path, True, {'source': 'redis_cache'}

        # Check PostgreSQL cache
        db_cache = MediaCacheRepository.get_tts_cache(
            text_hash=text_hash,
            voice_id=voice,
            voice_provider=voice_provider,
            speed=speed
        )

        if db_cache and os.path.exists(db_cache['storage_path']):
            # Found in DB, add to Redis for faster access
            CacheService.cache_set(redis_key, db_cache['storage_path'], ttl=7200)
            logger.info(f"TTS DB cache hit: {db_cache['media_id']}")
            return db_cache['storage_path'], True, {
                'source': 'db_cache',
                'media_id': db_cache['media_id'],
                'access_count': db_cache.get('access_count', 0)
            }

        # Generate new TTS
        logger.info(f"TTS cache miss, generating: {text[:50]}...")

        try:
            audio_bytes = AIAdapter.text_to_speech(
                text=text,
                voice=voice,
                model='tts-1',
                speed=speed
            )

            # Save to file
            storage_path = MediaCacheService._save_tts_file(
                audio_bytes, text_hash, voice
            )

            # Calculate cost (OpenAI TTS: $0.015 per 1000 chars)
            cost = (len(text) / 1000) * 0.015

            # Estimate duration (rough: 150 words/min, 5 chars/word)
            duration_ms = int((len(text) / 5 / 150) * 60 * 1000)

            # Save to database
            cache_entry = MediaCacheRepository.create_tts_cache(
                agent_id=agent_id,
                text=text,
                voice_id=voice,
                voice_provider=voice_provider,
                speed=speed,
                storage_path=storage_path,
                file_size=len(audio_bytes),
                duration_ms=duration_ms,
                cost=cost
            )

            # Add to Redis cache
            CacheService.cache_set(redis_key, storage_path, ttl=7200)

            return storage_path, False, {
                'source': 'generated',
                'media_id': cache_entry.get('media_id'),
                'cost': cost,
                'duration_ms': duration_ms
            }

        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            raise

    @staticmethod
    def _save_tts_file(audio_bytes: bytes, text_hash: str, voice: str) -> str:
        """Save TTS audio file to storage"""
        # Create directory structure
        storage_dir = Path(MEDIA_BASE_PATH) / 'tts' / text_hash[:2] / text_hash[2:4]
        storage_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{text_hash[:16]}_{voice}.mp3"
        file_path = storage_dir / filename

        with open(file_path, 'wb') as f:
            f.write(audio_bytes)

        return str(file_path)

    # =========================================================================
    # Transcript Caching
    # =========================================================================

    @staticmethod
    def get_or_generate_transcript(
        audio_path: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Tuple[Dict[str, Any], bool]:
        """
        Get transcript from cache or generate with Whisper

        Args:
            audio_path: Path to audio file
            language: Optional language hint
            prompt: Optional context prompt

        Returns:
            Tuple of (transcript_data, from_cache)
        """
        # Hash the file
        file_hash = MediaCacheService._hash_file(audio_path)

        # Check Redis cache
        redis_key = CacheService.make_key('TRANSCRIPT', file_hash[:16])
        cached_transcript = CacheService.cache_get(redis_key)

        if cached_transcript:
            logger.info(f"Transcript Redis cache hit: {redis_key}")
            return cached_transcript, True

        # Check PostgreSQL cache
        db_cache = MediaCacheRepository.get_transcript_cache(file_hash)

        if db_cache:
            result = {
                'text': db_cache['transcript_text'],
                'language': db_cache['transcript_language'],
                'segments': db_cache.get('segments', []),
                'confidence': db_cache.get('confidence_score')
            }
            # Add to Redis
            CacheService.cache_set(redis_key, result, ttl=86400)
            logger.info(f"Transcript DB cache hit: {db_cache['transcript_id']}")
            return result, True

        # Generate new transcript
        logger.info(f"Transcript cache miss, generating for: {audio_path}")

        try:
            result = AIAdapter.transcribe_audio(
                audio_path=audio_path,
                language=language,
                prompt=prompt
            )

            # Calculate cost (Whisper: $0.006 per minute)
            duration_minutes = result.get('duration', 0) / 60
            cost = duration_minutes * 0.006

            # Save to database
            MediaCacheRepository.create_transcript_cache(
                file_hash=file_hash,
                file_path=audio_path,
                duration_ms=int(result.get('duration', 0) * 1000),
                transcript_text=result['text'],
                segments=result.get('segments', []),
                language=result.get('language', language or 'de'),
                model='whisper-1',
                cost=cost,
                confidence=None
            )

            # Add to Redis
            CacheService.cache_set(redis_key, result, ttl=86400)

            return result, False

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise

    @staticmethod
    def _hash_file(file_path: str) -> str:
        """Generate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    # =========================================================================
    # Agent Response with Audio
    # =========================================================================

    @staticmethod
    def get_agent_response_with_audio(
        agent_id: str,
        text_response: str,
        voice: str = 'nova',
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """
        Get agent text response with cached TTS audio

        This is the main method for getting a complete response
        with both text and audio from cache.

        Args:
            agent_id: Agent UUID
            text_response: Text answer from agent
            voice: TTS voice
            speed: Speech speed

        Returns:
            {
                'text': str,
                'audio_path': str,
                'audio_from_cache': bool,
                'audio_url': str,
                'duration_ms': int
            }
        """
        audio_path, from_cache, meta = MediaCacheService.get_or_generate_tts(
            text=text_response,
            voice=voice,
            speed=speed,
            agent_id=agent_id
        )

        # Generate URL for frontend
        audio_url = f"/api/v1/media/tts/{meta.get('media_id', 'local')}"

        return {
            'text': text_response,
            'audio_path': audio_path,
            'audio_from_cache': from_cache,
            'audio_url': audio_url,
            'duration_ms': meta.get('duration_ms', 0),
            'tts_cost': meta.get('cost', 0) if not from_cache else 0,
            'tts_saved': meta.get('cost', 0.015 * len(text_response) / 1000) if from_cache else 0
        }

    # =========================================================================
    # Realtime Session Management
    # =========================================================================

    @staticmethod
    def start_realtime_session(
        agent_id: str,
        user_id: str,
        session_type: str = 'voice_chat'
    ) -> Dict[str, Any]:
        """
        Start a realtime voice/video session

        Returns session context for tracking cache hits/misses
        """
        return {
            'agent_id': agent_id,
            'user_id': user_id,
            'session_type': session_type,
            'started_at': datetime.now(),
            'turns': [],
            'cache_hits': 0,
            'cache_misses': 0,
            'tokens_saved': 0,
            'total_cost': 0
        }

    @staticmethod
    def end_realtime_session(session: Dict[str, Any]) -> Dict[str, Any]:
        """
        End realtime session and save stats

        Args:
            session: Session context from start_realtime_session

        Returns:
            Final session statistics
        """
        duration_ms = int((datetime.now() - session['started_at']).total_seconds() * 1000)

        # Calculate totals
        stats = {
            'total_turns': len(session.get('turns', [])),
            'user_audio_ms': sum(t.get('user_audio_ms', 0) for t in session.get('turns', [])),
            'agent_audio_ms': sum(t.get('agent_audio_ms', 0) for t in session.get('turns', [])),
            'transcription_cost': sum(t.get('transcription_cost', 0) for t in session.get('turns', [])),
            'tts_cost': sum(t.get('tts_cost', 0) for t in session.get('turns', [])),
            'ai_cost': sum(t.get('ai_cost', 0) for t in session.get('turns', [])),
            'total_cost': session.get('total_cost', 0),
            'cache_hits': session.get('cache_hits', 0),
            'cache_misses': session.get('cache_misses', 0),
            'tokens_saved': session.get('tokens_saved', 0)
        }

        # Log to database
        result = MediaCacheRepository.log_realtime_session(
            agent_id=session['agent_id'],
            user_id=session['user_id'],
            session_type=session['session_type'],
            duration_ms=duration_ms,
            stats=stats
        )

        return {
            'session_id': result.get('session_id'),
            'duration_ms': duration_ms,
            **stats
        }

    # =========================================================================
    # Cache Statistics
    # =========================================================================

    @staticmethod
    def get_cache_stats(agent_id: str) -> Dict[str, Any]:
        """Get comprehensive cache statistics for an agent"""
        db_stats = MediaCacheRepository.get_media_stats(agent_id)

        if not db_stats:
            return {
                'tts_cached': 0,
                'videos_cached': 0,
                'transcripts_cached': 0,
                'total_storage_mb': 0,
                'estimated_savings_eur': 0
            }

        return {
            'tts_cached': db_stats.get('tts_cached', 0),
            'tts_accesses': db_stats.get('tts_accesses', 0),
            'videos_cached': db_stats.get('videos_cached', 0),
            'video_accesses': db_stats.get('video_accesses', 0),
            'transcripts_cached': db_stats.get('transcripts_cached', 0),
            'total_storage_mb': round((db_stats.get('total_storage_bytes', 0) or 0) / 1024 / 1024, 2),
            'tts_generation_cost_eur': float(db_stats.get('tts_generation_cost', 0) or 0),
            'transcription_cost_eur': float(db_stats.get('transcription_cost', 0) or 0),
            'estimated_savings_eur': float(db_stats.get('estimated_savings', 0) or 0)
        }

    @staticmethod
    def cleanup_expired_media(days_expired: int = 7) -> int:
        """
        Clean up expired media files

        Args:
            days_expired: Only delete files expired for this many days

        Returns:
            Number of files deleted
        """
        query = """
            DELETE FROM agent_media_cache
            WHERE expires_at < NOW() - INTERVAL '%s days'
              AND never_expire = FALSE
            RETURNING storage_path
        """
        results = MediaCacheRepository.fetch_all(query, (days_expired,))

        deleted = 0
        for row in results:
            path = row.get('storage_path')
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    deleted += 1
                except Exception as e:
                    logger.error(f"Failed to delete {path}: {e}")

        logger.info(f"Cleaned up {deleted} expired media files")
        return deleted
