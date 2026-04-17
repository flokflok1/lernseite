"""
AP2 Attempt — Ein User-Versuch eines LearningItems.

Attempts sind unveränderliche Records (Event-Sourcing-Pattern): einmal
erstellt, nicht mehr geändert. Aggregate werden in TopicMastery berechnet.

DDD Layer: Domain — NO Flask, DB, or Infrastructure imports.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from .enums import Phase


@dataclass(frozen=True)
class AttemptFeedback:
    """Strukturiertes KI-Prüfer-Feedback.

    Stellt dar *was* richtig / falsch / fehlend war — ermöglicht
    gezielte Wiederholung der Lücken.
    """
    summary: str                          # Kurze Zusammenfassung
    correct_aspects: list[str] = field(default_factory=list)
    missing_aspects: list[str] = field(default_factory=list)
    partial_aspects: list[str] = field(default_factory=list)
    incorrect_aspects: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Attempt:
    """Ein User-Versuch eines Items (unveränderlich).

    time_spent_sec hilft zu erkennen ob User rushed / unsicher ist.
    sm2_quality (0-5) ist die User-Selbsteinschätzung für SM-2-Scheduling.
    """
    attempt_id: UUID
    user_id: UUID
    item_id: UUID
    phase: Phase
    pct: int                              # 0-100
    points_earned: float
    points_total: float
    created_at: datetime
    answer_text: Optional[str] = None
    answer_hotspots: Optional[dict] = None  # { hotspot_id: user_value }
    feedback: Optional[str] = None
    feedback_structured: Optional[AttemptFeedback] = None
    ai_model: Optional[str] = None
    time_spent_sec: Optional[int] = None
    sm2_quality: Optional[int] = None     # 0-5

    @property
    def is_passing(self) -> bool:
        """IHK-Bestehensgrenze: 50%."""
        return self.pct >= 50

    @property
    def is_mastered(self) -> bool:
        """Gilt als 'gut gekonnt'."""
        return self.pct >= 80
