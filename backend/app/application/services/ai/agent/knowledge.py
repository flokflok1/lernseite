"""
Agent Knowledge Management - Learning system and knowledge base operations

Handles:
- Learning from interactions
- Knowledge base access and updates
- Quality scoring and feedback
- Cache invalidation
"""

import logging
from typing import Dict, Any, Optional

from app.infrastructure.cache.service import CacheService
from app.infrastructure.persistence.repositories.agent import AgentRepository
from app.infrastructure.persistence.repositories.knowledge import KnowledgeRepository

logger = logging.getLogger(__name__)


class KnowledgeManager:
    """
    Manages agent knowledge base and learning from interactions.
    """

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
        Manually add knowledge to agent.

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
    def learn_from_interaction(
        agent_id: str,
        question: str,
        answer: str,
        context: Optional[Dict[str, Any]] = None,
        course_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Learn from a single interaction (cache-first question-answer pair).

        Args:
            agent_id: Agent UUID
            question: Normalized question
            answer: Generated answer
            context: Optional context dict with lesson_id, chapter_id, etc.
            course_id: Course UUID

        Returns:
            Created knowledge entry
        """
        # Determine scope
        scope_type = 'course'
        scope_id = course_id

        if context:
            if context.get('lesson_id'):
                scope_type = 'lesson'
                scope_id = context['lesson_id']
            elif context.get('chapter_id'):
                scope_type = 'chapter'
                scope_id = context['chapter_id']

        # Store in knowledge base
        return KnowledgeRepository.learn_from_interaction(
            agent_id=agent_id,
            question=question,
            answer=answer,
            scope_type=scope_type,
            scope_id=scope_id,
            quality_score=0.7  # Default quality for AI-generated
        )

    @staticmethod
    def submit_feedback(
        query_id: str,
        rating: int,
        helpful: bool = True,
        feedback_text: Optional[str] = None
    ) -> bool:
        """
        Submit feedback for an agent response.

        Adjusts knowledge quality scores based on user feedback.

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
            logger.info(f"Knowledge quality boosted: knowledge_id={knowledge_id}")

        elif knowledge_id and rating <= 2:
            # Reduce quality score for negative feedback
            KnowledgeRepository.update_quality_score(
                knowledge_id=knowledge_id,
                delta=-0.1
            )
            logger.info(f"Knowledge quality reduced: knowledge_id={knowledge_id}")

        # TODO: Store feedback in dedicated table

        return True

    @staticmethod
    def invalidate_cache(course_id: str) -> int:
        """
        Invalidate all cache entries for a course agent.

        Args:
            course_id: Course UUID

        Returns:
            Number of keys deleted
        """
        pattern = CacheService.make_key('AGENT', course_id, '*')
        deleted = CacheService.cache_delete_pattern(pattern)

        logger.info(f"Agent cache invalidated: course={course_id}, deleted={deleted}")
        return deleted

    @staticmethod
    def update_agent_config(
        course_id: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Update agent configuration.

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
