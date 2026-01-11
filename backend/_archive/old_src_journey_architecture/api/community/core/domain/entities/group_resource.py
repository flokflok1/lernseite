"""
GroupResource Entity (DDD Domain Entity)

Represents a shared resource within a community group.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class GroupResource:
    """
    GroupResource domain entity.

    Resources shared within groups (files, links, notes, quizzes, etc.).

    Attributes:
        resource_id: UUID
        group_id: Parent group UUID
        shared_by: User who shared the resource
        title: Resource title
        resource_type: Type (file, link, course_copy, note, quiz, flashcard_set)
        data: JSONB resource data
        description: Resource description
        created_at: Creation timestamp
    """

    resource_id: str
    group_id: str
    title: str
    resource_type: str
    data: Dict[str, Any]
    shared_by: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate group resource entity."""
        if not self.resource_id or not self.resource_id.strip():
            raise ValueError("Resource ID cannot be empty")

        if not self.group_id or not self.group_id.strip():
            raise ValueError("Group ID cannot be empty")

        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")

        valid_types = ('file', 'link', 'course_copy', 'note', 'quiz', 'flashcard_set')
        if self.resource_type not in valid_types:
            raise ValueError(f"Invalid resource type. Must be one of: {valid_types}")

        if not self.data:
            raise ValueError("Resource data cannot be empty")

    def is_file(self) -> bool:
        """Check if resource is a file."""
        return self.resource_type == 'file'

    def is_link(self) -> bool:
        """Check if resource is a link."""
        return self.resource_type == 'link'

    def is_course_copy(self) -> bool:
        """Check if resource is a course copy."""
        return self.resource_type == 'course_copy'

    def is_note(self) -> bool:
        """Check if resource is a note."""
        return self.resource_type == 'note'

    def is_quiz(self) -> bool:
        """Check if resource is a quiz."""
        return self.resource_type == 'quiz'

    def is_flashcard_set(self) -> bool:
        """Check if resource is a flashcard set."""
        return self.resource_type == 'flashcard_set'

    def was_shared_by(self, user_id: str) -> bool:
        """Check if resource was shared by specific user."""
        return self.shared_by == user_id
