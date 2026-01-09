"""
Agent Routing - AI provider selection and fallback logic

Handles:
- Primary provider routing
- Fallback provider management
- Error handling and recovery
"""

import logging
from typing import Dict, Any, Optional

from app.services.cache_service import CacheService
from app.services.ai_adapter import AIAdapter, AIProviderError
from app.repositories.agent import AgentRepository
from app.repositories.knowledge import KnowledgeRepository
from app.repositories.user import UserRepository
from app.services.billing_service import BillingService

from .knowledge import KnowledgeManager
from .prompts import PromptBuilder

logger = logging.getLogger(__name__)

# Cache TTLs
CACHE_TTL_TIER_2 = 24 * 3600       # 24 hours - MEDIUM KI usage


class AgentRouter:
    """
    Routes agent requests to appropriate AI providers with fallback logic.
    """

    @staticmethod
    def generate_with_ai(
        agent_id: str,
        user_id: str,
        course_id: str,
        organization_id: Optional[str],
        config: Dict[str, Any],
        question: str,
        normalized_question: str,
        context: Optional[Dict[str, Any]],
        language: str,
        cache_key: str,
        is_offline_mode: bool,
        offline_message: Optional[str]
    ) -> Dict[str, Any]:
        """
        Generate answer using AI with fallback strategy.

        Primary provider → Fallback provider → Error response

        Args:
            agent_id: Agent UUID
            user_id: User UUID
            course_id: Course UUID
            organization_id: Optional organisation UUID
            config: Agent configuration with provider info
            question: Original question
            normalized_question: Normalized question
            context: Optional context
            language: Response language
            cache_key: Cache key for result
            is_offline_mode: Whether in offline mode
            offline_message: Offline mode message if applicable

        Returns:
            Generation result or error response
        """
        try:
            # Build prompts
            system_prompt = PromptBuilder.build_system_prompt(config, context)
            user_prompt = PromptBuilder.build_user_prompt(question, context, language)

            # Use configured provider and model
            provider = config.get('primary_provider', 'openai')
            model = config.get('primary_model', 'gpt-4o-mini')
            temperature = config.get('temperature', 0.7)
            max_tokens = config.get('max_tokens', 2000)

            # Try primary provider
            return AgentRouter._try_provider(
                provider=provider,
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                language=language,
                temperature=temperature,
                max_tokens=max_tokens,
                agent_id=agent_id,
                user_id=user_id,
                course_id=course_id,
                organization_id=organization_id,
                question=question,
                normalized_question=normalized_question,
                context=context,
                cache_key=cache_key,
                is_offline_mode=is_offline_mode,
                offline_message=offline_message,
                is_fallback=False,
                config=config
            )

        except AIProviderError as e:
            logger.error(f"Agent primary provider error: {e}")

            # Try fallback provider if configured
            fallback_provider = config.get('fallback_provider')
            fallback_model = config.get('fallback_model')

            if fallback_provider and fallback_model:
                try:
                    logger.info(f"Attempting fallback provider: {fallback_provider}")

                    return AgentRouter._try_provider(
                        provider=fallback_provider,
                        model=fallback_model,
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        language=language,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        agent_id=agent_id,
                        user_id=user_id,
                        course_id=course_id,
                        organization_id=organization_id,
                        question=question,
                        normalized_question=normalized_question,
                        context=context,
                        cache_key=cache_key,
                        is_offline_mode=is_offline_mode,
                        offline_message=offline_message,
                        is_fallback=True,
                        config=config
                    )

                except AIProviderError as fallback_error:
                    logger.error(f"Agent fallback provider error: {fallback_error}")

            # Both providers failed
            return {
                'answer': 'Ein Fehler ist bei der KI-Anfrage aufgetreten. Bitte versuche es spaeter erneut.',
                'source': 'error',
                'tokens_used': 0,
                'tokens_saved': 0,
                'was_offline_mode': False,
                'agent_id': agent_id,
                'error': str(e)
            }

    @staticmethod
    def _try_provider(
        provider: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        language: str,
        temperature: float,
        max_tokens: int,
        agent_id: str,
        user_id: str,
        course_id: str,
        organization_id: Optional[str],
        question: str,
        normalized_question: str,
        context: Optional[Dict[str, Any]],
        cache_key: str,
        is_offline_mode: bool,
        offline_message: Optional[str],
        is_fallback: bool,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Attempt to generate response from a single provider.

        Args:
            provider: AI provider name
            model: Model identifier
            system_prompt: System prompt
            user_prompt: User prompt
            language: Response language
            temperature: Temperature setting
            max_tokens: Max tokens to generate
            agent_id: Agent UUID
            user_id: User UUID
            course_id: Course UUID
            organization_id: Optional organisation UUID
            question: Original question
            normalized_question: Normalized question
            context: Optional context
            cache_key: Cache key
            is_offline_mode: Offline mode flag
            offline_message: Offline message if applicable
            is_fallback: Whether this is a fallback provider
            config: Agent configuration

        Returns:
            Generation result
        """
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

        logger.info(f"Agent AI generated: provider={provider}, tokens={tokens_used}")

        # Cache the result
        CacheService.cache_set(
            cache_key,
            {'answer': answer},
            ttl=CACHE_TTL_TIER_2
        )

        # Learn from interaction (add to knowledge base)
        KnowledgeManager.learn_from_interaction(
            agent_id=agent_id,
            question=normalized_question,
            answer=answer,
            context=context,
            course_id=course_id
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
            organization_id=organization_id or (user.get('organization_id') if user else None),
            method_id=0,  # Agent system
            tokens_used=tokens_used,
            provider=provider,
            meta={'agent_id': agent_id, 'course_id': course_id}
        )

        result = {
            'answer': answer,
            'source': 'ai_generated',
            'tokens_used': tokens_used,
            'tokens_saved': 0,
            'was_offline_mode': False,
            'agent_id': agent_id,
            'model': model,
            'provider': provider
        }

        if is_fallback:
            result['used_fallback'] = True

        return result
