"""
Agent Core Logic - Main ask() method and agent status

Flow:
1. BillingService.check() → Offline mode if wallet empty
2. CacheService.get() → Return cached if hit
3. KnowledgeRepository.find_similar() → Partial match
4. AIAdapter.generate() → Generate new + cache + learn

ISO 9001:2015 compliant - AI service layer
"""

import logging
import hashlib
from typing import Dict, Any, Optional

from app.infrastructure.cache.service import CacheService
from app.application.services.system.billing.service import BillingService
from app.infrastructure.persistence.repositories.agent import AgentRepository
from app.infrastructure.persistence.repositories.knowledge import KnowledgeRepository
from app.infrastructure.persistence.repositories.user import UserRepository

from .routing import AgentRouter
from .prompts import PromptBuilder
from .knowledge import KnowledgeManager

logger = logging.getLogger(__name__)

# Cache TTLs by tier (seconds)
CACHE_TTL_TIER_1 = 7 * 24 * 3600   # 7 days - OPTIONAL KI usage
CACHE_TTL_TIER_2 = 24 * 3600       # 24 hours - MEDIUM KI usage
CACHE_TTL_TIER_3 = 3600            # 1 hour - INTENSIVE KI usage


class AgentCore:
    """
    Smart Agent Service with Cache-First Strategy

    Main entry point for asking agent questions with multi-tier caching.
    """

    @staticmethod
    def ask(
        course_id: str,
        user_id: str,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        language: str = 'de',
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ask the course agent a question (Cache-First Strategy)

        Args:
            course_id: Course UUID
            user_id: User UUID
            question: User's question
            context: Optional context (lesson_id, chapter_id, etc.)
            language: Response language (default: 'de')
            organization_id: Optional organisation UUID for billing

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
        config = AgentRepository.get_effective_agent_config(course_id, organization_id)

        # Normalize question for caching
        normalized_question = PromptBuilder.normalize_question(question)
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
        result = AgentRouter.generate_with_ai(
            agent_id=agent_id,
            user_id=user_id,
            course_id=course_id,
            organization_id=organization_id,
            config=config,
            question=question,
            normalized_question=normalized_question,
            context=context,
            language=language,
            cache_key=cache_key,
            is_offline_mode=is_offline_mode,
            offline_message=offline_message
        )

        return result

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
