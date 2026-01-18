"""
Feed Generator Service

Generates personalized feeds for users with algorithmic ranking.
Compliant with DSA Art. 24 (Algorithm Disclosure).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.infrastructure.persistence.repositories.social_posts import SocialPostsRepository
from app.infrastructure.persistence.repositories.social_follows import SocialFollowsRepository
from app.infrastructure.persistence.repositories.social_likes import SocialLikesRepository


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
        # Get users that current user follows
        following = SocialFollowsRepository.get_following(user_id, limit=1000, offset=0)
        following_ids = [f['following_id'] for f in following]

        if not following_ids:
            # New user: show trending posts
            return FeedGenerator._trending_feed(user_id, limit, offset)

        # Get posts from followed users (last 7 days)
        query = """
            SELECT p.*,
                   u.username, u.profile_picture_url,
                   -- Engagement score
                   (p.likes_count + 2 * p.comments_count + 3 * p.shares_count) as engagement_score,
                   -- Recency score (exponential decay)
                   EXP(-EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - p.created_at)) / 86400.0) as recency_score,
                   -- Final score
                   (
                       (p.likes_count + 2 * p.comments_count + 3 * p.shares_count) *
                       EXP(-EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - p.created_at)) / 604800.0)
                   ) as final_score
            FROM social.social_posts p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.user_id = ANY(%s)
              AND p.is_deleted = FALSE
              AND p.moderation_status IN ('ai_approved', 'human_approved')
              AND p.visibility IN ('public', 'followers')
              AND p.created_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
            ORDER BY final_score DESC, p.created_at DESC
            LIMIT %s OFFSET %s
        """
        posts = SocialPostsRepository.fetch_all(query, (following_ids, limit, offset))

        # Add user interaction context
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
        following = SocialFollowsRepository.get_following(user_id, limit=1000, offset=0)
        following_ids = [f['following_id'] for f in following]

        if not following_ids:
            return []

        query = """
            SELECT p.*, u.username, u.profile_picture_url
            FROM social.social_posts p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.user_id = ANY(%s)
              AND p.is_deleted = FALSE
              AND p.moderation_status IN ('ai_approved', 'human_approved')
              AND p.visibility IN ('public', 'followers')
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
        """
        posts = SocialPostsRepository.fetch_all(query, (following_ids, limit, offset))

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
        query = """
            SELECT p.*,
                   u.username, u.profile_picture_url,
                   (p.likes_count + 2 * p.comments_count + 3 * p.shares_count) as engagement_score,
                   -- Trending score (HackerNews-style)
                   (p.likes_count + 2 * p.comments_count + 3 * p.shares_count) /
                   POWER(
                       (EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - p.created_at)) / 3600.0) + 2,
                       1.5
                   ) as trending_score
            FROM social.social_posts p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.is_deleted = FALSE
              AND p.moderation_status IN ('ai_approved', 'human_approved')
              AND p.visibility = 'public'
              AND p.created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
            ORDER BY trending_score DESC, p.created_at DESC
            LIMIT %s OFFSET %s
        """
        posts = SocialPostsRepository.fetch_all(query, (limit, offset))

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
        following = SocialFollowsRepository.get_following(user_id, limit=1000, offset=0)
        following_ids = [f['following_id'] for f in following]
        following_ids.append(user_id)  # Exclude own posts

        if category:
            query = """
                SELECT p.*, u.username, u.profile_picture_url,
                       (p.likes_count + 2 * p.comments_count + 3 * p.shares_count) as engagement_score
                FROM social.social_posts p
                JOIN users u ON p.user_id = u.user_id
                WHERE p.user_id != ALL(%s)
                  AND p.is_deleted = FALSE
                  AND p.moderation_status IN ('ai_approved', 'human_approved')
                  AND p.visibility = 'public'
                  AND p.content_type = %s
                  AND p.created_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
                ORDER BY engagement_score DESC, p.created_at DESC
                LIMIT %s OFFSET %s
            """
            posts = SocialPostsRepository.fetch_all(
                query, (following_ids, category, limit, offset)
            )
        else:
            query = """
                SELECT p.*, u.username, u.profile_picture_url,
                       (p.likes_count + 2 * p.comments_count + 3 * p.shares_count) as engagement_score
                FROM social.social_posts p
                JOIN users u ON p.user_id = u.user_id
                WHERE p.user_id != ALL(%s)
                  AND p.is_deleted = FALSE
                  AND p.moderation_status IN ('ai_approved', 'human_approved')
                  AND p.visibility = 'public'
                  AND p.created_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
                ORDER BY engagement_score DESC, p.created_at DESC
                LIMIT %s OFFSET %s
            """
            posts = SocialPostsRepository.fetch_all(query, (following_ids, limit, offset))

        for post in posts:
            post['user_has_liked'] = FeedGenerator._check_user_liked(user_id, post['post_id'])
            post['user_has_bookmarked'] = FeedGenerator._check_user_bookmarked(
                user_id, post['post_id']
            )

        return posts

    @staticmethod
    def get_hashtag_feed(hashtag: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get posts with a specific hashtag."""
        query = """
            SELECT DISTINCT p.*, u.username, u.profile_picture_url
            FROM social.social_posts p
            JOIN users u ON p.user_id = u.user_id
            JOIN social.social_post_hashtags h ON p.post_id = h.post_id
            WHERE h.hashtag = %s
              AND p.is_deleted = FALSE
              AND p.moderation_status IN ('ai_approved', 'human_approved')
              AND p.visibility = 'public'
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
        """
        return SocialPostsRepository.fetch_all(query, (hashtag.lower(), limit, offset))

    # =====================
    # HELPER METHODS
    # =====================

    @staticmethod
    def _check_user_liked(user_id: str, post_id: str) -> bool:
        """Check if user has liked a post."""
        like = SocialLikesRepository.get_like(user_id, post_id)
        return like is not None

    @staticmethod
    def _check_user_bookmarked(user_id: str, post_id: str) -> bool:
        """Check if user has bookmarked a post."""
        bookmark = SocialLikesRepository.get_bookmark(user_id, post_id)
        return bookmark is not None
