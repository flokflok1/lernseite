"""
LernsystemX Cache Service - Part 2

Domain-specific cache invalidation methods and caching decorator.

Extends CacheServiceBase (from service.py) with:
- invalidate_user_cache
- invalidate_course_cache
- invalidate_organisation_cache
- invalidate_category_cache
- invalidate_learning_methods_cache

Also provides the @cached decorator for function-level caching.

ISO 9001:2015 compliant - Service layer
"""

import inspect
import logging
from typing import Any, Optional, Callable
from functools import wraps

from flask import current_app

logger = logging.getLogger(__name__)


class CacheInvalidationMixin:
    """
    Mixin providing domain-specific cache invalidation methods.

    These methods build on the core cache operations (make_key,
    cache_delete_pattern) defined in CacheServiceBase.
    """

    @classmethod
    def invalidate_user_cache(cls, user_id: int) -> int:
        """
        Invalidate all cache entries for user

        Args:
            user_id: User ID

        Returns:
            int: Number of keys deleted

        Example:
            >>> CacheService.invalidate_user_cache(123)
        """
        pattern = cls.make_key('USER', str(user_id), '*')
        return cls.cache_delete_pattern(pattern)

    @classmethod
    def invalidate_course_cache(cls, course_id: int) -> int:
        """
        Invalidate all cache entries for course

        Args:
            course_id: Course ID

        Returns:
            int: Number of keys deleted

        Example:
            >>> CacheService.invalidate_course_cache(42)
        """
        pattern = cls.make_key('COURSE', str(course_id), '*')
        return cls.cache_delete_pattern(pattern)

    @classmethod
    def invalidate_organisation_cache(cls, org_id: int) -> int:
        """
        Invalidate all cache entries for organisation

        Args:
            org_id: Organisation ID

        Returns:
            int: Number of keys deleted

        Example:
            >>> CacheService.invalidate_organisation_cache(5)
        """
        pattern = cls.make_key('ORG', str(org_id), '*')
        return cls.cache_delete_pattern(pattern)

    @classmethod
    def invalidate_category_cache(cls) -> int:
        """
        Invalidate category tree cache

        Returns:
            int: Number of keys deleted

        Example:
            >>> CacheService.invalidate_category_cache()
        """
        pattern = cls.make_key('CATEGORY', '*')
        return cls.cache_delete_pattern(pattern)

    @classmethod
    def invalidate_learning_methods_cache(cls) -> int:
        """
        Invalidate learning methods cache

        Returns:
            int: Number of keys deleted

        Example:
            >>> CacheService.invalidate_learning_methods_cache()
        """
        pattern = cls.make_key('METHODS', '*')
        return cls.cache_delete_pattern(pattern)


def cached(
    key_pattern: str,
    ttl_config_key: Optional[str] = None,
    ttl: Optional[int] = None
) -> Callable:
    """
    Decorator for caching function results

    Args:
        key_pattern: Cache key pattern with {arg} placeholders
        ttl_config_key: Config key for TTL (e.g., 'CACHE_COURSE_TTL')
        ttl: Fixed TTL in seconds (overrides ttl_config_key)

    Returns:
        Callable: Decorated function with caching behavior

    Example:
        >>> @cached('CACHE:COURSE:{course_id}:detail', ttl_config_key='CACHE_COURSE_TTL')
        >>> def get_course_details(course_id):
        ...     return CourseRepository.get_by_id(course_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Import here to avoid circular dependency at module level
            from app.infrastructure.cache.service import CacheService

            try:
                # Get function argument names
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                # Replace placeholders in key pattern
                cache_key = key_pattern
                for arg_name, arg_value in bound_args.arguments.items():
                    cache_key = cache_key.replace(
                        f'{{{arg_name}}}', str(arg_value)
                    )

                # Get TTL from config or use fixed value
                cache_ttl = ttl
                if cache_ttl is None and ttl_config_key:
                    cache_ttl = current_app.config.get(ttl_config_key)

                # Use cache_get_or_set
                return CacheService.cache_get_or_set(
                    cache_key,
                    cache_ttl,
                    lambda: func(*args, **kwargs)
                )

            except Exception as e:
                logger.error(f"Cache decorator error: {e}")
                # Fallback to direct function call
                return func(*args, **kwargs)

        return wrapper
    return decorator
