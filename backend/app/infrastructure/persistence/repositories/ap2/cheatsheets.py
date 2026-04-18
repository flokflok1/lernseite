"""
AP2 Cheatsheet Repository — User-Markdown pro Topic.

DDD Layer: Infrastructure. Only psycopg3, parameterized queries.
"""

from typing import Optional
from uuid import UUID

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query,
)
from app.domain.models.ap2 import Cheatsheet


def _row_to_cheatsheet(row: dict) -> Cheatsheet:
    return Cheatsheet(
        user_id=row['user_id'],
        topic_id=row['topic_id'],
        markdown_content=row['markdown_content'],
        word_count=row['word_count'],
        created_at=row.get('created_at'),
        updated_at=row.get('updated_at'),
    )


class Ap2CheatsheetRepository:
    """Repository für assessments.ap2_cheatsheets."""

    @classmethod
    def get(cls, user_id: UUID, topic_id: UUID) -> Optional[Cheatsheet]:
        row = fetch_one(
            """
            SELECT * FROM assessments.ap2_cheatsheets
            WHERE user_id = %s AND topic_id = %s
            """,
            (str(user_id), str(topic_id)),
        )
        return _row_to_cheatsheet(row) if row else None

    @classmethod
    def upsert(cls, user_id: UUID, topic_id: UUID, markdown: str) -> Cheatsheet:
        word_count = len(markdown.split())
        execute_query(
            """
            INSERT INTO assessments.ap2_cheatsheets
                (user_id, topic_id, markdown_content, word_count)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id, topic_id) DO UPDATE SET
                markdown_content = EXCLUDED.markdown_content,
                word_count = EXCLUDED.word_count
            """,
            (str(user_id), str(topic_id), markdown, word_count),
        )
        return Cheatsheet(
            user_id=user_id,
            topic_id=topic_id,
            markdown_content=markdown,
            word_count=word_count,
        )

    @classmethod
    def find_all_for_user(cls, user_id: UUID) -> list[dict]:
        """Alle Cheatsheets des Users mit Topic-Namen (für Übersicht)."""
        rows = fetch_all(
            """
            SELECT c.*, t.name_de, t.slug, t.bereich
            FROM assessments.ap2_cheatsheets c
            JOIN assessments.ap2_topics t ON t.topic_id = c.topic_id
            WHERE c.user_id = %s
            ORDER BY c.updated_at DESC
            """,
            (str(user_id),),
        )
        return list(rows or [])
