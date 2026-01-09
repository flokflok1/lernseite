"""
Translation Cache Service

Redis-based caching for translations with permanent TTL.
Improves performance by caching frequently accessed translations.
"""

from typing import Optional, Dict, Any
from src.infrastructure.database.redis_client import RedisClient


class TranslationCache:
    """
    Translation cache using Redis.

    Caches translations with permanent TTL (no expiration).
    Cache invalidation happens on translation updates only.
    """

    CACHE_PREFIX = 'i18n:translation:'

    @classmethod
    def get(cls, key: str, language_code: str) -> Optional[str]:
        """
        Get cached translation.

        Args:
            key: Translation key (e.g., 'common.save')
            language_code: Language code (e.g., 'de')

        Returns:
            Cached translation or None if not found
        """
        cache_key = cls._build_cache_key(key, language_code)
        return RedisClient.get(cache_key)

    @classmethod
    def set(cls, key: str, language_code: str, translation: str) -> bool:
        """
        Cache translation with permanent TTL.

        Args:
            key: Translation key
            language_code: Language code
            translation: Translated text

        Returns:
            True if successful
        """
        cache_key = cls._build_cache_key(key, language_code)
        # Permanent cache (no expiration)
        return RedisClient.set(cache_key, translation, expire=None)

    @classmethod
    def delete(cls, key: str, language_code: str) -> int:
        """
        Delete cached translation.

        Args:
            key: Translation key
            language_code: Language code

        Returns:
            Number of keys deleted
        """
        cache_key = cls._build_cache_key(key, language_code)
        return RedisClient.delete(cache_key)

    @classmethod
    def delete_all(cls, key: str) -> int:
        """
        Delete all language variants of a translation key.

        Args:
            key: Translation key

        Returns:
            Number of keys deleted
        """
        # Get all keys matching pattern
        pattern = f"{cls.CACHE_PREFIX}{key}:*"
        client = RedisClient.get_client()
        keys = list(client.scan_iter(match=pattern))
        if keys:
            return client.delete(*keys)
        return 0

    @classmethod
    def invalidate_language(cls, language_code: str) -> int:
        """
        Invalidate entire language cache.

        Args:
            language_code: Language code to invalidate

        Returns:
            Number of keys deleted
        """
        pattern = f"{cls.CACHE_PREFIX}*:{language_code}"
        client = RedisClient.get_client()
        keys = list(client.scan_iter(match=pattern))
        if keys:
            return client.delete(*keys)
        return 0

    @classmethod
    def clear_all(cls) -> int:
        """
        Clear entire translation cache.

        Returns:
            Number of keys deleted
        """
        pattern = f"{cls.CACHE_PREFIX}*"
        client = RedisClient.get_client()
        keys = list(client.scan_iter(match=pattern))
        if keys:
            return client.delete(*keys)
        return 0

    @classmethod
    def exists(cls, key: str, language_code: str) -> bool:
        """
        Check if translation exists in cache.

        Args:
            key: Translation key
            language_code: Language code

        Returns:
            True if cached
        """
        cache_key = cls._build_cache_key(key, language_code)
        return RedisClient.exists(cache_key)

    @staticmethod
    def _build_cache_key(key: str, language_code: str) -> str:
        """
        Build cache key.

        Args:
            key: Translation key
            language_code: Language code

        Returns:
            Redis cache key
        """
        return f"i18n:translation:{key}:{language_code}"
