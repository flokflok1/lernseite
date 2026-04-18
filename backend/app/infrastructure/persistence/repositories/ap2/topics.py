"""
AP2 Topic Repository — Read-heavy reference data.

DDD Layer: Infrastructure. Only psycopg3, parameterized queries.
"""

from typing import Optional
from uuid import UUID

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all
from app.domain.models.ap2 import Topic, Bereich, Priority


def _row_to_topic(row: dict) -> Topic:
    """Map DB row → Topic domain model."""
    return Topic(
        topic_id=row['topic_id'],
        slug=row['slug'],
        name_de=row['name_de'],
        name_en=row.get('name_en'),
        bereich=Bereich(row['bereich']),
        priority=Priority(row['priority']),
        expected_points=row['expected_points'],
        exam_count=row['exam_count'],
        description=row.get('description'),
        created_at=row.get('created_at'),
    )


class Ap2TopicRepository:
    """Repository für assessments.ap2_topics."""

    _PRIORITY_ORDER_SQL = """
        CASE priority
            WHEN 'sehr-hoch' THEN 1
            WHEN 'hoch'      THEN 2
            WHEN 'mittel'    THEN 3
            WHEN 'niedrig'   THEN 4
            ELSE 5
        END
    """

    @classmethod
    def find_all(cls) -> list[Topic]:
        rows = fetch_all(
            f"""
            SELECT * FROM assessments.ap2_topics
            ORDER BY {cls._PRIORITY_ORDER_SQL},
                     expected_points DESC NULLS LAST,
                     name_de
            """
        )
        return [_row_to_topic(r) for r in (rows or [])]

    @classmethod
    def find_by_id(cls, topic_id: UUID) -> Optional[Topic]:
        row = fetch_one(
            "SELECT * FROM assessments.ap2_topics WHERE topic_id = %s",
            (str(topic_id),),
        )
        return _row_to_topic(row) if row else None

    @classmethod
    def find_by_slug(cls, slug: str) -> Optional[Topic]:
        row = fetch_one(
            "SELECT * FROM assessments.ap2_topics WHERE slug = %s",
            (slug,),
        )
        return _row_to_topic(row) if row else None

    @classmethod
    def find_by_bereich(cls, bereich: Bereich) -> list[Topic]:
        rows = fetch_all(
            f"""
            SELECT * FROM assessments.ap2_topics
            WHERE bereich = %s OR bereich = 'both'
            ORDER BY {cls._PRIORITY_ORDER_SQL},
                     expected_points DESC NULLS LAST,
                     name_de
            """,
            (bereich.value,),
        )
        return [_row_to_topic(r) for r in (rows or [])]

    @classmethod
    def find_by_priority(cls, priority: Priority) -> list[Topic]:
        rows = fetch_all(
            "SELECT * FROM assessments.ap2_topics WHERE priority = %s ORDER BY name_de",
            (priority.value,),
        )
        return [_row_to_topic(r) for r in (rows or [])]
