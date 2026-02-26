"""
Plan Wizard Domain Value Objects.

Immutable value objects for the AI Editor plan wizard workflow.
These represent the structured output of plan generation phases:
course metadata and chapter drafts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_DIFFICULTIES: tuple[str, ...] = (
    "beginner",
    "intermediate",
    "advanced",
    "expert",
)

VALID_LANGUAGES: tuple[str, ...] = (
    "de",
    "en",
    "pl",
)

VALID_PLAN_PHASES: tuple[int, ...] = (1, 2, 3, 4)


# ---------------------------------------------------------------------------
# Value Objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CourseMeta:
    """Immutable value object holding high-level course metadata.

    Created during the *meta_draft* phase of the plan wizard and
    confirmed by the editor before chapter generation begins.
    """

    title: str
    description: str
    target_audience: str
    difficulty: str
    language: str

    def __post_init__(self) -> None:
        if not self.title:
            raise ValueError("CourseMeta.title must not be empty")
        if self.difficulty and self.difficulty not in VALID_DIFFICULTIES:
            raise ValueError(
                f"Invalid difficulty '{self.difficulty}'. "
                f"Must be one of {VALID_DIFFICULTIES}"
            )
        if self.language and self.language not in VALID_LANGUAGES:
            raise ValueError(
                f"Invalid language '{self.language}'. "
                f"Must be one of {VALID_LANGUAGES}"
            )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dictionary for API responses and persistence."""
        return {
            "title": self.title,
            "description": self.description,
            "target_audience": self.target_audience,
            "difficulty": self.difficulty,
            "language": self.language,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CourseMeta:
        """Reconstruct from a plain dictionary."""
        return cls(
            title=data["title"],
            description=data.get("description", ""),
            target_audience=data.get("target_audience", ""),
            difficulty=data.get("difficulty", ""),
            language=data.get("language", ""),
        )


@dataclass(frozen=True)
class ChapterDraft:
    """Immutable value object representing a single chapter in a course plan.

    Generated during the *chapters_draft* phase. The ``order`` field
    determines display and execution sequence.
    """

    id: str
    title: str
    description: str
    order: int

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("ChapterDraft.id must not be empty")
        if not self.title:
            raise ValueError("ChapterDraft.title must not be empty")
        if self.order < 0:
            raise ValueError("ChapterDraft.order must be non-negative")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dictionary for API responses and persistence."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "order": self.order,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChapterDraft:
        """Reconstruct from a plain dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            order=data.get("order", 0),
        )
