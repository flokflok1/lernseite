"""
AP2 AttemptService — zentraler Orchestrator für "submit answer".

Use-Case:
  User submittet Antwort zu Item
   → KI bewertet (EvaluationService)
   → Attempt persistieren (Repository)
   → SM-2 Schedule updaten (SchedulerService)
   → TopicMastery updaten (MasteryService)
   → Session-Aggregate updaten (optional, via SessionService)

DDD Layer: Application. Keine SQL, kein Flask.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.models.ap2 import (
    Attempt, LearningItem, Phase, AttemptFeedback, Anlage,
)
from app.infrastructure.persistence.repositories.ap2 import (
    Ap2LearningItemRepository,
    Ap2AnlageRepository,
    Ap2AttemptRepository,
)

from .evaluation_service import Ap2EvaluationService
from .scheduler_service import Ap2SchedulerService
from .mastery_service import Ap2MasteryService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SubmittedAttempt:
    """Ergebnis eines vollständig verarbeiteten Attempts."""
    attempt: Attempt
    item: LearningItem
    mastery_score: float
    next_review_at: datetime


class Ap2AttemptService:
    """Orchestriert den kompletten 'submit answer'-Flow."""

    @classmethod
    def submit(
        cls,
        user_id: UUID,
        item_id: UUID,
        phase: Phase,
        answer_text: str,
        answer_hotspots: Optional[dict] = None,
        time_spent_sec: Optional[int] = None,
        user_quality_override: Optional[int] = None,
    ) -> SubmittedAttempt:
        """Verarbeitet einen User-Attempt vollständig.

        user_quality_override: wenn gesetzt (0-5), wird statt pct→quality
        dieser Wert für SM-2 verwendet. Erlaubt User-Selbsteinschätzung.
        """
        item = Ap2LearningItemRepository.find_by_id(item_id)
        if item is None:
            raise ValueError(f'LearningItem {item_id} not found')

        anlage: Optional[Anlage] = None
        if item.anlage_id:
            anlage = Ap2AnlageRepository.find_by_id(item.anlage_id)

        # 1. KI-Bewertung
        pct, points_earned, feedback, ai_model = Ap2EvaluationService.evaluate(
            item=item,
            phase=phase,
            answer_text=answer_text,
            anlage=anlage,
            answer_hotspots=answer_hotspots,
        )

        # 2. Attempt persistieren
        now = datetime.utcnow()
        attempt = Ap2AttemptRepository.record(
            user_id=user_id,
            item_id=item_id,
            phase=phase,
            pct=pct,
            points_earned=points_earned,
            points_total=item.points,
            answer_text=answer_text,
            answer_hotspots=answer_hotspots,
            feedback=feedback.summary,
            feedback_structured=feedback,
            ai_model=ai_model,
            time_spent_sec=time_spent_sec,
            sm2_quality=user_quality_override,
        )

        # 3. SM-2 Schedule updaten
        quality = (
            user_quality_override
            if user_quality_override is not None
            else Ap2SchedulerService.quality_from_pct(pct)
        )
        schedule_entry = Ap2SchedulerService.record_review(
            user_id=user_id,
            item_id=item_id,
            quality=quality,
            now=now,
        )

        # 4. TopicMastery updaten
        mastery = Ap2MasteryService.apply_attempt(
            user_id=user_id,
            topic_id=item.topic_id,
            pct=pct,
            points_earned=points_earned,
            points_total=item.points,
            now=now,
        )

        return SubmittedAttempt(
            attempt=attempt,
            item=item,
            mastery_score=mastery.mastery_score,
            next_review_at=schedule_entry.next_review_at,
        )
