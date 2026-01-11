"""
Exam Systems Domain - Value Objects

Immutable value objects representing Exam Systems domain concepts.

Value Objects:
- ExamType: Type of exam (IHK, Practical, Chapter Completion)
- QuestionType: Type of question (Multiple Choice, Scenario, Calculation, etc.)
- ExamStatus: Status of exam attempt (not_started, in_progress, completed, etc.)
- GradingCriteria: Criteria for grading
- ExamScore: Score result with percentage and pass/fail
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum
from decimal import Decimal
from datetime import datetime


class ExamTypeEnum(str, Enum):
    """Exam type enumeration"""
    IHK = "ihk"
    PRACTICAL = "practical"
    CHAPTER_COMPLETION = "chapter_completion"


class QuestionTypeEnum(str, Enum):
    """Question type enumeration"""
    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_CHOICE = "single_choice"
    SCENARIO = "scenario"
    CALCULATION = "calculation"
    PRACTICAL_STEP = "practical_step"
    FREE_TEXT = "free_text"


class ExamStatusEnum(str, Enum):
    """Exam attempt status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    GRADED = "graded"
    FAILED = "failed"
    PASSED = "passed"
    EXPIRED = "expired"


@dataclass(frozen=True)
class ExamType:
    """
    Exam Type Value Object.

    Represents the type of exam system.
    Immutable.

    Attributes:
        type_code: Type code (ihk, practical, chapter_completion)
        display_name: Human-readable name
        requires_certification: Whether this exam type issues certificates
    """
    type_code: ExamTypeEnum
    display_name: str
    requires_certification: bool = False

    @staticmethod
    def ihk() -> 'ExamType':
        """Create IHK exam type"""
        return ExamType(
            type_code=ExamTypeEnum.IHK,
            display_name="IHK-Prüfung",
            requires_certification=True
        )

    @staticmethod
    def practical() -> 'ExamType':
        """Create Practical exam type"""
        return ExamType(
            type_code=ExamTypeEnum.PRACTICAL,
            display_name="Praxisprüfung",
            requires_certification=False
        )

    @staticmethod
    def chapter_completion() -> 'ExamType':
        """Create Chapter Completion exam type"""
        return ExamType(
            type_code=ExamTypeEnum.CHAPTER_COMPLETION,
            display_name="Kapitelabschluss",
            requires_certification=True
        )


@dataclass(frozen=True)
class QuestionType:
    """
    Question Type Value Object.

    Represents the type of question in an exam.
    Immutable.

    Attributes:
        type_code: Type code (multiple_choice, scenario, etc.)
        display_name: Human-readable name
        allows_partial_credit: Whether partial credit is allowed
    """
    type_code: QuestionTypeEnum
    display_name: str
    allows_partial_credit: bool = False

    @staticmethod
    def multiple_choice() -> 'QuestionType':
        """Multiple choice question (multiple correct answers)"""
        return QuestionType(
            type_code=QuestionTypeEnum.MULTIPLE_CHOICE,
            display_name="Multiple Choice",
            allows_partial_credit=True
        )

    @staticmethod
    def single_choice() -> 'QuestionType':
        """Single choice question (one correct answer)"""
        return QuestionType(
            type_code=QuestionTypeEnum.SINGLE_CHOICE,
            display_name="Single Choice",
            allows_partial_credit=False
        )

    @staticmethod
    def scenario() -> 'QuestionType':
        """Scenario-based question"""
        return QuestionType(
            type_code=QuestionTypeEnum.SCENARIO,
            display_name="Szenario-Frage",
            allows_partial_credit=True
        )

    @staticmethod
    def calculation() -> 'QuestionType':
        """Calculation question"""
        return QuestionType(
            type_code=QuestionTypeEnum.CALCULATION,
            display_name="Rechenaufgabe",
            allows_partial_credit=False
        )


@dataclass(frozen=True)
class GradingCriteria:
    """
    Grading Criteria Value Object.

    Defines how an exam is graded.
    Immutable.

    Attributes:
        passing_percentage: Minimum percentage to pass (0-100)
        allow_partial_credit: Whether partial credit is allowed
        time_bonus: Whether time bonus is applied
        penalty_for_wrong: Whether wrong answers incur penalties
    """
    passing_percentage: Decimal
    allow_partial_credit: bool = True
    time_bonus: bool = False
    penalty_for_wrong: bool = False

    def __post_init__(self):
        """Validate grading criteria"""
        if not 0 <= self.passing_percentage <= 100:
            raise ValueError("passing_percentage must be between 0 and 100")

    @staticmethod
    def ihk_standard() -> 'GradingCriteria':
        """Standard IHK grading (50% to pass, no partial credit)"""
        return GradingCriteria(
            passing_percentage=Decimal("50.0"),
            allow_partial_credit=False,
            time_bonus=False,
            penalty_for_wrong=False
        )

    @staticmethod
    def practical_standard() -> 'GradingCriteria':
        """Standard Practical grading (60% to pass, partial credit allowed)"""
        return GradingCriteria(
            passing_percentage=Decimal("60.0"),
            allow_partial_credit=True,
            time_bonus=False,
            penalty_for_wrong=False
        )

    @staticmethod
    def chapter_completion_standard() -> 'GradingCriteria':
        """Standard Chapter Completion grading (70% to pass)"""
        return GradingCriteria(
            passing_percentage=Decimal("70.0"),
            allow_partial_credit=True,
            time_bonus=False,
            penalty_for_wrong=False
        )


@dataclass(frozen=True)
class ExamScore:
    """
    Exam Score Value Object.

    Represents the result of an exam attempt.
    Immutable.

    Attributes:
        points_earned: Points earned
        points_total: Total possible points
        percentage: Percentage score (0-100)
        passed: Whether the exam was passed
        grading_criteria: The criteria used for grading
    """
    points_earned: Decimal
    points_total: Decimal
    percentage: Decimal
    passed: bool
    grading_criteria: GradingCriteria

    def __post_init__(self):
        """Validate score"""
        if self.points_earned < 0 or self.points_total <= 0:
            raise ValueError("Invalid points values")
        if not 0 <= self.percentage <= 100:
            raise ValueError("Percentage must be between 0 and 100")

    @staticmethod
    def calculate(
        points_earned: Decimal,
        points_total: Decimal,
        grading_criteria: GradingCriteria
    ) -> 'ExamScore':
        """
        Calculate exam score.

        Args:
            points_earned: Points earned
            points_total: Total possible points
            grading_criteria: Grading criteria to use

        Returns:
            ExamScore instance
        """
        if points_total == 0:
            percentage = Decimal("0.0")
        else:
            percentage = round((points_earned / points_total) * Decimal("100"), 2)

        passed = percentage >= grading_criteria.passing_percentage

        return ExamScore(
            points_earned=points_earned,
            points_total=points_total,
            percentage=percentage,
            passed=passed,
            grading_criteria=grading_criteria
        )

    def get_grade_letter(self) -> str:
        """
        Get letter grade based on percentage.

        Returns:
            Letter grade (A, B, C, D, F)
        """
        if self.percentage >= 90:
            return "A"
        elif self.percentage >= 80:
            return "B"
        elif self.percentage >= 70:
            return "C"
        elif self.percentage >= 60:
            return "D"
        else:
            return "F"


@dataclass(frozen=True)
class ExamTimeLimit:
    """
    Exam Time Limit Value Object.

    Represents time constraints for an exam.
    Immutable.

    Attributes:
        time_limit_minutes: Time limit in minutes
        started_at: When the exam was started
        expires_at: When the exam expires
    """
    time_limit_minutes: int
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate time limit"""
        if self.time_limit_minutes <= 0:
            raise ValueError("time_limit_minutes must be positive")

    def is_expired(self, current_time: datetime) -> bool:
        """
        Check if exam has expired.

        Args:
            current_time: Current timestamp

        Returns:
            True if expired, False otherwise
        """
        if not self.expires_at:
            return False
        return current_time > self.expires_at

    def remaining_minutes(self, current_time: datetime) -> int:
        """
        Get remaining minutes.

        Args:
            current_time: Current timestamp

        Returns:
            Remaining minutes (0 if expired)
        """
        if not self.expires_at:
            return self.time_limit_minutes

        if self.is_expired(current_time):
            return 0

        remaining = (self.expires_at - current_time).total_seconds() / 60
        return max(0, int(remaining))
