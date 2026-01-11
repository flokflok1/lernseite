"""
Lesson Entity (DDD Domain Entity)

Represents a lesson within a chapter.
All lesson data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Lesson:
    """
    Lesson domain entity.

    All lesson attributes loaded dynamically from database.
    NO hardcoded configurations.

    Attributes:
        lesson_id: UUID
        chapter_id: Parent chapter UUID
        title: Lesson title
        slug: URL-friendly slug
        lesson_type: Type of lesson (from DB: text, video, quiz, interactive, assignment, discussion)
        content: JSONB content (structure varies by lesson_type)
        duration_minutes: Estimated duration in minutes
        order_index: Order within chapter (1, 2, 3, ...)
        published: Publication status
        free_preview: Can be previewed without enrollment
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    lesson_id: str
    chapter_id: str
    title: str
    lesson_type: str  # Loaded from DB, not hardcoded
    order_index: int
    slug: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    duration_minutes: Optional[int] = None
    published: bool = False
    free_preview: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate lesson entity."""
        if not self.lesson_id or not self.lesson_id.strip():
            raise ValueError("Lesson ID cannot be empty")
        if not self.chapter_id or not self.chapter_id.strip():
            raise ValueError("Chapter ID is required")
        if not self.title or not self.title.strip():
            raise ValueError("Lesson title cannot be empty")
        if not self.lesson_type or not self.lesson_type.strip():
            raise ValueError("Lesson type is required")
        if self.order_index < 1:
            raise ValueError("Order index must be >= 1")
        if self.duration_minutes is not None and self.duration_minutes < 0:
            raise ValueError("Duration cannot be negative")

    def publish(self) -> None:
        """
        Publish lesson.

        Business rule: Can only publish if not already published.
        """
        if self.published:
            raise ValueError(f"Lesson {self.lesson_id} is already published")

        self.published = True
        self.updated_at = datetime.utcnow()

    def unpublish(self) -> None:
        """Unpublish lesson."""
        self.published = False
        self.updated_at = datetime.utcnow()

    def update_metadata(self, **kwargs) -> None:
        """
        Update lesson metadata.

        Args:
            **kwargs: Fields to update
        """
        allowed_fields = {
            'title', 'slug', 'lesson_type', 'duration_minutes',
            'order_index', 'free_preview'
        }

        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)

        self.updated_at = datetime.utcnow()

    def update_content(self, content: Dict[str, Any]) -> None:
        """
        Update lesson content.

        Args:
            content: New JSONB content
        """
        self.content = content
        self.updated_at = datetime.utcnow()

    def set_free_preview(self, is_free: bool) -> None:
        """
        Set free preview status.

        Args:
            is_free: Whether lesson is free to preview
        """
        self.free_preview = is_free
        self.updated_at = datetime.utcnow()

    def is_accessible_by(
        self,
        user_id: str,
        is_enrolled: bool,
        user_role: str
    ) -> bool:
        """
        Check if user can access this lesson.

        Args:
            user_id: User ID to check
            is_enrolled: Whether user is enrolled in course
            user_role: User role

        Returns:
            True if user can access
        """
        # Admin can access all
        if user_role == 'admin':
            return True

        # Free preview lessons accessible to all
        if self.free_preview:
            return True

        # Enrolled users can access published lessons
        if is_enrolled and self.published:
            return True

        return False

    def get_content_summary(self) -> Dict[str, Any]:
        """
        Get summary of lesson content.

        Returns:
            Summary dict with key information
        """
        summary = {
            'lesson_id': self.lesson_id,
            'title': self.title,
            'lesson_type': self.lesson_type,
            'duration_minutes': self.duration_minutes,
            'published': self.published,
            'free_preview': self.free_preview
        }

        # Add content-specific info
        if self.content:
            if self.lesson_type == 'video':
                summary['video_url'] = self.content.get('video_url')
            elif self.lesson_type == 'quiz':
                summary['question_count'] = len(self.content.get('questions', []))
            elif self.lesson_type == 'text':
                summary['text_length'] = len(self.content.get('text', ''))

        return summary
