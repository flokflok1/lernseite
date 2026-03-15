"""
Exam Practice Grouping Strategy — Application Layer.

Hybrid approach:
1. DB clusters (admin-configured per exam type) → curated grouping
2. Dynamic fallback → auto-clusters from actual question topic distribution

Works for ANY exam type without hardcoding.
"""
import logging
from collections import Counter
from typing import Dict, List, Tuple

from app.domain.models.exam_course_plan import ChapterPlan
from app.domain.services.exam_topic_utils import normalize_topic
from app.domain.services.lm_content_mapper import LMContentMapper
from app.infrastructure.persistence.repositories.exams.questions import (
    ExamQuestionRepository,
)
from app.infrastructure.persistence.repositories.exams.topic_clusters import (
    ExamTopicClusterRepository,
)

logger = logging.getLogger(__name__)

_FALLBACK_KEY = 'sonstiges'
_FALLBACK_LABEL = {'de': 'Sonstige Themen', 'en': 'Other Topics'}


def group_by_exam_practice(
    exam_type_key: str,
    region: str,
) -> Tuple[List[ChapterPlan], Dict]:
    """Group questions into practical exam chapters.

    Uses DB clusters if configured, otherwise derives clusters
    dynamically from the actual topic distribution.

    Returns (chapters, metadata) where metadata contains grouping info
    for transparency in the API response.
    """
    questions = ExamQuestionRepository.find_for_course_generation(
        exam_type_key, region,
    )
    if not questions:
        logger.warning(
            "No questions for exam_practice grouping: type=%s region=%s",
            exam_type_key, region,
        )
        return [], {'source': 'none', 'cluster_count': 0}

    # Try DB clusters first (admin-curated)
    topic_lookup = ExamTopicClusterRepository.build_topic_lookup(exam_type_key)
    cluster_labels = ExamTopicClusterRepository.get_cluster_labels(exam_type_key)

    if topic_lookup:
        logger.info(
            "Using %d DB clusters for %s",
            len(cluster_labels), exam_type_key,
        )
        clusters = _assign_with_db_clusters(
            questions, topic_lookup, cluster_labels,
        )
        source = 'db_clusters'
    else:
        logger.warning(
            "NO clusters configured for exam type '%s' in "
            "assessments.exam_topic_clusters — using auto-clustering. "
            "Configure clusters in Admin Panel for better results.",
            exam_type_key,
        )
        clusters = _assign_dynamically(questions)
        source = 'auto_dynamic'

    chapters = _build_chapters(clusters)
    chapters.sort(key=lambda ch: ch.point_weight, reverse=True)

    meta = {
        'source': source,
        'cluster_count': len(chapters),
        'question_count': len(questions),
    }
    return chapters, meta


def _assign_with_db_clusters(
    questions: List[Dict],
    topic_lookup: Dict[str, str],
    cluster_labels: Dict[str, Dict],
) -> Dict[str, Dict]:
    """Assign questions using DB-configured cluster mappings."""
    clusters: Dict[str, Dict] = {}
    seen_qids: set = set()

    for q in questions:
        qid = q.get('question_id')
        if qid in seen_qids:
            continue

        cluster_key = _resolve_cluster_key(q, topic_lookup)

        if cluster_key not in clusters:
            clusters[cluster_key] = {
                'questions': [],
                'child_topics': set(),
                'label': cluster_labels.get(cluster_key, _FALLBACK_LABEL),
            }

        primary = normalize_topic(_primary_topic(q))
        clusters[cluster_key]['questions'].append(q)
        clusters[cluster_key]['child_topics'].add(primary)
        seen_qids.add(qid)

    return clusters


def _resolve_cluster_key(
    question: Dict, topic_lookup: Dict[str, str],
) -> str:
    """Find cluster for question: try primary topic, then secondary."""
    topics = question.get('topics') or []
    for topic in topics:
        normalized = normalize_topic(topic)
        cluster_key = topic_lookup.get(normalized)
        if cluster_key:
            return cluster_key
    return _FALLBACK_KEY


def _assign_dynamically(questions: List[Dict]) -> Dict[str, Dict]:
    """Auto-cluster by most frequent primary topics (no DB config needed).

    Takes the top N topics (by question count) as cluster anchors.
    Questions with rare topics go into a fallback cluster.
    """
    # Count primary topic frequency
    topic_counts: Counter = Counter()
    for q in questions:
        primary = normalize_topic(_primary_topic(q))
        topic_counts[primary] += 1

    # Top topics become clusters (at least 3 questions to qualify)
    min_questions = 3
    max_clusters = 12
    anchor_topics = [
        topic for topic, count in topic_counts.most_common(max_clusters)
        if count >= min_questions
    ]

    clusters: Dict[str, Dict] = {}
    seen_qids: set = set()

    for q in questions:
        qid = q.get('question_id')
        if qid in seen_qids:
            continue

        primary = normalize_topic(_primary_topic(q))
        cluster_key = primary if primary in anchor_topics else _FALLBACK_KEY

        if cluster_key not in clusters:
            label = _topic_to_label(cluster_key)
            clusters[cluster_key] = {
                'questions': [],
                'child_topics': set(),
                'label': label,
            }

        clusters[cluster_key]['questions'].append(q)
        clusters[cluster_key]['child_topics'].add(primary)
        seen_qids.add(qid)

    return clusters


def _topic_to_label(topic_key: str) -> Dict[str, str]:
    """Convert a topic key to a human-readable label dict."""
    if topic_key == _FALLBACK_KEY:
        return _FALLBACK_LABEL
    display = topic_key.replace('_', ' ').title()
    return {'de': display, 'en': display}


def _build_chapters(
    clusters: Dict[str, Dict],
) -> List[ChapterPlan]:
    """Convert cluster dict to list of ChapterPlan value objects."""
    chapters = []
    for cluster_key, cluster_data in clusters.items():
        questions = cluster_data['questions']
        if not questions:
            continue

        child_topics = sorted(cluster_data['child_topics'])
        label = cluster_data.get('label', _FALLBACK_LABEL)

        lm_types = LMContentMapper.select_lm_types(
            questions, exam_mode=True,
        )
        total_points = sum(
            float(q.get('points', 0)) for q in questions
        )

        chapters.append(ChapterPlan(
            topic=cluster_key,
            question_ids=[str(q['question_id']) for q in questions],
            lm_types=lm_types,
            point_weight=total_points,
            question_count=len(questions),
            parent_topic=cluster_key,
            parent_label=label,
            child_topics=child_topics,
            coverage_source='exam_questions',
            coverage_pct=100.0,
        ))

    return chapters


def _primary_topic(question: Dict) -> str:
    """Extract the first (primary) topic from a question dict."""
    topics = question.get('topics') or []
    return topics[0] if topics and topics[0] else 'allgemein'
