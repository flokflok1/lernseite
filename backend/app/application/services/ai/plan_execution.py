"""
Plan Execution — Background thread for plan step execution.

Materializes AI-generated content into the course structure:
1. Updates course title from plan metadata
2. Creates chapters from plan phases
3. Executes each step via AI and creates a lesson with the result
4. Updates step status in plan_data after each step
"""

from typing import Dict, Any, Optional
import json
import logging

from app.infrastructure.persistence.repositories.ai.content_plans import ContentPlanRepository

logger = logging.getLogger(__name__)


def execute_plan_background(plan_id: str, plan: Dict[str, Any], user_id: str) -> None:
    """
    Execute all plan steps in a background thread.

    Runs outside the Flask request context, so creates its own app context.
    """
    from flask import current_app
    from app.application.services.ai.skill_service import SkillExecutionService
    from app.infrastructure.persistence.repositories.courses.crud import CourseRepositoryCRUD
    from app.infrastructure.persistence.repositories.courses.chapters import ChapterRepository

    try:
        from app import create_app
        app = create_app()
    except Exception:
        app = current_app._get_current_object()

    with app.app_context():
        try:
            course_id = plan['course_id']
            plan_data = plan['plan_data']
            if isinstance(plan_data, str):
                plan_data = json.loads(plan_data)

            # ── Step 0: Update course title from plan metadata ──
            _update_course_title(course_id, plan)

            # ── Step 1: Create chapters from plan phases ──
            phase_chapter_map = _create_chapters(
                course_id, plan_data, plan_id
            )

            # ── Step 2: Execute steps and create lessons ──
            total_tokens = 0
            has_failures = False

            for phase_idx, phase in enumerate(plan_data.get('phases', [])):
                chapter_id = phase_chapter_map.get(phase_idx)

                for step_idx, step in enumerate(phase.get('steps', [])):
                    step_id = step.get('step_id', f'{phase_idx}-{step_idx}')

                    step['status'] = 'running'
                    ContentPlanRepository.update_plan_data(plan_id, plan_data)

                    try:
                        # Enrich parameters with topic context
                        step_params = dict(step.get('parameters') or {})
                        step_params['topic'] = step.get('target_title', '')
                        step_params['chapter_title'] = phase.get('title', '')
                        step_params['course_title'] = plan.get('course_meta', {}).get('title', '') if isinstance(plan.get('course_meta'), dict) else ''

                        result = SkillExecutionService.execute(
                            skill_code=step['skill_code'],
                            course_id=course_id,
                            user_id=user_id,
                            target_type=step.get('target_type'),
                            target_id=step.get('target_id'),
                            parameters=step_params,
                            plan_id=plan_id,
                        )

                        if chapter_id:
                            _create_lesson_from_result(
                                chapter_id=chapter_id,
                                step=step,
                                result=result,
                                order_index=step_idx + 1,
                            )

                        step['status'] = 'completed'
                        tokens = result.get('tokens_input', 0) + result.get('tokens_output', 0)
                        total_tokens += tokens
                    except Exception as e:
                        logger.error(f"Step {step_id} failed: {e}")
                        step['status'] = 'failed'
                        has_failures = True

                    ContentPlanRepository.update_plan_data(plan_id, plan_data)
                    ContentPlanRepository.update_token_count(plan_id, total_tokens)

            final_status = 'completed' if not has_failures else 'paused'
            ContentPlanRepository.update_status(plan_id, final_status)
            logger.info(
                f"Plan {plan_id} execution finished: {final_status}, "
                f"{total_tokens} tokens"
            )

        except Exception as e:
            logger.error(f"Plan {plan_id} background execution crashed: {e}")
            ContentPlanRepository.update_status(plan_id, 'paused')


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _update_course_title(course_id: str, plan: Dict[str, Any]) -> None:
    """Update course title from plan's course_meta if available."""
    from app.infrastructure.persistence.repositories.courses.crud import CourseRepositoryCRUD

    course_meta = plan.get('course_meta')
    if isinstance(course_meta, str):
        course_meta = json.loads(course_meta)
    if course_meta and course_meta.get('title'):
        try:
            CourseRepositoryCRUD.update(course_id, {
                'title': course_meta['title'],
            })
            logger.info(f"Updated course {course_id} title to: {course_meta['title']}")
        except Exception as e:
            logger.warning(f"Could not update course title: {e}")


def _create_chapters(
    course_id: str,
    plan_data: Dict[str, Any],
    plan_id: str,
) -> Dict[int, Optional[str]]:
    """Create chapters from plan phases. Returns phase_idx → chapter_id map."""
    from app.infrastructure.persistence.repositories.courses.chapters import ChapterRepository

    phase_chapter_map: Dict[int, Optional[str]] = {}
    for phase_idx, phase in enumerate(plan_data.get('phases', [])):
        # Reuse existing chapter_id if already created (idempotent)
        existing_id = phase.get('chapter_id')
        if existing_id:
            phase_chapter_map[phase_idx] = str(existing_id)
            logger.info(f"Reusing chapter '{phase.get('title')}' -> {existing_id}")
            continue

        try:
            chapter = ChapterRepository.create({
                'course_id': course_id,
                'title': phase.get('title', f'Kapitel {phase_idx + 1}'),
                'order_index': phase_idx + 1,
                'ai_generated': True,
            })
            chapter_id = str(chapter['chapter_id'])
            phase_chapter_map[phase_idx] = chapter_id
            phase['chapter_id'] = chapter_id
            logger.info(f"Created chapter '{phase.get('title')}' -> {chapter_id}")
        except Exception as e:
            logger.error(f"Failed to create chapter for phase {phase_idx}: {e}")
            phase_chapter_map[phase_idx] = None

    ContentPlanRepository.update_plan_data(plan_id, plan_data)
    return phase_chapter_map


def _create_lesson_from_result(
    chapter_id: str,
    step: Dict[str, Any],
    result: Dict[str, Any],
    order_index: int,
) -> Optional[Dict[str, Any]]:
    """Create a lesson and its learning method instance from an AI skill result."""
    from app.infrastructure.persistence.repositories.courses.lessons import LessonRepository

    skill_code = step.get('skill_code', '')
    title = step.get('target_title', skill_code)
    content = result.get('content', {})
    lesson_type = _skill_to_lesson_type(skill_code)

    try:
        lesson = LessonRepository.create({
            'chapter_id': chapter_id,
            'title': title,
            'lesson_type': lesson_type,
            'content': json.dumps(content) if isinstance(content, dict) else content,
            'order_index': order_index,
        })
        logger.info(f"Created lesson '{title}' ({lesson_type}) in chapter {chapter_id}")

        # Create learning method instances from explicit plan assignments
        difficulty = step.get('parameters', {}).get('difficulty', 'medium') if step.get('parameters') else 'medium'
        _create_method_instances(
            chapter_id=chapter_id,
            lesson_id=str(lesson['lesson_id']),
            step=step,
            title=title,
            content=content,
            difficulty=difficulty,
            order_index=order_index,
        )

        return lesson
    except Exception as e:
        logger.error(f"Failed to create lesson '{title}': {e}")
        return None


def _create_method_instances(
    chapter_id: str,
    lesson_id: str,
    step: Dict[str, Any],
    title: str,
    content: Any,
    difficulty: str = 'medium',
    order_index: int = 0,
) -> None:
    """Create learning method instances for a lesson.

    Uses explicit ``learning_methods`` array from the plan step if available.
    Falls back to implicit skill→LM mapping for backward compatibility.
    """
    from app.domain.ai.configuration.skills import get_skill
    from app.infrastructure.persistence.repositories.learning_method.instances import (
        LearningMethodInstanceRepository,
    )

    explicit_lms = step.get('learning_methods')
    skill_code = step.get('skill_code', '')
    raw_data = content if isinstance(content, dict) else {}

    # Determine which LM IDs to create
    lm_ids: list[int] = []
    if explicit_lms and isinstance(explicit_lms, list):
        lm_ids = [int(lm) for lm in explicit_lms if isinstance(lm, (int, float))]
    else:
        # Fallback: use implicit skill→LM mapping
        skill_def = get_skill(skill_code)
        if skill_def and skill_def.learning_method_id is not None:
            lm_ids = [skill_def.learning_method_id]

    if not lm_ids:
        return

    for idx, lm_id in enumerate(lm_ids):
        try:
            data = _transform_data_for_method(lm_id, raw_data, title)
            LearningMethodInstanceRepository.create({
                'chapter_id': chapter_id,
                'lesson_id': lesson_id,
                'method_type': lm_id,
                'title': title,
                'data': data,
                'difficulty': difficulty,
                'order_index': order_index * 100 + idx,
                'published': True,
            })
            logger.info(
                f"Created method instance (type={lm_id}) "
                f"for lesson '{title}'"
            )
        except Exception as e:
            logger.warning(f"Failed to create method instance type={lm_id} for '{title}': {e}")


def _transform_data_for_method(
    method_type: int,
    raw_data: Dict[str, Any],
    title: str,
) -> Dict[str, Any]:
    """Transform raw AI output into the structured format each renderer expects.

    If the data already has the right structure (e.g. ``cards`` for flashcards),
    it is returned as-is.  Otherwise, ``raw_text`` is converted into the expected
    shape so the frontend renderer can display it.
    """
    import re

    raw_text = raw_data.get('raw_text', '')
    if not raw_text:
        return raw_data

    # --- Type 0: Deep Explanation → {content: str, keyPoints: list[str]} ---
    if method_type == 0:
        if raw_data.get('content'):
            return raw_data
        return {
            'content': raw_text,
            'keyPoints': _extract_key_points(raw_text),
        }

    # --- Type 1: Step by Step → {steps: [{step, title, content}]} ---
    if method_type == 1:
        if raw_data.get('steps'):
            return raw_data
        return {'steps': _extract_steps(raw_text)}

    # --- Type 2: Interactive Theory → {concept, examples, interactiveQuestion} ---
    if method_type == 2:
        if raw_data.get('concept') or raw_data.get('examples'):
            return raw_data
        return {'concept': raw_text}

    # --- Type 3: Diagram → {diagram, description} ---
    if method_type == 3:
        if raw_data.get('diagram') or raw_data.get('description'):
            return raw_data
        return {'description': raw_text}

    # --- Type 4: Scenario → {scenario, requirements} ---
    if method_type == 4:
        if raw_data.get('scenario'):
            return raw_data
        return {'scenario': raw_text}

    # --- Type 6: Flashcards → {cards: [{front, back}]} ---
    if method_type == 6:
        if raw_data.get('cards'):
            return raw_data
        return {'cards': _extract_flashcards(raw_text, title)}

    # --- Type 7: Drag & Drop → {items, categories} ---
    if method_type == 7:
        if raw_data.get('items'):
            return raw_data
        items, cats = _extract_drag_drop(raw_text)
        return {'items': items, 'categories': cats}

    # --- Type 8: Cloze → {blanks, codeTemplate} ---
    if method_type == 8:
        if raw_data.get('blanks'):
            return raw_data
        return {'blanks': _extract_cloze_blanks(raw_text)}

    # --- Type 9: Free Text → {question, hints} ---
    if method_type == 9:
        if raw_data.get('question'):
            return raw_data
        return {'question': raw_text}

    # --- Type 10: Multiple Choice → {questions: [{question, options, correctAnswers}]} ---
    if method_type == 10:
        if raw_data.get('questions'):
            return raw_data
        return {'questions': _extract_mc_questions(raw_text)}

    # --- Type 11: Multi-Step → {task, steps} ---
    if method_type == 11:
        if raw_data.get('steps'):
            return raw_data
        return {'task': title, 'description': raw_text}

    # All other types: return as-is
    return raw_data


def _extract_key_points(text: str) -> list:
    """Extract bullet points or numbered items from markdown text."""
    import re
    points = []
    for line in text.split('\n'):
        line = line.strip()
        m = re.match(r'^[-*]\s+(.+)$', line)
        if m:
            point = re.sub(r'\*\*(.+?)\*\*', r'\1', m.group(1)).strip().rstrip(':')
            if 10 < len(point) < 200:
                points.append(point)
    return points[:8]


def _extract_steps(text: str) -> list:
    """Extract numbered steps from markdown."""
    import re
    steps = []
    sections = re.split(r'\n##\s+', text)
    for i, sec in enumerate(sections[1:], 1):
        lines = sec.strip().split('\n')
        step_title = lines[0].strip()
        step_content = '\n'.join(lines[1:]).strip()
        steps.append({'step': i, 'title': step_title, 'content': step_content})
    if not steps:
        # Fallback: split by numbered lines
        for m in re.finditer(r'(\d+)\.\s+\*?\*?(.+?)\*?\*?\s*\n(.*?)(?=\n\d+\.|$)', text, re.DOTALL):
            steps.append({
                'step': int(m.group(1)),
                'title': m.group(2).strip(),
                'content': m.group(3).strip()
            })
    return steps or [{'step': 1, 'title': 'Inhalt', 'content': text}]


def _extract_flashcards(text: str, title: str) -> list:
    """Extract flashcard-like Q&A pairs from markdown headings/sections."""
    import re
    cards = []
    # Try heading-based extraction
    sections = re.split(r'\n##\s+', text)
    for sec in sections[1:]:
        lines = sec.strip().split('\n')
        heading = lines[0].strip()
        body = '\n'.join(lines[1:]).strip()
        if heading and body:
            # Use heading as question, first paragraph as answer
            answer = body.split('\n\n')[0].strip()
            if answer:
                cards.append({'front': heading, 'back': answer[:300]})

    # Fallback: use bullet points as Q&A
    if not cards:
        for m in re.finditer(r'\*\*(.+?)\*\*[:\s]+(.+?)(?=\n|$)', text):
            cards.append({'front': m.group(1).strip(), 'back': m.group(2).strip()})

    # Last resort: split into chunks
    if not cards:
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip() and len(p.strip()) > 20]
        for i in range(0, min(len(paragraphs), 10), 2):
            front = paragraphs[i][:150]
            back = paragraphs[i + 1][:300] if i + 1 < len(paragraphs) else front
            cards.append({'front': front, 'back': back})

    return cards[:20]


def _extract_drag_drop(text: str) -> tuple:
    """Extract drag-drop items from markdown."""
    import re
    items = []
    categories = set()
    sections = re.split(r'\n##\s+', text)
    for sec in sections[1:]:
        lines = sec.strip().split('\n')
        cat = lines[0].strip()
        categories.add(cat)
        for line in lines[1:]:
            m = re.match(r'^[-*]\s+(.+)$', line.strip())
            if m:
                items.append({'label': m.group(1).strip(), 'correctCategory': cat})
    cat_list = sorted(categories) if categories else ['Kategorie A', 'Kategorie B']
    if not items:
        items = [{'label': 'Element', 'correctCategory': cat_list[0]}]
    return items, cat_list


def _extract_cloze_blanks(text: str) -> list:
    """Create cloze blanks from important terms in the text."""
    import re
    blanks = []
    for i, m in enumerate(re.finditer(r'\*\*(.+?)\*\*', text)):
        term = m.group(1).strip()
        if 2 < len(term) < 50:
            blanks.append({'position': i, 'answer': term, 'hint': f'Tipp: {term[0]}...'})
        if len(blanks) >= 8:
            break
    return blanks


def _extract_mc_questions(text: str) -> list:
    """Extract multiple choice questions from markdown."""
    questions = []
    # Simple heuristic: use headings as questions with bullets as options
    import re
    sections = re.split(r'\n##\s+', text)
    for sec in sections[1:]:
        lines = sec.strip().split('\n')
        q_text = lines[0].strip()
        options = []
        for line in lines[1:]:
            m = re.match(r'^[-*]\s+(.+)$', line.strip())
            if m:
                options.append(m.group(1).strip())
        if options:
            questions.append({
                'question': q_text,
                'options': options[:4],
                'correctAnswers': [options[0]] if options else [],
            })
    return questions[:10]


def _skill_to_lesson_type(skill_code: str) -> str:
    """Map a skill code to the appropriate lesson_type for the DB."""
    mapping = {
        'generate_theory_sheet': 'text',
        'generate_deep_explanation': 'text',
        'generate_step_by_step': 'text',
        'generate_interactive_theory': 'text',
        'generate_diagram': 'text',
        'generate_example_scenario': 'text',
        'generate_summary': 'text',
        'generate_oral_explanation': 'text',
        'generate_flashcards': 'quiz',
        'generate_drag_and_drop': 'quiz',
        'generate_cloze_test': 'quiz',
        'generate_true_false': 'quiz',
        'generate_quiz': 'quiz',
        'generate_free_text': 'quiz',
        'generate_ihk_tasks': 'quiz',
        'generate_multi_step': 'quiz',
        'generate_math_interactive': 'quiz',
        'generate_comprehension_check': 'quiz',
        'generate_chapter_exam': 'quiz',
        'generate_timed_challenge': 'quiz',
        'generate_whiteboard': 'assignment',
        'generate_hands_on_lab': 'assignment',
    }
    return mapping.get(skill_code, 'text')
