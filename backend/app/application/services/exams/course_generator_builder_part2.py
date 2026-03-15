"""Course Generator Builder Part 2 — simulation chapters and support functions.

Split from course_generator_builder.py to comply with G01 (500 LOC limit).
"""
import logging
from typing import Dict, Any, List

from app.domain.models.exam_course_plan import ExamCoursePlan, ChapterPlan, parse_label
from app.domain.services.lm_content_mapper import LMContentMapper
from app.application.services.exams.lesson_content_builder import (
    build_lesson_markdown,
)
from app.application.services.exams.question_helpers import (
    make_json_safe,
    group_questions_by_scenario,
)
from app.infrastructure.persistence.repositories.courses.content.chapters import (
    ChapterRepository,
)
from app.infrastructure.persistence.repositories.learning_method.execution.instances import (
    LearningMethodInstanceRepository,
)
from app.infrastructure.persistence.repositories.exams.questions import (
    ExamQuestionRepository,
)
from app.infrastructure.persistence.repositories.exams.core import (
    ExamRepository,
)
from app.infrastructure.persistence.repositories.courses.content.lessons import (
    LessonRepository,
)

logger = logging.getLogger(__name__)


def _estimate_duration(lm_type: int, item_count: int) -> int:
    """Estimate lesson duration in minutes from LM type and item count."""
    per_item = {
        0: 12, 1: 10,          # Explanation: ~12 min
        5: 5,                   # Math: 5 min/problem
        6: 2,                   # Flashcards: 2 min/card
        7: 2,                   # Drag & drop: 2 min/pair
        8: 3,                   # Cloze: 3 min/gap
        10: 6,                  # IHK tasks: 6 min/task
        11: 8,                  # Case study: 8 min/step
    }
    base = per_item.get(lm_type, 5)
    return max(2, base * max(1, item_count))


def build_simulation_chapter(
    course_id: str,
    exam_id: str,
    language: str = 'de',
) -> Dict[str, Any]:
    """Build simulation chapter with real exam structure.

    One lesson per scenario, preserving GA1 question order with
    time limit and point distribution metadata.
    """
    questions = ExamQuestionRepository.find_by_exam(exam_id)
    if not questions:
        return {'lm_count': 0}

    exam = ExamRepository.find_by_id(exam_id)
    exam_label = exam.get('title', 'Exam') if exam else 'Exam'
    total_points = sum(float(q.get('points', 0) or 0) for q in questions)

    scenario_groups = group_questions_by_scenario(questions)
    if not scenario_groups:
        return {'lm_count': 0}

    sim_title = {
        'de': f'Simulation: {exam_label}',
        'en': f'Simulation: {exam_label}',
    }
    desc = {
        'de': (f'{len(questions)} Aufgaben, {len(scenario_groups)} Szenarien, '
               f'{int(total_points)} Punkte — 90 Minuten Bearbeitungszeit'),
        'en': (f'{len(questions)} tasks, {len(scenario_groups)} scenarios, '
               f'{int(total_points)} points — 90 minutes time limit'),
    }
    chapter = ChapterRepository.create({
        'course_id': course_id,
        'title': sim_title.get(language, sim_title['de']),
        'description': desc.get(language, desc['de']),
    })
    chapter_id = str(chapter['chapter_id'])

    lm_count = 0
    for order_idx, (scenario_title, group_qs) in enumerate(scenario_groups):
        tasks = LMContentMapper.map_to_ihk_tasks(group_qs, include_mcq=True)
        if not tasks or not tasks.get('tasks'):
            continue

        scenario_pts = sum(float(q.get('points', 0) or 0) for q in group_qs)
        lesson_title = scenario_title or f"Teil {order_idx + 1}"
        sim_content = build_lesson_markdown(10, tasks, lesson_title, language)
        duration = _estimate_duration(10, len(tasks.get('tasks', [])))

        exam_config = {
            'exam_id': exam_id,
            'exam_title': exam_label,
            'question_count': len(group_qs),
            'scenario_points': scenario_pts,
            'total_points': total_points,
            'time_limit_minutes': 90,
            'scenario_index': order_idx,
            'total_scenarios': len(scenario_groups),
            'mode': 'simulation',
        }

        lesson = LessonRepository.create({
            'chapter_id': chapter_id,
            'title': lesson_title,
            'lesson_type': 'ihk_tasks',
            'content': sim_content or None,
            'duration_minutes': duration,
            'published': True,
        })
        lesson_id = str(lesson['lesson_id'])

        LearningMethodInstanceRepository.create({
            'chapter_id': chapter_id,
            'lesson_id': lesson_id,
            'method_type': 10,
            'title': lesson_title,
            'data': make_json_safe({**tasks, 'exam_config': exam_config}),
            'order_index': order_idx + 1,
            'published': True,
            'difficulty': 'hard',
        })
        lm_count += 1

    return {'lm_count': lm_count, 'question_count': len(questions)}


def build_chapter_metadata(chapter_plan: ChapterPlan) -> dict:
    """Build ai_metadata JSONB with intelligence data for frontend badges."""
    meta = {
        'coverage_source': chapter_plan.coverage_source,
        'coverage_pct': chapter_plan.coverage_pct,
        'intelligence_score': chapter_plan.intelligence_score,
        'relevance_score': chapter_plan.relevance_score,
        'prognosis_probability': chapter_plan.prognosis_probability,
    }
    if chapter_plan.prognosis_confidence:
        meta['prognosis_confidence'] = chapter_plan.prognosis_confidence
    if chapter_plan.user_proficiency is not None:
        meta['user_proficiency'] = chapter_plan.user_proficiency
        meta['user_severity'] = chapter_plan.user_severity
    return meta


def enrich_with_web_research(
    chapter_plan: ChapterPlan, plan_data: dict,
    language: str = 'de', region: str = '', exam_type: str = '',
) -> None:
    """Enrich AI plan with web research (Grounding + PDFs) for validation."""
    from app.domain.exceptions.web_research import WebResearchError

    label = chapter_plan.curriculum_position_code or chapter_plan.topic
    result = None
    try:
        result = _fetch_web_research(chapter_plan, language, region, exam_type)
    except WebResearchError as e:
        logger.warning("Grounding failed for %s: %s", label, e)
    except Exception:
        logger.exception("Web research failed for %s", label)

    if result and result.get('summary'):
        plan_data['web_research_context'] = result
        plan_data['grounding_status'] = result.get('grounding_status', 'success')
        plan_data['research_sources'] = result.get('sources', [])
        logger.info("Web research enriched %s (grounding=%s, src=%d)",
                     label, result.get('grounding_status', '?'),
                     len(result.get('sources', [])))
    else:
        plan_data['grounding_status'] = 'failed'
        plan_data['research_sources'] = []


def _fetch_web_research(
    chapter_plan: ChapterPlan, language: str,
    region: str = '', exam_type: str = '',
) -> dict:
    """Fetch web research — curriculum-based or topic-based."""
    if chapter_plan.curriculum_position_id:
        from app.application.services.exams.gap_content_service import (
            GapContentService,
        )
        results = GapContentService.generate_gap_content(
            framework_id=0,
            position_id=chapter_plan.curriculum_position_id,
            language=language, region=region, exam_type=exam_type,
        )
        return results[0] if results else {}

    from app.infrastructure.web_research.search_service import WebSearchService
    topic_name = chapter_plan.topic.replace('_', ' ')
    return WebSearchService.research_position(
        position_id=0, position_title=topic_name,
        objectives=[topic_name], language=language,
        region=region, exam_type=exam_type,
    )


def chapter_title_from_plan(chapter_plan: ChapterPlan, language: str) -> str:
    """Derive chapter title from parent_label or topic key."""
    label = parse_label(chapter_plan.parent_label)
    return label.get(language, chapter_plan.topic.replace('_', ' ').title())
