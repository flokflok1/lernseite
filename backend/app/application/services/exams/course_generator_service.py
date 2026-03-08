"""
Exam Course Generator Service — Application Layer.

Orchestrates course generation from exam archive questions.
Two phases: preview() returns a plan, generate() persists it.
"""
import json
import logging
from typing import Dict, Any, Optional, List, Tuple

from app.domain.models.exam_course_plan import ExamCoursePlan, ChapterPlan
from app.domain.services.exam_topic_utils import normalize_topic
from app.domain.services.lm_content_mapper import LMContentMapper
from app.infrastructure.persistence.repositories.exams.core import ExamRepository
from app.infrastructure.persistence.repositories.exams.questions import ExamQuestionRepository
from app.infrastructure.persistence.repositories.exams.sessions import ExamSessionRepository
from app.infrastructure.persistence.repositories.exams.topic_taxonomy import (
    TopicTaxonomyRepository,
)

logger = logging.getLogger(__name__)


class ExamCourseGeneratorService:
    """Generates structured courses from real IHK exam questions."""

    @staticmethod
    def preview(
        exam_type_key: str,
        region: str = 'alle',
        language: str = 'de',
    ) -> ExamCoursePlan:
        """
        Build a course plan without persisting anything.

        1. Fetch all ready exam questions for the given type + region
        2. Group by topic
        3. For each topic: determine LM types
        4. Return ExamCoursePlan VO
        """
        questions = _fetch_questions_for_course(exam_type_key, region)

        if not questions:
            logger.warning(
                "No questions found for type=%s region=%s",
                exam_type_key, region,
            )
            return ExamCoursePlan(
                title=f'{exam_type_key} — {region}',
                exam_type=exam_type_key,
                region=region,
            )

        grouped = _group_by_taxonomy(questions, exam_type_key)
        chapters = _build_chapters_from_groups(grouped)

        simulation_exam_ids = _find_simulation_exams(exam_type_key, region)
        title = _build_title(exam_type_key, region, language)

        return ExamCoursePlan(
            title=title,
            exam_type=exam_type_key,
            region=region,
            chapters=chapters,
            simulation_exam_ids=simulation_exam_ids,
        )

    @staticmethod
    def generate(
        plan: ExamCoursePlan,
        creator_user_id: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Persist the plan as a real course.
        Delegated to CourseGeneratorBuilder.
        """
        from app.application.services.exams.course_generator_builder import (
            CourseGeneratorBuilder,
        )
        return CourseGeneratorBuilder.build(plan, creator_user_id, options)


def _fetch_questions_for_course(
    exam_type_key: str, region: str
) -> List[Dict]:
    """Fetch all ready exam questions for given type + region."""
    return ExamQuestionRepository.find_for_course_generation(
        exam_type_key, region,
    )


def _group_by_taxonomy(
    questions: List[Dict], exam_type: str,
) -> Dict[str, Dict]:
    """Group questions by taxonomy parent categories.

    When a taxonomy exists the child->parent lookup drives grouping.
    When no taxonomy data is found we fall back to flat grouping.

    Returns {parent_key: {'questions': [...], 'label': {...}, 'children': [...]}}
    """
    all_topics = TopicTaxonomyRepository.find_all_by_exam_type(exam_type)
    if not all_topics:
        return _group_flat(questions)

    child_to_parent, parent_labels = _build_taxonomy_lookup(all_topics)
    return _assign_questions_to_parents(
        questions, child_to_parent, parent_labels,
    )


def _build_taxonomy_lookup(
    all_topics: List[Dict],
) -> Tuple[Dict[str, str], Dict[str, Dict]]:
    """Build child->parent lookup and parent label map from taxonomy rows."""
    id_to_key: Dict[str, str] = {}
    parent_labels: Dict[str, Dict] = {}
    child_to_parent: Dict[str, str] = {}

    for row in all_topics:
        tid = str(row['topic_id'])
        key = row['topic_key']
        id_to_key[tid] = key
        label = _ensure_dict_label(row.get('topic_label'))
        if row.get('parent_topic_id') is None:
            parent_labels[key] = label

    for row in all_topics:
        key = row['topic_key']
        pid = row.get('parent_topic_id')
        if pid is not None:
            parent_key = id_to_key.get(str(pid), key)
            child_to_parent[key] = parent_key
        else:
            child_to_parent[key] = key

    return child_to_parent, parent_labels


def _assign_questions_to_parents(
    questions: List[Dict],
    child_to_parent: Dict[str, str],
    parent_labels: Dict[str, Dict],
) -> Dict[str, Dict]:
    """Assign each question to exactly one parent chapter (dedup by qid)."""
    groups: Dict[str, Dict] = {}
    seen_qids: set = set()

    for q in questions:
        qid = q.get('question_id')
        if qid in seen_qids:
            continue

        primary_topic = _primary_topic(q)
        normalized = normalize_topic(primary_topic)
        parent_key = child_to_parent.get(normalized, normalized)

        if parent_key not in groups:
            groups[parent_key] = {
                'questions': [],
                'label': parent_labels.get(parent_key, {}),
                'children': [],
            }

        groups[parent_key]['questions'].append(q)
        seen_qids.add(qid)

        if normalized != parent_key and normalized not in groups[parent_key]['children']:
            groups[parent_key]['children'].append(normalized)

    return groups


def _group_flat(questions: List[Dict]) -> Dict[str, Dict]:
    """Legacy fallback: group by primary topic when no taxonomy exists."""
    groups: Dict[str, Dict] = {}
    seen_qids: set = set()

    for q in questions:
        qid = q.get('question_id')
        if qid in seen_qids:
            continue

        primary_topic = _primary_topic(q)
        normalized = normalize_topic(primary_topic)

        if normalized not in groups:
            groups[normalized] = {
                'questions': [],
                'label': {},
                'children': [],
            }

        groups[normalized]['questions'].append(q)
        seen_qids.add(qid)

    return groups


def _ensure_dict_label(value: Any) -> Dict:
    """Parse topic_label to dict, handling both str (JSON) and dict inputs."""
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    return {}


def _primary_topic(question: Dict) -> str:
    """Extract the first (primary) topic from a question dict."""
    topics = question.get('topics') or []
    return topics[0] if topics and topics[0] else 'allgemein'


def _build_chapters_from_groups(
    grouped: Dict[str, Dict],
) -> List['ChapterPlan']:
    """Convert grouped dict to sorted list of ChapterPlan VOs."""
    chapters = []
    for parent_key, group in grouped.items():
        topic_questions = group['questions']
        lm_types = LMContentMapper.select_lm_types(topic_questions)
        total_points = sum(q.get('points', 0) for q in topic_questions)

        chapters.append(ChapterPlan(
            topic=parent_key,
            question_ids=[q['question_id'] for q in topic_questions],
            lm_types=lm_types,
            point_weight=total_points,
            question_count=len(topic_questions),
            parent_topic=parent_key,
            parent_label=group.get('label') or None,
            child_topics=group.get('children') or None,
        ))

    chapters.sort(key=lambda ch: ch.point_weight, reverse=True)
    return chapters


def _find_simulation_exams(
    exam_type_key: str, region: str
) -> List[str]:
    """Find distinct exam IDs that can serve as simulation chapters."""
    return ExamRepository.find_simulation_exam_ids(
        exam_type_key, region,
    )


def _build_title(
    exam_type_key: str, region: str, language: str = 'de',
) -> str:
    """Build a human-readable course title from DB display_name fields."""
    type_row = ExamSessionRepository.find_type_display_name(exam_type_key)
    if type_row and type_row.get('display_name'):
        dn = type_row['display_name']
        type_label = (
            dn.get(language, dn.get('de', exam_type_key))
            if isinstance(dn, dict) else str(dn)
        )
    else:
        type_label = exam_type_key

    region_row = ExamSessionRepository.find_region_display_name(region)
    if region_row and region_row.get('display_name'):
        dn = region_row['display_name']
        region_label = (
            dn.get(language, dn.get('de', region))
            if isinstance(dn, dict) else str(dn)
        )
    else:
        region_label = region

    return f'{type_label} — {region_label}'
