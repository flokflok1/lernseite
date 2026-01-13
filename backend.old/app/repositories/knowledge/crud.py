"""
Knowledge Base CRUD Operations (Create, Read, Update)

Handles basic knowledge entry operations:
- Knowledge entry creation and retrieval
- Knowledge entry updates
- Quality scoring and feedback tracking
- Usage counting

Inherits from BaseRepository for connection pooling and standard operations.
"""

from typing import Optional, Dict, List, Any
import hashlib

from app.repositories.base_repository import BaseRepository


class KnowledgeRepositoryCRUD(BaseRepository):
    """
    CRUD operations for Knowledge Base entries

    Handles all basic database operations for knowledge entries including:
    - Knowledge creation with hash-based deduplication
    - Finding knowledge by ID or question hash
    - Updating knowledge metadata and quality scores
    - Usage and feedback tracking
    """

    table_name = 'smart_agents.agent_knowledge_base'

    @staticmethod
    def get_knowledge_by_id(knowledge_id: str) -> Optional[Dict[str, Any]]:
        """
        Get knowledge entry by ID

        Args:
            knowledge_id: Knowledge UUID

        Returns:
            Knowledge data or None
        """
        query = """
            SELECT *
            FROM smart_agents.agent_knowledge_base
            WHERE knowledge_id = %s
        """
        return KnowledgeRepositoryCRUD.fetch_one(query, (knowledge_id,))

    @staticmethod
    def get_knowledge_by_hash(
        agent_id: str,
        question_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get knowledge by question hash (exact match)

        Args:
            agent_id: Agent UUID
            question_hash: SHA256 hash of question

        Returns:
            Knowledge data or None
        """
        query = """
            SELECT *
            FROM smart_agents.agent_knowledge_base
            WHERE agent_id = %s
            AND question_hash = %s
            AND superseded_by IS NULL
            ORDER BY version DESC
            LIMIT 1
        """
        return KnowledgeRepositoryCRUD.fetch_one(
            query,
            (agent_id, question_hash)
        )

    @staticmethod
    def create_knowledge(
        agent_id: str,
        answer_text: str,
        scope_type: str = 'course',
        knowledge_type: str = 'qa_pair',
        source: str = 'auto_generated',
        question_text: Optional[str] = None,
        scope_id: Optional[str] = None,
        method_type: Optional[int] = None,
        answer_html: Optional[str] = None,
        generated_by: Optional[str] = None,
        quality_score: float = 0.5
    ) -> Dict[str, Any]:
        """
        Create a new knowledge entry

        Args:
            agent_id: Agent UUID
            answer_text: Answer content
            scope_type: Scope (course, chapter, lesson, method)
            knowledge_type: Type (qa_pair, explanation, example, etc.)
            source: Source (auto_generated, user_interaction, manual, imported)
            question_text: Optional question text
            scope_id: Optional scope UUID
            method_type: Optional learning method type
            answer_html: Optional HTML formatted answer
            generated_by: Optional model name
            quality_score: Initial quality score (0.0-1.0)

        Returns:
            Created knowledge data
        """
        question_hash = None
        if question_text:
            question_hash = hashlib.sha256(
                question_text.lower().strip().encode()
            ).hexdigest()

        query = """
            INSERT INTO smart_agents.agent_knowledge_base (
                agent_id,
                scope_type,
                scope_id,
                knowledge_type,
                method_type,
                question_hash,
                question_text,
                answer_text,
                answer_html,
                source,
                generated_by,
                quality_score
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING *
        """
        return KnowledgeRepositoryCRUD.fetch_one(query, (
            agent_id,
            scope_type,
            scope_id,
            knowledge_type,
            method_type,
            question_hash,
            question_text,
            answer_text,
            answer_html,
            source,
            generated_by,
            quality_score
        ))

    @staticmethod
    def update_knowledge(
        knowledge_id: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Update knowledge entry

        Args:
            knowledge_id: Knowledge UUID
            **kwargs: Fields to update (answer_text, answer_html, quality_score)

        Returns:
            Updated knowledge data
        """
        allowed_fields = {
            'answer_text', 'answer_html', 'quality_score'
        }

        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return KnowledgeRepositoryCRUD.get_knowledge_by_id(knowledge_id)

        set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
        query = f"""
            UPDATE smart_agents.agent_knowledge_base
            SET {set_clause}, updated_at = NOW()
            WHERE knowledge_id = %s
            RETURNING *
        """
        values = list(updates.values()) + [knowledge_id]
        return KnowledgeRepositoryCRUD.fetch_one(query, tuple(values))

    @staticmethod
    def increment_usage(knowledge_id: str) -> bool:
        """
        Increment usage count for a knowledge entry

        Args:
            knowledge_id: Knowledge UUID

        Returns:
            True if updated
        """
        query = """
            UPDATE smart_agents.agent_knowledge_base
            SET usage_count = usage_count + 1, updated_at = NOW()
            WHERE knowledge_id = %s
        """
        result = KnowledgeRepositoryCRUD.execute(query, (knowledge_id,))
        return result is not None

    @staticmethod
    def record_feedback(
        knowledge_id: str,
        is_positive: bool
    ) -> bool:
        """
        Record user feedback for a knowledge entry

        Args:
            knowledge_id: Knowledge UUID
            is_positive: True for positive, False for negative

        Returns:
            True if updated
        """
        if is_positive:
            query = """
                UPDATE smart_agents.agent_knowledge_base
                SET positive_feedback = positive_feedback + 1, updated_at = NOW()
                WHERE knowledge_id = %s
            """
        else:
            query = """
                UPDATE smart_agents.agent_knowledge_base
                SET negative_feedback = negative_feedback + 1, updated_at = NOW()
                WHERE knowledge_id = %s
            """
        result = KnowledgeRepositoryCRUD.execute(query, (knowledge_id,))
        return result is not None

    @staticmethod
    def update_quality_score(
        knowledge_id: str,
        delta: float = 0.1
    ) -> Optional[Dict[str, Any]]:
        """
        Update quality score for a knowledge entry

        Args:
            knowledge_id: Knowledge UUID
            delta: Amount to add/subtract from quality score

        Returns:
            Updated knowledge data
        """
        query = """
            UPDATE smart_agents.agent_knowledge_base
            SET quality_score = GREATEST(0, LEAST(1, quality_score + %s)),
                updated_at = NOW()
            WHERE knowledge_id = %s
            RETURNING *
        """
        return KnowledgeRepositoryCRUD.fetch_one(query, (delta, knowledge_id))

    @staticmethod
    def get_knowledge_count(agent_id: str) -> int:
        """
        Get total knowledge count for an agent

        Args:
            agent_id: Agent UUID

        Returns:
            Count of knowledge entries
        """
        query = """
            SELECT COUNT(*) as count
            FROM smart_agents.agent_knowledge_base
            WHERE agent_id = %s AND superseded_by IS NULL
        """
        result = KnowledgeRepositoryCRUD.fetch_one(query, (agent_id,))
        return result['count'] if result else 0
