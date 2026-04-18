"""
AP2 StudySession — Zusammenhängende Lerneinheit.

Aggregiert mehrere Attempts zu einer "Sitzung" (z.B. 3-Phasen-Flow EPK,
Review-Queue heute, 90-Min Prüfungssimulation). Basis für History-Ansicht
und Streak-Berechnung.

DDD Layer: Domain — NO Flask, DB, or Infrastructure imports.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from .enums import SessionType


@dataclass
class StudySession:
    """Eine Lerneinheit mit Start/Ende und Aggregat-Metriken.

    metadata ist flexibel — für topic_study z.B. welche Phasen
    absolviert wurden: {"phases_done": ["blurt", "cued"]}.
    """
    session_id: UUID
    user_id: UUID
    session_type: SessionType
    started_at: datetime
    topic_id: Optional[UUID] = None          # None bei mixed_practice
    ended_at: Optional[datetime] = None
    duration_sec: Optional[int] = None
    items_attempted: int = 0
    items_correct: int = 0
    points_earned: float = 0.0
    points_possible: float = 0.0
    completed: bool = False
    metadata: dict = field(default_factory=dict)

    def mark_ended(self, now: datetime) -> None:
        """Session abschließen."""
        self.ended_at = now
        self.duration_sec = int((now - self.started_at).total_seconds())
        self.completed = True

    def record_attempt(
        self,
        pct: int,
        points_earned: float,
        points_total: float,
    ) -> None:
        """Zählt einen Attempt in die Session-Aggregate."""
        self.items_attempted += 1
        if pct >= 50:
            self.items_correct += 1
        self.points_earned += points_earned
        self.points_possible += points_total

    @property
    def is_active(self) -> bool:
        return self.ended_at is None

    @property
    def accuracy_pct(self) -> float:
        if self.items_attempted == 0:
            return 0.0
        return round(self.items_correct / self.items_attempted * 100, 2)

    @property
    def points_pct(self) -> float:
        if self.points_possible == 0:
            return 0.0
        return round(self.points_earned / self.points_possible * 100, 2)
