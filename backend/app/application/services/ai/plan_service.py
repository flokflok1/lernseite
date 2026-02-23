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

        Uses existing CourseFileRepository to load ai_extracted_text,
        then generates a structural plan via AI.
        """
        from app.infrastructure.persistence.repositories.courses.files import CourseFileRepository

        # Load extracted text
        file_data = CourseFileRepository.get_by_id(file_id)
        if not file_data:
            raise ValueError(f'File not found: {file_id}')

        extracted_text = file_data.get('ai_extracted_text', '')
        if not extracted_text:
            # Try PDF extraction
            try:
                from app.application.services.content.pdf.bridge import PDFService
                extracted_text = PDFService.extract_text(file_data.get('file_path', ''))
                CourseFileRepository.mark_ai_processed(file_id, extracted_text)
            except Exception as e:
                logger.error(f"PDF extraction failed: {e}")
                raise ValueError('Could not extract text from file')

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


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _load_course_context(
    course_id: str, scope: str, scope_id: Optional[str]
) -> Dict[str, Any]:
    """Load course structure for AI plan generation."""
    from app.infrastructure.persistence.repositories.courses.core import CourseRepository

    course = CourseRepository.get_by_id(course_id)
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

    adapter = AIAdapter(provider=provider, model=model)
    messages = [
        {
            'role': 'system',
            'content': (
                'You are an expert educational content planner. '
                'Generate a structured content plan as JSON. '
                'The plan should have phases, each with steps. '
                'Each step should specify a skill_code from the available skills.'
            ),
        },
        {
            'role': 'user',
            'content': (
                f"Create a content plan for the course: {context.get('course_title', 'Untitled')}\n"
                f"Scope: {context.get('scope', 'course')}\n"
                f"Existing chapters: {json.dumps(context.get('chapters', []))}\n\n"
                'Return JSON with format: {"phases": [{"phase_id": "...", "order": 1, '
                '"title": "...", "steps": [{"step_id": "...", "order": 1, '
                '"skill_code": "generate_...", "target_type": "lesson", '
                '"target_id": "...", "target_title": "...", "parameters": {}, '
                '"status": "pending"}]}]}'
            ),
        },
    ]

    try:
        response = adapter.send_messages(messages=messages, max_tokens=4000)
        output = response.get('output_text', '{}')
        plan_data = json.loads(output)
        if 'phases' not in plan_data:
            plan_data = {'phases': []}
        return plan_data
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

    # Truncate text to avoid token limits
    max_chars = 15000
    text_snippet = extracted_text[:max_chars]

    adapter = AIAdapter(provider=provider, model=model)
    messages = [
        {
            'role': 'system',
            'content': (
                'You are an expert educational content planner. '
                'Analyze the provided text and create a structured course plan as JSON. '
                'Suggest chapters, lessons, and appropriate learning methods.'
            ),
        },
        {
            'role': 'user',
            'content': (
                f"Analyze this educational material and create a content plan:\n\n"
                f"{text_snippet}\n\n"
                'Return JSON with format: {"phases": [{"phase_id": "...", "order": 1, '
                '"title": "...", "steps": [{"step_id": "...", "order": 1, '
                '"skill_code": "generate_...", "target_type": "lesson", '
                '"target_id": "...", "target_title": "...", "parameters": {}, '
                '"status": "pending"}]}]}'
            ),
        },
    ]

    try:
        response = adapter.send_messages(messages=messages, max_tokens=4000)
        output = response.get('output_text', '{}')
        plan_data = json.loads(output)
        if 'phases' not in plan_data:
            plan_data = {'phases': []}
        return plan_data
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
