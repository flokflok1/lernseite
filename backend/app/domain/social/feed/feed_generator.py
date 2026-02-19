"""
Feed Generator Service

Generates personalized feeds for users with algorithmic ranking.
Compliant with DSA Art. 24 (Algorithm Disclosure).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.domain.ports.core.registry import repos


class FeedGenerator:
    """Service for generating personalized social feeds"""

    @staticmethod
    def generate_feed(user_id: str, limit: int = 20, offset: int = 0,
                     algorithm: str = 'personalized') -> Dict[str, Any]:
        """
        Generate personalized feed for user.

        Args:
            user_id: User ID
            limit: Max posts
            offset: Pagination offset
            algorithm: 'personalized', 'chronological', 'trending'

        Returns:
            Dict with posts and metadata (DSA disclosure)
        """
        if algorithm == 'chronological':
            posts = FeedGenerator._chronological_feed(user_id, limit, offset)
            disclosure = "This feed shows posts in chronological order from users you follow."
        elif algorithm == 'trending':
            posts = FeedGenerator._trending_feed(user_id, limit, offset)
            disclosure = "This feed shows trending posts based on engagement metrics."
        else:
            posts = FeedGenerator._personalized_feed(user_id, limit, offset)
            disclosure = (
                "This feed is ranked by an algorithm that considers: "
                "1) Posts from users you follow, "
                "2) Engagement (likes, comments, shares), "
                "3) Recency (newer posts ranked higher), "
                "4) Your past interactions. "
                "You can switch to chronological order in settings. (DSA Art. 24)"
            )

        return {
            'posts': posts,
            'meta': {
                'algorithm': algorithm,
                'disclosure': disclosure,
                'total': len(posts),
                'limit': limit,
                'offset': offset
            }
        }

    @staticmethod
    def _personalized_feed(user_id: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """
        Personalized feed with algorithmic ranking.

        Ranking factors:
        - Following relationship (10x weight)
        - Engagement score (likes + 2*comments + 3*shares)
        - Recency decay (exponential decay over 7 days)
        - User interaction history
        """
        following = repos.social_follows.get_following(user_id, limit=1000, offset=0)
        following_ids = [f['following_id'] for f in following]

        if not following_ids:
            return FeedGenerator._trending_feed(user_id, limit, offset)

        posts = repos.social_posts.get_personalized_feed(following_ids, limit, offset)

        for post in posts:
            post['user_has_liked'] = FeedGenerator._check_user_liked(user_id, post['post_id'])
            post['user_has_bookmarked'] = FeedGenerator._check_user_bookmarked(
                user_id, post['post_id']
            )

        return posts

    @staticmethod
    def _chronological_feed(user_id: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """
        Chronological feed (newest first).
        No algorithmic ranking - simple time-based ordering.
        """
        following = repos.social_follows.get_following(user_id, limit=1000, offset=0)
        following_ids = [f['following_id'] for f in following]

        if not following_ids:
            return []

        posts = repos.social_posts.get_chronological_feed(following_ids, limit, offset)

        for post in posts:
            post['user_has_liked'] = FeedGenerator._check_user_liked(user_id, post['post_id'])
            post['user_has_bookmarked'] = FeedGenerator._check_user_bookmarked(
                user_id, post['post_id']
            )

        return posts

    @staticmethod
    def _trending_feed(user_id: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """
        Trending feed (hot posts from last 24h).

        Trending score = (engagement_score / time_penalty)
        time_penalty = (hours_since_post + 2) ^ 1.5
        """
        posts = repos.social_posts.get_trending_feed(limit, offset)

        for post in posts:
            post['user_has_liked'] = FeedGenerator._check_user_liked(user_id, post['post_id'])
            post['user_has_bookmarked'] = FeedGenerator._check_user_bookmarked(
                user_id, post['post_id']
            )

        return posts

    @staticmethod
    def get_explore_feed(user_id: str, category: Optional[str] = None,
                        limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Explore feed (discover new content outside following).

        Args:
            user_id: User ID
            category: Optional filter (e.g., 'course_portfolio', 'achievement')
            limit: Max posts
            offset: Pagination offset

        Returns:
            List of public posts user doesn't follow
        """
        following = repos.social_follows.get_following(user_id, limit=1000, offset=0)
        following_ids = [f['following_id'] for f in following]
        following_ids.append(user_id)  # Exclude own posts

        posts = repos.social_posts.get_explore_feed(
            following_ids, limit, offset, category=category
        )

        for post in posts:
            post['user_has_liked'] = FeedGenerator._check_user_liked(user_id, post['post_id'])
            post['user_has_bookmarked'] = FeedGenerator._check_user_bookmarked(
                user_id, post['post_id']
            )

        return posts

    @staticmethod
    def get_hashtag_feed(hashtag: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get posts with a specific hashtag."""
        return repos.social_posts.get_hashtag_feed(hashtag, limit, offset)

    # =====================
    # HELPER METHODS
    # =====================

    @staticmethod
    def _check_user_liked(user_id: str, post_id: str) -> bool:
        """Check if user has liked a post."""
        like = repos.social_likes.get_like(user_id, post_id)
        return like is not None

    @staticmethod
    def _check_user_bookmarked(user_id: str, post_id: str) -> bool:
        """Check if user has bookmarked a post."""
        bookmark = repos.social_likes.get_bookmark(user_id, post_id)
        return bookmark is not None
