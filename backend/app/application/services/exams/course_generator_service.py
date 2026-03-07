"""
Exam Course Generator Service — Application Layer.

Orchestrates course generation from exam archive questions.
Two phases: preview() returns a plan, generate() persists it.
"""
import logging
from typing import Dict, Any, Optional, List

from app.domain.models.exam_course_plan import ExamCoursePlan, ChapterPlan
from app.domain.services.exam_topic_utils import normalize_topic
from app.domain.services.lm_content_mapper import LMContentMapper
from app.infrastructure.persistence.repositories.exams.core import ExamRepository
from app.infrastructure.persistence.repositories.exams.questions import ExamQuestionRepository
from app.infrastructure.persistence.repositories.exams.sessions import ExamSessionRepository

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

        topic_groups = _group_by_topic(questions)
        topic_groups = _merge_small_topics(topic_groups)

        chapters = []
        for topic, topic_questions in sorted(
            topic_groups.items(),
            key=lambda x: sum(q.get('points', 0) for q in x[1]),
            reverse=True,
        ):
            lm_types = LMContentMapper.select_lm_types(topic_questions)
            total_points = sum(q.get('points', 0) for q in topic_questions)

            chapters.append(ChapterPlan(
                topic=topic,
                question_ids=[q['question_id'] for q in topic_questions],
                lm_types=lm_types,
                point_weight=total_points,
                question_count=len(topic_questions),
            ))

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


MIN_TOPIC_SIZE = 3  # Minimum questions for a standalone chapter


def _group_by_topic(questions: List[Dict]) -> Dict[str, List[Dict]]:
    """Group questions by their normalized topics."""
    groups: Dict[str, List[Dict]] = {}
    for q in questions:
        topics = q.get('topics') or []
        if not topics:
            topics = ['allgemein']
        for topic in topics:
            normalized = normalize_topic(topic)
            if normalized not in groups:
                groups[normalized] = []
            groups[normalized].append(q)
    return groups


def _merge_small_topics(groups: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
    """Merge topics with fewer than MIN_TOPIC_SIZE questions into related larger topics."""
    large = {k: v for k, v in groups.items() if len(v) >= MIN_TOPIC_SIZE}
    small = {k: v for k, v in groups.items() if len(v) < MIN_TOPIC_SIZE}

    for topic, questions in small.items():
        merged = False
        for parent in large:
            if parent in topic or topic in parent:
                large[parent].extend(questions)
                merged = True
                break
        if not merged:
            large.setdefault('allgemein', []).extend(questions)

    return large


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
