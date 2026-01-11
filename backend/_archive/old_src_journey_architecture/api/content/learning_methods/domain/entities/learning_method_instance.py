"""
Learning Method Instance Entity (DDD Domain Entity)

Represents a specific instance of a learning method within a chapter.
All data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class LearningMethodInstance:
    """
    Learning Method Instance domain entity.

    Represents a concrete instance of one of the 12 Content-Lernmethoden.
    All attributes loaded dynamically from database.

    Attributes:
        method_id: UUID
        chapter_id: Parent chapter UUID
        method_type: Type ID (0-11 for 12 Content-LMs)
        title: Instance title
        instructions: Instructions text
        data: JSONB data (structure varies by method_type)
        solution: JSONB solution data
        tier: Access tier (basic, premium from DB)
        duration_minutes: Estimated duration
        difficulty: Difficulty level (from DB)
        order_index: Order within chapter
        published: Publication status
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    method_id: str
    chapter_id: str
    method_type: int  # 0-11 (12 Content-LMs)
    title: str
    data: Dict[str, Any]
    tier: str  # Loaded from DB (basic, premium)
    instructions: Optional[str] = None
    solution: Optional[Dict[str, Any]] = None
    duration_minutes: Optional[int] = None
    difficulty: Optional[str] = None  # Loaded from DB
    order_index: int = 0
    published: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate learning method instance entity."""
        if not self.method_id or not self.method_id.strip():
            raise ValueError("Method ID cannot be empty")
        if not self.chapter_id or not self.chapter_id.strip():
            raise ValueError("Chapter ID is required")
        if self.method_type < 0 or self.method_type > 11:
            raise ValueError("Method type must be between 0 and 11 (12 Content-LMs)")
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not self.data:
            raise ValueError("Data is required")
        if self.duration_minutes is not None and self.duration_minutes < 0:
            raise ValueError("Duration cannot be negative")

    def publish(self) -> None:
        """
        Publish learning method instance.

        Business rule: Can only publish if not already published.
        """
        if self.published:
            raise ValueError(f"Learning method {self.method_id} is already published")

        self.published = True
        self.updated_at = datetime.utcnow()

    def unpublish(self) -> None:
        """Unpublish learning method instance."""
        self.published = False
        self.updated_at = datetime.utcnow()

    def update_metadata(self, **kwargs) -> None:
        """
        Update instance metadata.

        Args:
            **kwargs: Fields to update
        """
        allowed_fields = {
            'title', 'instructions', 'duration_minutes',
            'difficulty', 'order_index'
        }

        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)

        self.updated_at = datetime.utcnow()

    def update_data(self, data: Dict[str, Any]) -> None:
        """
        Update instance data.

        Args:
            data: New JSONB data
        """
        self.data = data
        self.updated_at = datetime.utcnow()

    def update_solution(self, solution: Dict[str, Any]) -> None:
        """
        Update instance solution.

        Args:
            solution: New JSONB solution
        """
        self.solution = solution
        self.updated_at = datetime.utcnow()

    def is_premium(self) -> bool:
        """Check if this instance requires premium access."""
        return self.tier == 'premium'

    def is_accessible_by(
        self,
        user_id: str,
        is_enrolled: bool,
        user_role: str,
        has_premium: bool
    ) -> bool:
        """
        Check if user can access this learning method instance.

        Args:
            user_id: User ID to check
            is_enrolled: Whether user is enrolled in course
            user_role: User role
            has_premium: Whether user has premium access

        Returns:
            True if user can access
        """
        # Admin can always access
        if user_role == 'admin':
            return True

        # Must be published
        if not self.published:
            return False

        # Must be enrolled
        if not is_enrolled:
            return False

        # Check premium requirement
        if self.is_premium() and not has_premium:
            return False

        return True

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of learning method instance.

        Returns:
            Summary dict with key information
        """
        return {
            'method_id': self.method_id,
            'method_type': self.method_type,
            'title': self.title,
            'tier': self.tier,
            'difficulty': self.difficulty,
            'duration_minutes': self.duration_minutes,
            'published': self.published,
            'order_index': self.order_index
        }
