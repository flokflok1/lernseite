"""
Knowledge Base Search Operations

Handles knowledge discovery and retrieval:
- Full-text search for similar questions
- Scope-based knowledge filtering
- Best match finding (exact + fuzzy)

Inherits from BaseRepository for connection pooling and standard operations.
"""

from typing import Optional, Dict, List, Any
import hashlib

from app.repositories.base_repository import BaseRepository


class KnowledgeRepositorySearch(BaseRepository):
    """
    Search operations for Knowledge Base entries

    Handles knowledge discovery including:
    - Full-text search using PostgreSQL capabilities
    - Scope-based filtering (course, chapter, lesson, method)
    - Best match finding with fallback strategies
    - Similarity ranking
    """

    @staticmethod
    def find_similar_knowledge(
        agent_id: str,
        query_text: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar questions using PostgreSQL full-text search

        Args:
            agent_id: Agent UUID
            query_text: Question to search for
            limit: Max results (default 5)

        Returns:
            List of similar knowledge entries with similarity rank
        """
        query = """
            SELECT * FROM find_similar_knowledge(%s, %s, %s)
        """
        return KnowledgeRepositorySearch.fetch_all(
            query,
            (agent_id, query_text, limit)
        )

    @staticmethod
    def get_knowledge_for_scope(
        agent_id: str,
        scope_type: str,
        scope_id: Optional[str] = None,
        knowledge_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get knowledge entries for a specific scope

        Args:
            agent_id: Agent UUID
            scope_type: Scope type (course, chapter, lesson, method)
            scope_id: Optional specific scope ID
            knowledge_type: Optional filter by knowledge type
            limit: Max results (default 100)

        Returns:
            List of knowledge entries ordered by quality and usage
        """
        conditions = ["agent_id = %s", "scope_type = %s"]
        params: List[Any] = [agent_id, scope_type]

        if scope_id:
            conditions.append("scope_id = %s")
            params.append(scope_id)

        if knowledge_type:
            conditions.append("knowledge_type = %s")
            params.append(knowledge_type)

        conditions.append("superseded_by IS NULL")

        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT *
            FROM smart_agents.agent_knowledge_base
            WHERE {where_clause}
            ORDER BY quality_score DESC, usage_count DESC
            LIMIT %s
        """
        params.append(limit)
        return KnowledgeRepositorySearch.fetch_all(query, tuple(params))

    @staticmethod
    def get_best_match(
        agent_id: str,
        question: str,
        min_similarity: float = 0.1
    ) -> Optional[Dict[str, Any]]:
        """
        Get best matching knowledge entry for a question

        First tries exact hash match, then falls back to full-text search.

        Args:
            agent_id: Agent UUID
            question: Question to match
            min_similarity: Minimum similarity threshold (0.0-1.0)

        Returns:
            Best matching knowledge entry with match metadata or None
            Returns dict with keys: match_type ('exact' or 'similar'),
                                   similarity (float 0.0-1.0)
        """
        from app.repositories.knowledge.crud import KnowledgeRepositoryCRUD

        # Try exact match first
        question_hash = hashlib.sha256(
            question.lower().strip().encode()
        ).hexdigest()
        exact = KnowledgeRepositoryCRUD.get_knowledge_by_hash(
            agent_id,
            question_hash
        )
        if exact:
            return {**exact, 'match_type': 'exact', 'similarity': 1.0}

        # Fall back to full-text search
        similar = KnowledgeRepositorySearch.find_similar_knowledge(
            agent_id,
            question,
            limit=1
        )
        if similar and similar[0].get('similarity_rank', 0) >= min_similarity:
            return {
                **similar[0],
                'match_type': 'similar',
                'similarity': similar[0]['similarity_rank']
            }

        return None
