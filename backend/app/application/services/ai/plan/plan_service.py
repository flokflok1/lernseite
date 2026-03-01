"""
Plan Service

Orchestrates AI content plan creation, approval, and execution
for the Unified AI Editor.

DDD: Application layer — depends on Domain ports and Infrastructure
repositories, never calls AI adapters directly.
"""

from typing import Dict, Any, Optional, List
import logging

from app.core.bootstrap.container import get_plan_generator
from app.infrastructure.persistence.repositories.ai.content_plans import ContentPlanRepository

logger = logging.getLogger(__name__)


class PlanService:
    """Orchestrates content plan lifecycle.

    Uses PlanGeneratorPort (domain contract) for all AI calls.
    """

    @staticmethod
    def create_plan(
        course_id: str,
        user_id: str,
        scope: str = 'course',
        scope_id: Optional[str] = None,
        language: str = 'de',
    ) -> Dict[str, Any]:
        """Create a new content plan via AI analysis."""
        course_context = _load_course_context(course_id, scope, scope_id)

        active_sfs = _get_active_sf_codes()
        skill_catalog = _get_skill_catalog_prompt(active_sf_codes=active_sfs)

        generator = get_plan_generator()
        plan_data = generator.generate_flat_plan(
            course_title=course_context.get('course_title', 'Untitled'),
            scope=scope,
            chapters=course_context.get('chapters', []),
            language=language,
            skill_catalog_section=skill_catalog,
        )

        estimated_tokens = estimate_plan_tokens(plan_data)

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
        language: str = 'de',
    ) -> Dict[str, Any]:
        """Create a plan from an uploaded file's extracted text."""
        from app.infrastructure.persistence.repositories.authoring.files import AuthoringFilesRepository

        file_data = AuthoringFilesRepository.get_file_by_id(file_id)
        if not file_data:
            raise ValueError(f'File not found: {file_id}')

        extracted_text = file_data.get('extracted_text', '')
        if not extracted_text:
            raise ValueError('File has no extracted text. Please wait for processing to complete.')

        active_sfs = _get_active_sf_codes()
        skill_catalog = _get_skill_catalog_prompt(active_sf_codes=active_sfs)

        generator = get_plan_generator()
        plan_data = generator.generate_plan_from_text(
            extracted_text=extracted_text,
            language=language,
            skill_catalog_section=skill_catalog,
        )
        estimated_tokens = estimate_plan_tokens(plan_data)

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
    def delete_plan(plan_id: str) -> bool:
        """Delete a plan and its generation logs. Returns True if deleted."""
        return ContentPlanRepository.delete(plan_id)

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
        """Start async execution of an approved plan.

        Validates the plan, sets status to 'executing', and launches
        a background thread. Returns immediately with 'executing' status.
        """
        plan = ContentPlanRepository.find_by_id(plan_id)
        if not plan:
            raise ValueError(f'Plan not found: {plan_id}')
        if plan['status'] not in ('approved', 'paused'):
            raise ValueError(f"Plan must be approved to execute (current: {plan['status']})")

        ContentPlanRepository.update_status(plan_id, 'executing')

        from app.application.services.ai.plan.plan_execution import execute_plan_background
        import threading
        thread = threading.Thread(
            target=execute_plan_background,
            args=(plan_id, plan, user_id),
            daemon=True,
        )
        thread.start()

        return {
            'plan_id': plan_id,
            'status': 'executing',
        }


# ---------------------------------------------------------------------------
# Shared helpers (used by plan_service_part2.py too)
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
    from app.infrastructure.persistence.repositories.courses.management.crud import CourseRepositoryCRUD

    course = CourseRepositoryCRUD.get_by_id_simple(course_id)
    context: Dict[str, Any] = {
        'course_id': course_id,
        'course_title': course.get('title', '') if course else '',
        'scope': scope,
        'scope_id': scope_id,
    }

    try:
        from app.infrastructure.persistence.repositories.courses.content.chapters import ChapterRepository
        chapters = ChapterRepository.get_by_course(course_id)
        context['chapters'] = [
            {'chapter_id': ch['chapter_id'], 'title': ch.get('title', '')}
            for ch in (chapters or [])
        ]
    except Exception:
        context['chapters'] = []

    return context


def estimate_plan_tokens(plan_data: Dict[str, Any]) -> int:
    """Estimate total tokens for a plan."""
    from app.domain.ai.configuration.skills import get_skill

    total = 0
    for phase in plan_data.get('phases', []):
        for step in phase.get('steps', []):
            skill = get_skill(step.get('skill_code', ''))
            total += skill.estimated_tokens if skill else 2000
    return total
