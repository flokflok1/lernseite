"""
Curriculum Grouping Strategy — Application Layer.

Groups exam questions by curriculum framework positions.
Each position becomes a chapter. Positions without questions
get AI-only content. Includes intelligence scoring (relevance,
prognosis, user weakness).
"""
import logging
from typing import Dict, List, Optional

from app.domain.models.exam_course_plan import ChapterPlan
from app.domain.services.lm_content_mapper import LMContentMapper
from app.application.services.exams.course_plan_factory import _GAP_AI_LM_TYPES
from app.infrastructure.persistence.repositories.exams.questions import (
    ExamQuestionRepository,
)
from app.infrastructure.persistence.repositories.exams.curriculum import (
    CurriculumFrameworkRepository,
)

logger = logging.getLogger(__name__)


def group_by_curriculum(
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
    question_data = _load_question_data(positions)
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


def build_prognosis_map(framework_id: int) -> Dict[int, Dict]:
    """Load prognosis predictions: {position_id: {probability, ...}}."""
    from app.application.services.exams.prognosis_service import PrognosisService
    try:
        predictions = PrognosisService.predict_all(framework_id)
        return {p['position_id']: p for p in predictions}
    except Exception:
        logger.exception("Failed to load prognosis for framework %d", framework_id)
        return {}


def build_weakness_map(user_id: str, exam_type_key: str) -> Dict[int, Dict]:
    """Load user weakness data: {position_id: {proficiency_score, severity, ...}}."""
    from app.application.services.exams.prognosis_service import PrognosisService
    try:
        weaknesses = PrognosisService.get_user_weakness_map(user_id, exam_type_key)
        return {w['position_id']: w for w in weaknesses}
    except (ValueError, Exception):
        logger.debug("No weakness data for user=%s type=%s", user_id, exam_type_key)
        return {}


def _build_relevance_map(framework_id: int) -> Dict[int, Dict]:
    """Load relevance scores and compute trend per position."""
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


def _load_question_data(
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


def _parse_position_label(pos: Dict) -> Dict[str, str]:
    """Build a label dict from position title (JSONB or str)."""
    title = pos.get('position_title', '')
    if isinstance(title, dict):
        return title
    return {'de': str(title)} if title else {}
