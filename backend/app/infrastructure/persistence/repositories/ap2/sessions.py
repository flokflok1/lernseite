"""
AP2 StudySession Repository.

DDD Layer: Infrastructure. Only psycopg3, parameterized queries.
"""

import json
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, insert_returning, update_returning,
)
from app.domain.models.ap2 import StudySession, SessionType


def _row_to_session(row: dict) -> StudySession:
    metadata = row.get('metadata') or {}
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    return StudySession(
        session_id=row['session_id'],
        user_id=row['user_id'],
        session_type=SessionType(row['session_type']),
        started_at=row['started_at'],
        topic_id=row.get('topic_id'),
        ended_at=row.get('ended_at'),
        duration_sec=row.get('duration_sec'),
        items_attempted=row.get('items_attempted', 0),
        items_correct=row.get('items_correct', 0),
        points_earned=float(row.get('points_earned', 0)),
        points_possible=float(row.get('points_possible', 0)),
        completed=row.get('completed', False),
        metadata=metadata,
    )


class Ap2StudySessionRepository:
    """Repository für assessments.ap2_study_sessions."""

    @classmethod
    def start(
        cls,
        user_id: UUID,
        session_type: SessionType,
        topic_id: Optional[UUID] = None,
        metadata: Optional[dict] = None,
    ) -> StudySession:
        row = insert_returning('assessments.ap2_study_sessions', {
            'user_id': str(user_id),
            'session_type': session_type.value,
            'topic_id': str(topic_id) if topic_id else None,
            'started_at': datetime.utcnow(),
            'metadata': json.dumps(metadata) if metadata else None,
        })
        return _row_to_session(row)

    @classmethod
    def update_aggregates(
        cls,
        session_id: UUID,
        items_attempted: int,
        items_correct: int,
        points_earned: float,
        points_possible: float,
    ) -> None:
        update_returning(
            'assessments.ap2_study_sessions',
            {
                'items_attempted': items_attempted,
                'items_correct': items_correct,
                'points_earned': points_earned,
                'points_possible': points_possible,
            },
            'session_id = %s',
            (str(session_id),),
        )

    @classmethod
    def end(cls, session_id: UUID, ended_at: datetime, duration_sec: int) -> None:
        update_returning(
            'assessments.ap2_study_sessions',
            {
                'ended_at': ended_at,
                'duration_sec': duration_sec,
                'completed': True,
            },
            'session_id = %s',
            (str(session_id),),
        )

    @classmethod
    def find_by_id(cls, session_id: UUID) -> Optional[StudySession]:
        row = fetch_one(
            "SELECT * FROM assessments.ap2_study_sessions WHERE session_id = %s",
            (str(session_id),),
        )
        return _row_to_session(row) if row else None

    @classmethod
    def find_recent_for_user(cls, user_id: UUID, limit: int = 20) -> list[StudySession]:
        rows = fetch_all(
            """
            SELECT * FROM assessments.ap2_study_sessions
            WHERE user_id = %s
            ORDER BY started_at DESC
            LIMIT %s
            """,
            (str(user_id), limit),
        )
        return [_row_to_session(r) for r in (rows or [])]
