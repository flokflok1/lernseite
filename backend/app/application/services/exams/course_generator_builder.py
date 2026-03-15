"""Course Generator Builder -- persists ExamCoursePlan as course/chapter/LM records."""
import logging
from typing import Dict, Any, Optional, List

from app.domain.models.exam_course_plan import ExamCoursePlan, ChapterPlan, parse_label
from app.domain.services.lm_content_mapper import LMContentMapper
from app.application.services.exams.lesson_content_builder import (
    build_lesson_markdown,
)
from app.application.services.exams.course_plan_factory import (
    CoursePlanFactory,
    get_ai_lm_types,
)
from app.application.services.exams.question_helpers import (
    filter_usable_questions,
    split_questions_into_chunks,
    lm_lesson_title,
    make_json_safe,
    group_questions_by_scenario,
    build_static_lm_data,
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
from app.infrastructure.persistence.repositories.courses.content.lessons import (
    LessonRepository,
)

logger = logging.getLogger(__name__)


class CourseGeneratorBuilder:
    """Builds and persists course structure from ExamCoursePlan."""

    @staticmethod
    def build(
        plan: ExamCoursePlan,
        creator_user_id: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create course + chapters + LM instances from plan."""
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
        'de': f'Automatisch generiert aus {plan.total_questions} echten Aufgaben.',
        'en': f'Auto-generated from {plan.total_questions} real exam questions.',
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
            course_id, chapter_plan, idx, creator_user_id,
            options, language, plan.region_display_name, plan.exam_type,
        )
        total_lm += result['lm_count']
        total_tokens += result.get('tokens_used', 0)
        if result.get('ai_plan_id'):
            all_ai_plan_ids.append(result['ai_plan_id'])

    for sim_exam_id in plan.simulation_exam_ids:
        sim = _build_simulation_chapter(course_id, sim_exam_id, language)
        total_lm += sim['lm_count']

    return total_lm, total_tokens, all_ai_plan_ids


def _build_chapter(
    course_id: str, chapter_plan: ChapterPlan, order_index: int,
    creator_user_id: str, options: Dict[str, Any],
    language: str = 'de', region: str = '', exam_type: str = '',
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
    questions = filter_usable_questions(questions)

    if not questions:
        logger.warning(
            "Chapter '%s' has no usable questions after filtering",
            chapter_plan.topic,
        )
        return {'lm_count': 0, 'tokens_used': 0}

    # Create static LM instances (types 5-11)
    result = _create_static_lm_instances(
        chapter_id, chapter_plan, questions, language,
    )

    ai_plan_id = _create_ai_plan_if_needed(
        course_id, chapter_id, chapter_plan,
        questions, creator_user_id, language, region, exam_type,
    )
    if ai_plan_id:
        result['ai_plan_id'] = ai_plan_id

    return result


def _fetch_chapter_questions(question_ids: List[str]) -> List[Dict]:
    """Fetch questions and make JSON-serializable (for JSONB LM data)."""
    if not question_ids:
        return []
    rows = ExamQuestionRepository.find_by_ids(question_ids)
    return [make_json_safe(row) for row in rows]


def _create_static_lm_instances(
    chapter_id: str,
    chapter_plan: ChapterPlan,
    questions: List[Dict],
    language: str,
) -> Dict[str, Any]:
    """Create LM instances for static types only (skip AI-generated).

    Questions are split into batches of MAX_QUESTIONS_PER_LESSON so each
    lesson stays manageable.  Each batch gets its own lesson + LM instance.
    """
    ai_types = get_ai_lm_types(chapter_plan)
    lm_count = 0
    global_order = 0

    for lm_type in chapter_plan.lm_types:
        if lm_type in ai_types:
            continue

        chunks = split_questions_into_chunks(questions)
        chapter_label = _chapter_title_from_plan(chapter_plan, language)

        for chunk_idx, chunk in enumerate(chunks):
            lm_data = build_static_lm_data(lm_type, chunk)
            if lm_data is None:
                continue

            title = lm_lesson_title(
                chunk, lm_type, chunk_idx, len(chunks), language,
            )
            content = build_lesson_markdown(
                lm_type, lm_data, chapter_label, language,
            )

            lesson = LessonRepository.create({
                'chapter_id': chapter_id,
                'title': title,
                'lesson_type': 'text',
                'content': content or None,
                'published': True,
            })
            lesson_id = str(lesson['lesson_id'])

            global_order += 1
            LearningMethodInstanceRepository.create({
                'chapter_id': chapter_id,
                'lesson_id': lesson_id,
                'method_type': lm_type,
                'title': title,
                'data': lm_data,
                'order_index': global_order,
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
    region: str = '',
    exam_type: str = '',
) -> Optional[str]:
    """Create AI Editor plan if chapter needs AI generation. Returns plan_id or None."""
    if not CoursePlanFactory.needs_ai_generation(chapter_plan):
        return None

    plan_data = CoursePlanFactory.create_chapter_plan(
        course_id, chapter_id, chapter_plan, questions, language,
    )

    if not plan_data:
        return None

    # Enrich AI plan with web research (cross-reference + validation)
    _enrich_with_web_research(
        chapter_plan, plan_data, language, region, exam_type,
    )

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



def _build_simulation_chapter(
    course_id: str,
    exam_id: str,
    language: str = 'de',
) -> Dict[str, Any]:
    """Build simulation chapter — one lesson per scenario for rotation."""
    questions = ExamQuestionRepository.find_by_exam(exam_id)
    if not questions:
        return {'lm_count': 0}

    exam = ExamRepository.find_by_id(exam_id)
    exam_label = exam.get('title', 'Exam') if exam else 'Exam'

    scenario_groups = group_questions_by_scenario(questions)
    if not scenario_groups:
        return {'lm_count': 0}

    chapter = ChapterRepository.create({
        'course_id': course_id,
        'title': f"Simulation — {exam_label}",
        'description': f'{len(questions)} items, {len(scenario_groups)} scenarios',
    })
    chapter_id = str(chapter['chapter_id'])

    lm_count = 0
    for order_idx, (scenario_title, group_qs) in enumerate(scenario_groups):
        tasks = LMContentMapper.map_to_ihk_tasks(group_qs, include_mcq=True)
        if not tasks or not tasks.get('tasks'):
            continue

        lesson_title = scenario_title or f"Part {order_idx + 1}"
        sim_content = build_lesson_markdown(10, tasks, lesson_title, language)

        exam_config = {
            'exam_id': exam_id,
            'question_count': len(group_qs),
            'scenario_index': order_idx,
            'total_scenarios': len(scenario_groups),
            'mode': 'simulation',
        }

        lesson = LessonRepository.create({
            'chapter_id': chapter_id,
            'title': lesson_title,
            'lesson_type': 'text',
            'content': sim_content or None,
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


def _enrich_with_web_research(
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


def _chapter_title_from_plan(chapter_plan: ChapterPlan, language: str) -> str:
    """Derive chapter title from parent_label or topic key."""
    label = parse_label(chapter_plan.parent_label)
    return label.get(language, chapter_plan.topic.replace('_', ' ').title())


