"""
Agent Service Package - Smart Agent with Cache-First Strategy

Modular structure:
- core: Main ask() and status methods
- routing: AI provider routing and fallback
- knowledge: Knowledge base management
- prompts: Prompt building and normalization
- media: Audio/TTS responses

Public API:
  from app.application.services.agent import AgentService

  AgentService.ask(course_id, user_id, question)
  AgentService.get_status(course_id)
  AgentService.add_knowledge(course_id, question, answer)
  AgentService.submit_feedback(query_id, rating)
  AgentService.ask_with_audio(course_id, user_id, question, voice='nova')
  AgentService.transcribe_user_audio(audio_path)
  AgentService.voice_conversation_turn(course_id, user_id, audio_path, session)
"""

from .core import AgentCore, CACHE_TTL_TIER_1, CACHE_TTL_TIER_2, CACHE_TTL_TIER_3
from .routing import AgentRouter
from .knowledge import KnowledgeManager
from .prompts import PromptBuilder
from .media import MediaOperations

__all__ = [
    'AgentService',
    'AgentCore',
    'AgentRouter',
    'KnowledgeManager',
    'PromptBuilder',
    'MediaOperations',
    'CACHE_TTL_TIER_1',
    'CACHE_TTL_TIER_2',
    'CACHE_TTL_TIER_3'
]


class AgentService:
    """
    Smart Agent Service - Main public API (backwards compatible).

    This class delegates to modular components:
    - AgentCore for ask() and status
    - KnowledgeManager for knowledge operations
    - MediaOperations for audio/voice

    All existing code using AgentService continues to work unchanged.
    """

    @staticmethod
    def ask(course_id: str, user_id: str, question: str, context=None, language='de', organization_id=None):
        """Delegate to AgentCore.ask()"""
        return AgentCore.ask(
            course_id=course_id,
            user_id=user_id,
            question=question,
            context=context,
            language=language,
            organization_id=organization_id
        )

    @staticmethod
    def get_status(course_id: str):
        """Delegate to AgentCore.get_status()"""
        return AgentCore.get_status(course_id)

    @staticmethod
    def update_config(course_id: str, **kwargs):
        """Delegate to KnowledgeManager.update_agent_config()"""
        return KnowledgeManager.update_agent_config(course_id, **kwargs)

    @staticmethod
    def add_knowledge(course_id: str, question: str, answer: str, scope_type='course', scope_id=None, knowledge_type='qa_pair'):
        """Delegate to KnowledgeManager.add_knowledge()"""
        return KnowledgeManager.add_knowledge(
            course_id=course_id,
            question=question,
            answer=answer,
            scope_type=scope_type,
            scope_id=scope_id,
            knowledge_type=knowledge_type
        )

    @staticmethod
    def invalidate_cache(course_id: str):
        """Delegate to KnowledgeManager.invalidate_cache()"""
        return KnowledgeManager.invalidate_cache(course_id)

    @staticmethod
    def submit_feedback(query_id: str, rating: int, helpful=True, feedback_text=None):
        """Delegate to KnowledgeManager.submit_feedback()"""
        return KnowledgeManager.submit_feedback(
            query_id=query_id,
            rating=rating,
            helpful=helpful,
            feedback_text=feedback_text
        )

    @staticmethod
    def ask_with_audio(course_id: str, user_id: str, question: str, context=None, language='de', organization_id=None, voice='nova', speech_speed=1.0):
        """Delegate to MediaOperations.ask_with_audio()"""
        return MediaOperations.ask_with_audio(
            course_id=course_id,
            user_id=user_id,
            question=question,
            context=context,
            language=language,
            organization_id=organization_id,
            voice=voice,
            speech_speed=speech_speed,
            ask_func=AgentCore.ask  # Inject ask() function
        )

    @staticmethod
    def transcribe_user_audio(audio_path: str, agent_id=None, language=None):
        """Delegate to MediaOperations.transcribe_user_audio()"""
        return MediaOperations.transcribe_user_audio(
            audio_path=audio_path,
            agent_id=agent_id,
            language=language
        )

    @staticmethod
    def voice_conversation_turn(course_id: str, user_id: str, audio_path: str, session: dict, voice='nova', language='de'):
        """Delegate to MediaOperations.voice_conversation_turn()"""
        return MediaOperations.voice_conversation_turn(
            course_id=course_id,
            user_id=user_id,
            audio_path=audio_path,
            session=session,
            voice=voice,
            language=language,
            ask_with_audio_func=AgentService.ask_with_audio  # Inject ask_with_audio() function
        )
