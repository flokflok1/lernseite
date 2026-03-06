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
from app.infrastructure.persistence.repositories.exams.core import (
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

# LM type -> human-readable title template
LM_TITLES: Dict[int, str] = {
    0: '{topic} — Erklaerung',
    1: '{topic} — Schritt fuer Schritt',
    5: '{topic} — Rechenaufgaben',
    6: '{topic} — Karteikarten',
    7: '{topic} — Zuordnungen',
    8: '{topic} — Lueckentexte',
    10: '{topic} — Pruefungsaufgaben',
    11: '{topic} — Fallstudien',
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
        total_lm_count = 0
        total_tokens = 0

        # 1. Create course
        course = CourseRepositoryCRUD.create({
            'title': plan.title,
            'creator_id': creator_user_id,
            'description': (
                f'Automatisch generiert aus {plan.total_questions} '
                f'echten Pruefungsaufgaben.'
            ),
            'tags': ['ihk', 'auto-generated', plan.exam_type.lower()],
            'level': 'intermediate',
        })
        course_id = str(course['course_id'])
        logger.info("Created course %s: %s", course_id, plan.title)

        # 2. Build chapters
        for idx, chapter_plan in enumerate(plan.chapters):
            chapter_result = _build_chapter(
                course_id, chapter_plan, idx, options,
            )
            total_lm_count += chapter_result['lm_count']
            total_tokens += chapter_result.get('tokens_used', 0)

        # 3. Build simulation chapters
        for sim_exam_id in plan.simulation_exam_ids:
            sim_result = _build_simulation_chapter(
                course_id, sim_exam_id,
            )
            total_lm_count += sim_result['lm_count']

        logger.info(
            "Course generation complete: %s — %d chapters, %d LMs, %d tokens",
            course_id, len(plan.chapters), total_lm_count, total_tokens,
        )

        return {
            'course_id': course_id,
            'chapters_count': (
                len(plan.chapters) + len(plan.simulation_exam_ids)
            ),
            'lm_count': total_lm_count,
            'tokens_used': total_tokens,
        }


def _build_chapter(
    course_id: str,
    chapter_plan: ChapterPlan,
    order_index: int,
    options: Dict[str, Any],
) -> Dict[str, Any]:
    """Build a single topic chapter with its LM instances."""
    chapter = ChapterRepository.create({
        'course_id': course_id,
        'title': chapter_plan.topic.replace('_', ' ').title(),
        'description': (
            f'{chapter_plan.question_count} Aufgaben, '
            f'{int(chapter_plan.point_weight)} Punkte'
        ),
        'order_index': order_index + 1,
    })
    chapter_id = str(chapter['chapter_id'])

    # Fetch full question data for this chapter
    questions = []
    for qid in chapter_plan.question_ids:
        q = ExamQuestionRepository.find_by_id(qid)
        if q:
            questions.append(q)

    # Create LM instances for each selected type
    lm_count = 0
    tokens_used = 0

    for lm_order, lm_type in enumerate(chapter_plan.lm_types):
        lm_data, used_tokens = _build_lm_data(
            lm_type, chapter_plan.topic, questions, options,
        )

        if lm_data is None:
            continue

        title = LM_TITLES.get(lm_type, '{topic}').format(
            topic=chapter_plan.topic.replace('_', ' ').title(),
        )

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


def _build_simulation_chapter(
    course_id: str,
    exam_id: str,
) -> Dict[str, Any]:
    """Build a simulation chapter from a full exam."""
    questions = ExamQuestionRepository.find_by_exam(exam_id)
    if not questions:
        return {'lm_count': 0}

    first_q = questions[0]
    title = f"Simulation — {first_q.get('exam_title', 'Pruefung')}"

    chapter = ChapterRepository.create({
        'course_id': course_id,
        'title': title,
        'description': (
            f'Pruefungssimulation mit {len(questions)} Aufgaben'
        ),
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


def _generate_deep_explanation(
    topic: str,
    questions: List[Dict],
    options: Dict[str, Any],
) -> tuple:
    """Generate Deep Explanation content via AI."""
    from app.application.services.exams.course_generator_prompts import (
        build_deep_explanation_prompt,
    )
    from app.infrastructure.ai.adapter import AIAdapter

    prompt = build_deep_explanation_prompt(topic, questions)
    provider = options.get('provider', 'openai')
    model = options.get('model', 'gpt-4o-mini')

    try:
        adapter = AIAdapter(provider=provider, model=model)
        response = adapter.send_request(
            prompt=prompt,
            language='de',
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
            'content': f'Thema: {topic.replace("_", " ").title()}',
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
    from app.infrastructure.ai.adapter import AIAdapter

    prompt = build_step_by_step_prompt(topic, questions)
    provider = options.get('provider', 'openai')
    model = options.get('model', 'gpt-4o-mini')

    try:
        adapter = AIAdapter(provider=provider, model=model)
        response = adapter.send_request(
            prompt=prompt,
            language='de',
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
