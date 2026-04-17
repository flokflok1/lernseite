"""
AP2 SessionService — Lifecycle einer StudySession.

DDD Layer: Application. Keine SQL, kein Flask.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.models.ap2 import StudySession, SessionType
from app.infrastructure.persistence.repositories.ap2 import (
    Ap2StudySessionRepository,
)


class Ap2SessionService:
    """Lifecycle: start → record attempts → end."""

    @classmethod
    def start(
        cls,
        user_id: UUID,
        session_type: SessionType,
        topic_id: Optional[UUID] = None,
        metadata: Optional[dict] = None,
    ) -> StudySession:
        return Ap2StudySessionRepository.start(
            user_id=user_id,
            session_type=session_type,
            topic_id=topic_id,
            metadata=metadata,
        )

    @classmethod
    def record_attempt(
        cls,
        session_id: UUID,
        pct: int,
        points_earned: float,
        points_total: float,
    ) -> None:
        """Inkrementiert Session-Aggregate."""
        session = Ap2StudySessionRepository.find_by_id(session_id)
        if session is None:
            return
        session.record_attempt(pct, points_earned, points_total)
        Ap2StudySessionRepository.update_aggregates(
            session_id=session_id,
            items_attempted=session.items_attempted,
            items_correct=session.items_correct,
            points_earned=session.points_earned,
            points_possible=session.points_possible,
        )

    @classmethod
    def end(cls, session_id: UUID) -> None:
        session = Ap2StudySessionRepository.find_by_id(session_id)
        if session is None:
            return
        now = datetime.utcnow()
        duration_sec = int((now - session.started_at).total_seconds())
        Ap2StudySessionRepository.end(
            session_id=session_id,
            ended_at=now,
            duration_sec=duration_sec,
        )
