"""TopicNodeRepository -- CRUD for assessments.exam_topic_nodes.

Manages the self-referencing topic hierarchy used to group
exam question topics into parent categories.
"""
import json
from typing import List, Dict, Any, Optional

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query,
)


class TopicNodeRepository:
    """Repository for exam topic hierarchy nodes."""

    @staticmethod
    def find_all() -> List[Dict[str, Any]]:
        """Get all topic nodes ordered by hierarchy."""
        return fetch_all("""
            SELECT topic_key, parent_key, display_name, sort_order, source
            FROM assessments.exam_topic_nodes
            ORDER BY sort_order, topic_key
        """)

    @staticmethod
    def find_roots() -> List[Dict[str, Any]]:
        """Get root-level topics (no parent)."""
        return fetch_all("""
            SELECT topic_key, display_name, sort_order, source
            FROM assessments.exam_topic_nodes
            WHERE parent_key IS NULL
            ORDER BY sort_order, topic_key
        """)

    @staticmethod
    def find_children(parent_key: str) -> List[Dict[str, Any]]:
        """Get children of a parent topic."""
        return fetch_all("""
            SELECT topic_key, display_name, sort_order, source
            FROM assessments.exam_topic_nodes
            WHERE parent_key = %s
            ORDER BY sort_order, topic_key
        """, (parent_key,))

    @staticmethod
    def find_tree() -> List[Dict[str, Any]]:
        """Get full topic tree with children nested."""
        all_nodes = fetch_all("""
            SELECT topic_key, parent_key, display_name, sort_order, source
            FROM assessments.exam_topic_nodes
            ORDER BY sort_order, topic_key
        """)
        by_parent: Dict[Optional[str], list] = {}
        for n in all_nodes:
            pk = n.get('parent_key')
            by_parent.setdefault(pk, []).append(n)

        def build(parent: Optional[str]) -> List[Dict]:
            nodes = by_parent.get(parent, [])
            for node in nodes:
                node['children'] = build(node['topic_key'])
            return nodes

        return build(None)

    @staticmethod
    def upsert(topic_key: str, parent_key: Optional[str],
               display_name: Dict, source: str = 'ai') -> Optional[Dict]:
        """Insert or update a topic node."""
        return fetch_one("""
            INSERT INTO assessments.exam_topic_nodes
                (topic_key, parent_key, display_name, source)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (topic_key) DO UPDATE SET
                parent_key = EXCLUDED.parent_key,
                display_name = EXCLUDED.display_name,
                source = EXCLUDED.source
            RETURNING *
        """, (topic_key, parent_key, json.dumps(display_name), source))

    @staticmethod
    def upsert_batch(nodes: List[Dict]) -> int:
        """Bulk upsert topic nodes. Returns count inserted/updated.

        Each node: {topic_key, parent_key, display_name, source}
        Must insert parents before children (caller ensures order).
        """
        count = 0
        for n in nodes:
            TopicNodeRepository.upsert(
                n['topic_key'],
                n.get('parent_key'),
                n.get('display_name', {}),
                n.get('source', 'ai'),
            )
            count += 1
        return count

    @staticmethod
    def update_parent(topic_key: str, parent_key: Optional[str]) -> bool:
        """Move a topic to a different parent (admin action)."""
        result = fetch_one("""
            UPDATE assessments.exam_topic_nodes
            SET parent_key = %s, source = 'admin'
            WHERE topic_key = %s
            RETURNING topic_key
        """, (parent_key, topic_key))
        return result is not None

    @staticmethod
    def delete(topic_key: str) -> bool:
        """Delete a topic node (children become roots)."""
        execute_query(
            "DELETE FROM assessments.exam_topic_nodes WHERE topic_key = %s",
            (topic_key,),
        )
        return True

    @staticmethod
    def get_unmapped_topics() -> List[Dict[str, Any]]:
        """Find topics in exam_questions that have no node entry."""
        return fetch_all("""
            SELECT t.topic, count(*) AS question_count
            FROM (
                SELECT unnest(topics) AS topic
                FROM assessments.exam_questions eq
                JOIN assessments.exams e ON e.exam_id = eq.exam_id
                WHERE e.analysis_status = 'ready'
            ) t
            LEFT JOIN assessments.exam_topic_nodes n ON n.topic_key = t.topic
            WHERE n.topic_key IS NULL
            GROUP BY t.topic
            ORDER BY count(*) DESC
        """)

    @staticmethod
    def find_all_topics_with_counts() -> List[Dict[str, Any]]:
        """Get all distinct topics from exam questions with counts."""
        return fetch_all("""
            SELECT unnest(topics) AS topic, count(*) AS cnt
            FROM assessments.exam_questions eq
            JOIN assessments.exams e ON e.exam_id = eq.exam_id
            WHERE e.analysis_status = 'ready'
            GROUP BY topic
            ORDER BY cnt DESC
        """)

    @staticmethod
    def get_topic_stats_aggregated(
        user_id: str, exam_type_key: str = None
    ) -> List[Dict[str, Any]]:
        """Get topic stats aggregated by root parent.

        For each root topic, sums up question counts and user stats
        from all child topics. Only includes topics that are in the
        hierarchy (have a display_name), orphan sub-topics are excluded.

        Args:
            user_id: Current user ID
            exam_type_key: Optional filter by exam type (e.g. 'FI_AP1')
        """
        exam_type_filter = "AND e.exam_type_key = %s" if exam_type_key else ""
        params = (exam_type_key, user_id) if exam_type_key else (user_id,)
        return fetch_all(f"""
            WITH topic_roots AS (
                -- Map each topic to its root ancestor
                SELECT
                    n.topic_key,
                    COALESCE(n.parent_key, n.topic_key) AS root_key
                FROM assessments.exam_topic_nodes n
            ),
            question_topics AS (
                SELECT unnest(eq.topics) AS topic, eq.question_id
                FROM assessments.exam_questions eq
                JOIN assessments.exams e ON e.exam_id = eq.exam_id
                WHERE e.analysis_status = 'ready' AND e.published = true
                {exam_type_filter}
            ),
            aggregated AS (
                SELECT
                    COALESCE(tr.root_key, qt.topic) AS root_topic,
                    count(DISTINCT qt.question_id) AS question_count,
                    count(DISTINCT CASE WHEN uqs.question_id IS NOT NULL
                        THEN qt.question_id END) AS attempted,
                    count(DISTINCT CASE
                        WHEN uqs.times_correct > 0
                        AND uqs.times_correct::float
                            / GREATEST(uqs.times_seen, 1) >= 0.5
                        THEN qt.question_id END) AS correct_count
                FROM question_topics qt
                LEFT JOIN topic_roots tr ON tr.topic_key = qt.topic
                LEFT JOIN assessments.user_question_stats uqs
                    ON uqs.question_id = qt.question_id
                    AND uqs.user_id = %s
                GROUP BY COALESCE(tr.root_key, qt.topic)
            )
            SELECT
                a.root_topic AS topic,
                COALESCE(rn.display_name, '{{}}'::jsonb) AS display_name,
                a.question_count,
                a.attempted AS attempts,
                a.correct_count,
                (SELECT array_agg(c.topic_key ORDER BY c.sort_order)
                 FROM assessments.exam_topic_nodes c
                 WHERE c.parent_key = a.root_topic
                ) AS child_topics
            FROM aggregated a
            JOIN assessments.exam_topic_nodes rn
                ON rn.topic_key = a.root_topic
               AND rn.parent_key IS NULL
            ORDER BY a.question_count DESC
        """, params)
