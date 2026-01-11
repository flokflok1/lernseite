"""
GroupPost Entity (DDD Domain Entity)

Represents a post within a discussion thread.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class GroupPost:
    """
    GroupPost domain entity.

    Posts within discussion threads.

    Attributes:
        post_id: UUID
        discussion_id: Parent discussion UUID
        user_id: Author user UUID
        content: Post content
        attachments: JSONB attachments
        likes_count: Number of likes
        edited: Whether post was edited
        edited_at: Edit timestamp
        created_at: Creation timestamp
    """

    post_id: str
    discussion_id: str
    content: str
    user_id: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    likes_count: int = 0
    edited: bool = False
    edited_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate group post entity."""
        if not self.post_id or not self.post_id.strip():
            raise ValueError("Post ID cannot be empty")

        if not self.discussion_id or not self.discussion_id.strip():
            raise ValueError("Discussion ID cannot be empty")

        if not self.content or not self.content.strip():
            raise ValueError("Content cannot be empty")

        if self.likes_count < 0:
            raise ValueError("Likes count cannot be negative")

    def has_attachments(self) -> bool:
        """Check if post has attachments."""
        return self.attachments is not None and len(self.attachments) > 0

    def is_edited(self) -> bool:
        """Check if post was edited."""
        return self.edited

    def has_likes(self) -> bool:
        """Check if post has any likes."""
        return self.likes_count > 0

    def edit_post(self, new_content: str) -> None:
        """
        Edit post content.

        Args:
            new_content: New content

        Raises:
            ValueError: If content is empty
        """
        if not new_content or not new_content.strip():
            raise ValueError("Content cannot be empty")

        self.content = new_content
        self.edited = True
        self.edited_at = datetime.utcnow()

    def increment_likes(self) -> None:
        """Increment likes count."""
        self.likes_count += 1

    def decrement_likes(self) -> None:
        """Decrement likes count."""
        if self.likes_count > 0:
            self.likes_count -= 1

    def get_attachment_count(self) -> int:
        """Get number of attachments."""
        return len(self.attachments) if self.attachments else 0

    def was_posted_by(self, user_id: str) -> bool:
        """Check if post was made by specific user."""
        return self.user_id == user_id
