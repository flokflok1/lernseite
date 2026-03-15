"""
Exam Course Generator Service — Application Layer.

Orchestrates course generation from exam archive questions.
Two phases: preview() returns a plan, generate() persists it.
"""
import logging
from typing import Dict, Any, Optional, List, Tuple

from app.domain.models.exam_course_plan import ExamCoursePlan, ChapterPlan, parse_label
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
        framework_id: int = None,
        sort_mode: str = 'relevance',
        user_id: str = None,
        grouping_strategy: str = 'auto',
    ) -> ExamCoursePlan:
        """Build a course plan without persisting anything.

        grouping_strategy controls chapter structure:
        - 'exam_practice': ~7 practical topic chapters (best for exam prep)
        - 'curriculum': chapters per curriculum position (needs framework_id)
        - 'topic': chapters per taxonomy parent category
        - 'auto': curriculum if framework_id given, else topic (legacy)

        When user_id is provided, enriches chapters with user-specific
        weakness data for personalized priority sorting.
        """
        simulation_exam_ids = _find_simulation_exams(exam_type_key, region)
        title = _build_title(exam_type_key, region, language)
        region_name = _resolve_region_name(region, language, for_query=True)

        # Exam practice strategy: practical topic clusters
        if grouping_strategy == 'exam_practice':
            from app.application.services.exams.exam_practice_grouping import (
                group_by_exam_practice,
            )
            chapters, grouping_meta = group_by_exam_practice(
                exam_type_key, region,
            )
            logger.info(
                "Exam practice grouping: source=%s, %d clusters, %d questions",
                grouping_meta.get('source'),
                grouping_meta.get('cluster_count', 0),
                grouping_meta.get('question_count', 0),
            )
            return ExamCoursePlan(
                title=title,
                exam_type=exam_type_key,
                region=region,
                region_display_name=region_name,
                sort_mode=sort_mode,
                chapters=chapters,
                simulation_exam_ids=simulation_exam_ids,
            )

        if framework_id:
            from app.application.services.exams.curriculum_grouping import (
                group_by_curriculum,
                build_prognosis_map,
                build_weakness_map,
            )
            prognosis_map = build_prognosis_map(framework_id)
            weakness_map = (
                build_weakness_map(user_id, exam_type_key)
                if user_id else {}
            )
            chapters = group_by_curriculum(
                framework_id, sort_mode,
                prognosis_map=prognosis_map,
                weakness_map=weakness_map,
            )
            return ExamCoursePlan(
                title=title,
                exam_type=exam_type_key,
                region=region,
                region_display_name=region_name,
                curriculum_framework_id=framework_id,
                sort_mode=sort_mode,
                chapters=chapters,
                simulation_exam_ids=simulation_exam_ids,
            )

        # Fallback: topic-based grouping (existing logic)
        questions = _fetch_questions_for_course(exam_type_key, region)

        if not questions:
            logger.warning(
                "No questions found for type=%s region=%s",
                exam_type_key, region,
            )
            return ExamCoursePlan(
                title=title,
                exam_type=exam_type_key,
                region=region,
                region_display_name=region_name,
            )

        grouped = _group_by_taxonomy(questions, exam_type_key)
        chapters = _build_chapters_from_groups(grouped)

        return ExamCoursePlan(
            title=title,
            exam_type=exam_type_key,
            region=region,
            region_display_name=region_name,
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

    @staticmethod
    def get_generation_progress(course_id: str) -> Dict[str, Any]:
        """
        Read generation progress from infrastructure layer (Redis).

        Returns a dict with {total, completed, failed, status}.
        """
        from app.infrastructure.tasks.course_generation_tasks import (
            get_generation_progress as _get_progress,
        )
        return _get_progress(course_id)


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
        label = parse_label(row.get('topic_label'))
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
        lm_types = LMContentMapper.select_lm_types(
            topic_questions, exam_mode=True,
        )
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


def _resolve_region_name(region: str, language: str = 'de', for_query: bool = False) -> str:
    """Resolve region code to display name. Returns '' for 'alle' when for_query=True."""
    if not region or (for_query and region == 'alle'):
        return ''
    row = ExamSessionRepository.find_region_display_name(region)
    if row and row.get('display_name'):
        dn = row['display_name']
        return dn.get(language, dn.get('de', region)) if isinstance(dn, dict) else str(dn)
    return region


def _build_title(exam_type_key: str, region: str, language: str = 'de') -> str:
    """Build a human-readable course title from DB display_name fields.

    Combines program name ("Fachinformatiker") + exam type ("AP1")
    instead of just the generic exam type.
    """
    type_row = ExamSessionRepository.find_type_display_name(exam_type_key)

    # Resolve program name (e.g. "Fachinformatiker")
    program_label = ''
    if type_row and type_row.get('program_display_name'):
        pdn = type_row['program_display_name']
        program_label = pdn.get(language, pdn.get('de', '')) if isinstance(pdn, dict) else str(pdn)

    # Resolve exam type name (e.g. "AP1 (gemeinsam)")
    type_label = exam_type_key
    if type_row and type_row.get('display_name'):
        dn = type_row['display_name']
        type_label = dn.get(language, dn.get('de', exam_type_key)) if isinstance(dn, dict) else str(dn)

    # Combine: "Fachinformatiker — AP1 (gemeinsam)"
    if program_label:
        title = f'{program_label} — {type_label}'
    else:
        title = type_label

    # Only append region if it's specific (not "alle")
    region_name = _resolve_region_name(region, language, for_query=True)
    if region_name:
        title = f'{title} ({region_name})'

    return title


