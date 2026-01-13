"""
Exam Domain Value Objects.

Immutable value objects for the exam domain following DDD principles.
These represent core business concepts with built-in validation.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


class ExamType(str, Enum):
    """
    Types of exams in the system.

    Values:
        PRACTICE: Practice exam for learning
        SIMULATION: Realistic exam simulation
        OFFICIAL: Official assessment
        MOCK: Mock exam (similar to official)
        CUSTOM: Custom/manual exam
    """
    PRACTICE = 'practice'
    SIMULATION = 'simulation'
    OFFICIAL = 'official'
    MOCK = 'mock'
    CUSTOM = 'custom'

    @classmethod
    def from_string(cls, value: str) -> 'ExamType':
        """Convert string to ExamType."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.PRACTICE


class QuestionType(str, Enum):
    """
    Types of exam questions.

    Values:
        MULTIPLE_CHOICE: Multiple choice with one correct answer
        MULTIPLE_ANSWER: Multiple choice with multiple correct answers
        TRUE_FALSE: True/False question
        SHORT_ANSWER: Short text answer
        ESSAY: Long-form text answer
        CALCULATION: Numerical calculation
        CODE: Programming/code question
        MATCHING: Match items from two lists
    """
    MULTIPLE_CHOICE = 'multiple_choice'
    MULTIPLE_ANSWER = 'multiple_answer'
    TRUE_FALSE = 'true_false'
    SHORT_ANSWER = 'short_answer'
    ESSAY = 'essay'
    CALCULATION = 'calculation'
    CODE = 'code'
    MATCHING = 'matching'

    @classmethod
    def from_string(cls, value: str) -> 'QuestionType':
        """Convert string to QuestionType."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.MULTIPLE_CHOICE


class ExamStatus(str, Enum):
    """
    Status of exam simulation.

    Values:
        PENDING: Waiting for generation
        GENERATING: Currently being generated
        READY: Ready to take
        FAILED: Generation failed
        ARCHIVED: Archived/inactive
    """
    PENDING = 'pending'
    GENERATING = 'generating'
    READY = 'ready'
    FAILED = 'failed'
    ARCHIVED = 'archived'

    @classmethod
    def from_string(cls, value: str) -> 'ExamStatus':
        """Convert string to ExamStatus."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.PENDING

    def can_start_attempt(self) -> bool:
        """Check if exam is ready for an attempt."""
        return self == ExamStatus.READY

    def can_regenerate(self) -> bool:
        """Check if exam can be regenerated."""
        return self in [ExamStatus.PENDING, ExamStatus.FAILED]


class AttemptStatus(str, Enum):
    """
    Status of exam attempt.

    Values:
        IN_PROGRESS: Attempt in progress
        COMPLETED: Attempt completed
        ABANDONED: Attempt abandoned/timed out
        INVALIDATED: Attempt invalidated (e.g., cheating detected)
    """
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    ABANDONED = 'abandoned'
    INVALIDATED = 'invalidated'

    @classmethod
    def from_string(cls, value: str) -> 'AttemptStatus':
        """Convert string to AttemptStatus."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.IN_PROGRESS


class Difficulty(str, Enum):
    """
    Difficulty levels for exams.

    Values:
        EASY: Easy difficulty
        REALISTIC: Realistic difficulty (default)
        HARD: Hard difficulty
    """
    EASY = 'easy'
    REALISTIC = 'realistic'
    HARD = 'hard'

    @classmethod
    def from_string(cls, value: str) -> 'Difficulty':
        """Convert string to Difficulty."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.REALISTIC


class ExamMode(str, Enum):
    """
    Exam generation modes.

    Values:
        SMART: AI-powered smart generation based on analytics
        MANUAL: Manual configuration by user
    """
    SMART = 'smart'
    MANUAL = 'manual'

    @classmethod
    def from_string(cls, value: str) -> 'ExamMode':
        """Convert string to ExamMode."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.SMART


@dataclass(frozen=True)
class ExamConfig:
    """
    Immutable exam configuration value object.

    Attributes:
        mode: Generation mode (smart/manual)
        difficulty: Difficulty level
        time_limit_minutes: Time limit in minutes
        focus_distribution: Topic focus distribution (topic -> percentage)
        extra_instructions: Optional extra instructions for AI
        selected_files: Optional list of file IDs to use
    """
    mode: ExamMode
    difficulty: Difficulty
    time_limit_minutes: int
    focus_distribution: Optional[Dict[str, int]] = None
    extra_instructions: Optional[str] = None
    selected_files: Optional[List[str]] = None

    def __post_init__(self):
        """Validate configuration."""
        if self.time_limit_minutes < 15 or self.time_limit_minutes > 180:
            raise ValueError("Time limit must be between 15 and 180 minutes")

        if self.focus_distribution:
            total = sum(self.focus_distribution.values())
            if total != 100:
                raise ValueError(f"Focus distribution must sum to 100%, got {total}%")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'mode': self.mode.value,
            'difficulty': self.difficulty.value,
            'time_limit_minutes': self.time_limit_minutes,
            'focus_distribution': self.focus_distribution,
            'extra_instructions': self.extra_instructions,
            'selected_files': self.selected_files or []
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExamConfig':
        """Create ExamConfig from dictionary."""
        return cls(
            mode=ExamMode.from_string(data.get('mode', 'smart')),
            difficulty=Difficulty.from_string(data.get('difficulty', 'realistic')),
            time_limit_minutes=data.get('time_limit_minutes', 90),
            focus_distribution=data.get('focus_distribution'),
            extra_instructions=data.get('extra_instructions'),
            selected_files=data.get('selected_files')
        )


@dataclass(frozen=True)
class ExamContext:
    """
    Immutable exam context value object.

    Contains detected context information for exam generation.

    Attributes:
        profession: Detected profession
        exam_level: Exam level (AP1, AP2, etc.)
        region: Geographic region
        ihk_standard: IHK standard string
        weak_topics: Topics user is weak in
        strong_topics: Topics user is strong in
        detected_topics: Detected relevant topics
        confidence: Detection confidence (0-1)
    """
    profession: Optional[str] = None
    exam_level: Optional[str] = None
    region: Optional[str] = None
    ihk_standard: Optional[str] = None
    weak_topics: Optional[List[Dict[str, Any]]] = None
    strong_topics: Optional[List[Dict[str, Any]]] = None
    detected_topics: Optional[List[str]] = None
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'profession': self.profession,
            'exam_level': self.exam_level,
            'region': self.region,
            'ihk_standard': self.ihk_standard,
            'weak_topics': self.weak_topics or [],
            'strong_topics': self.strong_topics or [],
            'detected_topics': self.detected_topics or [],
            'confidence': self.confidence
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExamContext':
        """Create ExamContext from dictionary."""
        return cls(
            profession=data.get('profession'),
            exam_level=data.get('exam_level'),
            region=data.get('region'),
            ihk_standard=data.get('ihk_standard'),
            weak_topics=data.get('weak_topics'),
            strong_topics=data.get('strong_topics'),
            detected_topics=data.get('detected_topics'),
            confidence=data.get('confidence', 0.0)
        )
