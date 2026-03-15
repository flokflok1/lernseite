"""Repository for exam topic clusters — DB-managed per exam type."""
import json
import logging
from typing import Dict, List, Optional

from app.infrastructure.persistence.database.connection import (
    fetch_all, fetch_one, execute_query,
)

logger = logging.getLogger(__name__)


class ExamTopicClusterRepository:
    """CRUD for assessments.exam_topic_clusters."""

    table_name = 'assessments.exam_topic_clusters'

    @classmethod
    def find_by_exam_type(cls, exam_type_key: str) -> List[Dict]:
        """Get all clusters for an exam type, sorted by sort_order."""
        sql = f"""
            SELECT cluster_key, label, topics, sort_order
            FROM {cls.table_name}
            WHERE exam_type_key = %s
            ORDER BY sort_order
        """
        return fetch_all(sql, (exam_type_key,)) or []

    @classmethod
    def find_one(cls, exam_type_key: str, cluster_key: str) -> Optional[Dict]:
        """Get a single cluster."""
        sql = f"""
            SELECT cluster_id, cluster_key, label, topics, sort_order
            FROM {cls.table_name}
            WHERE exam_type_key = %s AND cluster_key = %s
        """
        return fetch_one(sql, (exam_type_key, cluster_key))

    @classmethod
    def build_topic_lookup(cls, exam_type_key: str) -> Dict[str, str]:
        """Build reverse lookup: topic -> cluster_key for an exam type.

        Returns empty dict if no clusters configured (triggers dynamic fallback).
        """
        clusters = cls.find_by_exam_type(exam_type_key)
        if not clusters:
            return {}
        lookup = {}
        for cluster in clusters:
            for topic in (cluster.get('topics') or []):
                lookup[topic] = cluster['cluster_key']
        return lookup

    @classmethod
    def get_cluster_labels(cls, exam_type_key: str) -> Dict[str, Dict]:
        """Get {cluster_key: label_dict} for all clusters of an exam type."""
        clusters = cls.find_by_exam_type(exam_type_key)
        result = {}
        for c in clusters:
            label = c.get('label', {})
            if isinstance(label, str):
                label = json.loads(label)
            result[c['cluster_key']] = label
        return result

    @classmethod
    def upsert_cluster(
        cls, exam_type_key: str, cluster_key: str,
        label: dict, topics: list, sort_order: int = 0,
    ) -> Optional[Dict]:
        """Insert or update a cluster. Returns the saved row."""
        sql = f"""
            INSERT INTO {cls.table_name}
                (exam_type_key, cluster_key, label, topics, sort_order)
            VALUES (%s, %s, %s::jsonb, %s, %s)
            ON CONFLICT (exam_type_key, cluster_key)
            DO UPDATE SET label = EXCLUDED.label,
                          topics = EXCLUDED.topics,
                          sort_order = EXCLUDED.sort_order,
                          updated_at = NOW()
            RETURNING *
        """
        return fetch_one(sql, (
            exam_type_key, cluster_key,
            json.dumps(label), topics, sort_order,
        ))

    @classmethod
    def delete_by_exam_type(cls, exam_type_key: str) -> int:
        """Delete all clusters for an exam type. Returns rows deleted."""
        sql = f"DELETE FROM {cls.table_name} WHERE exam_type_key = %s"
        return execute_query(sql, (exam_type_key,)) or 0

    @classmethod
    def replace_all_clusters(
        cls, exam_type_key: str, clusters: List[Dict],
    ) -> int:
        """Replace all clusters for an exam type atomically."""
        cls.delete_by_exam_type(exam_type_key)
        count = 0
        for idx, c in enumerate(clusters):
            cls.upsert_cluster(
                exam_type_key, c['cluster_key'],
                c.get('label', {}), c.get('topics', []),
                c.get('sort_order', idx + 1),
            )
            count += 1
        logger.info(
            "Replaced %d clusters for exam type %s",
            count, exam_type_key,
        )
        return count
