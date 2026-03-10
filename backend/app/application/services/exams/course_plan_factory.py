"""
Course Plan Factory -- Creates AI Editor plans for exam course chapters.

Bridges the Exam Course Generator (structure) with the AI Editor Pipeline
(content).  Only LM types that require AI generation (0, 1) get plan steps;
static LM types (5-11) are handled by LMContentMapper directly in the builder.
"""
import logging
from typing import Dict, Any, List

from app.domain.models.exam_course_plan import ChapterPlan

logger = logging.getLogger(__name__)

# LM types that require AI content generation via the editor pipeline
AI_GENERATED_LM_TYPES = {0, 1}

# Mapping from LM type to the AI skill code used by plan_execution
LM_SKILL_MAP: Dict[int, str] = {
    0: 'generate_deep_explanation',
    1: 'generate_step_by_step',
}


class CoursePlanFactory:
    """Creates AI Editor plan_data dicts for exam course chapters."""

    @staticmethod
    def needs_ai_generation(chapter_plan: ChapterPlan) -> bool:
        """Return True if any LM type in the chapter needs AI generation."""
        return bool(AI_GENERATED_LM_TYPES & set(chapter_plan.lm_types))

    @staticmethod
    def create_chapter_plan(
        course_id: str,
        chapter_id: str,
        chapter_plan: ChapterPlan,
        questions: List[Dict[str, Any]],
        language: str = 'de',
    ) -> Dict[str, Any]:
        """
        Create an AI Editor plan_data dict for a single chapter.

        Only includes steps for LM types in AI_GENERATED_LM_TYPES.
        Returns a dict compatible with plan_execution.py format.
        """
        steps = _build_ai_steps(
            chapter_id, chapter_plan, questions, language,
        )

        if not steps:
            return {}

        phase_title = _resolve_topic_label(chapter_plan, language)

        return {
            'course_id': course_id,
            'source': 'exam_course_generator',
            'phases': [{
                'phase_idx': 0,
                'title': phase_title,
                'chapter_id': chapter_id,
                'steps': steps,
            }],
        }


def _build_ai_steps(
    chapter_id: str,
    chapter_plan: ChapterPlan,
    questions: List[Dict[str, Any]],
    language: str,
) -> List[Dict[str, Any]]:
    """Build plan steps for each AI-generated LM type in the chapter."""
    steps: List[Dict[str, Any]] = []
    question_context = _build_question_context(questions)
    topic_label = _resolve_topic_label(chapter_plan, language)

    for idx, lm_type in enumerate(chapter_plan.lm_types):
        if lm_type not in AI_GENERATED_LM_TYPES:
            continue

        skill_code = LM_SKILL_MAP[lm_type]

        steps.append({
            'step_id': f'0-{idx}',
            'skill_code': skill_code,
            'target_title': topic_label,
            'target_type': 'chapter',
            'target_id': chapter_id,
            'learning_methods': [lm_type],
            'parameters': {
                'difficulty': 'medium',
                'topic': topic_label,
                'language': language,
                'question_context': question_context,
            },
            'status': 'pending',
            'tokens_used': 0,
        })

    return steps


def _resolve_topic_label(
    chapter_plan: ChapterPlan, language: str = 'de',
) -> str:
    """Extract a human-readable topic label from the chapter plan.

    Prefers parent_label (localized curriculum position title) over
    the raw topic code (e.g. "A.1") which is meaningless for AI.
    """
    label = chapter_plan.parent_label
    if label and isinstance(label, dict):
        resolved = label.get(language) or label.get('de') or ''
        if resolved:
            return resolved
    # Fallback: topic key (only useful for topic-based grouping)
    return chapter_plan.topic.replace('_', ' ').title()


def _build_question_context(
    questions: List[Dict[str, Any]],
    max_questions: int = 10,
) -> str:
    """Summarize exam questions as text context for the AI.

    Returns a compact string listing question texts and types,
    capped at max_questions.
    """
    if not questions:
        return ''

    lines: List[str] = []
    for q in questions[:max_questions]:
        q_text = q.get('question_text', '').strip()
        q_type = q.get('question_type', '')
        points = q.get('points', 0)
        if q_text:
            snippet = q_text[:200]
            lines.append(f'- [{q_type}, {points}P] {snippet}')

    if len(questions) > max_questions:
        lines.append(f'... and {len(questions) - max_questions} more questions')

    return '\n'.join(lines)
