"""
Cache System

Redis cache management and operations.
"""

from app.infrastructure.cache.service import CacheService
from app.infrastructure.cache.service_part2 import cached

__all__ = ['CacheService', 'cached']
