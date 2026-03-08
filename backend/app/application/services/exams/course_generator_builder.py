"""
Course Generator Builder — Application Layer.

Persists an ExamCoursePlan as real course/chapter/LM records.
Separated from the service to keep both under 300 LOC.
"""
import logging
from typing import Dict, Any, Optional, List

from app.domain.models.exam_course_plan import ExamCoursePlan, ChapterPlan
from app.domain.services.lm_content_mapper import LMContentMapper
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

logger = logging.getLogger(__name__)

# LM type -> mapper function name
LM_MAPPER: Dict[int, str] = {
    5: 'map_to_math_interactive',
    6: 'map_to_flashcards',
    7: 'map_to_drag_drop',
    8: 'map_to_cloze',
    10: 'map_to_ihk_tasks',
    11: 'map_to_multi_step',
}

# LM type -> title suffix per language
LM_TITLE_SUFFIXES: Dict[str, Dict[int, str]] = {
    'de': {
        0: 'Erklaerung', 1: 'Schritt fuer Schritt',
        5: 'Rechenaufgaben', 6: 'Karteikarten',
        7: 'Zuordnungen', 8: 'Lueckentexte',
        10: 'Pruefungsaufgaben', 11: 'Fallstudien',
    },
    'en': {
        0: 'Explanation', 1: 'Step by Step',
        5: 'Math Exercises', 6: 'Flashcards',
        7: 'Matching', 8: 'Cloze Tests',
        10: 'Exam Tasks', 11: 'Case Studies',
    },
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
            {course_id, chapters_count, lm_count, tokens_used}
        """
        options = options or {}
        language = options.get('language', 'de')

        course_id = _create_course(plan, creator_user_id, language)

        total_lm_count, total_tokens = _build_all_chapters(
            course_id, plan, options, language,
        )

        logger.info(
            "Course generation complete: %s — %d chapters, %d LMs",
            course_id, len(plan.chapters), total_lm_count,
        )

        return {
            'course_id': course_id,
            'chapters_count': (
                len(plan.chapters) + len(plan.simulation_exam_ids)
            ),
            'lm_count': total_lm_count,
            'tokens_used': total_tokens,
        }


def _create_course(
    plan: ExamCoursePlan, creator_user_id: str, language: str,
) -> str:
    """Create the course record and return course_id."""
    descriptions = {
        'de': f'Automatisch generiert aus {plan.total_questions} '
              f'echten Pruefungsaufgaben.',
        'en': f'Auto-generated from {plan.total_questions} '
              f'real exam questions.',
    }
    course = CourseRepositoryCRUD.create({
        'title': plan.title,
        'creator_id': creator_user_id,
        'description': descriptions.get(language, descriptions['de']),
        'tags': ['exam-based', 'auto-generated', plan.exam_type.lower()],
        'level': 'intermediate',
    })
    course_id = str(course['course_id'])
    logger.info("Created course %s: %s", course_id, plan.title)
    return course_id


def _build_all_chapters(
    course_id: str,
    plan: ExamCoursePlan,
    options: Dict[str, Any],
    language: str,
) -> tuple:
    """Build topic chapters + simulation chapters. Returns (lm_count, tokens)."""
    total_lm = 0
    total_tokens = 0

    for idx, chapter_plan in enumerate(plan.chapters):
        result = _build_chapter(
            course_id, chapter_plan, idx, options, language,
        )
        total_lm += result['lm_count']
        total_tokens += result.get('tokens_used', 0)

    for sim_exam_id in plan.simulation_exam_ids:
        sim = _build_simulation_chapter(course_id, sim_exam_id)
        total_lm += sim['lm_count']

    return total_lm, total_tokens


def _build_chapter(
    course_id: str,
    chapter_plan: ChapterPlan,
    order_index: int,
    options: Dict[str, Any],
    language: str = 'de',
) -> Dict[str, Any]:
    """Build a single topic chapter with its LM instances."""
    desc_templates = {
        'de': f'{chapter_plan.question_count} Aufgaben, '
              f'{int(chapter_plan.point_weight)} Punkte',
        'en': f'{chapter_plan.question_count} questions, '
              f'{int(chapter_plan.point_weight)} points',
    }
    chapter_title = _chapter_title_from_plan(chapter_plan, language)
    chapter = ChapterRepository.create({
        'course_id': course_id,
        'title': chapter_title,
        'description': desc_templates.get(language, desc_templates['de']),
        'order_index': order_index + 1,
    })
    chapter_id = str(chapter['chapter_id'])

    questions = _fetch_chapter_questions(chapter_plan.question_ids)

    return _create_lm_instances(
        chapter_id, chapter_plan, questions, options, language,
    )


def _fetch_chapter_questions(question_ids: List[str]) -> List[Dict]:
    """Fetch full question data for a set of question IDs."""
    questions = []
    for qid in question_ids:
        q = ExamQuestionRepository.find_by_id(qid)
        if q:
            questions.append(q)
    return questions


def _create_lm_instances(
    chapter_id: str,
    chapter_plan: ChapterPlan,
    questions: List[Dict],
    options: Dict[str, Any],
    language: str,
) -> Dict[str, Any]:
    """Create LM instances for each selected type. Returns {lm_count, tokens_used}."""
    lm_count = 0
    tokens_used = 0

    for lm_order, lm_type in enumerate(chapter_plan.lm_types):
        lm_data, used_tokens = _build_lm_data(
            lm_type, chapter_plan.topic, questions, options,
        )
        if lm_data is None:
            continue

        title = _lm_title(chapter_plan.topic, lm_type, language)
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
        tokens_used += used_tokens

    return {'lm_count': lm_count, 'tokens_used': tokens_used}


def _lm_title(topic: str, lm_type: int, language: str) -> str:
    """Build a localized LM instance title."""
    suffixes = LM_TITLE_SUFFIXES.get(language, LM_TITLE_SUFFIXES['de'])
    suffix = suffixes.get(lm_type, '')
    topic_label = topic.replace('_', ' ').title()
    return f'{topic_label} — {suffix}' if suffix else topic_label


def _build_simulation_chapter(
    course_id: str,
    exam_id: str,
) -> Dict[str, Any]:
    """Build a simulation chapter from a full exam."""
    questions = ExamQuestionRepository.find_by_exam(exam_id)
    if not questions:
        return {'lm_count': 0}

    first_q = questions[0]
    exam_label = first_q.get('exam_title', 'Exam')
    title = f"Simulation — {exam_label}"

    chapter = ChapterRepository.create({
        'course_id': course_id,
        'title': title,
        'description': f'Exam simulation — {len(questions)} questions',
    })
    chapter_id = str(chapter['chapter_id'])

    # Create one IHK-Style Tasks (LM10) with all questions
    tasks = LMContentMapper.map_to_ihk_tasks(questions)
    LearningMethodInstanceRepository.create({
        'chapter_id': chapter_id,
        'method_type': 10,
        'title': title,
        'data': tasks,
        'published': True,
        'difficulty': 'hard',
    })

    return {'lm_count': 1}


def _chapter_title_from_plan(
    chapter_plan: ChapterPlan, language: str,
) -> str:
    """Derive chapter title from parent_label (taxonomy) or topic key."""
    label = chapter_plan.parent_label or {}
    if isinstance(label, str):
        import json
        try:
            label = json.loads(label)
        except (json.JSONDecodeError, TypeError):
            label = {}
    return label.get(language, chapter_plan.topic.replace('_', ' ').title())


def _build_lm_data(
    lm_type: int,
    topic: str,
    questions: List[Dict],
    options: Dict[str, Any],
) -> tuple:
    """
    Build JSONB data for a specific LM type.

    Returns:
        (data_dict, tokens_used) — data_dict is None if no content
        could be generated.
    """
    mapper = LM_MAPPER.get(lm_type)

    # LM 0 (Deep Explanation) — needs AI generation
    if lm_type == 0:
        return _generate_deep_explanation(topic, questions, options)

    # LM 1 (Step by Step) — needs AI generation
    if lm_type == 1:
        return _generate_step_by_step(topic, questions, options)

    # Static mapping from exam data
    if mapper:
        map_fn = getattr(LMContentMapper, mapper, None)
        if map_fn:
            data = map_fn(questions)
            # Skip if no content was mapped
            items_key = list(data.keys())[0] if data else None
            if items_key and len(data.get(items_key, [])) == 0:
                return None, 0
            return data, 0

    return None, 0


def _create_ai_adapter(options: Dict[str, Any]):
    """Create AIAdapter from options, letting infra defaults apply."""
    from app.infrastructure.ai.adapter import AIAdapter
    kwargs: Dict[str, Any] = {}
    if options.get('provider'):
        kwargs['provider'] = options['provider']
    if options.get('model'):
        kwargs['model'] = options['model']
    return AIAdapter(**kwargs)


def _generate_deep_explanation(
    topic: str,
    questions: List[Dict],
    options: Dict[str, Any],
) -> tuple:
    """Generate Deep Explanation content via AI."""
    from app.application.services.exams.course_generator_prompts import (
        build_deep_explanation_prompt,
    )

    prompt = build_deep_explanation_prompt(topic, questions)
    language = options.get('language', 'de')

    try:
        adapter = _create_ai_adapter(options)
        response = adapter.send_request(
            prompt=prompt,
            language=language,
            temperature=0.5,
            max_tokens=4000,
        )
        explanation = response.get('output_text', '')
        tokens = response.get('total_tokens', 0)

        return {
            'content': explanation,
            'topic': topic,
            'source_questions': len(questions),
        }, tokens

    except Exception as e:
        logger.error("AI generation failed for %s: %s", topic, e)
        return {
            'content': topic.replace('_', ' ').title(),
            'topic': topic,
            'source_questions': len(questions),
        }, 0


def _generate_step_by_step(
    topic: str,
    questions: List[Dict],
    options: Dict[str, Any],
) -> tuple:
    """Generate Step-by-Step content via AI."""
    from app.application.services.exams.course_generator_prompts import (
        build_step_by_step_prompt,
    )

    prompt = build_step_by_step_prompt(topic, questions)
    language = options.get('language', 'de')

    try:
        adapter = _create_ai_adapter(options)
        response = adapter.send_request(
            prompt=prompt,
            language=language,
            temperature=0.5,
            max_tokens=4000,
        )
        content = response.get('output_text', '')
        tokens = response.get('total_tokens', 0)

        return {
            'content': content,
            'topic': topic,
            'source_questions': len(questions),
        }, tokens

    except Exception as e:
        logger.error(
            "AI step-by-step generation failed for %s: %s", topic, e,
        )
        return None, 0
