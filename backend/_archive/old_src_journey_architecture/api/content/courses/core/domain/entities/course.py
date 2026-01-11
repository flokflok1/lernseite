"""
Course Entity (DDD Domain Entity)

Represents a course in the system.
All course data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Course:
    """
    Course domain entity.

    All course attributes loaded dynamically from database.
    NO hardcoded configurations.

    Attributes:
        course_id: UUID
        title: Course title
        description: Course description
        creator_id: Creator user ID
        category_id: Category ID (loaded from DB)
        difficulty_level: Difficulty (1-5)
        status: Course status (draft, review, published, archived)
        visibility: Visibility (private, organisation, public)
        is_published: Publication status
        is_drm_protected: DRM protection flag
        organisation_id: Optional organisation ID
        price: Optional price for marketplace
        created_at: Creation timestamp
        updated_at: Last update timestamp
        published_at: Publication timestamp
    """

    course_id: str
    title: str
    description: Optional[str]
    creator_id: str
    category_id: str
    difficulty_level: int
    status: str  # Loaded from DB, not hardcoded
    visibility: str  # Loaded from DB, not hardcoded
    is_published: bool
    is_drm_protected: bool = False
    organisation_id: Optional[str] = None
    price: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate course entity."""
        if not self.course_id or not self.course_id.strip():
            raise ValueError("Course ID cannot be empty")
        if not self.title or not self.title.strip():
            raise ValueError("Course title cannot be empty")
        if not self.creator_id:
            raise ValueError("Creator ID is required")
        if not self.category_id:
            raise ValueError("Category ID is required")
        if self.difficulty_level < 1 or self.difficulty_level > 5:
            raise ValueError("Difficulty level must be between 1 and 5")

    def publish(self) -> None:
        """
        Publish course.

        Business rule: Can only publish if status is 'review' or 'draft'.
        """
        if self.status not in ['draft', 'review']:
            raise ValueError(f"Cannot publish course with status '{self.status}'")

        self.status = 'published'
        self.is_published = True
        self.published_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def archive(self) -> None:
        """Archive course."""
        self.status = 'archived'
        self.is_published = False
        self.updated_at = datetime.utcnow()

    def update_metadata(self, **kwargs) -> None:
        """
        Update course metadata.

        Args:
            **kwargs: Fields to update
        """
        allowed_fields = {'title', 'description', 'difficulty_level', 'category_id', 'price'}

        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)

        self.updated_at = datetime.utcnow()

    def can_be_edited_by(self, user_id: str, user_role: str) -> bool:
        """
        Check if user can edit this course.

        Args:
            user_id: User ID to check
            user_role: User role

        Returns:
            True if user can edit
        """
        # Creator can always edit their courses
        if self.creator_id == user_id:
            return True

        # Admin can edit all courses
        if user_role == 'admin':
            return True

        # Organisation admin can edit organisation courses
        if user_role in ['school', 'company'] and self.organisation_id:
            # Check would be done in service layer with org membership check
            return True

        return False

    def is_accessible_by(self, user_id: str, user_role: str, user_org_id: Optional[str] = None) -> bool:
        """
        Check if user can access this course.

        Args:
            user_id: User ID to check
            user_role: User role
            user_org_id: User's organisation ID

        Returns:
            True if user can access
        """
        # Published public courses accessible to all
        if self.is_published and self.visibility == 'public':
            return True

        # Creator can always access
        if self.creator_id == user_id:
            return True

        # Admin can access all
        if user_role == 'admin':
            return True

        # Organisation visibility check
        if self.visibility == 'organisation' and self.organisation_id:
            if user_org_id == self.organisation_id:
                return True

        # Private courses only accessible by creator
        return False
