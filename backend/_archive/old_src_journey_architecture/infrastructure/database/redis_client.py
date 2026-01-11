"""
Redis Client

Manages Redis connections for caching, JWT blacklist, and rate limiting.
"""

import os
from typing import Optional, Any
import redis
from redis import Redis


class RedisClient:
    """
    Redis client singleton.

    Used for:
    - JWT token blacklist
    - Rate limiting
    - Translation cache
    - Session management
    """

    _client: Optional[Redis] = None

    @classmethod
    def initialize(cls, redis_url: str) -> None:
        """
        Initialize Redis client.

        Args:
            redis_url: Redis connection URL
        """
        if cls._client is None:
            cls._client = redis.from_url(
                redis_url,
                decode_responses=True,
                encoding='utf-8'
            )

    @classmethod
    def get_client(cls) -> Redis:
        """
        Get Redis client instance.

        Returns:
            Redis client

        Raises:
            RuntimeError: If client not initialized
        """
        if cls._client is None:
            raise RuntimeError("Redis client not initialized. Call initialize() first.")
        return cls._client

    @classmethod
    def set(cls, key: str, value: str, expire: Optional[int] = None) -> bool:
        """
        Set key-value pair.

        Args:
            key: Redis key
            value: Value to store
            expire: Optional expiration in seconds

        Returns:
            True if successful
        """
        client = cls.get_client()
        return client.set(key, value, ex=expire)

    @classmethod
    def get(cls, key: str) -> Optional[str]:
        """
        Get value by key.

        Args:
            key: Redis key

        Returns:
            Value or None if not found
        """
        client = cls.get_client()
        return client.get(key)

    @classmethod
    def delete(cls, key: str) -> int:
        """
        Delete key.

        Args:
            key: Redis key

        Returns:
            Number of keys deleted
        """
        client = cls.get_client()
        return client.delete(key)

    @classmethod
    def exists(cls, key: str) -> bool:
        """
        Check if key exists.

        Args:
            key: Redis key

        Returns:
            True if key exists
        """
        client = cls.get_client()
        return client.exists(key) > 0

    @classmethod
    def close(cls) -> None:
        """Close Redis connection."""
        if cls._client:
            cls._client.close()
            cls._client = None
