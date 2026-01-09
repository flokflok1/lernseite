"""
Routing Value Objects (DDD)

Immutable domain concepts for LM routing.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class LMIDRange:
    """
    Valid learning method ID range (0-11 for 12 Content-LMs).

    Domain Rule: Only 12 Content-LMs exist (LM00-LM11).
    """
    MIN = 0
    MAX = 11

    @classmethod
    def validate(cls, lm_id: int) -> bool:
        """Validate if LM ID is in valid range."""
        return cls.MIN <= lm_id <= cls.MAX

    @classmethod
    def format_code(cls, lm_id: int) -> str:
        """Format LM ID as code (e.g., 'LM00', 'LM11')."""
        if not cls.validate(lm_id):
            raise ValueError(f"Invalid LM ID: {lm_id}. Must be {cls.MIN}-{cls.MAX}")
        return f'LM{str(lm_id).zfill(2)}'


class CostLevel(Enum):
    """Model cost levels (from cheapest to most expensive)."""
    FREE = "free"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

    @property
    def display_name(self) -> str:
        names = {
            self.FREE: "Kostenlos",
            self.LOW: "Niedrig",
            self.MEDIUM: "Mittel",
            self.HIGH: "Hoch",
            self.VERY_HIGH: "Sehr Hoch"
        }
        return names.get(self, self.value)


class CostPreset(Enum):
    """
    Cost preset configurations for automatic model assignment.

    Domain Rules:
    - CHEAP: Prefer free/low cost models
    - MEDIUM: Balanced cost/quality
    - EXPENSIVE: Premium models (best quality)
    - Chat slot ALWAYS uses best available model
    """
    CHEAP = "cheap"
    MEDIUM = "medium"
    EXPENSIVE = "expensive"

    @property
    def display_name(self) -> str:
        names = {
            self.CHEAP: "Günstig",
            self.MEDIUM: "Mittel",
            self.EXPENSIVE: "Premium"
        }
        return names.get(self, self.value)

    @property
    def cost_priority(self) -> List[str]:
        """
        Get cost level priority for this preset.

        Returns:
            List of cost levels in order of preference
        """
        priorities = {
            self.CHEAP: [
                CostLevel.FREE.value,
                CostLevel.LOW.value,
                CostLevel.MEDIUM.value,
                CostLevel.HIGH.value,
                CostLevel.VERY_HIGH.value
            ],
            self.MEDIUM: [
                CostLevel.MEDIUM.value,
                CostLevel.LOW.value,
                CostLevel.HIGH.value,
                CostLevel.FREE.value,
                CostLevel.VERY_HIGH.value
            ],
            self.EXPENSIVE: [
                CostLevel.VERY_HIGH.value,
                CostLevel.HIGH.value,
                CostLevel.MEDIUM.value,
                CostLevel.LOW.value,
                CostLevel.FREE.value
            ]
        }
        return priorities[self]

    @staticmethod
    def chat_priority() -> List[str]:
        """
        Chat slot always uses best model regardless of preset.

        Domain Rule: Chat is critical for UX, always use premium.
        """
        return [
            CostLevel.VERY_HIGH.value,
            CostLevel.HIGH.value,
            CostLevel.MEDIUM.value,
            CostLevel.LOW.value,
            CostLevel.FREE.value
        ]


class AssignmentScope(Enum):
    """
    Assignment scope levels (hierarchical).

    Resolution order: system → course → chapter
    More specific scopes override less specific.
    """
    SYSTEM = "system"
    COURSE = "course"
    CHAPTER = "chapter"

    @property
    def priority(self) -> int:
        """Higher priority = more specific."""
        priorities = {
            self.SYSTEM: 1,
            self.COURSE: 2,
            self.CHAPTER: 3
        }
        return priorities[self]


@dataclass(frozen=True)
class ModelRequirement:
    """
    Requirements that a model must meet for a learning method.

    Attributes:
        required: Whether a model is required (vs optional)
        recommended_categories: AI model categories (chat, completion, etc.)
        requires_vision: Whether multimodal vision is needed
        requires_functions: Whether function calling is needed
        min_context_window: Minimum context window size
        description: Human-readable description
    """
    required: bool = True
    recommended_categories: List[str] = None
    requires_vision: bool = False
    requires_functions: bool = False
    min_context_window: Optional[int] = None
    description: Optional[str] = None

    def __post_init__(self):
        """Ensure recommended_categories has default."""
        if self.recommended_categories is None:
            object.__setattr__(self, 'recommended_categories', ['chat'])

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            'required': self.required,
            'recommended_categories': self.recommended_categories,
            'requires_vision': self.requires_vision,
            'requires_functions': self.requires_functions,
            'min_context_window': self.min_context_window,
            'description': self.description
        }


@dataclass(frozen=True)
class SlotCode:
    """
    Capability slot code (e.g., 'chat', 'vision', 'code').

    Slots enable multi-model support where different capabilities
    use different AI models.
    """
    code: str
    display_name: str
    required_category: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            'slot_code': self.code,
            'display_name': self.display_name,
            'required_category': self.required_category
        }


@dataclass(frozen=True)
class RoutingStats:
    """
    Routing overview statistics.

    Attributes:
        total: Total number of learning methods
        configured: Methods with assigned models
        unconfigured_required: Methods requiring model but missing one
        unconfigured_optional: Methods where model is optional and missing
    """
    total: int
    configured: int
    unconfigured_required: int
    unconfigured_optional: int

    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage (configured / required)."""
        required = self.configured + self.unconfigured_required
        if required == 0:
            return 100.0
        return (self.configured / required) * 100

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            'total': self.total,
            'configured': self.configured,
            'unconfigured_required': self.unconfigured_required,
            'unconfigured_optional': self.unconfigured_optional,
            'completion_percentage': round(self.completion_percentage, 1)
        }
