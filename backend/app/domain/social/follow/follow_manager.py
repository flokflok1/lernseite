"""
Follow Manager Service

Manages follow/unfollow operations, suggestions, blocks, and mutes.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from app.domain.ports.core.registry import repos


class FollowManager:
    """Service for managing follow relationships"""

    @staticmethod
    def follow_user(follower_id: str, following_id: str) -> Dict[str, Any]:
        """
        Follow a user.

        Args:
            follower_id: User ID who follows
            following_id: User ID being followed

        Returns:
            Success status and follow relationship
        """
        # Prevent self-follow
        if follower_id == following_id:
            return {
                'success': False,
                'error': 'Cannot follow yourself'
            }

        # Check if already following
        existing = repos.social_follows.get_follow(follower_id, following_id)
        if existing:
            return {
                'success': False,
                'error': 'Already following this user',
                'data': existing
            }

        # Check if blocked
        if repos.social_follows.is_blocked(following_id, follower_id):
            return {
                'success': False,
                'error': 'Cannot follow this user'
            }

        # Get target user profile
        target_user = repos.users.find_by_id(following_id)
        if not target_user:
            return {
                'success': False,
                'error': 'User not found'
            }

        # Check if account is private (requires approval)
        requires_approval = target_user.get('is_private', False)

        # Create follow
        follow = repos.social_follows.create_follow(
            follower_id, following_id, requires_approval
        )

        if not follow:
            return {
                'success': False,
                'error': 'Failed to create follow'
            }

        return {
            'success': True,
            'data': follow,
            'status': 'pending' if requires_approval else 'active'
        }

    @staticmethod
    def unfollow_user(follower_id: str, following_id: str) -> Dict[str, Any]:
        """
        Unfollow a user.

        Args:
            follower_id: User ID who unfollows
            following_id: User ID being unfollowed

        Returns:
            Success status
        """
        success = repos.social_follows.delete_follow(follower_id, following_id)

        if success:
            return {
                'success': True,
                'message': 'Unfollowed successfully'
            }
        else:
            return {
                'success': False,
                'error': 'Not following this user'
            }

    @staticmethod
    def approve_follow_request(user_id: str, follower_id: str) -> Dict[str, Any]:
        """
        Approve a pending follow request.

        Args:
            user_id: User ID who approves (being followed)
            follower_id: User ID who sent request

        Returns:
            Approved follow relationship
        """
        follow = repos.social_follows.approve_follow(follower_id, user_id)

        if follow:
            return {
                'success': True,
                'data': follow
            }
        else:
            return {
                'success': False,
                'error': 'No pending request found'
            }

    @staticmethod
    def reject_follow_request(user_id: str, follower_id: str) -> Dict[str, Any]:
        """
        Reject a pending follow request.

        Args:
            user_id: User ID who rejects (being followed)
            follower_id: User ID who sent request

        Returns:
            Success status
        """
        success = repos.social_follows.reject_follow(follower_id, user_id)

        if success:
            return {
                'success': True,
                'message': 'Request rejected'
            }
        else:
            return {
                'success': False,
                'error': 'No pending request found'
            }

    @staticmethod
    def get_followers(user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get list of followers."""
        return repos.social_follows.get_followers(user_id, limit, offset)

    @staticmethod
    def get_following(user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get list of users being followed."""
        return repos.social_follows.get_following(user_id, limit, offset)

    @staticmethod
    def get_pending_requests(user_id: str) -> List[Dict[str, Any]]:
        """Get pending follow requests."""
        return repos.social_follows.get_pending_requests(user_id)

    @staticmethod
    def get_follow_stats(user_id: str) -> Dict[str, Any]:
        """
        Get follow statistics for a user.

        Returns:
            Followers count, following count, posts count, engagement rate
        """
        stats = repos.social_follows.get_user_stats(user_id)

        if not stats:
            # User has no stats yet, return defaults
            return {
                'followers_count': 0,
                'following_count': 0,
                'posts_count': 0,
                'engagement_rate': 0.0
            }

        return stats

    # =====================
    # SUGGESTIONS
    # =====================

    @staticmethod
    def get_follow_suggestions(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get AI-powered follow suggestions.

        Suggestions are based on:
        - Mutual follows
        - Similar interests (courses, categories)
        - Geographic proximity
        - Organization membership
        """
        return repos.social_follows.get_follow_suggestions(user_id, limit)

    @staticmethod
    def create_suggestion(user_id: str, suggested_user_id: str,
                         reason: str, score: float = 0.5) -> Optional[Dict[str, Any]]:
        """Create a follow suggestion (for AI system)."""
        return repos.social_follows.create_suggestion(
            user_id, suggested_user_id, reason, score
        )

    @staticmethod
    def dismiss_suggestion(user_id: str, suggested_user_id: str) -> bool:
        """Dismiss a follow suggestion."""
        return repos.social_follows.dismiss_suggestion(user_id, suggested_user_id)

    # =====================
    # BLOCK & MUTE
    # =====================

    @staticmethod
    def block_user(blocker_id: str, blocked_id: str,
                  reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Block a user.

        Automatically removes follow relationships via DB trigger.

        Args:
            blocker_id: User ID who blocks
            blocked_id: User ID being blocked
            reason: Optional reason

        Returns:
            Success status and block record
        """
        if blocker_id == blocked_id:
            return {
                'success': False,
                'error': 'Cannot block yourself'
            }

        block = repos.social_follows.create_block(blocker_id, blocked_id, reason)

        if block:
            return {
                'success': True,
                'data': block,
                'message': 'User blocked successfully'
            }
        else:
            return {
                'success': False,
                'error': 'Failed to block user (may already be blocked)'
            }

    @staticmethod
    def unblock_user(blocker_id: str, blocked_id: str) -> Dict[str, Any]:
        """Unblock a user."""
        success = repos.social_follows.remove_block(blocker_id, blocked_id)

        if success:
            return {
                'success': True,
                'message': 'User unblocked successfully'
            }
        else:
            return {
                'success': False,
                'error': 'User is not blocked'
            }

    @staticmethod
    def get_blocks(user_id: str) -> List[Dict[str, Any]]:
        """Get all blocked users."""
        return repos.social_follows.get_blocks(user_id)

    @staticmethod
    def mute_user(muter_id: str, muted_id: str,
                 duration_days: Optional[int] = None) -> Dict[str, Any]:
        """
        Mute a user (hide content without unfollowing).

        Args:
            muter_id: User ID who mutes
            muted_id: User ID being muted
            duration_days: Optional duration (None = permanent)

        Returns:
            Success status and mute record
        """
        if muter_id == muted_id:
            return {
                'success': False,
                'error': 'Cannot mute yourself'
            }

        mute = repos.social_follows.create_mute(muter_id, muted_id, duration_days)

        if mute:
            return {
                'success': True,
                'data': mute,
                'message': f'User muted for {duration_days} days' if duration_days else 'User muted permanently'
            }
        else:
            return {
                'success': False,
                'error': 'Failed to mute user (may already be muted)'
            }

    @staticmethod
    def unmute_user(muter_id: str, muted_id: str) -> Dict[str, Any]:
        """Unmute a user."""
        success = repos.social_follows.remove_mute(muter_id, muted_id)

        if success:
            return {
                'success': True,
                'message': 'User unmuted successfully'
            }
        else:
            return {
                'success': False,
                'error': 'User is not muted'
            }

    @staticmethod
    def get_mutes(user_id: str) -> List[Dict[str, Any]]:
        """Get all active mutes."""
        return repos.social_follows.get_mutes(user_id)

    @staticmethod
    def is_following(follower_id: str, following_id: str) -> bool:
        """Check if user A follows user B (active status)."""
        follow = repos.social_follows.get_follow(follower_id, following_id)
        return follow is not None and follow.get('status') == 'active'

    @staticmethod
    def is_blocked(blocker_id: str, blocked_id: str) -> bool:
        """Check if user A has blocked user B."""
        return repos.social_follows.is_blocked(blocker_id, blocked_id)

    @staticmethod
    def is_muted(muter_id: str, muted_id: str) -> bool:
        """Check if user A has muted user B (and mute is still active)."""
        return repos.social_follows.is_muted(muter_id, muted_id)
