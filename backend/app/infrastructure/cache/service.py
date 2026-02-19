"""
LernsystemX Cache Service

Central caching abstraction layer for Redis operations:
- Consistent key generation with namespace convention
- JSON serialization with Pydantic support
- TTL management with configuration-based defaults
- Graceful error handling (system continues if Redis unavailable)
- Lazy loading pattern with cache_get_or_set
- Multi-tenancy support in key structure

Key Namespace Convention:
  CACHE:USER:{user_id}:profile
  CACHE:COURSE:{course_id}:detail
  CACHE:MODULE:{module_id}:detail
  CACHE:ORG:{org_id}:settings
  CACHE:CATEGORY:tree:active
  CACHE:METHODS:list
  CACHE:ANALYTICS:org:{org_id}:stats
  CACHE:KI:{hash}:result

Security:
- NO sensitive data (passwords, tokens, secrets, 2FA codes)
- NO cross-tenant leaks (org_id/user_id in keys)
- NO caching of auth responses with JWT

ISO 9001:2015 compliant - Service layer
"""

import json
import hashlib
import logging
from typing import Any, Optional, Callable

from app.core.bootstrap.extensions import redis_client
from app.infrastructure.cache.service_part2 import CacheInvalidationMixin, cached  # noqa: F401

logger = logging.getLogger(__name__)

# Import monitoring (if available)
try:
    from app.infrastructure.monitoring import record_cache_operation
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False


class CacheService(CacheInvalidationMixin):
    """
    Central cache service for Redis operations

    Provides consistent caching interface with:
    - Key generation
    - Get/Set/Delete operations
    - Lazy loading pattern
    - JSON serialization
    - Error handling

    Domain-specific invalidation methods are provided via
    CacheInvalidationMixin (service_part2.py).
    """

    # Cache key prefix
    CACHE_PREFIX = "CACHE"

    @classmethod
    def get_cache_client(cls):
        """
        Get Redis client instance

        Returns:
            Redis client from extensions

        Example:
            >>> client = CacheService.get_cache_client()
        """
        return redis_client

    @classmethod
    def make_key(cls, *parts: str) -> str:
        """
        Generate consistent cache key from parts

        Args:
            *parts: Key parts to join

        Returns:
            str: Cache key in format CACHE:PART1:PART2:...

        Example:
            >>> CacheService.make_key('USER', '123', 'profile')
            'CACHE:USER:123:profile'
            >>> CacheService.make_key('COURSE', '42', 'detail')
            'CACHE:COURSE:42:detail'
        """
        # Filter out None values and convert all to strings
        clean_parts = [str(p) for p in parts if p is not None]
        return f"{cls.CACHE_PREFIX}:{':'.join(clean_parts)}"

    @classmethod
    def _serialize(cls, value: Any) -> str:
        """
        Serialize value to JSON string

        Supports:
        - Pydantic models (via model_dump())
        - Dicts, lists, primitives
        - Custom objects with __dict__

        Args:
            value: Value to serialize

        Returns:
            str: JSON string

        Raises:
            ValueError: If value cannot be serialized
        """
        try:
            # Handle Pydantic models
            if hasattr(value, 'model_dump'):
                return json.dumps(value.model_dump())

            # Handle dict/list/primitives
            if isinstance(value, (dict, list, str, int, float, bool, type(None))):
                return json.dumps(value)

            # Try to serialize object with __dict__
            if hasattr(value, '__dict__'):
                return json.dumps(value.__dict__)

            # Fallback: convert to string
            return json.dumps(str(value))

        except (TypeError, ValueError) as e:
            raise ValueError(f"Cannot serialize value of type {type(value)}: {e}")

    @classmethod
    def _deserialize(cls, value: str) -> Any:
        """
        Deserialize JSON string to Python object

        Args:
            value: JSON string

        Returns:
            Deserialized object

        Raises:
            ValueError: If value cannot be deserialized
        """
        try:
            return json.loads(value)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Cannot deserialize value: {e}")

    @classmethod
    def cache_get(cls, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or error

        Example:
            >>> key = CacheService.make_key('COURSE', '42', 'detail')
            >>> course = CacheService.cache_get(key)
        """
        try:
            value = redis_client.get(key)
            if value is None:
                logger.debug(f"Cache miss: {key}")
                # Record cache miss metric
                if MONITORING_AVAILABLE:
                    record_cache_operation(operation='get', result='miss')
                return None

            logger.debug(f"Cache hit: {key}")
            # Record cache hit metric
            if MONITORING_AVAILABLE:
                record_cache_operation(operation='get', result='hit')
            return cls._deserialize(value)

        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            # Record cache error metric
            if MONITORING_AVAILABLE:
                record_cache_operation(operation='get', result='error')
            # Graceful degradation - return None on error
            return None

    @classmethod
    def cache_set(
        cls,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache with optional TTL

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (None = no expiry)

        Returns:
            bool: True if successful, False on error

        Example:
            >>> key = CacheService.make_key('COURSE', '42', 'detail')
            >>> CacheService.cache_set(key, course_data, ttl=3600)
        """
        try:
            serialized = cls._serialize(value)

            if ttl is not None:
                redis_client.setex(key, ttl, serialized)
            else:
                redis_client.set(key, serialized)

            logger.debug(f"Cache set: {key} (TTL: {ttl})")
            # Record cache set metric
            if MONITORING_AVAILABLE:
                record_cache_operation(operation='set', result='success')
            return True

        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            # Record cache error metric
            if MONITORING_AVAILABLE:
                record_cache_operation(operation='set', result='error')
            # Graceful degradation - continue even if cache fails
            return False

    @classmethod
    def cache_delete(cls, key: str) -> bool:
        """
        Delete value from cache

        Args:
            key: Cache key

        Returns:
            bool: True if deleted, False if not found or error

        Example:
            >>> key = CacheService.make_key('COURSE', '42', 'detail')
            >>> CacheService.cache_delete(key)
        """
        try:
            result = redis_client.delete(key)
            logger.debug(f"Cache delete: {key} (deleted: {result})")
            # Record cache delete metric
            if MONITORING_AVAILABLE:
                record_cache_operation(operation='delete', result='success' if result > 0 else 'miss')
            return result > 0

        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            # Record cache error metric
            if MONITORING_AVAILABLE:
                record_cache_operation(operation='delete', result='error')
            return False

    @classmethod
    def cache_delete_pattern(cls, pattern: str) -> int:
        """
        Delete all keys matching pattern

        Args:
            pattern: Key pattern (supports * wildcard)

        Returns:
            int: Number of keys deleted

        Example:
            >>> # Delete all course caches
            >>> CacheService.cache_delete_pattern('CACHE:COURSE:*')
            >>> # Delete all caches for specific organisation
            >>> CacheService.cache_delete_pattern('CACHE:ORG:5:*')
        """
        try:
            keys = redis_client.keys(pattern)
            if not keys:
                return 0

            deleted = redis_client.delete(*keys)
            logger.info(f"Cache delete pattern '{pattern}': {deleted} keys deleted")
            return deleted

        except Exception as e:
            logger.error(f"Cache delete pattern error for '{pattern}': {e}")
            return 0

    @classmethod
    def cache_exists(cls, key: str) -> bool:
        """
        Check if key exists in cache

        Args:
            key: Cache key

        Returns:
            bool: True if key exists, False otherwise

        Example:
            >>> key = CacheService.make_key('COURSE', '42', 'detail')
            >>> if CacheService.cache_exists(key):
            ...     print("Cache hit!")
        """
        try:
            return redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error for key '{key}': {e}")
            return False

    @classmethod
    def cache_get_or_set(
        cls,
        key: str,
        ttl: Optional[int],
        loader_func: Callable[[], Any]
    ) -> Any:
        """
        Get value from cache or load and cache it (lazy loading pattern)

        Args:
            key: Cache key
            ttl: Time to live in seconds (None = no expiry)
            loader_func: Function to call if cache miss (returns value to cache)

        Returns:
            Cached or freshly loaded value

        Example:
            >>> def load_course():
            ...     return CourseRepository.get_by_id(42)
            >>>
            >>> key = CacheService.make_key('COURSE', '42', 'detail')
            >>> course = CacheService.cache_get_or_set(
            ...     key,
            ...     ttl=3600,
            ...     loader_func=load_course
            ... )
        """
        try:
            # Try to get from cache first
            cached_value = cls.cache_get(key)
            if cached_value is not None:
                return cached_value

            # Cache miss - load fresh data
            logger.debug(f"Cache miss, loading fresh data for: {key}")
            fresh_value = loader_func()

            # Cache the result
            if fresh_value is not None:
                cls.cache_set(key, fresh_value, ttl)

            return fresh_value

        except Exception as e:
            logger.error(f"Cache get_or_set error for key '{key}': {e}")
            # On error, try to load fresh data
            try:
                return loader_func()
            except Exception as load_error:
                logger.error(f"Loader function failed for key '{key}': {load_error}")
                raise

    @classmethod
    def cache_get_ttl(cls, key: str) -> Optional[int]:
        """
        Get remaining TTL for key

        Args:
            key: Cache key

        Returns:
            int: Seconds until expiry, -1 if no expiry, None if key doesn't exist

        Example:
            >>> key = CacheService.make_key('COURSE', '42', 'detail')
            >>> ttl = CacheService.cache_get_ttl(key)
        """
        try:
            ttl = redis_client.ttl(key)
            if ttl == -2:  # Key doesn't exist
                return None
            return ttl
        except Exception as e:
            logger.error(f"Cache get TTL error for key '{key}': {e}")
            return None

    @classmethod
    def generate_hash(cls, *args: Any) -> str:
        """
        Generate SHA256 hash from arguments (for KI cache keys)

        Args:
            *args: Values to hash

        Returns:
            str: Hex digest of SHA256 hash

        Example:
            >>> # KI prompt caching
            >>> prompt = "Generate flashcards for Python basics"
            >>> hash_key = CacheService.generate_hash(prompt, 'flashcards', 'claude-3')
            >>> cache_key = CacheService.make_key('KI', hash_key, 'result')
        """
        try:
            # Convert all args to string and join
            content = '|'.join(str(arg) for arg in args)
            return hashlib.sha256(content.encode('utf-8')).hexdigest()
        except Exception as e:
            logger.error(f"Hash generation error: {e}")
            # Fallback to simple string join
            return hashlib.sha256('|'.join(str(arg) for arg in args).encode()).hexdigest()
