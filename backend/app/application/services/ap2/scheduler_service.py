"""
AP2 SchedulerService — SM-2 Spaced Repetition Orchestrierung.

Nach jedem Attempt wird next_review_at neu berechnet. Domain-Logik liegt
in ReviewScheduleEntry.apply_quality() — dieser Service koordiniert nur
den Repository-Roundtrip.

DDD Layer: Application. Keine SQL, kein Flask.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from app.domain.models.ap2 import ReviewScheduleEntry
from app.infrastructure.persistence.repositories.ap2 import (
    Ap2ReviewScheduleRepository,
)

logger = logging.getLogger(__name__)


class Ap2SchedulerService:
    """SM-2 Coordination für User+Item Reviews."""

    @classmethod
    def record_review(
        cls,
        user_id: UUID,
        item_id: UUID,
        quality: int,
        now: Optional[datetime] = None,
    ) -> ReviewScheduleEntry:
        """Aktualisiert SM-2 State nach einem Attempt.

        Quality (0-5) ist das Self-Rating. Bei keinem vorhandenen Entry
        wird ein neuer angelegt (Erstbegegnung).
        """
        now = now or datetime.utcnow()
        existing = Ap2ReviewScheduleRepository.get(user_id, item_id)

        if existing is None:
            existing = ReviewScheduleEntry(
                user_id=user_id,
                item_id=item_id,
                next_review_at=now,
            )

        result = existing.apply_quality(quality, now)

        Ap2ReviewScheduleRepository.upsert(
            user_id=user_id,
            item_id=item_id,
            ease_factor=result.new_ease_factor,
            interval_days=result.new_interval_days,
            repetitions=result.new_repetitions,
            next_review_at=result.next_review_at,
            last_quality=quality,
            last_reviewed_at=now,
        )

        # Return updated entry (Domain-Model reflects new state)
        return ReviewScheduleEntry(
            user_id=user_id,
            item_id=item_id,
            next_review_at=result.next_review_at,
            ease_factor=result.new_ease_factor,
            interval_days=result.new_interval_days,
            repetitions=result.new_repetitions,
            last_quality=quality,
            last_reviewed_at=now,
        )

    @classmethod
    def quality_from_pct(cls, pct: int) -> int:
        """Heuristik: Konvertiert Bewertungsprozent in SM-2 Quality.

        Grobe Abbildung (kann später durch User-Self-Rating überschrieben
        werden):
          >= 90: 5 (perfekt)
          >= 75: 4 (richtig, leicht zögernd)
          >= 60: 3 (richtig, schwierig)
          >= 40: 2 (falsch, erinnerte sich leicht)
          >= 20: 1 (falsch, bei Sichtung erinnert)
          <  20: 0 (komplett vergessen)
        """
        if pct >= 90:
            return 5
        if pct >= 75:
            return 4
        if pct >= 60:
            return 3
        if pct >= 40:
            return 2
        if pct >= 20:
            return 1
        return 0

    @classmethod
    def get_due_queue(cls, user_id: UUID, limit: int = 20) -> list[dict]:
        """Liefert fällige Items mit Item-Metadaten."""
        return Ap2ReviewScheduleRepository.find_due_with_items(user_id, limit)

    @classmethod
    def count_due(cls, user_id: UUID) -> int:
        return Ap2ReviewScheduleRepository.count_due_for_user(user_id)
