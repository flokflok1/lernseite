"""
GroupDiscussion Entity (DDD Domain Entity)

Represents a discussion thread within a community group.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class GroupDiscussion:
    """
    GroupDiscussion domain entity.

    Discussion threads within community groups.

    Attributes:
        discussion_id: UUID
        group_id: Parent group UUID
        created_by: Creator user UUID
        title: Discussion title
        description: Discussion description
        pinned: Whether discussion is pinned
        locked: Whether discussion is locked
        view_count: Number of views
        reply_count: Number of replies
        last_activity_at: Last activity timestamp
        created_at: Creation timestamp
    """

    discussion_id: str
    group_id: str
    title: str
    created_by: Optional[str] = None
    description: Optional[str] = None
    pinned: bool = False
    locked: bool = False
    view_count: int = 0
    reply_count: int = 0
    last_activity_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate group discussion entity."""
        if not self.discussion_id or not self.discussion_id.strip():
            raise ValueError("Discussion ID cannot be empty")

        if not self.group_id or not self.group_id.strip():
            raise ValueError("Group ID cannot be empty")

        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")

        if self.view_count < 0:
            raise ValueError("View count cannot be negative")

        if self.reply_count < 0:
            raise ValueError("Reply count cannot be negative")

    def is_pinned(self) -> bool:
        """Check if discussion is pinned."""
        return self.pinned

    def is_locked(self) -> bool:
        """Check if discussion is locked."""
        return self.locked

    def is_active(self) -> bool:
        """Check if discussion is active (not locked)."""
        return not self.locked

    def has_replies(self) -> bool:
        """Check if discussion has replies."""
        return self.reply_count > 0

    def pin_discussion(self) -> None:
        """Pin discussion to top."""
        self.pinned = True

    def unpin_discussion(self) -> None:
        """Unpin discussion."""
        self.pinned = False

    def lock_discussion(self) -> None:
        """Lock discussion (no more replies)."""
        if self.locked:
            raise ValueError("Discussion already locked")
        self.locked = True

    def unlock_discussion(self) -> None:
        """Unlock discussion."""
        if not self.locked:
            raise ValueError("Discussion not locked")
        self.locked = False

    def increment_view_count(self) -> None:
        """Increment view count."""
        self.view_count += 1

    def increment_reply_count(self) -> None:
        """Increment reply count and update activity."""
        self.reply_count += 1
        self.last_activity_at = datetime.utcnow()

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity_at = datetime.utcnow()

    def was_created_by(self, user_id: str) -> bool:
        """Check if discussion was created by specific user."""
        return self.created_by == user_id
