"""
AP2 ReviewScheduleEntry — SM-2 Spaced Repetition State.

SM-2 Algorithmus (Piotr Woźniak, 1987): ease_factor + interval_days
steuern wann ein Item erneut wiederholt wird. Quality 0-5 ist die
Selbsteinschätzung des Users nach einem Versuch.

DDD Layer: Domain — NO Flask, DB, or Infrastructure imports.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID


# SM-2 Konstanten
EASE_FACTOR_MIN = 1.3
EASE_FACTOR_DEFAULT = 2.5
INITIAL_INTERVAL_DAYS = 1
SECOND_INTERVAL_DAYS = 6


@dataclass(frozen=True)
class SM2Result:
    """Das Ergebnis einer SM-2 Berechnung (neuer Scheduler-State)."""
    new_ease_factor: float
    new_interval_days: int
    new_repetitions: int
    next_review_at: datetime


@dataclass
class ReviewScheduleEntry:
    """Persistenter SM-2 State pro User+Item.

    Nach jedem Attempt wird dieser Eintrag aktualisiert — neuer
    Next-Review basierend auf der Quality-Bewertung.
    """
    user_id: UUID
    item_id: UUID
    next_review_at: datetime
    ease_factor: float = EASE_FACTOR_DEFAULT
    interval_days: int = INITIAL_INTERVAL_DAYS
    repetitions: int = 0
    last_quality: Optional[int] = None     # 0-5
    last_reviewed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def apply_quality(self, quality: int, now: datetime) -> SM2Result:
        """Berechnet neuen SM-2 State gegeben eine Quality-Bewertung.

        Quality-Semantik (SM-2 Original):
        - 0: Komplett vergessen
        - 1: Falsch, aber erinnerte sich beim Sehen
        - 2: Falsch, erinnerte sich leicht
        - 3: Richtig, aber schwierig
        - 4: Richtig, etwas zögernd
        - 5: Perfekt erinnert
        """
        if not (0 <= quality <= 5):
            raise ValueError(f'quality must be 0..5, got {quality}')

        if quality < 3:
            new_reps = 0
            new_interval = INITIAL_INTERVAL_DAYS
        else:
            new_reps = self.repetitions + 1
            if new_reps == 1:
                new_interval = INITIAL_INTERVAL_DAYS
            elif new_reps == 2:
                new_interval = SECOND_INTERVAL_DAYS
            else:
                new_interval = round(self.interval_days * self.ease_factor)

        delta = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        new_ef = max(EASE_FACTOR_MIN, self.ease_factor + delta)

        return SM2Result(
            new_ease_factor=round(new_ef, 2),
            new_interval_days=new_interval,
            new_repetitions=new_reps,
            next_review_at=now + timedelta(days=new_interval),
        )
