"""Course Generator Builder -- persists ExamCoursePlan as course/chapter/LM records."""
import logging
from typing import Dict, Any, Optional, List

from app.domain.models.exam_course_plan import ExamCoursePlan, ChapterPlan, parse_label
from app.domain.services.lm_content_mapper import LMContentMapper
from app.application.services.exams.course_plan_factory import (
    CoursePlanFactory,
    get_ai_lm_types,
)
from app.infrastructure.persistence.repositories.courses.management.crud import (
    CourseRepositoryCRUD,
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
from app.infrastructure.persistence.repositories.ai.content_plans import (
    ContentPlanRepository,
)

logger = logging.getLogger(__name__)

# LM type -> mapper function name (static content from exam data)
LM_MAPPER: Dict[int, str] = {
    5: 'map_to_math_interactive',
    6: 'map_to_flashcards',
    7: 'map_to_drag_drop',
    8: 'map_to_cloze',
    10: 'map_to_ihk_tasks',
    11: 'map_to_multi_step',
}

# LM type -> English title suffix (language-neutral internal labels)
LM_TITLE_SUFFIX: Dict[int, str] = {
    0: 'Explanation',
    1: 'Step by Step',
    5: 'Math Exercises',
    6: 'Flashcards',
    7: 'Matching',
    8: 'Cloze Tests',
    10: 'Exam Tasks',
    11: 'Case Studies',
}


class CourseGeneratorBuilder:
    """Builds and persists course structure from ExamCoursePlan."""

    @staticmethod
    def build(
        plan: ExamCoursePlan,
        creator_user_id: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create course + chapters + LM instances from plan.

        Returns:
            {course_id, chapters_count, lm_count, tokens_used,
             ai_plan_ids, status}
        """
        options = options or {}
        language = options.get('language', 'de')

        course_id = _create_course(plan, creator_user_id, language)

        total_lm_count, total_tokens, ai_plan_ids = _build_all_chapters(
            course_id, plan, creator_user_id, options, language,
        )

        # Initialize spaced repetition schedule for the creator
        if plan.exam_type:
            try:
                from app.application.services.learning.review_service import ReviewService
                srs_result = ReviewService.initialize_course_reviews(
                    creator_user_id, course_id,
                )
                logger.info(
                    "SRS initialized: %d review items for course %s",
                    srs_result.get('initialized', 0), course_id,
                )
            except Exception:
                logger.exception(
                    "SRS initialization failed for course %s (non-blocking)",
                    course_id,
                )

        status = 'generating' if ai_plan_ids else 'ready'

        if ai_plan_ids:
            _dispatch_ai_generation(course_id, ai_plan_ids, creator_user_id)

        logger.info(
            "Course generation complete: %s -- %d chapters, %d LMs, "
            "%d AI plans (%s)",
            course_id, len(plan.chapters), total_lm_count,
            len(ai_plan_ids), status,
        )

        return {
            'course_id': course_id,
            'chapters_count': (
                len(plan.chapters) + len(plan.simulation_exam_ids)
            ),
            'lm_count': total_lm_count,
            'tokens_used': total_tokens,
            'ai_plan_ids': ai_plan_ids,
            'status': status,
        }


def _create_course(
    plan: ExamCoursePlan, creator_user_id: str, language: str,
) -> str:
    """Create the course record and return course_id."""
    desc_map = {
        'de': (
            f'Automatisch generiert aus {plan.total_questions} '
            f'echten Aufgaben.'
        ),
        'en': (
            f'Auto-generated from {plan.total_questions} '
            f'real exam questions.'
        ),
    }
    course = CourseRepositoryCRUD.create({
        'title': plan.title,
        'creator_id': creator_user_id,
        'description': desc_map.get(language, desc_map['en']),
        'tags': ['exam-based', 'auto-generated', plan.exam_type.lower()],
        'level': 'intermediate',
        'exam_mode': True,
        'exam_config': {
            'time_limit_minutes': 90,
            'total_points': plan.total_points,
            'passing_percentage': 50,
            'source_exam_type': plan.exam_type,
            'source_region': plan.region,
            'simulation_exam_ids': plan.simulation_exam_ids,
        },
    })
    course_id = str(course['course_id'])
    logger.info("Created course %s: %s", course_id, plan.title)
    return course_id


def _dispatch_ai_generation(
    course_id: str,
    ai_plan_ids: List[str],
    creator_user_id: str,
) -> None:
    """Queue Celery task for background AI content generation."""
    from app.infrastructure.tasks.course_generation_tasks import (
        generate_course_content_task,
    )
    generate_course_content_task.delay(
        course_id, ai_plan_ids, creator_user_id,
    )
    logger.info(
        "Queued Celery task for %d AI plans (course %s)",
        len(ai_plan_ids), course_id,
    )


def _build_all_chapters(
    course_id: str,
    plan: ExamCoursePlan,
    creator_user_id: str,
    options: Dict[str, Any],
    language: str,
) -> tuple:
    """Build topic chapters + simulation chapters.

    Returns (lm_count, tokens, ai_plan_ids).
    """
    total_lm = 0
    total_tokens = 0
    all_ai_plan_ids: List[str] = []

    for idx, chapter_plan in enumerate(plan.chapters):
        result = _build_chapter(
            course_id, chapter_plan, idx,
            creator_user_id, options, language,
        )
        total_lm += result['lm_count']
        total_tokens += result.get('tokens_used', 0)
        if result.get('ai_plan_id'):
            all_ai_plan_ids.append(result['ai_plan_id'])

    for sim_exam_id in plan.simulation_exam_ids:
        sim = _build_simulation_chapter(course_id, sim_exam_id)
        total_lm += sim['lm_count']

    return total_lm, total_tokens, all_ai_plan_ids


def _build_chapter(
    course_id: str,
    chapter_plan: ChapterPlan,
    order_index: int,
    creator_user_id: str,
    options: Dict[str, Any],
    language: str = 'de',
) -> Dict[str, Any]:
    """Build a single topic chapter with its LM instances."""
    is_ai_only = chapter_plan.coverage_source == 'ai_generated'
    desc_map = {
        'de': (
            f'{chapter_plan.question_count} Fragen, '
            f'{int(chapter_plan.point_weight)} Punkte'
        ),
        'en': (
            f'{chapter_plan.question_count} questions, '
            f'{int(chapter_plan.point_weight)} points'
        ),
    }
    chapter_title = _chapter_title_from_plan(chapter_plan, language)
    chapter = ChapterRepository.create({
        'course_id': course_id,
        'title': chapter_title,
        'description': desc_map.get(language, desc_map['en']),
        'order_index': order_index + 1,
        'ai_generated': is_ai_only,
        'ai_metadata': _build_chapter_metadata(chapter_plan),
    })
    chapter_id = str(chapter['chapter_id'])

    questions = _fetch_chapter_questions(chapter_plan.question_ids)

    # Create static LM instances (types 5-11)
    result = _create_static_lm_instances(
        chapter_id, chapter_plan, questions, language,
    )

    ai_plan_id = _create_ai_plan_if_needed(
        course_id, chapter_id, chapter_plan,
        questions, creator_user_id, language,
    )
    if ai_plan_id:
        result['ai_plan_id'] = ai_plan_id

    return result


def _fetch_chapter_questions(question_ids: List[str]) -> List[Dict]:
    """Fetch full question data for a set of question IDs (batch)."""
    if not question_ids:
        return []
    return ExamQuestionRepository.find_by_ids(question_ids)


def _create_static_lm_instances(
    chapter_id: str,
    chapter_plan: ChapterPlan,
    questions: List[Dict],
    language: str,
) -> Dict[str, Any]:
    """Create LM instances for static types only (skip AI-generated)."""
    ai_types = get_ai_lm_types(chapter_plan)
    lm_count = 0

    for lm_order, lm_type in enumerate(chapter_plan.lm_types):
        # Skip AI-generated types -- handled by AI Editor pipeline
        if lm_type in ai_types:
            continue

        lm_data = _build_static_lm_data(lm_type, questions)
        if lm_data is None:
            continue

        title = _lm_title(chapter_plan, lm_type, language)
        LearningMethodInstanceRepository.create({
            'chapter_id': chapter_id,
            'method_type': lm_type,
            'title': title,
            'data': lm_data,
            'order_index': lm_order + 1,
            'published': True,
            'difficulty': 'medium',
        })
        lm_count += 1

    return {'lm_count': lm_count, 'tokens_used': 0}


def _create_ai_plan_if_needed(
    course_id: str,
    chapter_id: str,
    chapter_plan: ChapterPlan,
    questions: List[Dict],
    creator_user_id: str,
    language: str,
) -> Optional[str]:
    """Create an AI Editor plan for AI-generated LM types if needed.

    Returns the plan_id or None if no AI generation is needed.
    """
    if not CoursePlanFactory.needs_ai_generation(chapter_plan):
        return None

    plan_data = CoursePlanFactory.create_chapter_plan(
        course_id, chapter_id, chapter_plan, questions, language,
    )

    if not plan_data:
        return None

    # Enrich AI plan with web research for gap positions
    _enrich_ai_plan_with_gap_content(chapter_plan, plan_data, language)

    plan = ContentPlanRepository.create({
        'course_id': course_id,
        'scope': 'chapter',
        'scope_id': chapter_id,
        'user_id': creator_user_id,
        'status': 'approved',
        'plan_data': plan_data,
    })

    if not plan:
        logger.error(
            "Failed to create AI plan for chapter %s", chapter_id,
        )
        return None

    plan_id = str(plan['plan_id'])
    logger.info(
        "Created AI plan %s for chapter %s (topic: %s)",
        plan_id, chapter_id, chapter_plan.topic,
    )
    return plan_id


def _lm_title(
    chapter_plan: ChapterPlan, lm_type: int, language: str = 'de',
) -> str:
    """Build an LM instance title with English suffix.

    Uses parent_label (human-readable curriculum title) when available,
    falls back to topic key for topic-based grouping.
    """
    suffix = LM_TITLE_SUFFIX.get(lm_type, '')
    label = parse_label(chapter_plan.parent_label)
    topic_label = (
        label.get(language)
        or label.get('de')
        or chapter_plan.topic.replace('_', ' ').title()
    )
    return f'{topic_label} -- {suffix}' if suffix else topic_label


def _build_simulation_chapter(
    course_id: str,
    exam_id: str,
) -> Dict[str, Any]:
    """Build a simulation chapter from a full exam."""
    questions = ExamQuestionRepository.find_by_exam(exam_id)
    if not questions:
        return {'lm_count': 0}

    # Map ALL question types for realistic exam simulation
    tasks = LMContentMapper.map_to_ihk_tasks(questions, include_mcq=True)
    if not tasks or not tasks.get('tasks'):
        logger.warning(
            "Simulation exam %s has no IHK-compatible questions, skipping",
            exam_id,
        )
        return {'lm_count': 0}

    # Get exam title from exams table (not from questions)
    exam = ExamRepository.find_by_id(exam_id)
    exam_label = exam.get('title', 'Exam') if exam else 'Exam'
    title = f"Simulation -- {exam_label}"

    chapter = ChapterRepository.create({
        'course_id': course_id,
        'title': title,
        'description': f'Exam simulation -- {len(questions)} questions',
    })
    chapter_id = str(chapter['chapter_id'])

    question_count = len(questions)
    exam_config = {
        'exam_id': exam_id,
        'question_count': question_count,
        'time_limit_minutes': 90,
        'passing_percentage': 50,
        'mode': 'simulation',
    }

    LearningMethodInstanceRepository.create({
        'chapter_id': chapter_id,
        'method_type': 10,
        'title': title,
        'data': {**tasks, 'exam_config': exam_config},
        'published': True,
        'difficulty': 'hard',
    })

    return {'lm_count': 1, 'question_count': question_count}


def _build_chapter_metadata(chapter_plan: ChapterPlan) -> dict:
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


def _enrich_ai_plan_with_gap_content(
    chapter_plan: ChapterPlan,
    plan_data: dict,
    language: str = 'de',
) -> None:
    """Enrich AI plan with Grounding web research for gap positions (<50% coverage)."""
    if chapter_plan.coverage_pct >= 50:
        return
    if not chapter_plan.curriculum_position_id:
        return

    from app.domain.exceptions.web_research import WebResearchError

    try:
        from app.application.services.exams.gap_content_service import (
            GapContentService,
        )
        gap_results = GapContentService.generate_gap_content(
            framework_id=0,  # not needed — position_id is provided
            position_id=chapter_plan.curriculum_position_id,
            language=language,
        )
        if gap_results:
            result = gap_results[0]
            plan_data['gap_research_context'] = result
            plan_data['grounding_status'] = result.get('grounding_status', 'success')
            plan_data['research_sources'] = result.get('sources', [])
            logger.info("Gap enriched position %s (grounding=%s, src=%d)",
                        chapter_plan.curriculum_position_code,
                        result.get('grounding_status', '?'), len(result.get('sources', [])))
    except WebResearchError as e:
        logger.warning("Grounding failed for position %s: %s",
                        chapter_plan.curriculum_position_code, str(e))
        plan_data['grounding_status'] = 'failed'
        plan_data['research_sources'] = []
    except Exception:
        logger.exception("Gap enrichment failed for position %s",
                          chapter_plan.curriculum_position_code)
        plan_data['grounding_status'] = 'failed'
        plan_data['research_sources'] = []


def _chapter_title_from_plan(
    chapter_plan: ChapterPlan, language: str,
) -> str:
    """Derive chapter title from parent_label (taxonomy) or topic key."""
    label = parse_label(chapter_plan.parent_label)
    return label.get(language, chapter_plan.topic.replace('_', ' ').title())


def _build_static_lm_data(
    lm_type: int,
    questions: List[Dict],
) -> Optional[Dict[str, Any]]:
    """Build JSONB data for a static LM type via LMContentMapper."""
    mapper = LM_MAPPER.get(lm_type)
    if not mapper:
        return None

    map_fn = getattr(LMContentMapper, mapper, None)
    if not map_fn:
        return None

    data = map_fn(questions)
    if not data:
        return None
    # Skip if content dict exists but all values are empty lists
    items_key = next(iter(data), None)
    if items_key is not None and len(data.get(items_key, [])) == 0:
        return None
    return data
