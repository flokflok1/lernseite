"""
LernsystemX Smart Agent Service

Business logic for intelligent course agents:
- Cache-First strategy for token savings
- Offline mode when wallet is empty
- Knowledge base learning from interactions
- Multi-tier caching based on KI-Usage

Token Savings Architecture:
1. Check wallet balance (offline mode if empty)
2. Check Redis cache (instant response)
3. Check Knowledge Base (PostgreSQL full-text search)
4. Generate with AI (cache result + learn)

Expected savings: 50-70% token reduction

ISO 9001:2015 compliant - AI service layer
"""

import logging
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.services.cache_service import CacheService
from app.services.billing_service import BillingService
from app.services.ai_adapter import AIAdapter, AIProviderError
from app.repositories.agent_repository import AgentRepository
from app.repositories.knowledge_repository import KnowledgeRepository
from app.repositories.user_repository import UserRepository
from app.repositories.course_repository import CourseRepository

logger = logging.getLogger(__name__)


# Cache TTLs by tier (seconds)
CACHE_TTL_TIER_1 = 7 * 24 * 3600   # 7 days - OPTIONAL KI usage
CACHE_TTL_TIER_2 = 24 * 3600       # 24 hours - MEDIUM KI usage
CACHE_TTL_TIER_3 = 3600            # 1 hour - INTENSIVE KI usage


class AgentService:
    """
    Smart Agent Service with Cache-First Strategy

    Flow:
    1. BillingService.check() → Offline mode if wallet empty
    2. CacheService.get() → Return cached if hit
    3. KnowledgeRepository.find_similar() → Partial match
    4. AIAdapter.generate() → Generate new + cache + learn

    Example:
        >>> result = AgentService.ask(
        ...     course_id="uuid",
        ...     user_id="uuid",
        ...     question="Was ist Polymorphismus?",
        ...     context={"lesson_id": "uuid"}
        ... )
        >>> print(result['answer'])
        >>> print(result['source'])  # 'cache_hit', 'knowledge_match', 'ai_generated'
    """

    # =========================================================================
    # Main API: ask()
    # =========================================================================

    @staticmethod
    def ask(
        course_id: str,
        user_id: str,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        language: str = 'de',
        organisation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ask the course agent a question (Cache-First Strategy)

        Args:
            course_id: Course UUID
            user_id: User UUID
            question: User's question
            context: Optional context (lesson_id, chapter_id, etc.)
            language: Response language (default: 'de')
            organisation_id: Optional organisation UUID for billing

        Returns:
            {
                'answer': str,
                'source': str,  # 'cache_hit', 'knowledge_match', 'ai_generated', 'offline_fallback'
                'tokens_used': int,
                'tokens_saved': int,
                'was_offline_mode': bool,
                'agent_id': str,
                'knowledge_id': str (if from knowledge base),
                'offline_message': str (if offline mode)
            }
        """
        logger.info(f"Agent ask: course={course_id}, user={user_id}")

        # Get or create agent for course
        agent = AgentRepository.get_or_create_agent(course_id)
        agent_id = agent['agent_id']

        # Get effective agent config (with org extensions)
        config = AgentRepository.get_effective_agent_config(course_id, organisation_id)

        # Normalize question for caching
        normalized_question = AgentService._normalize_question(question)
        question_hash = hashlib.sha256(normalized_question.encode()).hexdigest()

        # Build cache key
        cache_key = CacheService.make_key('AGENT', course_id, 'Q', question_hash[:16])

        # =====================================================================
        # Step 1: Check Billing (Offline Mode if wallet empty)
        # =====================================================================
        billing_check = BillingService.ensure_user_can_use_ai(
            user_id=user_id,
            method_id=0,  # Agent system
            estimated_tokens=500  # Typical agent response
        )

        is_offline_mode = not billing_check.get('allowed', False)
        offline_message = None

        if is_offline_mode:
            offline_message = billing_check.get('reason', 'Token-Guthaben aufgebraucht')
            logger.info(f"Agent offline mode: user={user_id}, reason={offline_message}")

        # =====================================================================
        # Step 2: Check Redis Cache (fastest)
        # =====================================================================
        cached_answer = CacheService.cache_get(cache_key)
        if cached_answer:
            logger.info(f"Agent cache hit: key={cache_key}")

            # Log query
            KnowledgeRepository.log_query(
                agent_id=agent_id,
                user_id=user_id,
                query_text=question,
                response_source='cache_hit',
                tokens_used=0,
                tokens_saved=500,
                was_offline_mode=is_offline_mode
            )

            # Update agent stats
            AgentRepository.increment_stats(agent_id, cache_hit=True, tokens_saved=500)

            return {
                'answer': cached_answer.get('answer') if isinstance(cached_answer, dict) else cached_answer,
                'source': 'cache_hit',
                'tokens_used': 0,
                'tokens_saved': 500,
                'was_offline_mode': is_offline_mode,
                'agent_id': agent_id,
                'offline_message': offline_message
            }

        # =====================================================================
        # Step 3: Check Knowledge Base (PostgreSQL full-text search)
        # =====================================================================
        knowledge_match = KnowledgeRepository.get_best_match(
            agent_id=agent_id,
            question=normalized_question,
            min_similarity=0.3
        )

        if knowledge_match:
            answer = knowledge_match['answer_text']
            knowledge_id = knowledge_match['knowledge_id']

            logger.info(f"Agent knowledge match: knowledge_id={knowledge_id}")

            # Cache the result
            CacheService.cache_set(
                cache_key,
                {'answer': answer, 'knowledge_id': knowledge_id},
                ttl=CACHE_TTL_TIER_2
            )

            # Increment usage count
            KnowledgeRepository.increment_usage(knowledge_id)

            # Log query
            KnowledgeRepository.log_query(
                agent_id=agent_id,
                user_id=user_id,
                query_text=question,
                response_source='knowledge_match',
                tokens_used=0,
                tokens_saved=500,
                was_offline_mode=is_offline_mode,
                knowledge_id=knowledge_id
            )

            # Update agent stats
            AgentRepository.increment_stats(agent_id, cache_hit=True, tokens_saved=500)

            return {
                'answer': answer,
                'source': 'knowledge_match',
                'tokens_used': 0,
                'tokens_saved': 500,
                'was_offline_mode': is_offline_mode,
                'agent_id': agent_id,
                'knowledge_id': knowledge_id,
                'offline_message': offline_message
            }

        # =====================================================================
        # Step 4: Offline Mode - No cached answer available
        # =====================================================================
        if is_offline_mode:
            # Try to find any somewhat related knowledge
            related = KnowledgeRepository.find_similar_knowledge(
                agent_id=agent_id,
                query_text=normalized_question,
                limit=1
            )

            if related:
                answer = related[0]['answer_text']
                logger.info("Agent offline fallback: using related knowledge")

                # Log query
                KnowledgeRepository.log_query(
                    agent_id=agent_id,
                    user_id=user_id,
                    query_text=question,
                    response_source='offline_fallback',
                    tokens_used=0,
                    tokens_saved=0,
                    was_offline_mode=True,
                    knowledge_id=related[0]['knowledge_id']
                )

                return {
                    'answer': answer,
                    'source': 'offline_fallback',
                    'tokens_used': 0,
                    'tokens_saved': 0,
                    'was_offline_mode': True,
                    'agent_id': agent_id,
                    'knowledge_id': related[0]['knowledge_id'],
                    'offline_message': 'Dein Token-Guthaben ist aufgebraucht. Diese Antwort stammt aus dem Wissens-Cache. Lade Tokens auf für aktuelle KI-Antworten.'
                }

            # No knowledge available at all
            return {
                'answer': 'Dein Token-Guthaben ist aufgebraucht und zu dieser Frage gibt es noch keine gecachte Antwort. Bitte lade dein Guthaben auf.',
                'source': 'offline_no_data',
                'tokens_used': 0,
                'tokens_saved': 0,
                'was_offline_mode': True,
                'agent_id': agent_id,
                'offline_message': 'Token-Guthaben aufgebraucht. Keine gecachte Antwort verfuegbar.'
            }

        # =====================================================================
        # Step 5: Generate with AI
        # =====================================================================
        try:
            # Build prompt
            system_prompt = AgentService._build_system_prompt(config, context)
            user_prompt = AgentService._build_user_prompt(question, context, language)

            # Use configured provider and model
            provider = config.get('primary_provider', 'openai')
            model = config.get('primary_model', 'gpt-4o-mini')
            temperature = config.get('temperature', 0.7)
            max_tokens = config.get('max_tokens', 2000)

            adapter = AIAdapter(provider=provider, model=model)
            response = adapter.send_request(
                prompt=user_prompt,
                context=system_prompt,
                language=language,
                temperature=temperature,
                max_tokens=max_tokens
            )

            answer = response['output_text']
            tokens_used = response['total_tokens']

            logger.info(f"Agent AI generated: tokens={tokens_used}")

            # Cache the result
            CacheService.cache_set(
                cache_key,
                {'answer': answer},
                ttl=CACHE_TTL_TIER_2
            )

            # Learn from interaction (add to knowledge base)
            scope_type = 'course'
            scope_id = course_id
            if context:
                if context.get('lesson_id'):
                    scope_type = 'lesson'
                    scope_id = context['lesson_id']
                elif context.get('chapter_id'):
                    scope_type = 'chapter'
                    scope_id = context['chapter_id']

            KnowledgeRepository.learn_from_interaction(
                agent_id=agent_id,
                question=normalized_question,
                answer=answer,
                scope_type=scope_type,
                scope_id=scope_id,
                quality_score=0.7  # Default quality for AI-generated
            )

            # Log query
            KnowledgeRepository.log_query(
                agent_id=agent_id,
                user_id=user_id,
                query_text=question,
                response_source='ai_generated',
                tokens_used=tokens_used,
                tokens_saved=0,
                was_offline_mode=False
            )

            # Update agent stats
            AgentRepository.increment_stats(agent_id, cache_hit=False, tokens_saved=0)

            # Charge user
            user = UserRepository.find_by_id(user_id)
            BillingService.charge_ai_usage(
                user_id=user_id,
                organisation_id=organisation_id or (user.get('organization_id') if user else None),
                method_id=0,  # Agent system
                tokens_used=tokens_used,
                provider=provider,
                meta={'agent_id': agent_id, 'course_id': course_id}
            )

            return {
                'answer': answer,
                'source': 'ai_generated',
                'tokens_used': tokens_used,
                'tokens_saved': 0,
                'was_offline_mode': False,
                'agent_id': agent_id,
                'model': model,
                'provider': provider
            }

        except AIProviderError as e:
            logger.error(f"Agent AI error: {e}")

            # Try fallback provider if configured
            fallback_provider = config.get('fallback_provider')
            fallback_model = config.get('fallback_model')

            if fallback_provider and fallback_model:
                try:
                    adapter = AIAdapter(provider=fallback_provider, model=fallback_model)
                    response = adapter.send_request(
                        prompt=user_prompt,
                        context=system_prompt,
                        language=language,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )

                    answer = response['output_text']
                    tokens_used = response['total_tokens']

                    # Cache and log (same as above)
                    CacheService.cache_set(cache_key, {'answer': answer}, ttl=CACHE_TTL_TIER_2)

                    KnowledgeRepository.log_query(
                        agent_id=agent_id,
                        user_id=user_id,
                        query_text=question,
                        response_source='ai_generated',
                        tokens_used=tokens_used,
                        tokens_saved=0,
                        was_offline_mode=False
                    )

                    return {
                        'answer': answer,
                        'source': 'ai_generated',
                        'tokens_used': tokens_used,
                        'tokens_saved': 0,
                        'was_offline_mode': False,
                        'agent_id': agent_id,
                        'model': fallback_model,
                        'provider': fallback_provider,
                        'used_fallback': True
                    }

                except AIProviderError as fallback_error:
                    logger.error(f"Agent fallback AI error: {fallback_error}")

            # Return error response
            return {
                'answer': 'Ein Fehler ist bei der KI-Anfrage aufgetreten. Bitte versuche es spaeter erneut.',
                'source': 'error',
                'tokens_used': 0,
                'tokens_saved': 0,
                'was_offline_mode': False,
                'agent_id': agent_id,
                'error': str(e)
            }

    # =========================================================================
    # Agent Status
    # =========================================================================

    @staticmethod
    def get_status(course_id: str) -> Dict[str, Any]:
        """
        Get agent status for a course

        Args:
            course_id: Course UUID

        Returns:
            {
                'agent_id': str,
                'knowledge_status': str,
                'cache_hit_rate': float,
                'tokens_saved': int,
                'total_queries': int,
                'knowledge_entries': int
            }
        """
        agent = AgentRepository.get_agent_by_course(course_id)

        if not agent:
            return {
                'agent_id': None,
                'knowledge_status': 'not_created',
                'cache_hit_rate': 0,
                'tokens_saved': 0,
                'total_queries': 0,
                'knowledge_entries': 0
            }

        agent_id = agent['agent_id']

        # Get knowledge count
        knowledge_count = KnowledgeRepository.get_knowledge_count(agent_id)

        # Calculate cache hit rate
        total_queries = agent.get('total_queries', 0)
        cache_hits = agent.get('cache_hits', 0)
        cache_hit_rate = (cache_hits / total_queries * 100) if total_queries > 0 else 0

        return {
            'agent_id': agent_id,
            'knowledge_status': agent.get('knowledge_status', 'pending'),
            'cache_hit_rate': round(cache_hit_rate, 1),
            'tokens_saved': agent.get('tokens_saved', 0),
            'total_queries': total_queries,
            'cache_hits': cache_hits,
            'knowledge_entries': knowledge_count,
            'last_warmed_at': agent.get('last_warmed_at'),
            'knowledge_version': agent.get('knowledge_version')
        }

    # =========================================================================
    # Agent Configuration
    # =========================================================================

    @staticmethod
    def update_config(
        course_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update agent configuration

        Args:
            course_id: Course UUID
            **kwargs: Configuration fields to update

        Returns:
            Updated agent data
        """
        agent = AgentRepository.get_agent_by_course(course_id)

        if not agent:
            # Create new agent with settings
            return AgentRepository.create_agent(course_id, **kwargs)

        return AgentRepository.update_agent(agent['agent_id'], **kwargs)

    # =========================================================================
    # Knowledge Management
    # =========================================================================

    @staticmethod
    def add_knowledge(
        course_id: str,
        question: str,
        answer: str,
        scope_type: str = 'course',
        scope_id: Optional[str] = None,
        knowledge_type: str = 'qa_pair'
    ) -> Dict[str, Any]:
        """
        Manually add knowledge to agent

        Args:
            course_id: Course UUID
            question: Question text
            answer: Answer text
            scope_type: Scope type (course, chapter, lesson)
            scope_id: Scope ID
            knowledge_type: Knowledge type (qa_pair, explanation, example)

        Returns:
            Created knowledge entry
        """
        agent = AgentRepository.get_or_create_agent(course_id)

        return KnowledgeRepository.create_knowledge(
            agent_id=agent['agent_id'],
            scope_type=scope_type,
            scope_id=scope_id or course_id,
            knowledge_type=knowledge_type,
            question_text=question,
            answer_text=answer,
            source='manual',
            quality_score=1.0
        )

    @staticmethod
    def invalidate_cache(course_id: str) -> int:
        """
        Invalidate all cache entries for a course agent

        Args:
            course_id: Course UUID

        Returns:
            Number of keys deleted
        """
        pattern = CacheService.make_key('AGENT', course_id, '*')
        deleted = CacheService.cache_delete_pattern(pattern)

        logger.info(f"Agent cache invalidated: course={course_id}, deleted={deleted}")
        return deleted

    # =========================================================================
    # Feedback System
    # =========================================================================

    @staticmethod
    def submit_feedback(
        query_id: str,
        rating: int,
        helpful: bool = True,
        feedback_text: Optional[str] = None
    ) -> bool:
        """
        Submit feedback for an agent response

        Args:
            query_id: Query UUID from agent_query_log
            rating: Rating (1-5)
            helpful: Was the response helpful?
            feedback_text: Optional feedback text

        Returns:
            True if feedback saved
        """
        # Update knowledge quality based on feedback
        query_log = KnowledgeRepository.get_query_by_id(query_id)

        if not query_log:
            return False

        knowledge_id = query_log.get('knowledge_id')

        if knowledge_id and rating >= 4:
            # Boost quality score for positive feedback
            KnowledgeRepository.update_quality_score(
                knowledge_id=knowledge_id,
                delta=0.1
            )
        elif knowledge_id and rating <= 2:
            # Reduce quality score for negative feedback
            KnowledgeRepository.update_quality_score(
                knowledge_id=knowledge_id,
                delta=-0.1
            )

        # TODO: Store feedback in dedicated table

        return True

    # =========================================================================
    # Helper Methods
    # =========================================================================

    @staticmethod
    def _normalize_question(question: str) -> str:
        """
        Normalize question for consistent hashing

        - Lowercase
        - Remove extra whitespace
        - Remove common filler words
        """
        normalized = question.lower().strip()
        normalized = ' '.join(normalized.split())
        return normalized

    @staticmethod
    def _build_system_prompt(
        config: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build system prompt from agent config
        """
        persona = config.get('persona', 'friendly')
        language = config.get('language', 'de')
        blocked_topics = config.get('blocked_topics', [])
        terminology = config.get('custom_terminology', {})
        additional_context = config.get('additional_context', '')

        persona_map = {
            'friendly': 'Du bist ein freundlicher und geduldiger KI-Tutor.',
            'professional': 'Du bist ein professioneller und sachlicher KI-Tutor.',
            'encouraging': 'Du bist ein ermutigender und motivierender KI-Tutor.',
            'socratic': 'Du bist ein sokratischer Tutor, der durch Fragen zum Denken anregt.'
        }

        prompt = persona_map.get(persona, persona_map['friendly'])
        prompt += f"\nAntworte immer auf {language.upper()}."
        prompt += "\nGib klare, verstaendliche Erklaerungen."
        prompt += "\nVerwende Beispiele wo sinnvoll."

        if blocked_topics:
            prompt += f"\nVermeide folgende Themen: {', '.join(blocked_topics)}"

        if terminology:
            terms = [f"{k} = {v}" for k, v in terminology.items()]
            prompt += f"\nVerwende diese Terminologie: {'; '.join(terms)}"

        if additional_context:
            prompt += f"\n{additional_context}"

        return prompt

    @staticmethod
    def _build_user_prompt(
        question: str,
        context: Optional[Dict[str, Any]] = None,
        language: str = 'de'
    ) -> str:
        """
        Build user prompt with context
        """
        prompt = question

        if context:
            if context.get('lesson_title'):
                prompt = f"Lektion: {context['lesson_title']}\n\nFrage: {question}"
            elif context.get('chapter_title'):
                prompt = f"Kapitel: {context['chapter_title']}\n\nFrage: {question}"
            elif context.get('course_title'):
                prompt = f"Kurs: {context['course_title']}\n\nFrage: {question}"

        return prompt

    # =========================================================================
    # Audio/Video Response Methods
    # =========================================================================

    @staticmethod
    def ask_with_audio(
        course_id: str,
        user_id: str,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        language: str = 'de',
        organisation_id: Optional[str] = None,
        voice: str = 'nova',
        speech_speed: float = 1.0
    ) -> Dict[str, Any]:
        """
        Ask agent with TTS audio response (Cache-First for both text AND audio)

        This method first gets the text answer (with caching), then gets
        or generates TTS audio for that answer (also with caching).

        Args:
            course_id: Course UUID
            user_id: User UUID
            question: User's question
            context: Optional context
            language: Response language
            organisation_id: Optional org UUID
            voice: TTS voice (nova, alloy, echo, fable, onyx, shimmer)
            speech_speed: Speech speed (0.25-4.0)

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
        from app.services.media_cache_service import MediaCacheService

        # First get text answer (with caching)
        result = AgentService.ask(
            course_id=course_id,
            user_id=user_id,
            question=question,
            context=context,
            language=language,
            organisation_id=organisation_id
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
        Transcribe user audio input with caching

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
        from app.services.media_cache_service import MediaCacheService

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
        language: str = 'de'
    ) -> Dict[str, Any]:
        """
        Process a single turn in a voice conversation

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
        from app.services.media_cache_service import MediaCacheService

        turn_cost = 0.0
        turn_saved = 0.0

        # Step 1: Transcribe user audio
        transcript_result = AgentService.transcribe_user_audio(
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
        agent_result = AgentService.ask_with_audio(
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
