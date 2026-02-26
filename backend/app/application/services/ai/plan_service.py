"""
Plan Service

Orchestrates AI content plan creation, approval, and execution
for the Unified AI Editor.
"""

from typing import Dict, Any, Optional, List
import json
import logging
import uuid

from app.infrastructure.persistence.repositories.ai.content_plans import ContentPlanRepository
from app.infrastructure.persistence.repositories.ai.generation_log import GenerationLogRepository
from app.infrastructure.ai.adapter import AIAdapter
from app.infrastructure.persistence.repositories.ai_models import AIModelsRepository

logger = logging.getLogger(__name__)


class PlanService:
    """Orchestrates content plan lifecycle."""

    @staticmethod
    def create_plan(
        course_id: str,
        user_id: str,
        scope: str = 'course',
        scope_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new content plan via AI analysis.

        Loads course structure, sends to AI for plan generation,
        returns structured ContentPlan.
        """
        # Load course context for AI
        course_context = _load_course_context(course_id, scope, scope_id)

        # Generate plan via AI
        plan_data = _generate_plan_via_ai(course_context)

        # Estimate tokens
        estimated_tokens = _estimate_plan_tokens(plan_data)

        # Persist
        plan = ContentPlanRepository.create({
            'course_id': course_id,
            'scope': scope,
            'scope_id': scope_id,
            'user_id': user_id,
            'status': 'draft',
            'plan_data': plan_data,
            'estimated_tokens': estimated_tokens,
        })

        return plan

    @staticmethod
    def create_plan_from_file(
        course_id: str,
        file_id: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Create a plan from an uploaded file's extracted text.

        Uses AuthoringFilesRepository to load extracted_text from
        the multi-file upload system.
        """
        from app.infrastructure.persistence.repositories.authoring.files import AuthoringFilesRepository

        # Load extracted text from authoring files
        file_data = AuthoringFilesRepository.get_file_by_id(file_id)
        if not file_data:
            raise ValueError(f'File not found: {file_id}')

        extracted_text = file_data.get('extracted_text', '')
        if not extracted_text:
            raise ValueError('File has no extracted text. Please wait for processing to complete.')

        # Generate plan from extracted text
        plan_data = _generate_plan_from_text(extracted_text, course_id)
        estimated_tokens = _estimate_plan_tokens(plan_data)

        plan = ContentPlanRepository.create({
            'course_id': course_id,
            'scope': 'course',
            'scope_id': None,
            'user_id': user_id,
            'status': 'draft',
            'plan_data': plan_data,
            'estimated_tokens': estimated_tokens,
        })

        return plan

    @staticmethod
    def get_plan(plan_id: str) -> Optional[Dict[str, Any]]:
        """Load a plan by ID."""
        return ContentPlanRepository.find_by_id(plan_id)

    @staticmethod
    def list_plans(
        course_id: str, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List plans for a course."""
        return ContentPlanRepository.find_by_course(course_id, limit, offset)

    @staticmethod
    def update_plan(
        plan_id: str, plan_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update plan data (reorder steps, change parameters)."""
        return ContentPlanRepository.update_plan_data(plan_id, plan_data)

    @staticmethod
    def approve_plan(plan_id: str) -> Optional[Dict[str, Any]]:
        """Mark a plan as approved for execution."""
        return ContentPlanRepository.update_status(plan_id, 'approved')

    @staticmethod
    def execute_plan(
        plan_id: str, user_id: str
    ) -> Dict[str, Any]:
        """
        Execute an approved plan by running all steps via SkillExecutionService.
        """
        from app.application.services.ai.skill_service import SkillExecutionService

        plan = ContentPlanRepository.find_by_id(plan_id)
        if not plan:
            raise ValueError(f'Plan not found: {plan_id}')
        if plan['status'] not in ('approved', 'paused'):
            raise ValueError(f"Plan must be approved to execute (current: {plan['status']})")

        ContentPlanRepository.update_status(plan_id, 'executing')

        # Flatten phases into steps
        plan_data = plan['plan_data']
        if isinstance(plan_data, str):
            plan_data = json.loads(plan_data)

        steps = []
        for phase in plan_data.get('phases', []):
            for step in phase.get('steps', []):
                steps.append({
                    'skill_code': step['skill_code'],
                    'course_id': plan['course_id'],
                    'target_type': step.get('target_type'),
                    'target_id': step.get('target_id'),
                    'parameters': step.get('parameters', {}),
                })

        # Execute batch
        results = SkillExecutionService.execute_batch(plan_id, steps, user_id)

        # Update plan status and tokens
        total_tokens = sum(
            r.get('tokens_input', 0) + r.get('tokens_output', 0)
            for r in results
        )
        ContentPlanRepository.update_token_count(plan_id, total_tokens)

        failed = any(r.get('status') == 'failed' for r in results)
        final_status = 'completed' if not failed else 'paused'
        ContentPlanRepository.update_status(plan_id, final_status)

        return {
            'plan_id': plan_id,
            'status': final_status,
            'results': results,
            'total_tokens': total_tokens,
        }

    # -- Phased Wizard Methods (Plan Wizard redesign) -----------------------

    @staticmethod
    def create_phased_plan(
        course_id: str,
        user_id: str,
        topic: str = '',
        file_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a plan and run Phase 1 (course definition)."""
        from app.infrastructure.ai.plan_generator import PlanGeneratorAdapter
        from app.infrastructure.persistence.repositories.authoring.files import (
            AuthoringFilesRepository,
        )

        file_text = _collect_file_text(file_ids, AuthoringFilesRepository)

        generator = PlanGeneratorAdapter()
        course_meta = generator.generate_course_definition(
            topic=topic, file_text=file_text,
        )

        plan = ContentPlanRepository.create({
            'course_id': course_id,
            'user_id': user_id,
            'current_phase': 1,
            'status': 'draft',
            'course_meta': course_meta,
            'chapters': [],
            'plan_data': {},
            'chat_history': [],
        })
        return plan

    @staticmethod
    def advance_to_phase2(plan_id: str) -> Dict[str, Any]:
        """Load plan and run Phase 2 (chapter structure generation)."""
        from app.infrastructure.ai.plan_generator import PlanGeneratorAdapter

        plan = _load_plan_or_raise(plan_id)
        course_meta = _parse_jsonb_field(plan, 'course_meta', {})

        generator = PlanGeneratorAdapter()
        result = generator.generate_chapter_structure(course_meta)

        updated = ContentPlanRepository.update_phase(
            plan_id, 2, {'chapters': result.get('chapters', [])},
        )
        return updated

    @staticmethod
    def advance_to_phase3(plan_id: str) -> Dict[str, Any]:
        """Load plan and run Phase 3 (detailed content plan)."""
        from app.infrastructure.ai.plan_generator import PlanGeneratorAdapter

        plan = _load_plan_or_raise(plan_id)
        course_meta = _parse_jsonb_field(plan, 'course_meta', {})
        chapters = _parse_jsonb_field(plan, 'chapters', [])

        active_sf_codes = _get_active_sf_codes()

        generator = PlanGeneratorAdapter()
        result = generator.generate_content_plan(
            course_meta, chapters, active_sf_codes,
        )

        estimated_tokens = _estimate_plan_tokens(result)

        updated = ContentPlanRepository.update_phase(
            plan_id, 3, {'plan_data': result},
        )
        if updated:
            updated['estimated_tokens'] = estimated_tokens
        return updated

    @staticmethod
    def chat_about_plan(
        plan_id: str, message: str
    ) -> Dict[str, Any]:
        """Refine the current plan phase via conversational chat."""
        from app.infrastructure.ai.plan_generator import PlanGeneratorAdapter

        plan = _load_plan_or_raise(plan_id)
        current_phase = plan.get('current_phase', 1)

        plan_data = {
            'course_meta': _parse_jsonb_field(plan, 'course_meta', {}),
            'chapters': _parse_jsonb_field(plan, 'chapters', []),
            'phases': _parse_jsonb_field(plan, 'plan_data', {}).get('phases', []),
        }

        generator = PlanGeneratorAdapter()
        result = generator.chat_about_plan(plan_data, message, current_phase)

        ContentPlanRepository.append_chat_message(
            plan_id, {'role': 'user', 'content': message},
        )
        assistant_msg = result.get('response', '')
        ContentPlanRepository.append_chat_message(
            plan_id, {'role': 'assistant', 'content': assistant_msg},
        )

        plan_patch = result.get('updated_data')
        if plan_patch:
            ContentPlanRepository.update_phase(plan_id, current_phase, plan_patch)

        updated_plan = ContentPlanRepository.find_by_id(plan_id)
        return {
            'assistant_message': assistant_msg,
            'plan_patch': plan_patch,
            'plan': updated_plan,
        }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _load_plan_or_raise(plan_id: str) -> Dict[str, Any]:
    """Load a plan by ID or raise ValueError."""
    plan = ContentPlanRepository.find_by_id(plan_id)
    if not plan:
        raise ValueError(f'Plan not found: {plan_id}')
    return plan


def _parse_jsonb_field(plan: Dict[str, Any], field: str, default: Any) -> Any:
    """Parse a JSONB field from a plan row, handling string or native types."""
    value = plan.get(field, default)
    if isinstance(value, str):
        return json.loads(value) if value else default
    return value if value is not None else default


def _collect_file_text(
    file_ids: Optional[List[str]], files_repo: Any,
) -> Optional[str]:
    """Load and concatenate extracted text from authoring files."""
    if not file_ids:
        return None
    texts = []
    for fid in file_ids:
        file_data = files_repo.get_file_by_id(fid)
        if file_data and file_data.get('extracted_text'):
            texts.append(file_data['extracted_text'])
    return '\n\n---\n\n'.join(texts) if texts else None

def _get_active_sf_codes() -> set:
    """Return set of active system feature codes from DB."""
    from app.infrastructure.persistence.repositories.features.system_features_repository import (
        SystemFeaturesRepository,
    )
    try:
        active = SystemFeaturesRepository.find_active()
        return {sf.get('code', '') for sf in active}
    except Exception:
        return set()


# Mapping: system_feature_code → (skill_code, description for prompt)
_SF_TO_SKILL = {
    'whiteboard_engine': ('generate_whiteboard', 'Drawing/sketching task (diagrams, topologies, flowcharts)'),
    'it_sandbox': ('generate_hands_on_lab', 'Practical IT exercise with code/terminal'),
    'timer_wrapper': ('generate_timed_challenge', 'Time-limited quiz/challenge'),
    'comprehension_checker': ('generate_comprehension_check', 'Quick understanding verification'),
    'speech_to_text': ('generate_oral_explanation', 'Oral explanation task (speech-to-text)'),
    'chapter_completion_system': ('generate_chapter_exam', 'End-of-chapter exam with mixed questions'),
}

# TrueFalse has no SF dependency — always available
_ALWAYS_AVAILABLE_EXTENSIONS = {
    'generate_true_false': 'True/false statements for knowledge testing',
}


def _get_skill_catalog_prompt(active_sf_codes: Optional[set] = None) -> str:
    """Build a description of available skills for AI plan generation prompts."""
    parts = [
        'You MUST use ONLY the following skill_code values. Do NOT invent new ones.\n\n'
        'EXPLANATORY SKILLS (Group A — teach/explain concepts):\n'
        '  - generate_deep_explanation: In-depth explanation of a topic\n'
        '  - generate_step_by_step: Step-by-step walkthrough\n'
        '  - generate_interactive_theory: Interactive theory with questions\n'
        '  - generate_diagram: Visual diagram/visualization\n'
        '  - generate_example_scenario: Practical example/scenario\n\n'
        'PRACTICE SKILLS (Group B — hands-on practice):\n'
        '  - generate_flashcards: Flashcard sets for memorization\n'
        '  - generate_drag_and_drop: Drag & drop exercises\n'
        '  - generate_cloze_test: Fill-in-the-blank exercises\n'
        '  - generate_math_interactive: Math/calculation exercises\n\n'
        'ASSESSMENT SKILLS (Group C — test knowledge):\n'
        '  - generate_free_text: Open-ended text questions\n'
        '  - generate_ihk_tasks: Exam-style tasks (IHK format)\n'
        '  - generate_multi_step: Multi-step practical tasks\n\n'
        'UTILITY SKILLS:\n'
        '  - generate_theory_sheet: Theory summary sheet for a lesson\n'
        '  - generate_quiz: Multiple-choice quiz\n'
        '  - generate_summary: Chapter summary\n'
        '  - review_content: Review existing content for quality\n\n'
    ]

    # Build extension skills block based on active system features
    extension_lines = []
    if active_sf_codes is not None:
        for sf_code, (skill_code, desc) in _SF_TO_SKILL.items():
            if sf_code in active_sf_codes:
                extension_lines.append(f'  - {skill_code}: {desc}')
    else:
        # No SF info available — include all SF-gated extensions
        for _sf_code, (skill_code, desc) in _SF_TO_SKILL.items():
            extension_lines.append(f'  - {skill_code}: {desc}')

    # Always-available extensions
    for skill_code, desc in _ALWAYS_AVAILABLE_EXTENSIONS.items():
        extension_lines.append(f'  - {skill_code}: {desc}')

    if extension_lines:
        parts.append(
            'EXTENSION SKILLS (advanced task types):\n'
            + '\n'.join(extension_lines) + '\n\n'
        )

    # Didactic guidelines
    parts.append(
        'DIDACTIC GUIDELINES — when to use which skill:\n'
        '- Visual/spatial topics (diagrams, topologies, architecture) → generate_diagram + generate_whiteboard\n'
        '- Calculation/formulas (subnetting, math, conversion) → generate_math_interactive + generate_step_by_step\n'
        '- Terminology/definitions → generate_flashcards + generate_cloze_test + generate_true_false\n'
        '- Configuration/CLI commands → generate_hands_on_lab + generate_example_scenario\n'
        '- Quick knowledge check between topics → generate_comprehension_check\n'
        '- End of each major chapter → generate_chapter_exam\n'
        '- Theory introduction → generate_deep_explanation + generate_theory_sheet\n'
        '- Complex multi-step processes → generate_step_by_step + generate_multi_step\n\n'
    )

    parts.append(
        'PLAN STRUCTURE RULES:\n'
        '- Organize phases by chapter/topic from the material\n'
        '- Each phase = one chapter/major topic\n'
        '- For EACH chapter, include a MIX of learning methods:\n'
        '  1. At least one explanatory skill (theory)\n'
        '  2. At least one practice skill (exercises)\n'
        '  3. Optionally an assessment skill (test)\n'
        '  4. Use extension skills where didactically appropriate\n'
        '- Cover ALL content from the material — do not skip sections\n'
        '- Each step targets one lesson (target_type: "lesson")\n'
        '- Set target_title to a descriptive lesson name\n'
    )

    return ''.join(parts)


def _load_course_context(
    course_id: str, scope: str, scope_id: Optional[str]
) -> Dict[str, Any]:
    """Load course structure for AI plan generation."""
    from app.infrastructure.persistence.repositories.courses.crud import CourseRepositoryCRUD

    course = CourseRepositoryCRUD.get_by_id_simple(course_id)
    context = {
        'course_id': course_id,
        'course_title': course.get('title', '') if course else '',
        'scope': scope,
        'scope_id': scope_id,
    }

    # Load chapters and lessons
    try:
        from app.infrastructure.persistence.repositories.courses.chapters import ChapterRepository
        chapters = ChapterRepository.get_by_course(course_id)
        context['chapters'] = [
            {'chapter_id': ch['chapter_id'], 'title': ch.get('title', '')}
            for ch in (chapters or [])
        ]
    except Exception:
        context['chapters'] = []

    return context


def _generate_plan_via_ai(context: Dict[str, Any]) -> Dict[str, Any]:
    """Call AI to generate a content plan."""
    default_model = AIModelsRepository.get_default_model()
    provider = default_model.get('provider_name', 'openai') if default_model else 'openai'
    model = default_model.get('model_name', 'gpt-4o-mini') if default_model else 'gpt-4o-mini'

    active_sfs = _get_active_sf_codes()
    skill_catalog = _get_skill_catalog_prompt(active_sf_codes=active_sfs)

    adapter = AIAdapter(provider=provider, model=model)
    messages = [
        {
            'role': 'system',
            'content': (
                'You are an expert educational content planner. '
                'Generate a structured content plan as JSON.\n\n'
                f'{skill_catalog}'
            ),
        },
        {
            'role': 'user',
            'content': (
                f"Create a content plan for the course: {context.get('course_title', 'Untitled')}\n"
                f"Scope: {context.get('scope', 'course')}\n"
                f"Existing chapters: {json.dumps(context.get('chapters', []))}\n\n"
                'Return ONLY valid JSON (no markdown fences) with format:\n'
                '{"phases": [{"phase_id": "uuid", "order": 1, '
                '"title": "Chapter Name", "steps": [{"step_id": "uuid", "order": 1, '
                '"skill_code": "generate_deep_explanation", "target_type": "lesson", '
                '"target_id": null, "target_title": "Lesson Title", '
                '"parameters": {"language": "de"}, '
                '"status": "pending"}]}]}'
            ),
        },
    ]

    try:
        response = adapter.send_messages(messages=messages, max_tokens=4000)
        output = response.get('output_text', '').strip()
        # Strip markdown code fences if present
        if output.startswith('```'):
            lines = output.split('\n')
            # Remove first line (```json or ```) and last line (```)
            lines = [l for l in lines if not l.strip().startswith('```')]
            output = '\n'.join(lines).strip()
        if not output:
            logger.warning("AI returned empty output for plan generation")
            return _create_default_plan(context)
        plan_data = json.loads(output)
        if 'phases' not in plan_data:
            plan_data = {'phases': []}
        return plan_data
    except json.JSONDecodeError as e:
        logger.error(f"AI plan generation - invalid JSON: {e}, output: {output[:200]}")
        return _create_default_plan(context)
    except Exception as e:
        logger.error(f"AI plan generation failed: {e}")
        return _create_default_plan(context)


def _generate_plan_from_text(
    extracted_text: str, course_id: str
) -> Dict[str, Any]:
    """Generate a structural plan from uploaded file text."""
    default_model = AIModelsRepository.get_default_model()
    provider = default_model.get('provider_name', 'openai') if default_model else 'openai'
    model = default_model.get('model_name', 'gpt-4o-mini') if default_model else 'gpt-4o-mini'

    active_sfs = _get_active_sf_codes()
    skill_catalog = _get_skill_catalog_prompt(active_sf_codes=active_sfs)

    adapter = AIAdapter(provider=provider, model=model)
    messages = [
        {
            'role': 'system',
            'content': (
                'You are an expert educational content planner. '
                'Analyze educational material and create a comprehensive structured course plan as JSON.\n\n'
                f'{skill_catalog}'
            ),
        },
        {
            'role': 'user',
            'content': (
                f"Analyze this educational material and create a COMPLETE content plan "
                f"covering ALL chapters and topics:\n\n"
                f"{extracted_text}\n\n"
                'IMPORTANT: Cover the ENTIRE material. Each major topic/chapter = one phase.\n'
                'For each phase, include multiple steps with different learning methods '
                '(theory + practice + assessment).\n\n'
                'Return ONLY valid JSON (no markdown fences) with format:\n'
                '{"phases": [{"phase_id": "uuid", "order": 1, '
                '"title": "Chapter Name", "steps": [{"step_id": "uuid", "order": 1, '
                '"skill_code": "generate_deep_explanation", "target_type": "lesson", '
                '"target_id": null, "target_title": "Lesson Title", '
                '"parameters": {"language": "de"}, '
                '"status": "pending"}]}]}'
            ),
        },
    ]

    try:
        response = adapter.send_messages(messages=messages, max_tokens=8000)
        output = response.get('output_text', '').strip()
        if output.startswith('```'):
            lines = output.split('\n')
            lines = [l for l in lines if not l.strip().startswith('```')]
            output = '\n'.join(lines).strip()
        if not output:
            return {'phases': []}
        plan_data = json.loads(output)
        if 'phases' not in plan_data:
            plan_data = {'phases': []}
        return plan_data
    except json.JSONDecodeError as e:
        logger.error(f"AI plan from file - invalid JSON: {e}, output: {output[:200]}")
        return {'phases': []}
    except Exception as e:
        logger.error(f"AI plan from file failed: {e}")
        return {'phases': []}


def _create_default_plan(context: Dict[str, Any]) -> Dict[str, Any]:
    """Create a minimal default plan as fallback."""
    return {
        'phases': [
            {
                'phase_id': str(uuid.uuid4()),
                'order': 1,
                'title': 'Theory Generation',
                'steps': [
                    {
                        'step_id': str(uuid.uuid4()),
                        'order': 1,
                        'skill_code': 'generate_theory_sheet',
                        'target_type': 'lesson',
                        'target_id': None,
                        'target_title': context.get('course_title', 'Lesson'),
                        'parameters': {'language': 'de'},
                        'status': 'pending',
                    }
                ],
            }
        ]
    }


def _estimate_plan_tokens(plan_data: Dict[str, Any]) -> int:
    """Estimate total tokens for a plan."""
    from app.domain.ai.configuration.skills import get_skill

    total = 0
    for phase in plan_data.get('phases', []):
        for step in phase.get('steps', []):
            skill = get_skill(step.get('skill_code', ''))
            total += skill.estimated_tokens if skill else 2000
    return total
