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
from app.application.services.exams.course_plan_factory import _GAP_AI_LM_TYPES
from app.infrastructure.persistence.repositories.exams.core import ExamRepository
from app.infrastructure.persistence.repositories.exams.questions import ExamQuestionRepository
from app.infrastructure.persistence.repositories.exams.sessions import ExamSessionRepository
from app.infrastructure.persistence.repositories.exams.topic_taxonomy import (
    TopicTaxonomyRepository,
)
from app.infrastructure.persistence.repositories.exams.curriculum import (
    CurriculumFrameworkRepository,
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
    ) -> ExamCoursePlan:
        """Build a course plan without persisting anything.

        When framework_id is provided, uses curriculum positions as chapters.
        Otherwise falls back to topic-based grouping.

        When user_id is provided, enriches chapters with user-specific
        weakness data for personalized priority sorting.
        """
        simulation_exam_ids = _find_simulation_exams(exam_type_key, region)
        title = _build_title(exam_type_key, region, language)

        if framework_id:
            prognosis_map = _build_prognosis_map(framework_id)
            weakness_map = (
                _build_weakness_map(user_id, exam_type_key)
                if user_id else {}
            )
            chapters = _group_by_curriculum(
                framework_id, sort_mode,
                prognosis_map=prognosis_map,
                weakness_map=weakness_map,
            )
            return ExamCoursePlan(
                title=title,
                exam_type=exam_type_key,
                region=region,
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
                title=f'{exam_type_key} — {region}',
                exam_type=exam_type_key,
                region=region,
            )

        grouped = _group_by_taxonomy(questions, exam_type_key)
        chapters = _build_chapters_from_groups(grouped)

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


def _group_by_curriculum(
    framework_id: int,
    sort_mode: str = 'relevance',
    prognosis_map: Optional[Dict[int, Dict]] = None,
    weakness_map: Optional[Dict[int, Dict]] = None,
) -> List[ChapterPlan]:
    """Group by curriculum positions instead of topics.

    Each position becomes a chapter. Questions are pulled from
    curriculum tags. Positions without questions get AI-only content.

    When sort_mode='relevance', sorts by intelligence_score which
    combines exam relevance, prognosis predictions, and optionally
    user weakness data.
    """
    from app.domain.services.proficiency_scorer import compute_intelligence_score

    positions = CurriculumFrameworkRepository.find_positions_with_question_stats(
        framework_id,
    )

    if not positions:
        logger.warning("No positions found for framework %s", framework_id)
        return []

    relevance_map = _build_relevance_map(framework_id)
    question_data = _load_question_data_for_curriculum(positions)
    prog_map = prognosis_map or {}
    weak_map = weakness_map or {}
    chapters = []
    seen_qids: set = set()

    for pos in positions:
        raw_ids = [str(qid) for qid in (pos.get('question_ids') or [])]
        q_ids = [qid for qid in raw_ids if qid not in seen_qids]
        seen_qids.update(q_ids)

        objectives_total = pos.get('objectives_total', 0)
        objectives_with_q = pos.get('objectives_with_questions', 0)
        objectives_ai = objectives_total - objectives_with_q
        chapter_questions = [
            question_data[qid] for qid in q_ids if qid in question_data
        ]
        total_points = sum(
            float(q.get('points', 0)) for q in chapter_questions
        )

        cov_pct = round(
            objectives_with_q / objectives_total * 100,
        ) if objectives_total > 0 else 0

        if objectives_with_q > 0 and objectives_ai > 0:
            coverage = 'mixed'
        elif objectives_with_q > 0:
            coverage = 'exam_questions'
        else:
            coverage = 'ai_generated'

        if chapter_questions:
            lm_types = LMContentMapper.select_lm_types(
                chapter_questions, exam_mode=True,
            )
        else:
            # Full gap: use evidence-based LM types (single source of truth)
            lm_types = sorted(_GAP_AI_LM_TYPES)

        position_code = f"{pos['section_code']}.{pos['position_code']}"
        pid = pos['position_id']
        rel = relevance_map.get(pid, {})
        prog = prog_map.get(pid, {})
        weak = weak_map.get(pid, {})

        rel_score = rel.get('weighted_score', 0.0)
        prog_prob = prog.get('probability', 0.0)
        user_prof = weak.get('proficiency_score') if weak else None
        user_sev = weak.get('severity') if weak else None

        intel_score = compute_intelligence_score(
            relevance_score=rel_score,
            prognosis_probability=prog_prob,
            proficiency_score=user_prof,
            severity=user_sev,
        )

        chapters.append(ChapterPlan(
            topic=position_code,
            question_ids=q_ids,
            lm_types=lm_types,
            point_weight=total_points,
            question_count=len(q_ids),
            parent_topic=position_code,
            parent_label=_parse_position_label(pos),
            curriculum_position_id=pid,
            curriculum_position_code=position_code,
            objectives_total=objectives_total,
            objectives_with_questions=objectives_with_q,
            objectives_ai_only=objectives_ai,
            coverage_pct=cov_pct,
            coverage_source=coverage,
            relevance_score=rel_score,
            exam_appearance_rate=rel.get('appearance_rate', 0.0),
            relevance_trend=rel.get('trend'),
            prognosis_probability=prog_prob,
            prognosis_confidence=prog.get('confidence'),
            user_proficiency=user_prof,
            user_severity=user_sev,
            intelligence_score=intel_score,
        ))

    if sort_mode == 'relevance':
        chapters.sort(
            key=lambda ch: (
                ch.intelligence_score,
                ch.point_weight,
                ch.curriculum_position_code or '',
            ),
            reverse=True,
        )

    return chapters


def _build_relevance_map(framework_id: int) -> Dict[int, Dict]:
    """Load relevance scores and compute trend per position.

    Returns {position_id: {weighted_score, appearance_rate, trend}}.
    """
    from app.application.services.exams.curriculum_service import compute_trend

    rows = CurriculumFrameworkRepository.find_position_relevance_scores(
        framework_id,
    )
    result = {}
    for row in rows:
        trend = compute_trend(
            row.get('recent_count', 0),
            row.get('older_count', 0),
        )
        result[row['position_id']] = {
            'weighted_score': float(row.get('weighted_score', 0)),
            'appearance_rate': float(row.get('appearance_rate', 0)),
            'trend': trend,
        }
    return result


def _load_question_data_for_curriculum(
    positions: List[Dict],
) -> Dict[str, Dict]:
    """Load full question data for all question IDs across positions."""
    all_ids = []
    for pos in positions:
        all_ids.extend(pos.get('question_ids') or [])

    if not all_ids:
        return {}

    unique_ids = list(set(str(qid) for qid in all_ids))
    questions = ExamQuestionRepository.find_by_ids(unique_ids)
    return {str(q['question_id']): q for q in questions}


def _build_prognosis_map(framework_id: int) -> Dict[int, Dict]:
    """Load prognosis predictions: {position_id: {probability, ...}}."""
    from app.application.services.exams.prognosis_service import PrognosisService
    try:
        predictions = PrognosisService.predict_all(framework_id)
        return {p['position_id']: p for p in predictions}
    except Exception:
        logger.exception("Failed to load prognosis for framework %d", framework_id)
        return {}


def _build_weakness_map(user_id: str, exam_type_key: str) -> Dict[int, Dict]:
    """Load user weakness data: {position_id: {proficiency_score, severity, ...}}."""
    from app.application.services.exams.prognosis_service import PrognosisService
    try:
        weaknesses = PrognosisService.get_user_weakness_map(user_id, exam_type_key)
        return {w['position_id']: w for w in weaknesses}
    except (ValueError, Exception):
        logger.debug("No weakness data for user=%s type=%s", user_id, exam_type_key)
        return {}


def _parse_position_label(pos: Dict) -> Dict[str, str]:
    """Build a label dict from position title (JSONB or str)."""
    title = pos.get('position_title', '')
    if isinstance(title, dict):
        return title
    return {'de': str(title)} if title else {}
