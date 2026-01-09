"""
Feedback Note Entity (DDD Domain Entity)

Represents internal team notes for feedback management.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FeedbackNote:
    """
    Feedback Note domain entity.

    Internal team notes for feedback workflow (not shown to users).

    Attributes:
        note_id: UUID
        feedback_id: Parent feedback UUID
        author_id: Admin/team member who wrote note
        note_text: Note content
        is_internal: Whether note is internal (not shown to user)
        created_at: Note creation timestamp
    """

    note_id: str
    feedback_id: str
    author_id: str
    note_text: str
    is_internal: bool = True
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate feedback note entity."""
        if not self.note_id or not self.note_id.strip():
            raise ValueError("Note ID cannot be empty")

        if not self.feedback_id or not self.feedback_id.strip():
            raise ValueError("Feedback ID cannot be empty")

        if not self.author_id or not self.author_id.strip():
            raise ValueError("Author ID cannot be empty")

        if not self.note_text or not self.note_text.strip():
            raise ValueError("Note text cannot be empty")

    def is_visible_to_user(self) -> bool:
        """Check if note is visible to the feedback author."""
        return not self.is_internal

    def get_word_count(self) -> int:
        """Get word count of note."""
        return len(self.note_text.split())
