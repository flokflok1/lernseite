"""
AP2 LearningItem Repository.

DDD Layer: Infrastructure. Only psycopg3, parameterized queries.
"""

import json
from typing import Optional
from uuid import UUID

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, insert_returning,
)
from app.domain.models.ap2 import LearningItem, GradingCriterion, ItemType


def _criteria_from_json(raw) -> list[GradingCriterion]:
    if not raw:
        return []
    data = raw if isinstance(raw, list) else json.loads(raw)
    return [GradingCriterion(
        criterion=c['criterion'],
        weight=float(c['weight']),
        description=c['description'],
        required=c.get('required', False),
    ) for c in data]


def _criteria_to_json(criteria: list[GradingCriterion]) -> str:
    return json.dumps([{
        'criterion': c.criterion,
        'weight': c.weight,
        'description': c.description,
        'required': c.required,
    } for c in criteria])


def _row_to_item(row: dict) -> LearningItem:
    return LearningItem(
        item_id=row['item_id'],
        topic_id=row['topic_id'],
        item_type=ItemType(row['item_type']),
        prompt=row['prompt'],
        model_answer=row['model_answer'],
        points=float(row['points']),
        source_exam=row.get('source_exam'),
        anlage_id=row.get('anlage_id'),
        expected_answer_structure=row.get('expected_answer_structure'),
        grading_criteria=_criteria_from_json(row.get('grading_criteria')),
        difficulty=row.get('difficulty', 3),
        estimated_time_sec=row.get('estimated_time_sec', 120),
        is_active=row.get('is_active', True),
        calculator_hint=row.get('calculator_hint'),
        created_at=row.get('created_at'),
        updated_at=row.get('updated_at'),
    )


class Ap2LearningItemRepository:
    """Repository für assessments.ap2_learning_items."""

    @classmethod
    def find_by_id(cls, item_id: UUID) -> Optional[LearningItem]:
        row = fetch_one(
            "SELECT * FROM assessments.ap2_learning_items WHERE item_id = %s",
            (str(item_id),),
        )
        return _row_to_item(row) if row else None

    @classmethod
    def find_by_topic(
        cls,
        topic_id: UUID,
        item_type: Optional[ItemType] = None,
    ) -> list[LearningItem]:
        if item_type:
            rows = fetch_all(
                """
                SELECT * FROM assessments.ap2_learning_items
                WHERE topic_id = %s AND item_type = %s AND is_active = TRUE
                ORDER BY difficulty, item_id
                """,
                (str(topic_id), item_type.value),
            )
        else:
            rows = fetch_all(
                """
                SELECT * FROM assessments.ap2_learning_items
                WHERE topic_id = %s AND is_active = TRUE
                ORDER BY item_type, difficulty
                """,
                (str(topic_id),),
            )
        return [_row_to_item(r) for r in (rows or [])]

    @classmethod
    def find_due_for_user(cls, user_id: UUID, limit: int = 20) -> list[LearningItem]:
        """Items die für diesen User fällig sind (SM-2 Review-Queue)."""
        rows = fetch_all(
            """
            SELECT i.* FROM assessments.ap2_learning_items i
            INNER JOIN assessments.ap2_review_schedule rs
                ON rs.item_id = i.item_id
            WHERE rs.user_id = %s
              AND rs.next_review_at <= NOW()
              AND i.is_active = TRUE
            ORDER BY rs.next_review_at
            LIMIT %s
            """,
            (str(user_id), limit),
        )
        return [_row_to_item(r) for r in (rows or [])]

    @classmethod
    def create(cls, item: LearningItem) -> LearningItem:
        row = insert_returning('assessments.ap2_learning_items', {
            'topic_id': str(item.topic_id),
            'item_type': item.item_type.value,
            'prompt': item.prompt,
            'model_answer': item.model_answer,
            'points': item.points,
            'source_exam': item.source_exam,
            'anlage_id': str(item.anlage_id) if item.anlage_id else None,
            'expected_answer_structure': (
                json.dumps(item.expected_answer_structure)
                if item.expected_answer_structure else None
            ),
            'grading_criteria': _criteria_to_json(item.grading_criteria),
            'difficulty': item.difficulty,
            'estimated_time_sec': item.estimated_time_sec,
            'is_active': item.is_active,
        })
        return _row_to_item(row)
