"""
GroupMessage Entity (DDD Domain Entity)

Represents a message within a community group.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class GroupMessage:
    """
    GroupMessage domain entity.

    Messages and discussions within groups (with threading support).

    Attributes:
        message_id: UUID
        group_id: Parent group UUID
        user_id: Author user UUID
        parent_message_id: Parent message UUID for threads
        message_text: Message content
        attachments: JSONB attachments
        edited: Whether message was edited
        edited_at: Edit timestamp
        deleted: Soft delete flag
        deleted_at: Delete timestamp
        created_at: Creation timestamp
    """

    message_id: str
    group_id: str
    message_text: str
    user_id: Optional[str] = None
    parent_message_id: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    edited: bool = False
    edited_at: Optional[datetime] = None
    deleted: bool = False
    deleted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate group message entity."""
        if not self.message_id or not self.message_id.strip():
            raise ValueError("Message ID cannot be empty")

        if not self.group_id or not self.group_id.strip():
            raise ValueError("Group ID cannot be empty")

        if not self.message_text or not self.message_text.strip():
            raise ValueError("Message text cannot be empty")

    def is_reply(self) -> bool:
        """Check if message is a reply to another message."""
        return self.parent_message_id is not None

    def is_top_level(self) -> bool:
        """Check if message is a top-level message (not a reply)."""
        return self.parent_message_id is None

    def has_attachments(self) -> bool:
        """Check if message has attachments."""
        return self.attachments is not None and len(self.attachments) > 0

    def is_edited(self) -> bool:
        """Check if message was edited."""
        return self.edited

    def is_deleted(self) -> bool:
        """Check if message was deleted."""
        return self.deleted

    def is_visible(self) -> bool:
        """Check if message is visible (not deleted)."""
        return not self.deleted

    def edit_message(self, new_text: str) -> None:
        """
        Edit message content.

        Args:
            new_text: New message text

        Raises:
            ValueError: If message is deleted or text is empty
        """
        if self.deleted:
            raise ValueError("Cannot edit deleted message")

        if not new_text or not new_text.strip():
            raise ValueError("Message text cannot be empty")

        self.message_text = new_text
        self.edited = True
        self.edited_at = datetime.utcnow()

    def soft_delete(self) -> None:
        """
        Soft delete message.

        Raises:
            ValueError: If message already deleted
        """
        if self.deleted:
            raise ValueError("Message already deleted")

        self.deleted = True
        self.deleted_at = datetime.utcnow()

    def get_attachment_count(self) -> int:
        """Get number of attachments."""
        return len(self.attachments) if self.attachments else 0
