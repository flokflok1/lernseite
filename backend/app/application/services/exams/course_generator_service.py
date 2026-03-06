"""
Exam Course Generator Service — Application Layer.

Orchestrates course generation from exam archive questions.
Two phases: preview() returns a plan, generate() persists it.
"""
import logging
from typing import Dict, Any, Optional, List

from app.domain.models.exam_course_plan import ExamCoursePlan, ChapterPlan
from app.domain.services.lm_content_mapper import LMContentMapper
from app.infrastructure.persistence.database.connection import fetch_all

logger = logging.getLogger(__name__)


class ExamCourseGeneratorService:
    """Generates structured courses from real IHK exam questions."""

    @staticmethod
    def preview(
        exam_type_key: str,
        region: str = 'alle',
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
        title = _build_title(exam_type_key, region)

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
    query = """
        SELECT eq.question_id, eq.question_text, eq.question_type,
               eq.points, eq.topics, eq.data, eq.solution_text,
               eq.scenario_title, eq.scenario_text, eq.question_number,
               e.year, e.season, e.part
        FROM assessments.exam_questions eq
        JOIN assessments.exams e ON eq.exam_id = e.exam_id
        LEFT JOIN assessments.exam_sessions s ON e.session_id = s.session_id
        WHERE e.analysis_status = 'ready'
          AND (
              s.exam_type_key = %s
              OR e.exam_type_key = %s
          )
          AND (
              COALESCE(s.region, 'alle') = %s
              OR COALESCE(s.region, 'alle') = 'alle'
          )
        ORDER BY eq.topics, e.year DESC, eq.order_index
    """
    return fetch_all(query, (exam_type_key, exam_type_key, region))


def _group_by_topic(questions: List[Dict]) -> Dict[str, List[Dict]]:
    """Group questions by their topics (a question can belong to multiple topics)."""
    groups: Dict[str, List[Dict]] = {}
    for q in questions:
        topics = q.get('topics') or []
        if not topics:
            topics = ['allgemein']
        for topic in topics:
            if topic not in groups:
                groups[topic] = []
            groups[topic].append(q)
    return groups


def _find_simulation_exams(
    exam_type_key: str, region: str
) -> List[str]:
    """Find distinct exam IDs that can serve as simulation chapters."""
    query = """
        SELECT DISTINCT e.exam_id
        FROM assessments.exams e
        LEFT JOIN assessments.exam_sessions s ON e.session_id = s.session_id
        WHERE e.analysis_status = 'ready'
          AND (s.exam_type_key = %s OR e.exam_type_key = %s)
          AND (COALESCE(s.region, 'alle') = %s OR COALESCE(s.region, 'alle') = 'alle')
        ORDER BY e.exam_id
        LIMIT 6
    """
    rows = fetch_all(query, (exam_type_key, exam_type_key, region))
    return [str(r['exam_id']) for r in rows]


def _build_title(exam_type_key: str, region: str) -> str:
    """Build a human-readable course title."""
    type_labels = {
        'IHK_FISI': 'IHK Fachinformatiker Systemintegration AP1',
        'IHK_FIAE': 'IHK Fachinformatiker Anwendungsentwicklung AP1',
    }
    region_labels = {
        'alle': 'Alle Bundeslaender',
        'bw': 'Baden-Wuerttemberg',
        'bayern': 'Bayern',
        'nrw': 'Nordrhein-Westfalen',
    }
    type_label = type_labels.get(exam_type_key, exam_type_key)
    region_label = region_labels.get(region, region)
    return f'{type_label} — {region_label}'
