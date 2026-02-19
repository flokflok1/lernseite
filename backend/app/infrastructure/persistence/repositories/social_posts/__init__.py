"""
Social Posts Repository Package

- core.py: CRUD operations for social posts
- feed.py: Feed queries (personalized, chronological, trending, explore, search)
"""

from .core import SocialPostsCoreRepository
from .feed import SocialPostsFeedRepository


class SocialPostsRepository(SocialPostsCoreRepository, SocialPostsFeedRepository):
    """Combined social posts repository with CRUD + feed queries."""
    pass


__all__ = ['SocialPostsRepository', 'SocialPostsCoreRepository', 'SocialPostsFeedRepository']
