"""
AP2 ReviewSchedule Repository — SM-2 State pro User+Item.

UPSERT-heavy: nach jedem Attempt wird der Eintrag aktualisiert.

DDD Layer: Infrastructure. Only psycopg3, parameterized queries.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query,
)
from app.domain.models.ap2 import ReviewScheduleEntry


def _row_to_entry(row: dict) -> ReviewScheduleEntry:
    return ReviewScheduleEntry(
        user_id=row['user_id'],
        item_id=row['item_id'],
        next_review_at=row['next_review_at'],
        ease_factor=float(row['ease_factor']),
        interval_days=row['interval_days'],
        repetitions=row['repetitions'],
        last_quality=row.get('last_quality'),
        last_reviewed_at=row.get('last_reviewed_at'),
        created_at=row.get('created_at'),
        updated_at=row.get('updated_at'),
    )


class Ap2ReviewScheduleRepository:
    """Repository für assessments.ap2_review_schedule."""

    @classmethod
    def get(cls, user_id: UUID, item_id: UUID) -> Optional[ReviewScheduleEntry]:
        row = fetch_one(
            """
            SELECT * FROM assessments.ap2_review_schedule
            WHERE user_id = %s AND item_id = %s
            """,
            (str(user_id), str(item_id)),
        )
        return _row_to_entry(row) if row else None

    @classmethod
    def upsert(
        cls,
        user_id: UUID,
        item_id: UUID,
        ease_factor: float,
        interval_days: int,
        repetitions: int,
        next_review_at: datetime,
        last_quality: int,
        last_reviewed_at: datetime,
    ) -> None:
        execute_query(
            """
            INSERT INTO assessments.ap2_review_schedule
                (user_id, item_id, ease_factor, interval_days,
                 repetitions, next_review_at, last_quality, last_reviewed_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id, item_id) DO UPDATE SET
                ease_factor = EXCLUDED.ease_factor,
                interval_days = EXCLUDED.interval_days,
                repetitions = EXCLUDED.repetitions,
                next_review_at = EXCLUDED.next_review_at,
                last_quality = EXCLUDED.last_quality,
                last_reviewed_at = EXCLUDED.last_reviewed_at
            """,
            (str(user_id), str(item_id), ease_factor, interval_days,
             repetitions, next_review_at, last_quality, last_reviewed_at),
        )

    @classmethod
    def count_due_for_user(cls, user_id: UUID) -> int:
        row = fetch_one(
            """
            SELECT COUNT(*) AS n FROM assessments.ap2_review_schedule
            WHERE user_id = %s AND next_review_at <= NOW()
            """,
            (str(user_id),),
        )
        return int(row['n']) if row else 0

    @classmethod
    def find_due_with_items(cls, user_id: UUID, limit: int = 20) -> list[dict]:
        """Fällige Reviews mit Item-Metadaten gejoint (für Queue-UI).

        Returns dicts with: item_id, topic_id, item_type, prompt, points,
        next_review_at, repetitions.
        """
        rows = fetch_all(
            """
            SELECT rs.item_id, rs.next_review_at, rs.repetitions,
                   rs.ease_factor, rs.interval_days,
                   i.topic_id, i.item_type, i.prompt, i.points,
                   i.difficulty, i.estimated_time_sec,
                   t.name_de AS topic_name, t.bereich AS topic_bereich
            FROM assessments.ap2_review_schedule rs
            JOIN assessments.ap2_learning_items i ON i.item_id = rs.item_id
            JOIN assessments.ap2_topics t ON t.topic_id = i.topic_id
            WHERE rs.user_id = %s
              AND rs.next_review_at <= NOW()
              AND i.is_active = TRUE
            ORDER BY rs.next_review_at
            LIMIT %s
            """,
            (str(user_id), limit),
        )
        return list(rows or [])
