"""
TopicTaxonomy Repository

CRUD for exam topic catalogs per exam type.
Supports hierarchical topics (parent_topic_id).
All queries use parameterized SQL (%s) via psycopg3.
"""

import json
from typing import Optional, List, Dict, Any

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query,
)


class TopicTaxonomyRepository:
    """Repository for assessments.exam_topic_taxonomy table."""

    @staticmethod
    def find_by_exam_type(exam_type: str) -> List[Dict[str, Any]]:
        """List all topics for an exam type, ordered by weight desc."""
        query = """
            SELECT topic_id, exam_type, topic_key, topic_label,
                   parent_topic_id, weight, created_at
            FROM assessments.exam_topic_taxonomy
            WHERE exam_type = %s
            ORDER BY weight DESC, topic_key
        """
        return fetch_all(query, (exam_type,))

    @staticmethod
    def find_by_id(topic_id: str) -> Optional[Dict[str, Any]]:
        """Find a single topic by UUID."""
        query = """
            SELECT topic_id, exam_type, topic_key, topic_label,
                   parent_topic_id, weight, created_at
            FROM assessments.exam_topic_taxonomy
            WHERE topic_id = %s
        """
        return fetch_one(query, (topic_id,))

    @staticmethod
    def find_by_topic_keys(exam_type: str, topic_keys: List[str]) -> List[Dict[str, Any]]:
        """Find topics by their keys within an exam type."""
        if not topic_keys:
            return []
        query = """
            SELECT topic_id, exam_type, topic_key, topic_label,
                   parent_topic_id, weight
            FROM assessments.exam_topic_taxonomy
            WHERE exam_type = %s AND topic_key = ANY(%s)
        """
        return fetch_all(query, (exam_type, topic_keys))

    @staticmethod
    def create(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new topic in the taxonomy."""
        query = """
            INSERT INTO assessments.exam_topic_taxonomy
                (exam_type, topic_key, topic_label, parent_topic_id, weight)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        """
        return fetch_one(query, (
            data['exam_type'],
            data['topic_key'],
            json.dumps(data.get('topic_label', {})),
            data.get('parent_topic_id'),
            data.get('weight', 1.0),
        ))

    @staticmethod
    def update(topic_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing topic."""
        sets = []
        params = []
        if 'topic_label' in data:
            sets.append('topic_label = %s')
            params.append(json.dumps(data['topic_label']))
        if 'parent_topic_id' in data:
            sets.append('parent_topic_id = %s')
            params.append(data['parent_topic_id'])
        if 'weight' in data:
            sets.append('weight = %s')
            params.append(data['weight'])
        if not sets:
            return TopicTaxonomyRepository.find_by_id(topic_id)
        params.append(topic_id)
        query = f"""
            UPDATE assessments.exam_topic_taxonomy
            SET {', '.join(sets)}
            WHERE topic_id = %s
            RETURNING *
        """
        return fetch_one(query, tuple(params))

    @staticmethod
    def delete(topic_id: str) -> bool:
        """Delete a topic from the taxonomy."""
        query = "DELETE FROM assessments.exam_topic_taxonomy WHERE topic_id = %s"
        execute_query(query, (topic_id,))
        return True
