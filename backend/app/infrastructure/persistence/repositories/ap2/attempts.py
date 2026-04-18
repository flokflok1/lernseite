"""
AP2 Attempt Repository — Append-only versuche.

DDD Layer: Infrastructure. Only psycopg3, parameterized queries.
"""

import json
from typing import Optional
from uuid import UUID

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, insert_returning,
)
from app.domain.models.ap2 import Attempt, AttemptFeedback, Phase


def _feedback_from_json(raw) -> Optional[AttemptFeedback]:
    if not raw:
        return None
    data = raw if isinstance(raw, dict) else json.loads(raw)
    return AttemptFeedback(
        summary=data.get('summary', ''),
        correct_aspects=data.get('correct_aspects', []),
        missing_aspects=data.get('missing_aspects', []),
        partial_aspects=data.get('partial_aspects', []),
        incorrect_aspects=data.get('incorrect_aspects', []),
        suggestions=data.get('suggestions', []),
    )


def _feedback_to_json(fb: Optional[AttemptFeedback]) -> Optional[str]:
    if fb is None:
        return None
    return json.dumps({
        'summary': fb.summary,
        'correct_aspects': fb.correct_aspects,
        'missing_aspects': fb.missing_aspects,
        'partial_aspects': fb.partial_aspects,
        'incorrect_aspects': fb.incorrect_aspects,
        'suggestions': fb.suggestions,
    })


def _row_to_attempt(row: dict) -> Attempt:
    return Attempt(
        attempt_id=row['attempt_id'],
        user_id=row['user_id'],
        item_id=row['item_id'],
        phase=Phase(row['phase']),
        pct=row['pct'],
        points_earned=float(row['points_earned']) if row['points_earned'] is not None else 0.0,
        points_total=float(row['points_total']) if row['points_total'] is not None else 0.0,
        created_at=row['created_at'],
        answer_text=row.get('answer_text'),
        answer_hotspots=row.get('answer_hotspots'),
        feedback=row.get('feedback'),
        feedback_structured=_feedback_from_json(row.get('feedback_structured')),
        ai_model=row.get('ai_model'),
        time_spent_sec=row.get('time_spent_sec'),
        sm2_quality=row.get('sm2_quality'),
    )


class Ap2AttemptRepository:
    """Repository für assessments.ap2_attempts."""

    @classmethod
    def record(
        cls,
        user_id: UUID,
        item_id: UUID,
        phase: Phase,
        pct: int,
        points_earned: float,
        points_total: float,
        answer_text: Optional[str] = None,
        answer_hotspots: Optional[dict] = None,
        feedback: Optional[str] = None,
        feedback_structured: Optional[AttemptFeedback] = None,
        ai_model: Optional[str] = None,
        time_spent_sec: Optional[int] = None,
        sm2_quality: Optional[int] = None,
    ) -> Attempt:
        row = insert_returning('assessments.ap2_attempts', {
            'user_id': str(user_id),
            'item_id': str(item_id),
            'phase': phase.value,
            'pct': pct,
            'points_earned': points_earned,
            'points_total': points_total,
            'answer_text': answer_text,
            'answer_hotspots': json.dumps(answer_hotspots) if answer_hotspots else None,
            'feedback': feedback,
            'feedback_structured': _feedback_to_json(feedback_structured),
            'ai_model': ai_model,
            'time_spent_sec': time_spent_sec,
            'sm2_quality': sm2_quality,
        })
        return _row_to_attempt(row)

    @classmethod
    def find_recent_for_user(cls, user_id: UUID, limit: int = 50) -> list[Attempt]:
        rows = fetch_all(
            """
            SELECT * FROM assessments.ap2_attempts
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (str(user_id), limit),
        )
        return [_row_to_attempt(r) for r in (rows or [])]

    @classmethod
    def find_for_user_item(
        cls,
        user_id: UUID,
        item_id: UUID,
    ) -> list[Attempt]:
        rows = fetch_all(
            """
            SELECT * FROM assessments.ap2_attempts
            WHERE user_id = %s AND item_id = %s
            ORDER BY created_at DESC
            """,
            (str(user_id), str(item_id)),
        )
        return [_row_to_attempt(r) for r in (rows or [])]

    @classmethod
    def count_for_user(cls, user_id: UUID) -> int:
        row = fetch_one(
            "SELECT COUNT(*) AS n FROM assessments.ap2_attempts WHERE user_id = %s",
            (str(user_id),),
        )
        return int(row['n']) if row else 0
