"""
Social Posts Feed Repository

Feed queries: personalized, chronological, trending, explore, hashtag, search.
Extracted from domain/social/ to comply with DDD repository rules.
"""

from typing import Optional, List, Dict, Any

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all


class SocialPostsFeedRepository:
    """Repository for social feed queries"""

    @staticmethod
    def get_personalized_feed(following_ids: List[str], limit: int = 20,
                              offset: int = 0) -> List[Dict[str, Any]]:
        """Get personalized feed ranked by engagement and recency."""
        query = """
            SELECT p.*,
                   u.username, u.profile_picture_url,
                   (p.likes_count + 2 * p.comments_count + 3 * p.shares_count) as engagement_score,
                   EXP(-EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - p.created_at)) / 86400.0) as recency_score,
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
        return fetch_all(query, (following_ids, limit, offset))

    @staticmethod
    def get_chronological_feed(following_ids: List[str], limit: int = 20,
                               offset: int = 0) -> List[Dict[str, Any]]:
        """Get chronological feed (newest first, no ranking)."""
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
        return fetch_all(query, (following_ids, limit, offset))

    @staticmethod
    def get_trending_feed(limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get trending feed (HackerNews-style scoring, last 24h)."""
        query = """
            SELECT p.*,
                   u.username, u.profile_picture_url,
                   (p.likes_count + 2 * p.comments_count + 3 * p.shares_count) as engagement_score,
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
        return fetch_all(query, (limit, offset))

    @staticmethod
    def get_explore_feed(excluded_user_ids: List[str], limit: int = 20,
                         offset: int = 0,
                         category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get explore feed (public posts from unfollowed users)."""
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
            return fetch_all(
                query, (excluded_user_ids, category, limit, offset)
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
            return fetch_all(
                query, (excluded_user_ids, limit, offset)
            )

    @staticmethod
    def get_hashtag_feed(hashtag: str, limit: int = 20,
                         offset: int = 0) -> List[Dict[str, Any]]:
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
        return fetch_all(query, (hashtag.lower(), limit, offset))

    @staticmethod
    def get_trending_hashtags(limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending hashtags (last 24h)."""
        query = """
            SELECT hashtag, COUNT(*) as post_count
            FROM social.social_post_hashtags
            WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
            GROUP BY hashtag
            ORDER BY post_count DESC
            LIMIT %s
        """
        return fetch_all(query, (limit,))

    @staticmethod
    def get_trending_posts(limit: int = 20) -> List[Dict[str, Any]]:
        """Get trending posts by engagement score (last 24h)."""
        query = """
            SELECT p.*, u.username,
                   (p.likes_count + 2 * p.comments_count + 3 * p.shares_count) as engagement_score
            FROM social.social_posts p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
              AND p.visibility = 'public'
              AND p.moderation_status = 'ai_approved'
            ORDER BY engagement_score DESC, p.created_at DESC
            LIMIT %s
        """
        return fetch_all(query, (limit,))

    @staticmethod
    def get_explore_posts(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get explore posts (public, from unfollowed users)."""
        query = """
            SELECT p.*, u.username
            FROM social.social_posts p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.user_id NOT IN (
                SELECT following_id FROM social.social_follows WHERE follower_id = %s
            )
            AND p.visibility = 'public'
            AND p.moderation_status = 'ai_approved'
            ORDER BY p.created_at DESC
            LIMIT %s
        """
        return fetch_all(query, (user_id, limit))

    @staticmethod
    def search_posts_by_content(query_text: str,
                                limit: int = 20) -> List[Dict[str, Any]]:
        """Search posts by content (ILIKE)."""
        query = """
            SELECT p.*, u.username
            FROM social.social_posts p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.content ILIKE %s
              AND p.visibility = 'public'
            ORDER BY p.created_at DESC
            LIMIT %s
        """
        return fetch_all(query, (f'%{query_text}%', limit))

    @staticmethod
    def get_post_metrics(post_id: str) -> Dict[str, Any]:
        """Get engagement metrics for a post."""
        query = """
            SELECT
                likes_count,
                comments_count,
                shares_count,
                views_count
            FROM social.social_posts
            WHERE post_id = %s
        """
        return fetch_one(query, (post_id,)) or {}
