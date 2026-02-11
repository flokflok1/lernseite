"""
Knowledge Base Learning from Interactions

Handles knowledge acquisition from user interactions:
- Learning new knowledge from Q&A pairs
- Duplicate detection to prevent redundant entries
- Automatic knowledge base growth

Inherits from BaseRepository for connection pooling and standard operations.
"""

from typing import Optional, Dict
import hashlib

from app.infrastructure.persistence.repositories.core.base import BaseRepository


class KnowledgeRepositoryLearning(BaseRepository):
    """
    Learning operations for Knowledge Base

    Handles knowledge acquisition from interactions including:
    - Storing new Q&A pairs from user interactions
    - Deduplication using question hashing
    - Usage count increment for existing questions
    """

    @staticmethod
    def learn_from_interaction(
        agent_id: str,
        question: str,
        answer: str,
        context_scope: str = 'course',
        context_id: Optional[str] = None,
        method_type: Optional[int] = None,
        generated_by: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Learn from a user interaction by storing as knowledge

        Only stores if question is unique enough (not already in knowledge base).
        If question hash already exists, increments usage instead of creating duplicate.

        Args:
            agent_id: Agent UUID
            question: Question asked
            answer: Answer provided
            context_scope: Scope (course, chapter, lesson, method)
            context_id: Optional scope ID
            method_type: Optional learning method type (0-11)
            generated_by: Optional model name

        Returns:
            Created knowledge entry or None if duplicate was found
        """
        from app.infrastructure.persistence.repositories.knowledge.crud import KnowledgeRepositoryCRUD

        question_hash = hashlib.sha256(
            question.lower().strip().encode()
        ).hexdigest()

        # Check if already exists
        existing = KnowledgeRepositoryCRUD.get_knowledge_by_hash(
            agent_id,
            question_hash
        )
        if existing:
            # Just increment usage
            KnowledgeRepositoryCRUD.increment_usage(
                existing['knowledge_id']
            )
            return None

        # Create new knowledge entry
        return KnowledgeRepositoryCRUD.create_knowledge(
            agent_id=agent_id,
            answer_text=answer,
            scope_type=context_scope,
            scope_id=context_id,
            knowledge_type='qa_pair',
            source='user_interaction',
            question_text=question,
            method_type=method_type,
            generated_by=generated_by
        )
