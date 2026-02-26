"""
Plan Wizard Service

Phased wizard methods for the AI Editor Plan Wizard redesign.
Handles 3-phase plan creation: course definition, chapter structure,
and detailed content plan generation with chat-based refinement.

Split from plan_service.py to respect G01 (500 LOC limit).
"""

import json
import logging
from typing import Any

from app.domain.ai.configuration.skill_catalog_prompt import build_skill_catalog_prompt
from app.domain.ports.plan_generator import PlanGeneratorPort
from app.infrastructure.persistence.repositories.ai.content_plans import ContentPlanRepository
from app.application.services.ai.plan_service import (
    _get_active_sf_codes,
    _estimate_plan_tokens,
)

logger = logging.getLogger(__name__)


def _default_generator() -> PlanGeneratorPort:
    """Lazy-resolve the default PlanGeneratorPort implementation."""
    from app.infrastructure.ai.plan_generator import PlanGeneratorAdapter
    return PlanGeneratorAdapter()


class PlanWizardService:
    """Orchestrates phased plan wizard lifecycle.

    Depends on PlanGeneratorPort (domain contract).
    If no generator is injected, the default infrastructure adapter is used.
    """

    def __init__(self, generator: PlanGeneratorPort | None = None) -> None:
        self._generator = generator or _default_generator()

    def create_phased_plan(
        self,
        course_id: str,
        user_id: str,
        topic: str = '',
        file_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a plan and run Phase 1 (course definition)."""
        from app.infrastructure.persistence.repositories.authoring.files import (
            AuthoringFilesRepository,
        )

        file_text = _collect_file_text(file_ids, AuthoringFilesRepository)

        course_meta = self._generator.generate_course_definition(
            topic=topic, file_text=file_text,
        )

        plan = ContentPlanRepository.create({
            'course_id': course_id,
            'user_id': user_id,
            'scope': 'course',
            'current_phase': 1,
            'status': 'draft',
            'course_meta': course_meta,
            'chapters': [],
            'plan_data': {},
            'chat_history': [],
        })
        return plan

    def advance_to_phase2(self, plan_id: str) -> dict[str, Any]:
        """Load plan and run Phase 2 (chapter structure generation)."""
        plan = _load_plan_or_raise(plan_id)
        course_meta = _parse_jsonb_field(plan, 'course_meta', {})

        result = self._generator.generate_chapter_structure(course_meta)

        updated = ContentPlanRepository.update_phase(
            plan_id, 2, {'chapters': result.get('chapters', [])},
        )
        return updated

    def advance_to_phase3(self, plan_id: str) -> dict[str, Any]:
        """Load plan and run Phase 3 (detailed content plan)."""
        plan = _load_plan_or_raise(plan_id)
        course_meta = _parse_jsonb_field(plan, 'course_meta', {})
        chapters = _parse_jsonb_field(plan, 'chapters', [])

        active_sf_codes = _get_active_sf_codes()
        skill_catalog = build_skill_catalog_prompt(active_sf_codes)

        result = self._generator.generate_content_plan(
            course_meta, chapters, skill_catalog,
        )

        estimated_tokens = _estimate_plan_tokens(result)

        updated = ContentPlanRepository.update_phase(
            plan_id, 3, {'plan_data': result},
        )
        if updated:
            updated['estimated_tokens'] = estimated_tokens
        return updated

    def chat_about_plan(
        self, plan_id: str, message: str,
    ) -> dict[str, Any]:
        """Refine the current plan phase via conversational chat."""
        plan = _load_plan_or_raise(plan_id)
        current_phase = plan.get('current_phase', 1)

        plan_data = {
            'course_meta': _parse_jsonb_field(plan, 'course_meta', {}),
            'chapters': _parse_jsonb_field(plan, 'chapters', []),
            'phases': _parse_jsonb_field(plan, 'plan_data', {}).get('phases', []),
        }

        result = self._generator.chat_about_plan(plan_data, message, current_phase)

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
# Private helpers (wizard-specific)
# ---------------------------------------------------------------------------

def _load_plan_or_raise(plan_id: str) -> dict[str, Any]:
    """Load a plan by ID or raise ValueError."""
    plan = ContentPlanRepository.find_by_id(plan_id)
    if not plan:
        raise ValueError(f'Plan not found: {plan_id}')
    return plan


def _parse_jsonb_field(plan: dict[str, Any], field: str, default: Any) -> Any:
    """Parse a JSONB field from a plan row, handling string or native types."""
    value = plan.get(field, default)
    if isinstance(value, str):
        return json.loads(value) if value else default
    return value if value is not None else default


def _collect_file_text(
    file_ids: list[str] | None, files_repo: Any,
) -> str | None:
    """Load and concatenate extracted text from authoring files."""
    if not file_ids:
        return None
    texts = []
    for fid in file_ids:
        file_data = files_repo.get_file_by_id(fid)
        if file_data and file_data.get('extracted_text'):
            texts.append(file_data['extracted_text'])
    return '\n\n---\n\n'.join(texts) if texts else None


