"""
Chapter Entity (DDD Domain Entity)

Represents a chapter in a course.
All chapter data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Chapter:
    """
    Chapter domain entity.

    All chapter attributes loaded dynamically from database.
    NO hardcoded configurations.

    Attributes:
        chapter_id: UUID
        course_id: Parent course UUID
        title: Chapter title
        slug: URL-friendly slug
        description: Optional description
        order_index: Order within course (1, 2, 3, ...)
        duration_minutes: Estimated duration in minutes
        estimated_duration: Alternative duration estimate
        prerequisite_chapter_id: Optional prerequisite chapter
        published: Publication status
        has_video: Flag if chapter has video content
        has_quiz: Flag if chapter has quiz content
        has_exam: Flag if chapter has exam content
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    chapter_id: str
    course_id: str
    title: str
    order_index: int
    slug: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    estimated_duration: Optional[int] = None
    prerequisite_chapter_id: Optional[str] = None
    published: bool = False
    has_video: bool = False
    has_quiz: bool = False
    has_exam: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate chapter entity."""
        if not self.chapter_id or not self.chapter_id.strip():
            raise ValueError("Chapter ID cannot be empty")
        if not self.course_id or not self.course_id.strip():
            raise ValueError("Course ID is required")
        if not self.title or not self.title.strip():
            raise ValueError("Chapter title cannot be empty")
        if self.order_index < 1:
            raise ValueError("Order index must be >= 1")
        if self.duration_minutes is not None and self.duration_minutes < 0:
            raise ValueError("Duration cannot be negative")

    def publish(self) -> None:
        """
        Publish chapter.

        Business rule: Can only publish if not already published.
        """
        if self.published:
            raise ValueError(f"Chapter {self.chapter_id} is already published")

        self.published = True
        self.updated_at = datetime.utcnow()

    def unpublish(self) -> None:
        """Unpublish chapter."""
        self.published = False
        self.updated_at = datetime.utcnow()

    def update_metadata(self, **kwargs) -> None:
        """
        Update chapter metadata.

        Args:
            **kwargs: Fields to update
        """
        allowed_fields = {
            'title', 'slug', 'description', 'duration_minutes',
            'estimated_duration', 'order_index', 'prerequisite_chapter_id'
        }

        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)

        self.updated_at = datetime.utcnow()

    def update_content_flags(
        self,
        has_video: Optional[bool] = None,
        has_quiz: Optional[bool] = None,
        has_exam: Optional[bool] = None
    ) -> None:
        """
        Update content type flags.

        Args:
            has_video: Has video content
            has_quiz: Has quiz content
            has_exam: Has exam content
        """
        if has_video is not None:
            self.has_video = has_video
        if has_quiz is not None:
            self.has_quiz = has_quiz
        if has_exam is not None:
            self.has_exam = has_exam

        self.updated_at = datetime.utcnow()

    def can_be_accessed(self, completed_chapter_ids: list[str]) -> bool:
        """
        Check if chapter can be accessed based on prerequisites.

        Args:
            completed_chapter_ids: List of completed chapter IDs

        Returns:
            True if prerequisite is met or no prerequisite exists
        """
        # No prerequisite - always accessible
        if not self.prerequisite_chapter_id:
            return True

        # Check if prerequisite is completed
        return self.prerequisite_chapter_id in completed_chapter_ids

    def get_completion_requirements(self) -> dict[str, bool]:
        """
        Get completion requirements for this chapter.

        Returns:
            Dictionary of content types that need completion
        """
        return {
            'video': self.has_video,
            'quiz': self.has_quiz,
            'exam': self.has_exam
        }
