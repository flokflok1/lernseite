"""
Social Follows Repository

Handles database operations for social follows, blocks, mutes, and suggestions.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from app.repositories.base_repository import BaseRepository


class SocialFollowsRepository(BaseRepository):
    """Repository for social_follows and related tables"""

    @staticmethod
    def create_follow(follower_id: str, following_id: str,
                     requires_approval: bool = False) -> Optional[Dict[str, Any]]:
        """
        Create a new follow relationship.

        Args:
            follower_id: User ID who follows
            following_id: User ID being followed
            requires_approval: Whether follow needs approval

        Returns:
            Created follow record or None
        """
        query = """
            INSERT INTO social.social_follows
            (follower_id, following_id, status, followed_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING *
        """
        status = 'pending' if requires_approval else 'active'
        return SocialFollowsRepository.fetch_one(query, (follower_id, following_id, status))

    @staticmethod
    def get_follow(follower_id: str, following_id: str) -> Optional[Dict[str, Any]]:
        """Get follow relationship between two users."""
        query = """
            SELECT * FROM social.social_follows
            WHERE follower_id = %s AND following_id = %s
        """
        return SocialFollowsRepository.fetch_one(query, (follower_id, following_id))

    @staticmethod
    def delete_follow(follower_id: str, following_id: str) -> bool:
        """
        Delete a follow relationship.

        Returns:
            True if deleted, False otherwise
        """
        query = """
            DELETE FROM social.social_follows
            WHERE follower_id = %s AND following_id = %s
        """
        result = SocialFollowsRepository.execute(query, (follower_id, following_id))
        return result > 0

    @staticmethod
    def approve_follow(follower_id: str, following_id: str) -> Optional[Dict[str, Any]]:
        """Approve a pending follow request."""
        query = """
            UPDATE social.social_follows
            SET status = 'active', followed_at = CURRENT_TIMESTAMP
            WHERE follower_id = %s AND following_id = %s AND status = 'pending'
            RETURNING *
        """
        return SocialFollowsRepository.fetch_one(query, (follower_id, following_id))

    @staticmethod
    def reject_follow(follower_id: str, following_id: str) -> bool:
        """Reject a pending follow request."""
        query = """
            DELETE FROM social.social_follows
            WHERE follower_id = %s AND following_id = %s AND status = 'pending'
        """
        result = SocialFollowsRepository.execute(query, (follower_id, following_id))
        return result > 0

    @staticmethod
    def get_followers(user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get list of followers for a user."""
        query = """
            SELECT f.*, u.email, u.username, u.profile_picture_url
            FROM social.social_follows f
            JOIN users u ON f.follower_id = u.user_id
            WHERE f.following_id = %s AND f.status = 'active'
            ORDER BY f.followed_at DESC
            LIMIT %s OFFSET %s
        """
        return SocialFollowsRepository.fetch_all(query, (user_id, limit, offset))

    @staticmethod
    def get_following(user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get list of users that a user follows."""
        query = """
            SELECT f.*, u.email, u.username, u.profile_picture_url
            FROM social.social_follows f
            JOIN users u ON f.following_id = u.user_id
            WHERE f.follower_id = %s AND f.status = 'active'
            ORDER BY f.followed_at DESC
            LIMIT %s OFFSET %s
        """
        return SocialFollowsRepository.fetch_all(query, (user_id, limit, offset))

    @staticmethod
    def get_pending_requests(user_id: str) -> List[Dict[str, Any]]:
        """Get pending follow requests for a user."""
        query = """
            SELECT f.*, u.email, u.username, u.profile_picture_url
            FROM social.social_follows f
            JOIN users u ON f.follower_id = u.user_id
            WHERE f.following_id = %s AND f.status = 'pending'
            ORDER BY f.created_at DESC
        """
        return SocialFollowsRepository.fetch_all(query, (user_id,))

    @staticmethod
    def get_user_stats(user_id: str) -> Optional[Dict[str, Any]]:
        """Get social stats for a user."""
        query = """
            SELECT * FROM social.social_user_stats
            WHERE user_id = %s
        """
        return SocialFollowsRepository.fetch_one(query, (user_id,))

    @staticmethod
    def get_follow_suggestions(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get AI-powered follow suggestions."""
        query = """
            SELECT s.*, u.email, u.username, u.profile_picture_url
            FROM social.social_follow_suggestions s
            JOIN users u ON s.suggested_user_id = u.user_id
            WHERE s.user_id = %s
            ORDER BY s.score DESC, s.created_at DESC
            LIMIT %s
        """
        return SocialFollowsRepository.fetch_all(query, (user_id, limit))

    @staticmethod
    def create_suggestion(user_id: str, suggested_user_id: str,
                         reason: str, score: float = 0.5) -> Optional[Dict[str, Any]]:
        """Create a follow suggestion."""
        query = """
            INSERT INTO social.social_follow_suggestions
            (user_id, suggested_user_id, reason, score)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id, suggested_user_id)
            DO UPDATE SET score = EXCLUDED.score, reason = EXCLUDED.reason
            RETURNING *
        """
        return SocialFollowsRepository.fetch_one(
            query, (user_id, suggested_user_id, reason, score)
        )

    @staticmethod
    def dismiss_suggestion(user_id: str, suggested_user_id: str) -> bool:
        """Dismiss a follow suggestion."""
        query = """
            DELETE FROM social.social_follow_suggestions
            WHERE user_id = %s AND suggested_user_id = %s
        """
        result = SocialFollowsRepository.execute(query, (user_id, suggested_user_id))
        return result > 0

    @staticmethod
    def create_block(blocker_id: str, blocked_id: str, reason: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Block a user (auto-removes follows via trigger).

        Args:
            blocker_id: User ID who blocks
            blocked_id: User ID being blocked
            reason: Optional reason for blocking

        Returns:
            Created block record
        """
        query = """
            INSERT INTO social.social_blocks (blocker_id, blocked_id, reason)
            VALUES (%s, %s, %s)
            RETURNING *
        """
        return SocialFollowsRepository.fetch_one(query, (blocker_id, blocked_id, reason))

    @staticmethod
    def remove_block(blocker_id: str, blocked_id: str) -> bool:
        """Unblock a user."""
        query = """
            DELETE FROM social.social_blocks
            WHERE blocker_id = %s AND blocked_id = %s
        """
        result = SocialFollowsRepository.execute(query, (blocker_id, blocked_id))
        return result > 0

    @staticmethod
    def is_blocked(blocker_id: str, blocked_id: str) -> bool:
        """Check if user A has blocked user B."""
        query = """
            SELECT 1 FROM social.social_blocks
            WHERE blocker_id = %s AND blocked_id = %s
        """
        result = SocialFollowsRepository.fetch_one(query, (blocker_id, blocked_id))
        return result is not None

    @staticmethod
    def get_blocks(user_id: str) -> List[Dict[str, Any]]:
        """Get all users blocked by a user."""
        query = """
            SELECT b.*, u.email, u.username
            FROM social.social_blocks b
            JOIN users u ON b.blocked_id = u.user_id
            WHERE b.blocker_id = %s
            ORDER BY b.blocked_at DESC
        """
        return SocialFollowsRepository.fetch_all(query, (user_id,))

    @staticmethod
    def create_mute(muter_id: str, muted_id: str,
                   duration_days: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Mute a user (still follow, but hide content)."""
        query = """
            INSERT INTO social.social_mutes (muter_id, muted_id, duration_days)
            VALUES (%s, %s, %s)
            RETURNING *
        """
        return SocialFollowsRepository.fetch_one(query, (muter_id, muted_id, duration_days))

    @staticmethod
    def remove_mute(muter_id: str, muted_id: str) -> bool:
        """Unmute a user."""
        query = """
            DELETE FROM social.social_mutes
            WHERE muter_id = %s AND muted_id = %s
        """
        result = SocialFollowsRepository.execute(query, (muter_id, muted_id))
        return result > 0

    @staticmethod
    def is_muted(muter_id: str, muted_id: str) -> bool:
        """Check if user A has muted user B (and mute is still active)."""
        query = """
            SELECT 1 FROM social.social_mutes
            WHERE muter_id = %s AND muted_id = %s
            AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
        """
        result = SocialFollowsRepository.fetch_one(query, (muter_id, muted_id))
        return result is not None

    @staticmethod
    def get_mutes(user_id: str) -> List[Dict[str, Any]]:
        """Get all active mutes for a user."""
        query = """
            SELECT m.*, u.email, u.username
            FROM social.social_mutes m
            JOIN users u ON m.muted_id = u.user_id
            WHERE m.muter_id = %s
            AND (m.expires_at IS NULL OR m.expires_at > CURRENT_TIMESTAMP)
            ORDER BY m.muted_at DESC
        """
        return SocialFollowsRepository.fetch_all(query, (user_id,))
