"""
Agent Cache Entry Management

Handles Redis cache metadata tracking:
- Cache entry creation and lifecycle
- Hit count tracking
- Expired entry cleanup
- TTL management

Inherits from BaseRepository for connection pooling and standard operations.
"""

from typing import Optional, Dict, Any

from app.infrastructure.persistence.repositories.core.base import BaseRepository


class KnowledgeRepositoryCache(BaseRepository):
    """
    Cache entry management for Agent knowledge caching

    Handles Redis cache metadata including:
    - Creating cache entries with TTL tracking
    - Incrementing cache hit counters
    - Cleaning up expired entries
    - Multi-tier cache support
    """

    table_name = 'smart_agents.agent_cache_entries'

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

        Creates or updates a cache entry with TTL. Uses UPSERT pattern
        (ON CONFLICT) to handle re-caching of existing keys.

        Args:
            agent_id: Agent UUID
            cache_key: Redis cache key
            cache_tier: Cache tier (1-3) indicating priority/level
            ttl_seconds: TTL in seconds
            knowledge_id: Optional linked knowledge entry UUID

        Returns:
            Created or updated cache entry with metadata
        """
        query = """
            INSERT INTO smart_agents.agent_cache_entries (
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
                hit_count = smart_agents.agent_cache_entries.hit_count + 1,
                last_hit_at = NOW(),
                expires_at = NOW() + INTERVAL '%s seconds'
            RETURNING *
        """
        return KnowledgeRepositoryCache.fetch_one(query, (
            agent_id, cache_key, cache_tier, ttl_seconds, ttl_seconds,
            knowledge_id, ttl_seconds
        ))

    @staticmethod
    def increment_cache_hit(cache_key: str) -> bool:
        """
        Increment cache hit count for a cache entry

        Args:
            cache_key: Redis cache key

        Returns:
            True if updated successfully
        """
        query = """
            UPDATE smart_agents.agent_cache_entries
            SET hit_count = hit_count + 1, last_hit_at = NOW()
            WHERE cache_key = %s
        """
        result = KnowledgeRepositoryCache.execute(query, (cache_key,))
        return result is not None

    @staticmethod
    def cleanup_expired_cache_entries() -> int:
        """
        Delete all expired cache entries

        Removes cache entries where expires_at < NOW().
        Typically called by a background job.

        Returns:
            Number of deleted entries
        """
        query = """
            DELETE FROM smart_agents.agent_cache_entries
            WHERE expires_at < NOW()
            RETURNING cache_id
        """
        results = KnowledgeRepositoryCache.fetch_all(query)
        return len(results) if results else 0
