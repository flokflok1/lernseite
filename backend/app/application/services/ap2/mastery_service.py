"""
AP2 MasteryService — TopicMastery-Aggregate nach Attempts updaten.

DDD Layer: Application. Keine SQL, kein Flask.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.models.ap2 import TopicMastery
from app.infrastructure.persistence.repositories.ap2 import (
    Ap2TopicMasteryRepository,
)


class Ap2MasteryService:
    """Koordiniert TopicMastery-Updates."""

    @classmethod
    def apply_attempt(
        cls,
        user_id: UUID,
        topic_id: UUID,
        pct: int,
        points_earned: float,
        points_total: float,
        now: Optional[datetime] = None,
    ) -> TopicMastery:
        """Holt oder erstellt Mastery, wendet Attempt an, persistiert."""
        now = now or datetime.utcnow()

        mastery = Ap2TopicMasteryRepository.get(user_id, topic_id)
        if mastery is None:
            mastery = TopicMastery(user_id=user_id, topic_id=topic_id)

        mastery.apply_attempt(pct, points_earned, points_total, now)

        Ap2TopicMasteryRepository.upsert(mastery)
        return mastery
