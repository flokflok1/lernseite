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
    def set_plan_status(
        plan_id: str, new_status: str, required_current: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Transition plan status with optional current-status guard."""
        plan = ContentPlanRepository.find_by_id(plan_id)
        if not plan:
            return None
        if required_current and plan['status'] != required_current:
            raise ValueError(
                f"Plan must be '{required_current}' to transition to '{new_status}' "
                f"(current: {plan['status']})"
            )
        return ContentPlanRepository.update_status(plan_id, new_status)

    @staticmethod
    def execute_plan(
        plan_id: str, user_id: str
    ) -> Dict[str, Any]:
        """
        Start async execution of an approved plan.

        Validates the plan, sets status to 'executing', and launches
        a background thread. Returns immediately with 'executing' status.
        The frontend polls GET /plans/<id> for progress.
        """
        plan = ContentPlanRepository.find_by_id(plan_id)
        if not plan:
            raise ValueError(f'Plan not found: {plan_id}')
        if plan['status'] not in ('approved', 'paused'):
            raise ValueError(f"Plan must be approved to execute (current: {plan['status']})")

        ContentPlanRepository.update_status(plan_id, 'executing')

        # Launch background execution
        import threading
        thread = threading.Thread(
            target=_execute_plan_background,
            args=(plan_id, plan, user_id),
            daemon=True,
        )
        thread.start()

        return {
            'plan_id': plan_id,
            'status': 'executing',
        }


# ---------------------------------------------------------------------------
# Background execution
# ---------------------------------------------------------------------------

def _execute_plan_background(plan_id: str, plan: Dict[str, Any], user_id: str) -> None:
    """
    Execute all plan steps in a background thread.

    Updates each step's status in plan_data as it completes (Bug 3 fix).
    Runs outside the Flask request context, so uses its own app context.
    """
    from flask import current_app
    from app.application.services.ai.skill_service import SkillExecutionService

    # Import the app factory to get a fresh app context
    try:
        from app import create_app
        app = create_app()
    except Exception:
        # Fallback: try to use current_app if available
        app = current_app._get_current_object()

    with app.app_context():
        try:
            plan_data = plan['plan_data']
            if isinstance(plan_data, str):
                plan_data = json.loads(plan_data)

            total_tokens = 0
            has_failures = False

            for phase_idx, phase in enumerate(plan_data.get('phases', [])):
                for step_idx, step in enumerate(phase.get('steps', [])):
                    step_id = step.get('step_id', f'{phase_idx}-{step_idx}')

                    # Mark step as running
                    step['status'] = 'running'
                    ContentPlanRepository.update_plan_data(plan_id, plan_data)

                    try:
                        result = SkillExecutionService.execute(
                            skill_code=step['skill_code'],
                            course_id=plan['course_id'],
                            user_id=user_id,
                            target_type=step.get('target_type'),
                            target_id=step.get('target_id'),
                            parameters=step.get('parameters'),
                            plan_id=plan_id,
                        )
                        step['status'] = 'completed'
                        tokens = result.get('tokens_input', 0) + result.get('tokens_output', 0)
                        total_tokens += tokens
                    except Exception as e:
                        logger.error(f"Step {step_id} failed: {e}")
                        step['status'] = 'failed'
                        has_failures = True

                    # Persist step status + running token count
                    ContentPlanRepository.update_plan_data(plan_id, plan_data)
                    ContentPlanRepository.update_token_count(plan_id, total_tokens)

            final_status = 'completed' if not has_failures else 'paused'
            ContentPlanRepository.update_status(plan_id, final_status)
            logger.info(f"Plan {plan_id} execution finished: {final_status}, {total_tokens} tokens")

        except Exception as e:
            logger.error(f"Plan {plan_id} background execution crashed: {e}")
            ContentPlanRepository.update_status(plan_id, 'paused')


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _get_active_sf_codes() -> set:
    """Return set of active system feature codes from DB."""
    from app.infrastructure.persistence.repositories.features.system_features_repository import (
        SystemFeaturesRepository,
    )
    try:
        active = SystemFeaturesRepository.find_active()
        return {sf.get('code', '') for sf in active}
    except Exception as exc:
        logger.warning("Could not load active system features: %s", exc)
        return set()


# Delegate to domain layer — single source of truth for skill catalog prompt
from app.domain.ai.configuration.skill_catalog_prompt import (
    build_skill_catalog_prompt as _get_skill_catalog_prompt,
)


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
