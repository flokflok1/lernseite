"""
Practice Session Domain Models

Value Objects and Enums for the configurable practice system.
DDD Layer: Domain — NO Flask, DB, or Infrastructure imports.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class PracticeMode(Enum):
    """Learning strategy for mixed-mode practice."""
    DISCOVER = "discover"
    STRENGTHEN = "strengthen"
    EXAM_READY = "exam_ready"


class PracticeOrder(Enum):
    """Question ordering strategy."""
    SEQUENTIAL = "sequential"
    MIXED = "mixed"


class QuestionBucket(Enum):
    """Source bucket for question selection."""
    UNSEEN = "unseen"
    WEAK = "weak"
    REVIEW = "review"
    SPACED_REPEAT = "spaced_repeat"


class DifficultyShift(Enum):
    """Adaptive difficulty adjustment direction."""
    UP = "up"
    DOWN = "down"
    STAY = "stay"


@dataclass(frozen=True)
class SpacedRepetitionEntry:
    """Tracks a question scheduled for spaced repetition."""
    question_id: str
    wrong_count: int
    due_at_position: int


@dataclass(frozen=True)
class StreakAlert:
    """Alert when user gets multiple wrong answers in one topic."""
    topic: str
    consecutive_wrong: int
    suggested_extra_count: int = 5


@dataclass(frozen=True)
class PracticeConfig:
    """User-selected practice session configuration."""
    mode: PracticeMode
    order: PracticeOrder
    question_count: Optional[int] = None  # None = endless
    time_limit_minutes: Optional[int] = None
    exam_filter: list[str] = field(default_factory=list)
    topic_filter: list[str] = field(default_factory=list)
