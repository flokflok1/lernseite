"""
Port interfaces for social domain repositories.

These ABCs define the contract that infrastructure implementations must fulfill.
Domain code accesses repos through the registry, never by direct import.

Architecture: Domain Layer (ports) -> Infrastructure Layer (adapters/repos)
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


# ---------------------------------------------------------------------------
# SocialPostsPort
# ---------------------------------------------------------------------------

class SocialPostsPort(ABC):
    """Port for social posts persistence."""

    @staticmethod
    @abstractmethod
    def create(data: Dict) -> Dict: ...

    @staticmethod
    @abstractmethod
    def get_by_id(post_id: str) -> Optional[Dict]: ...

    @staticmethod
    @abstractmethod
    def update(post_id: str, data: Dict) -> Optional[Dict]: ...

    @staticmethod
    @abstractmethod
    def soft_delete(post_id: str) -> bool: ...

    @staticmethod
    @abstractmethod
    def get_user_posts(
        user_id: str, viewer_user_id: str, page: int, per_page: int
    ) -> Dict: ...

    @staticmethod
    @abstractmethod
    def pin(post_id: str) -> bool: ...

    @staticmethod
    @abstractmethod
    def unpin_all_for_user(user_id: str) -> None: ...

    @staticmethod
    @abstractmethod
    def add_mention(post_id: str, mentioned_user_id: str) -> None: ...

    @staticmethod
    @abstractmethod
    def add_hashtag(post_id: str, hashtag: str) -> None: ...

    # -- Feed queries --
    @staticmethod
    @abstractmethod
    def get_personalized_feed(
        following_ids: List[str], limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_chronological_feed(
        following_ids: List[str], limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_trending_feed(
        limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_explore_feed(
        excluded_user_ids: List[str], limit: int = 20, offset: int = 0,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_hashtag_feed(
        hashtag: str, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_trending_hashtags(limit: int = 10) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_trending_posts(limit: int = 20) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_explore_posts(
        user_id: str, limit: int = 20
    ) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def search_posts_by_content(
        query_text: str, limit: int = 20
    ) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_post_metrics(post_id: str) -> Dict[str, Any]: ...


# ---------------------------------------------------------------------------
# SocialNotificationsPort
# ---------------------------------------------------------------------------

class SocialNotificationsPort(ABC):
    """Port for notifications persistence."""

    @staticmethod
    @abstractmethod
    def create_notification(
        user_id: str, notification_type: str, content: str,
        reference_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_notifications(
        user_id: str, limit: int = 20
    ) -> List[Dict[str, Any]]: ...


# ---------------------------------------------------------------------------
# SocialLikesPort
# ---------------------------------------------------------------------------

class SocialLikesPort(ABC):
    """Port for likes, reactions, shares, and bookmarks persistence."""

    # -- Likes --
    @staticmethod
    @abstractmethod
    def create_like(user_id: str, post_id: str) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def delete_like(user_id: str, post_id: str) -> bool: ...

    @staticmethod
    @abstractmethod
    def get_like(user_id: str, post_id: str) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_post_likes(
        post_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]: ...

    # -- Reactions --
    @staticmethod
    @abstractmethod
    def create_reaction(
        user_id: str, post_id: str, reaction_type: str
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def delete_reaction(user_id: str, post_id: str) -> bool: ...

    @staticmethod
    @abstractmethod
    def get_reaction(
        user_id: str, post_id: str
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_post_reactions(post_id: str) -> List[Dict[str, Any]]: ...

    # -- Shares --
    @staticmethod
    @abstractmethod
    def create_share(
        user_id: str, post_id: str,
        share_caption: Optional[str] = None,
        share_type: str = 'repost'
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def delete_share(share_id: str, user_id: str) -> bool: ...

    @staticmethod
    @abstractmethod
    def get_post_shares(
        post_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_user_shares(
        user_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]: ...

    # -- Bookmarks --
    @staticmethod
    @abstractmethod
    def create_bookmark(
        user_id: str, post_id: str,
        collection_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def delete_bookmark(user_id: str, post_id: str) -> bool: ...

    @staticmethod
    @abstractmethod
    def get_bookmark(
        user_id: str, post_id: str
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_user_bookmarks(
        user_id: str, collection_id: Optional[str] = None,
        limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def update_bookmark_notes(
        user_id: str, post_id: str, notes: str
    ) -> Optional[Dict[str, Any]]: ...

    # -- Bookmark Collections --
    @staticmethod
    @abstractmethod
    def create_collection(
        user_id: str, name: str,
        description: Optional[str] = None,
        is_private: bool = True
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_user_collections(user_id: str) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def update_collection(
        collection_id: str, user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_private: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def delete_collection(collection_id: str, user_id: str) -> bool: ...


# ---------------------------------------------------------------------------
# SocialCommentsPort
# ---------------------------------------------------------------------------

class SocialCommentsPort(ABC):
    """Port for comments and threaded replies persistence."""

    @staticmethod
    @abstractmethod
    def create_comment(
        user_id: str, post_id: str, content: str,
        parent_comment_id: Optional[str] = None,
        thread_level: int = 0
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_comment(comment_id: str) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def update_comment(
        comment_id: str, user_id: str, content: str
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def soft_delete_comment(comment_id: str, user_id: str) -> bool: ...

    @staticmethod
    @abstractmethod
    def get_post_comments(
        post_id: str, limit: int = 50, offset: int = 0,
        sort: str = 'recent'
    ) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_comment_replies(
        parent_comment_id: str, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_user_comments(
        user_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_comment_count(post_id: str) -> int: ...

    @staticmethod
    @abstractmethod
    def like_comment(
        user_id: str, comment_id: str
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def unlike_comment(user_id: str, comment_id: str) -> bool: ...

    @staticmethod
    @abstractmethod
    def get_comment_like(
        user_id: str, comment_id: str
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_comment_likes(
        comment_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_thread_depth(comment_id: str) -> int: ...

    @staticmethod
    @abstractmethod
    def get_comment_tree(
        post_id: str, max_depth: int = 2
    ) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def pin_comment(
        comment_id: str, post_author_id: str
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def unpin_comment(
        comment_id: str, post_author_id: str
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_pinned_comments(post_id: str) -> List[Dict[str, Any]]: ...


# ---------------------------------------------------------------------------
# SocialFollowsPort
# ---------------------------------------------------------------------------

class SocialFollowsPort(ABC):
    """Port for follows, blocks, mutes, and suggestions persistence."""

    @staticmethod
    @abstractmethod
    def create_follow(
        follower_id: str, following_id: str,
        requires_approval: bool = False
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_follow(
        follower_id: str, following_id: str
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def delete_follow(follower_id: str, following_id: str) -> bool: ...

    @staticmethod
    @abstractmethod
    def approve_follow(
        follower_id: str, following_id: str
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def reject_follow(follower_id: str, following_id: str) -> bool: ...

    @staticmethod
    @abstractmethod
    def get_followers(
        user_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_following(
        user_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_pending_requests(user_id: str) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_user_stats(user_id: str) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def get_follow_suggestions(
        user_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def create_suggestion(
        user_id: str, suggested_user_id: str,
        reason: str, score: float = 0.5
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def dismiss_suggestion(
        user_id: str, suggested_user_id: str
    ) -> bool: ...

    @staticmethod
    @abstractmethod
    def create_block(
        blocker_id: str, blocked_id: str,
        reason: Optional[str] = None
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def remove_block(blocker_id: str, blocked_id: str) -> bool: ...

    @staticmethod
    @abstractmethod
    def is_blocked(blocker_id: str, blocked_id: str) -> bool: ...

    @staticmethod
    @abstractmethod
    def get_blocks(user_id: str) -> List[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def create_mute(
        muter_id: str, muted_id: str,
        duration_days: Optional[int] = None
    ) -> Optional[Dict[str, Any]]: ...

    @staticmethod
    @abstractmethod
    def remove_mute(muter_id: str, muted_id: str) -> bool: ...

    @staticmethod
    @abstractmethod
    def is_muted(muter_id: str, muted_id: str) -> bool: ...

    @staticmethod
    @abstractmethod
    def get_mutes(user_id: str) -> List[Dict[str, Any]]: ...
