"""
TopicTaxonomy Repository

CRUD for exam topic catalogs per exam type.
Supports hierarchical topics (parent_topic_id).
All queries use parameterized SQL (%s) via psycopg3.
"""

import json
from typing import Optional, List, Dict, Any

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query, get_connection,
)
from psycopg.rows import dict_row


class TopicTaxonomyRepository:
    """Repository for assessments.exam_topic_taxonomy table."""

    @staticmethod
    def find_by_exam_type(exam_type: str) -> List[Dict[str, Any]]:
        """List all topics for an exam type, ordered by weight desc.

        Simple weight-based ordering for display/selection contexts.
        See also find_all_by_exam_type() for hierarchy-aware ordering.
        """
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
            ON CONFLICT (exam_type, topic_key) DO NOTHING
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
    def find_roots_by_exam_type(exam_type: str) -> List[Dict[str, Any]]:
        """Find all root topics (no parent) for an exam type."""
        query = """
            SELECT topic_id, exam_type, topic_key, topic_label,
                   parent_topic_id, weight, created_at
            FROM assessments.exam_topic_taxonomy
            WHERE exam_type = %s AND parent_topic_id IS NULL
            ORDER BY weight DESC, topic_key
        """
        return fetch_all(query, (exam_type,))

    @staticmethod
    def find_children(parent_topic_id: str) -> List[Dict[str, Any]]:
        """Find all child topics for a given parent."""
        query = """
            SELECT topic_id, exam_type, topic_key, topic_label,
                   parent_topic_id, weight, created_at
            FROM assessments.exam_topic_taxonomy
            WHERE parent_topic_id = %s
            ORDER BY weight DESC, topic_key
        """
        return fetch_all(query, (parent_topic_id,))

    @staticmethod
    def find_all_by_exam_type(exam_type: str) -> List[Dict[str, Any]]:
        """Fetch every topic for an exam type, ordered for hierarchy building.

        Returns roots first (parent_topic_id IS NULL), then children.
        Used by bootstrap/taxonomy services that need parent-before-child ordering.
        See also find_by_exam_type() for simple weight-based ordering.
        """
        query = """
            SELECT topic_id, exam_type, topic_key, topic_label,
                   parent_topic_id, weight, created_at
            FROM assessments.exam_topic_taxonomy
            WHERE exam_type = %s
            ORDER BY parent_topic_id NULLS FIRST, weight DESC, topic_key
        """
        return fetch_all(query, (exam_type,))

    @staticmethod
    def bulk_create(records: List[Dict[str, Any]]) -> int:
        """Insert multiple topics with ON CONFLICT DO NOTHING.

        All inserts run within a single transaction for atomicity.
        Returns the number of actually inserted rows (conflicts are skipped).
        """
        if not records:
            return 0
        query = """
            INSERT INTO assessments.exam_topic_taxonomy
                (exam_type, topic_key, topic_label, parent_topic_id, weight)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """
        inserted = 0
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                for rec in records:
                    cur.execute(query, (
                        rec['exam_type'],
                        rec['topic_key'],
                        json.dumps(rec.get('topic_label', {})),
                        rec.get('parent_topic_id'),
                        rec.get('weight', 1.0),
                    ))
                    inserted += cur.rowcount
        return inserted

    @staticmethod
    def find_by_topic_key(
        exam_type: str, topic_key: str,
    ) -> Optional[Dict[str, Any]]:
        """Find a single topic by exam_type + topic_key."""
        query = """
            SELECT topic_id, exam_type, topic_key, topic_label,
                   parent_topic_id, weight, created_at
            FROM assessments.exam_topic_taxonomy
            WHERE exam_type = %s AND topic_key = %s
        """
        return fetch_one(query, (exam_type, topic_key))

    @staticmethod
    def find_distinct_question_topics(exam_type: str) -> List[str]:
        """Get distinct topic strings from exam_questions for an exam type.

        Unnests the topics TEXT[] column and deduplicates.
        """
        query = """
            SELECT DISTINCT unnest(eq.topics) AS topic
            FROM assessments.exam_questions eq
            JOIN assessments.exams e ON eq.exam_id = e.exam_id
            LEFT JOIN assessments.exam_sessions s ON e.session_id = s.session_id
            WHERE (s.exam_type_key = %s OR e.exam_type_key = %s)
              AND eq.topics IS NOT NULL
            ORDER BY topic
        """
        rows = fetch_all(query, (exam_type, exam_type))
        return [r['topic'] for r in rows]

    @staticmethod
    def delete(topic_id: str) -> bool:
        """Delete a topic from the taxonomy."""
        query = "DELETE FROM assessments.exam_topic_taxonomy WHERE topic_id = %s"
        execute_query(query, (topic_id,))
        return True
