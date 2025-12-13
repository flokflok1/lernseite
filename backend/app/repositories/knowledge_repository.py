"""
LernsystemX Knowledge Repository

Database access for Agent Knowledge Base:
- Knowledge entries (Q&A pairs, explanations, examples)
- Query logging and analytics
- Full-text search for similar questions

ISO 9001:2015 compliant - Knowledge data management
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib
from app.repositories.base_repository import BaseRepository


class KnowledgeRepository(BaseRepository):
    """
    Repository for Agent Knowledge Base operations

    Tables:
    - agent_knowledge_base: Pre-generated and learned knowledge entries
    - agent_query_log: Track all agent queries
    - agent_cache_entries: Redis cache metadata
    """

    # =========================================================================
    # Knowledge Base
    # =========================================================================

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
            FROM agent_knowledge_base
            WHERE knowledge_id = %s
        """
        return KnowledgeRepository.fetch_one(query, (knowledge_id,))

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
            FROM agent_knowledge_base
            WHERE agent_id = %s
            AND question_hash = %s
            AND superseded_by IS NULL
            ORDER BY version DESC
            LIMIT 1
        """
        return KnowledgeRepository.fetch_one(query, (agent_id, question_hash))

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
            limit: Max results

        Returns:
            List of similar knowledge entries with similarity rank
        """
        query = """
            SELECT * FROM find_similar_knowledge(%s, %s, %s)
        """
        return KnowledgeRepository.fetch_all(query, (agent_id, query_text, limit))

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

        Returns:
            Created knowledge data
        """
        # Generate hash from question if provided
        question_hash = None
        if question_text:
            question_hash = hashlib.sha256(
                question_text.lower().strip().encode()
            ).hexdigest()

        query = """
            INSERT INTO agent_knowledge_base (
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
        return KnowledgeRepository.fetch_one(query, (
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
            **kwargs: Fields to update

        Returns:
            Updated knowledge data
        """
        allowed_fields = {
            'answer_text', 'answer_html', 'quality_score'
        }

        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return KnowledgeRepository.get_knowledge_by_id(knowledge_id)

        set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
        query = f"""
            UPDATE agent_knowledge_base
            SET {set_clause}, updated_at = NOW()
            WHERE knowledge_id = %s
            RETURNING *
        """
        values = list(updates.values()) + [knowledge_id]
        return KnowledgeRepository.fetch_one(query, tuple(values))

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
            UPDATE agent_knowledge_base
            SET usage_count = usage_count + 1, updated_at = NOW()
            WHERE knowledge_id = %s
        """
        result = KnowledgeRepository.execute(query, (knowledge_id,))
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
                UPDATE agent_knowledge_base
                SET positive_feedback = positive_feedback + 1, updated_at = NOW()
                WHERE knowledge_id = %s
            """
        else:
            query = """
                UPDATE agent_knowledge_base
                SET negative_feedback = negative_feedback + 1, updated_at = NOW()
                WHERE knowledge_id = %s
            """
        result = KnowledgeRepository.execute(query, (knowledge_id,))
        return result is not None

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
            limit: Max results

        Returns:
            List of knowledge entries
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
            FROM agent_knowledge_base
            WHERE {where_clause}
            ORDER BY quality_score DESC, usage_count DESC
            LIMIT %s
        """
        params.append(limit)
        return KnowledgeRepository.fetch_all(query, tuple(params))

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
            FROM agent_knowledge_base
            WHERE agent_id = %s AND superseded_by IS NULL
        """
        result = KnowledgeRepository.fetch_one(query, (agent_id,))
        return result['count'] if result else 0

    # =========================================================================
    # Query Logging
    # =========================================================================

    @staticmethod
    def log_query(
        agent_id: str,
        user_id: str,
        query_text: str,
        response_source: str,
        response_text: Optional[str] = None,
        cache_key: Optional[str] = None,
        tokens_used: int = 0,
        tokens_saved: int = 0,
        cost_eur: float = 0,
        latency_ms: Optional[int] = None,
        ai_provider: Optional[str] = None,
        ai_model: Optional[str] = None,
        was_offline_mode: bool = False,
        context_scope: Optional[str] = None,
        context_id: Optional[str] = None,
        method_type: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Log an agent query

        Args:
            agent_id: Agent UUID
            user_id: User UUID
            query_text: Question asked
            response_source: Source of response (cache_hit, ai_generated, etc.)
            response_text: Optional response text
            cache_key: Optional cache key used
            tokens_used: Tokens consumed
            tokens_saved: Tokens saved (if cache hit)
            cost_eur: Cost in EUR
            latency_ms: Response latency in milliseconds
            ai_provider: AI provider used
            ai_model: AI model used
            was_offline_mode: Whether in offline mode
            context_scope: Optional context scope
            context_id: Optional context ID
            method_type: Optional learning method type

        Returns:
            Created query log entry
        """
        query_hash = hashlib.sha256(
            query_text.lower().strip().encode()
        ).hexdigest()

        query = """
            INSERT INTO agent_query_log (
                agent_id,
                user_id,
                query_text,
                query_hash,
                context_scope,
                context_id,
                method_type,
                response_text,
                response_source,
                cache_key,
                tokens_used,
                tokens_saved,
                cost_eur,
                latency_ms,
                ai_provider,
                ai_model,
                was_offline_mode
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING *
        """
        return KnowledgeRepository.fetch_one(query, (
            agent_id,
            user_id,
            query_text,
            query_hash,
            context_scope,
            context_id,
            method_type,
            response_text,
            response_source,
            cache_key,
            tokens_used,
            tokens_saved,
            cost_eur,
            latency_ms,
            ai_provider,
            ai_model,
            was_offline_mode
        ))

    @staticmethod
    def update_query_feedback(
        query_id: str,
        rating: Optional[int] = None,
        feedback: Optional[str] = None,
        was_helpful: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update query with user feedback

        Args:
            query_id: Query UUID
            rating: 1-5 rating
            feedback: Text feedback
            was_helpful: Boolean helpful indicator

        Returns:
            Updated query data
        """
        updates = []
        params: List[Any] = []

        if rating is not None:
            updates.append("user_rating = %s")
            params.append(rating)

        if feedback is not None:
            updates.append("user_feedback = %s")
            params.append(feedback)

        if was_helpful is not None:
            updates.append("was_helpful = %s")
            params.append(was_helpful)

        if not updates:
            return None

        set_clause = ", ".join(updates)
        query = f"""
            UPDATE agent_query_log
            SET {set_clause}
            WHERE query_id = %s
            RETURNING *
        """
        params.append(query_id)
        return KnowledgeRepository.fetch_one(query, tuple(params))

    @staticmethod
    def get_query_stats(
        agent_id: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get query statistics for an agent

        Args:
            agent_id: Agent UUID
            days: Number of days to look back

        Returns:
            Statistics dictionary
        """
        query = """
            SELECT
                COUNT(*) as total_queries,
                COUNT(*) FILTER (WHERE response_source = 'cache_hit') as cache_hits,
                COUNT(*) FILTER (WHERE response_source = 'ai_generated') as ai_generated,
                COUNT(*) FILTER (WHERE was_offline_mode = TRUE) as offline_queries,
                SUM(tokens_used) as total_tokens_used,
                SUM(tokens_saved) as total_tokens_saved,
                SUM(cost_eur) as total_cost_eur,
                AVG(latency_ms) as avg_latency_ms,
                AVG(user_rating) FILTER (WHERE user_rating IS NOT NULL) as avg_rating
            FROM agent_query_log
            WHERE agent_id = %s
            AND created_at > NOW() - INTERVAL '%s days'
        """
        return KnowledgeRepository.fetch_one(query, (agent_id, days))

    @staticmethod
    def get_popular_queries(
        agent_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get most popular queries for an agent

        Args:
            agent_id: Agent UUID
            limit: Max results

        Returns:
            List of popular queries with counts
        """
        query = """
            SELECT
                query_hash,
                MIN(query_text) as query_text,
                COUNT(*) as query_count,
                AVG(user_rating) FILTER (WHERE user_rating IS NOT NULL) as avg_rating
            FROM agent_query_log
            WHERE agent_id = %s
            GROUP BY query_hash
            ORDER BY query_count DESC
            LIMIT %s
        """
        return KnowledgeRepository.fetch_all(query, (agent_id, limit))

    # =========================================================================
    # Cache Entries
    # =========================================================================

    @staticmethod
    def create_cache_entry(
        agent_id: str,
        cache_key: str,
        cache_tier: int,
        ttl_seconds: int,
        knowledge_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a cache entry record

        Args:
            agent_id: Agent UUID
            cache_key: Redis cache key
            cache_tier: Cache tier (1-3)
            ttl_seconds: TTL in seconds
            knowledge_id: Optional linked knowledge entry

        Returns:
            Created cache entry
        """
        query = """
            INSERT INTO agent_cache_entries (
                agent_id,
                cache_key,
                cache_tier,
                ttl_seconds,
                expires_at,
                knowledge_id
            ) VALUES (
                %s, %s, %s, %s, NOW() + INTERVAL '%s seconds', %s
            )
            ON CONFLICT (cache_key) DO UPDATE SET
                hit_count = agent_cache_entries.hit_count + 1,
                last_hit_at = NOW(),
                expires_at = NOW() + INTERVAL '%s seconds'
            RETURNING *
        """
        return KnowledgeRepository.fetch_one(query, (
            agent_id, cache_key, cache_tier, ttl_seconds, ttl_seconds,
            knowledge_id, ttl_seconds
        ))

    @staticmethod
    def increment_cache_hit(cache_key: str) -> bool:
        """
        Increment cache hit count

        Args:
            cache_key: Redis cache key

        Returns:
            True if updated
        """
        query = """
            UPDATE agent_cache_entries
            SET hit_count = hit_count + 1, last_hit_at = NOW()
            WHERE cache_key = %s
        """
        result = KnowledgeRepository.execute(query, (cache_key,))
        return result is not None

    @staticmethod
    def cleanup_expired_cache_entries() -> int:
        """
        Delete expired cache entries

        Returns:
            Number of deleted entries
        """
        query = """
            DELETE FROM agent_cache_entries
            WHERE expires_at < NOW()
            RETURNING cache_id
        """
        results = KnowledgeRepository.fetch_all(query)
        return len(results) if results else 0

    @staticmethod
    def get_query_by_id(query_id: str) -> Optional[Dict[str, Any]]:
        """
        Get query log entry by ID

        Args:
            query_id: Query UUID

        Returns:
            Query log data or None
        """
        query = """
            SELECT *
            FROM agent_query_log
            WHERE query_id = %s
        """
        return KnowledgeRepository.fetch_one(query, (query_id,))

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
            UPDATE agent_knowledge_base
            SET quality_score = GREATEST(0, LEAST(1, quality_score + %s)),
                updated_at = NOW()
            WHERE knowledge_id = %s
            RETURNING *
        """
        return KnowledgeRepository.fetch_one(query, (delta, knowledge_id))

    # =========================================================================
    # Learning from Interactions
    # =========================================================================

    @staticmethod
    def learn_from_interaction(
        agent_id: str,
        question: str,
        answer: str,
        context_scope: str = 'course',
        context_id: Optional[str] = None,
        method_type: Optional[int] = None,
        generated_by: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Learn from a user interaction by storing as knowledge

        Only stores if question is unique enough (not already in knowledge base)

        Args:
            agent_id: Agent UUID
            question: Question asked
            answer: Answer provided
            context_scope: Scope (course, chapter, lesson, method)
            context_id: Optional scope ID
            method_type: Optional learning method type
            generated_by: Optional model name

        Returns:
            Created knowledge entry or None if duplicate
        """
        question_hash = hashlib.sha256(
            question.lower().strip().encode()
        ).hexdigest()

        # Check if already exists
        existing = KnowledgeRepository.get_knowledge_by_hash(agent_id, question_hash)
        if existing:
            # Just increment usage
            KnowledgeRepository.increment_usage(existing['knowledge_id'])
            return None

        # Create new knowledge entry
        return KnowledgeRepository.create_knowledge(
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

    @staticmethod
    def get_best_match(
        agent_id: str,
        question: str,
        min_similarity: float = 0.1
    ) -> Optional[Dict[str, Any]]:
        """
        Get best matching knowledge entry for a question

        First tries exact hash match, then falls back to full-text search

        Args:
            agent_id: Agent UUID
            question: Question to match
            min_similarity: Minimum similarity threshold

        Returns:
            Best matching knowledge entry or None
        """
        # Try exact match first
        question_hash = hashlib.sha256(
            question.lower().strip().encode()
        ).hexdigest()
        exact = KnowledgeRepository.get_knowledge_by_hash(agent_id, question_hash)
        if exact:
            return {**exact, 'match_type': 'exact', 'similarity': 1.0}

        # Fall back to full-text search
        similar = KnowledgeRepository.find_similar_knowledge(agent_id, question, limit=1)
        if similar and similar[0].get('similarity_rank', 0) >= min_similarity:
            return {**similar[0], 'match_type': 'similar', 'similarity': similar[0]['similarity_rank']}

        return None
