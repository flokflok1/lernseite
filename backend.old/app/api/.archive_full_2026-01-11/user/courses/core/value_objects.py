"""
Course Value Objects

Immutable objects representing domain concepts.
Used for type safety and enforcing business rules at the type level.

Usage:
    >>> status = CourseStatus.DRAFT
    >>> visibility = Visibility.PRIVATE
    >>> settings = CourseSettings(certificate_enabled=True)
    >>> price = Price(29.99, "EUR")
"""
from enum import Enum
from typing import Optional
from dataclasses import dataclass
from datetime import datetime


class CourseStatus(str, Enum):
    """
    Course lifecycle status.

    State Transitions:
    - DRAFT → PUBLISHED
    - PUBLISHED → DRAFT (unpublish)
    - PUBLISHED → ARCHIVED
    - ARCHIVED → (terminal state)
    """
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"  # Soft delete


class Visibility(str, Enum):
    """
    Course visibility level.

    Determines who can see the course in the catalog.
    """
    PRIVATE = "private"      # Only creator/admins
    UNLISTED = "unlisted"    # Anyone with link
    PUBLIC = "public"        # Listed in catalog


class EnrollmentType(str, Enum):
    """
    How users can enroll in course.

    Business Rules:
    - OPEN: Self-enrollment available
    - APPROVAL: Admin must approve enrollment request
    - INVITE: Invitation required
    - CLOSED: No enrollment possible
    """
    OPEN = "open"           # Anyone can enroll
    APPROVAL = "approval"   # Requires approval
    INVITE = "invite"       # Invite-only
    CLOSED = "closed"       # No enrollment


class EnrollmentStatus(str, Enum):
    """
    Status of user's enrollment in course.

    State Transitions:
    - ACTIVE → COMPLETED
    - ACTIVE → CANCELLED
    - COMPLETED/CANCELLED → (terminal states)
    """
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


class LessonType(str, Enum):
    """
    Type of lesson content.

    Maps to different lesson renderers in frontend.
    """
    TEXT = "text"                # Text-based lesson
    VIDEO = "video"              # Video lesson
    QUIZ = "quiz"                # Quiz/assessment
    AI = "ai"                    # AI-powered lesson
    WHITEBOARD = "whiteboard"    # Interactive whiteboard
    EXERCISE = "exercise"        # Practice exercise
    PRACTICAL = "practical"      # Practical assignment
    ASSESSMENT = "assessment"    # Formal assessment


@dataclass(frozen=True)
class CourseSettings:
    """
    Course configuration settings (immutable).

    Value Object Properties:
    - Immutable (frozen dataclass)
    - No identity
    - Compared by value
    - Can create modified copies

    Usage:
        >>> settings = CourseSettings(certificate_enabled=True)
        >>> new_settings = settings.with_certificates_enabled()
    """
    requires_enrollment: bool = True
    max_students: Optional[int] = None
    allow_reviews: bool = True
    auto_enroll: bool = False
    certificate_enabled: bool = False

    def with_certificates_enabled(self) -> 'CourseSettings':
        """Return new instance with certificates enabled."""
        return CourseSettings(
            requires_enrollment=self.requires_enrollment,
            max_students=self.max_students,
            allow_reviews=self.allow_reviews,
            auto_enroll=self.auto_enroll,
            certificate_enabled=True  # Changed
        )

    def with_max_students(self, max_students: Optional[int]) -> 'CourseSettings':
        """Return new instance with updated max_students."""
        return CourseSettings(
            requires_enrollment=self.requires_enrollment,
            max_students=max_students,  # Changed
            allow_reviews=self.allow_reviews,
            auto_enroll=self.auto_enroll,
            certificate_enabled=self.certificate_enabled
        )


@dataclass(frozen=True)
class Price:
    """
    Course price (Value Object).

    Immutable monetary value with currency.
    Enforces business rules at construction time.

    Usage:
        >>> price = Price(29.99, "EUR")
        >>> print(price)
        29.99 EUR
        >>> price.to_cents()
        2999
    """
    amount: float
    currency: str = "EUR"

    def __post_init__(self):
        """Validate price constraints."""
        if self.amount < 0:
            raise ValueError("Price cannot be negative")
        if self.currency not in ['EUR', 'USD', 'GBP']:
            raise ValueError(f"Invalid currency: {self.currency}")

    def to_cents(self) -> int:
        """Convert to cents/smallest unit."""
        return int(self.amount * 100)

    def __str__(self) -> str:
        """String representation."""
        return f"{self.amount:.2f} {self.currency}"


@dataclass(frozen=True)
class EnrollmentWindow:
    """
    Time window for course enrollment.

    Business Rules:
    - start_date must be before end_date
    - Both optional (None = no restriction)

    Usage:
        >>> from datetime import datetime
        >>> window = EnrollmentWindow(
        ...     start_date=datetime(2025, 1, 1),
        ...     end_date=datetime(2025, 12, 31)
        ... )
        >>> window.is_active()
        True
    """
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    def __post_init__(self):
        """Validate window constraints."""
        if (self.start_date and self.end_date and
                self.start_date >= self.end_date):
            raise ValueError("Start date must be before end date")

    def is_active(self) -> bool:
        """Check if enrollment window is currently active."""
        from datetime import datetime
        now = datetime.utcnow()

        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True

    def is_upcoming(self) -> bool:
        """Check if enrollment window is in the future."""
        from datetime import datetime
        if not self.start_date:
            return False
        return datetime.utcnow() < self.start_date

    def has_ended(self) -> bool:
        """Check if enrollment window has ended."""
        from datetime import datetime
        if not self.end_date:
            return False
        return datetime.utcnow() > self.end_date


@dataclass(frozen=True)
class ProgressSnapshot:
    """
    Immutable snapshot of user's course progress.

    Value Object representing progress at a point in time.
    Used for analytics and reporting.

    Usage:
        >>> snapshot = ProgressSnapshot(
        ...     user_id="user123",
        ...     course_id="course456",
        ...     progress_percentage=75.5,
        ...     lessons_completed=15,
        ...     total_lessons=20
        ... )
    """
    user_id: str
    course_id: str
    progress_percentage: float
    lessons_completed: int
    total_lessons: int
    chapters_completed: int = 0
    total_chapters: int = 0

    def is_complete(self) -> bool:
        """Check if course is fully completed."""
        return self.progress_percentage >= 100.0

    def completion_ratio(self) -> str:
        """Return human-readable completion ratio."""
        return f"{self.lessons_completed}/{self.total_lessons}"

    def __str__(self) -> str:
        """String representation."""
        return (
            f"Progress: {self.progress_percentage:.1f}% "
            f"({self.lessons_completed}/{self.total_lessons} lessons)"
        )


# Type aliases for common types
CourseId = str
ChapterId = str
LessonId = str
UserId = str
