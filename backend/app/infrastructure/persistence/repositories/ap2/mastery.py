"""
AP2 TopicMastery Repository — Aggregat pro User+Topic.

DDD Layer: Infrastructure. Only psycopg3, parameterized queries.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query,
)
from app.domain.models.ap2 import TopicMastery


def _row_to_mastery(row: dict) -> TopicMastery:
    return TopicMastery(
        user_id=row['user_id'],
        topic_id=row['topic_id'],
        mastery_score=float(row['mastery_score']),
        attempts_count=row['attempts_count'],
        correct_count=row['correct_count'],
        total_points_earned=float(row['total_points_earned']),
        total_points_possible=float(row['total_points_possible']),
        last_attempt_at=row.get('last_attempt_at'),
        last_review_at=row.get('last_review_at'),
        created_at=row.get('created_at'),
        updated_at=row.get('updated_at'),
    )


class Ap2TopicMasteryRepository:
    """Repository für assessments.ap2_topic_mastery."""

    @classmethod
    def get(cls, user_id: UUID, topic_id: UUID) -> Optional[TopicMastery]:
        row = fetch_one(
            """
            SELECT * FROM assessments.ap2_topic_mastery
            WHERE user_id = %s AND topic_id = %s
            """,
            (str(user_id), str(topic_id)),
        )
        return _row_to_mastery(row) if row else None

    @classmethod
    def upsert(cls, mastery: TopicMastery) -> None:
        execute_query(
            """
            INSERT INTO assessments.ap2_topic_mastery
                (user_id, topic_id, mastery_score, attempts_count,
                 correct_count, total_points_earned, total_points_possible,
                 last_attempt_at, last_review_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id, topic_id) DO UPDATE SET
                mastery_score = EXCLUDED.mastery_score,
                attempts_count = EXCLUDED.attempts_count,
                correct_count = EXCLUDED.correct_count,
                total_points_earned = EXCLUDED.total_points_earned,
                total_points_possible = EXCLUDED.total_points_possible,
                last_attempt_at = EXCLUDED.last_attempt_at,
                last_review_at = EXCLUDED.last_review_at
            """,
            (str(mastery.user_id), str(mastery.topic_id),
             mastery.mastery_score, mastery.attempts_count,
             mastery.correct_count, mastery.total_points_earned,
             mastery.total_points_possible,
             mastery.last_attempt_at, mastery.last_review_at),
        )

    @classmethod
    def find_all_for_user(cls, user_id: UUID) -> list[dict]:
        """Mastery mit Topic-Metadaten gejoint (für Dashboard)."""
        rows = fetch_all(
            """
            SELECT m.*, t.name_de, t.slug, t.bereich, t.priority,
                   t.expected_points
            FROM assessments.ap2_topic_mastery m
            JOIN assessments.ap2_topics t ON t.topic_id = m.topic_id
            WHERE m.user_id = %s
            ORDER BY t.priority, m.mastery_score DESC
            """,
            (str(user_id),),
        )
        return list(rows or [])

    @classmethod
    def find_weaknesses(cls, user_id: UUID, threshold: float = 40.0) -> list[dict]:
        """Themen mit Mastery < threshold (nach >= 3 Versuchen)."""
        rows = fetch_all(
            """
            SELECT m.*, t.name_de, t.slug, t.bereich, t.priority
            FROM assessments.ap2_topic_mastery m
            JOIN assessments.ap2_topics t ON t.topic_id = m.topic_id
            WHERE m.user_id = %s
              AND m.attempts_count >= 3
              AND m.mastery_score < %s
            ORDER BY m.mastery_score
            """,
            (str(user_id), threshold),
        )
        return list(rows or [])

    @classmethod
    def compute_bereich_summary(cls, user_id: UUID) -> dict:
        """Aggregierte Mastery pro Bereich (PB2/PB3/WISO) — für Dashboard-Balken."""
        rows = fetch_all(
            """
            SELECT t.bereich,
                   COUNT(*) AS topic_count,
                   COALESCE(AVG(m.mastery_score), 0) AS avg_mastery,
                   COALESCE(SUM(m.total_points_earned), 0) AS points_earned,
                   COALESCE(SUM(m.total_points_possible), 0) AS points_possible
            FROM assessments.ap2_topics t
            LEFT JOIN assessments.ap2_topic_mastery m
                ON m.topic_id = t.topic_id AND m.user_id = %s
            GROUP BY t.bereich
            """,
            (str(user_id),),
        )
        return {r['bereich']: {
            'topic_count': r['topic_count'],
            'avg_mastery': round(float(r['avg_mastery']), 2),
            'points_earned': float(r['points_earned']),
            'points_possible': float(r['points_possible']),
        } for r in (rows or [])}
