"""
Learning Methods Value Objects (DDD)

Immutable value objects for the Learning Methods domain.

Architecture: 12 Content-Lernmethoden (LM00-LM11) in 3 Gruppen (A-C)
Reference: LernsystemX-Doku/01_Core/02_Lernmethoden.md
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class MethodGroup(Enum):
    """
    Learning Method Groups.

    Value Object: 3 groups as defined in architecture.
    """
    A = "A"  # Erklärend (LM00-LM04)
    B = "B"  # Praxis (LM05-LM08)
    C = "C"  # Prüfung (LM09-LM11)

    @classmethod
    def from_method_type(cls, method_type: int) -> 'MethodGroup':
        """
        Determine group from method_type.

        Args:
            method_type: Method type (0-11)

        Returns:
            MethodGroup enum

        Business Rules:
        - 0-4: Group A
        - 5-8: Group B
        - 9-11: Group C
        """
        if 0 <= method_type <= 4:
            return cls.A
        elif 5 <= method_type <= 8:
            return cls.B
        elif 9 <= method_type <= 11:
            return cls.C
        else:
            raise ValueError(f"Invalid method_type: {method_type}. Must be 0-11.")


class MethodStatus(Enum):
    """
    Learning Method Instance Status.

    Value Object: Instance lifecycle states.
    """
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

    @property
    def is_visible(self) -> bool:
        """Check if instance is visible to students."""
        return self == MethodStatus.PUBLISHED


class KiUsage(Enum):
    """
    KI usage level for learning methods.

    Value Object: Defines AI intensity.
    """
    INTENSIVE = "intensive"  # Heavy AI usage (LM00, LM10, LM11)
    MEDIUM = "medium"        # Moderate AI usage (LM01-LM04, LM09)
    OPTIONAL = "optional"    # Optional AI (LM05-LM08)

    @property
    def display_name(self) -> str:
        """Human-readable display name."""
        names = {
            self.INTENSIVE: "Intensiv",
            self.MEDIUM: "Mittel",
            self.OPTIONAL: "Optional"
        }
        return names[self]


@dataclass(frozen=True)
class LearningMethodType:
    """
    Learning Method Type definition.

    Value Object: Immutable method type data.
    """
    method_type: int
    name: str
    description: str
    group_code: MethodGroup
    ki_usage: KiUsage
    tier: str  # 'basic' or 'premium'
    icon: Optional[str] = None

    def __post_init__(self):
        """Validate method type."""
        if not (0 <= self.method_type <= 11):
            raise ValueError(f"method_type must be 0-11, got {self.method_type}")

        if self.tier not in ['basic', 'premium']:
            raise ValueError(f"tier must be 'basic' or 'premium', got {self.tier}")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'method_type': self.method_type,
            'name': self.name,
            'description': self.description,
            'group_code': self.group_code.value,
            'ki_usage': self.ki_usage.value,
            'tier': self.tier,
            'icon': self.icon
        }


@dataclass(frozen=True)
class InstancePosition:
    """
    Position of a learning method instance within a chapter.

    Value Object: Immutable position data.
    """
    chapter_id: str
    order: int
    total_in_chapter: int

    def __post_init__(self):
        """Validate position."""
        if self.order < 0:
            raise ValueError("order must be >= 0")

        if self.order >= self.total_in_chapter:
            raise ValueError(f"order ({self.order}) must be < total ({self.total_in_chapter})")

    def is_first(self) -> bool:
        """Check if this is the first instance in chapter."""
        return self.order == 0

    def is_last(self) -> bool:
        """Check if this is the last instance in chapter."""
        return self.order == self.total_in_chapter - 1

    def can_move_up(self) -> bool:
        """Check if instance can move up."""
        return not self.is_first()

    def can_move_down(self) -> bool:
        """Check if instance can move down."""
        return not self.is_last()
