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

from app.core.bootstrap.container import get_plan_generator
from app.domain.ai.configuration.skill_catalog_prompt import build_skill_catalog_prompt
from app.domain.ports.plan_generator import PlanGeneratorPort
from app.infrastructure.persistence.repositories.ai.content_plans import ContentPlanRepository
from app.application.services.ai.plan.plan_service import (
    _get_active_sf_codes,
    estimate_plan_tokens,
)

logger = logging.getLogger(__name__)


class PlanWizardService:
    """Orchestrates phased plan wizard lifecycle.

    Depends on PlanGeneratorPort (domain contract).
    If no generator is injected, the default infrastructure adapter is used.
    """

    def __init__(self, generator: PlanGeneratorPort | None = None) -> None:
        self._generator = generator or get_plan_generator()

    def create_phased_plan(
        self,
        course_id: str,
        user_id: str,
        topic: str = '',
        file_ids: list[str] | None = None,
        quality_level: str = 'standard',
        language: str = 'de',
    ) -> dict[str, Any]:
        """Create a plan and run Phase 1 (course definition)."""
        from app.infrastructure.persistence.repositories.authoring.files import (
            AuthoringFilesRepository,
        )

        file_text = _collect_file_text(file_ids, AuthoringFilesRepository)

        course_meta = self._generator.generate_course_definition(
            topic=topic, file_text=file_text, quality_level=quality_level,
            language=language,
        )

        plan = ContentPlanRepository.create({
            'course_id': course_id,
            'user_id': user_id,
            'scope': 'course',
            'current_phase': 1,
            'status': 'draft',
            'course_meta': course_meta,
            'chapters': [],
            'plan_data': {'file_ids': file_ids or []},
            'chat_history': [],
        })
        return plan

    def advance_to_phase2(self, plan_id: str, quality_level: str = 'standard') -> dict[str, Any]:
        """Load plan and run Phase 2 (chapter structure generation)."""
        plan = _load_plan_or_raise(plan_id)
        course_meta = _parse_jsonb_field(plan, 'course_meta', {})
        file_text = _load_file_text_from_plan(plan)

        result = self._generator.generate_chapter_structure(
            course_meta, file_text=file_text, quality_level=quality_level,
        )

        updated = ContentPlanRepository.update_phase(
            plan_id, 2, {'chapters': result.get('chapters', [])},
        )
        return updated

    def advance_to_phase3(self, plan_id: str, quality_level: str = 'standard') -> dict[str, Any]:
        """Load plan and run Phase 3 (detailed content plan)."""
        plan = _load_plan_or_raise(plan_id)
        course_meta = _parse_jsonb_field(plan, 'course_meta', {})
        chapters = _parse_jsonb_field(plan, 'chapters', [])
        active_sf_codes = _get_active_sf_codes()
        skill_catalog = build_skill_catalog_prompt(active_sf_codes)

        result = self._generator.generate_content_plan(
            course_meta, chapters, skill_catalog, quality_level=quality_level,
        )

        estimated_tokens = estimate_plan_tokens(result)

        updated = ContentPlanRepository.update_phase(
            plan_id, 3, {'plan_data': result},
        )
        if updated:
            updated['estimated_tokens'] = estimated_tokens
        return updated

    def chat_about_plan(
        self, plan_id: str, message: str, quality_level: str = 'standard',
    ) -> dict[str, Any]:
        """Refine the current plan phase via multi-turn conversational chat."""
        plan = _load_plan_or_raise(plan_id)
        current_phase = plan.get('current_phase', 1)

        result = self._generator.chat_about_plan(
            _extract_plan_data(plan), message, current_phase,
            file_text=_load_file_text_from_plan(plan),
            quality_level=quality_level,
            chat_history=_parse_jsonb_field(plan, 'chat_history', []),
        )

        assistant_msg = result.get('response', '')
        _persist_chat_messages(plan_id, message, assistant_msg)

        plan_patch = result.get('updated_data')
        diff_summary, validation_warnings = _apply_plan_patch(
            plan_id, plan, plan_patch, current_phase,
        )

        updated_plan = ContentPlanRepository.find_by_id(plan_id)
        return {
            'assistant_message': assistant_msg,
            'plan_patch': plan_patch,
            'plan': updated_plan,
            'diff_summary': diff_summary,
            'validation_warnings': validation_warnings,
            'has_undo': bool(plan_patch),
        }

    def undo_last_chat_patch(self, plan_id: str) -> dict[str, Any]:
        """Undo the last chat patch by restoring the saved snapshot."""
        plan = _load_plan_or_raise(plan_id)
        current_phase = plan.get('current_phase', 1)
        snapshot = _load_undo_snapshot(plan_id)
        if not snapshot:
            raise ValueError('No undo snapshot available')

        restore_data: dict[str, Any] = {}
        if 'plan_data' in snapshot:
            restore_data['plan_data'] = snapshot['plan_data']
        if 'course_meta' in snapshot:
            restore_data['course_meta'] = snapshot['course_meta']
        if 'chapters' in snapshot:
            restore_data['chapters'] = snapshot['chapters']

        ContentPlanRepository.update_phase(plan_id, current_phase, restore_data)
        _clear_undo_snapshot(plan_id)

        updated_plan = ContentPlanRepository.find_by_id(plan_id)
        return {'plan': updated_plan, 'undone': True}


# ---------------------------------------------------------------------------
# Private helpers (wizard-specific)
# ---------------------------------------------------------------------------

def _extract_plan_data(plan: dict[str, Any]) -> dict[str, Any]:
    """Extract structured plan_data dict from a plan row for AI calls."""
    return {
        'course_meta': _parse_jsonb_field(plan, 'course_meta', {}),
        'chapters': _parse_jsonb_field(plan, 'chapters', []),
        'phases': _parse_jsonb_field(plan, 'plan_data', {}).get('phases', []),
    }


def _persist_chat_messages(plan_id: str, user_msg: str, assistant_msg: str) -> None:
    """Save user and assistant chat messages to plan history."""
    ContentPlanRepository.append_chat_message(
        plan_id, {'role': 'user', 'content': user_msg},
    )
    ContentPlanRepository.append_chat_message(
        plan_id, {'role': 'assistant', 'content': assistant_msg},
    )


def _apply_plan_patch(
    plan_id: str,
    plan: dict[str, Any],
    plan_patch: dict[str, Any] | None,
    current_phase: int,
) -> tuple[list[str], list[str]]:
    """Apply a chat patch to a plan, with undo snapshot, diff, and validation.

    Returns (diff_summary, validation_warnings).
    """
    if not plan_patch:
        return [], []

    old_plan_data = _parse_jsonb_field(plan, 'plan_data', {})
    _save_undo_snapshot(plan_id, old_plan_data, plan.get('course_meta'), plan.get('chapters'))

    resolved = _resolve_incremental_patch(plan, plan_patch, current_phase)
    ContentPlanRepository.update_phase(plan_id, current_phase, resolved)

    new_plan_data = resolved.get('plan_data', old_plan_data)
    diff_summary = _compute_plan_diff(old_plan_data, new_plan_data)
    validation_warnings = _validate_plan_after_patch(new_plan_data)

    return diff_summary, validation_warnings


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


def _resolve_incremental_patch(
    plan: dict[str, Any], patch: dict[str, Any], current_phase: int,
) -> dict[str, Any]:
    """Resolve incremental plan_patch operations for Phase 3.

    Supports: add_phases, remove_phases, replace_phase, add_steps.
    Falls back to returning the patch as-is for non-incremental patches.
    """
    incremental_keys = {'add_phases', 'remove_phases', 'replace_phase', 'replace_phases', 'add_steps'}
    if not (incremental_keys & set(patch.keys())):
        return patch

    plan_data = _parse_jsonb_field(plan, 'plan_data', {})
    phases = list(plan_data.get('phases', []))

    if 'add_phases' in patch:
        for new_phase in patch['add_phases']:
            idx = new_phase.pop('chapter_index', len(phases))
            phases.insert(idx, new_phase)

    if 'remove_phases' in patch:
        for idx in sorted(patch['remove_phases'], reverse=True):
            if 0 <= idx < len(phases):
                phases.pop(idx)

    # Batch replacement: replace_phases (array of {index, phase})
    if 'replace_phases' in patch:
        for rp in patch['replace_phases']:
            idx = rp.get('index', -1)
            if 0 <= idx < len(phases):
                phases[idx] = rp.get('phase', phases[idx])

    # Single replacement (legacy): replace_phase
    if 'replace_phase' in patch:
        rp = patch['replace_phase']
        idx = rp.get('index', -1)
        if 0 <= idx < len(phases):
            phases[idx] = rp.get('phase', phases[idx])

    if 'add_steps' in patch:
        info = patch['add_steps']
        idx = info.get('phase_index', -1)
        if 0 <= idx < len(phases):
            phases[idx].setdefault('steps', []).extend(info.get('steps', []))

    plan_data['phases'] = phases
    return {'plan_data': plan_data}


def _load_file_text_from_plan(plan: dict[str, Any]) -> str | None:
    """Extract file_ids from plan_data and load their text content."""
    from app.infrastructure.persistence.repositories.authoring.files import (
        AuthoringFilesRepository,
    )
    plan_data = _parse_jsonb_field(plan, 'plan_data', {})
    file_ids = plan_data.get('file_ids') if isinstance(plan_data, dict) else None
    return _collect_file_text(file_ids, AuthoringFilesRepository)


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


# ---------------------------------------------------------------------------
# #3: Post-patch validation
# ---------------------------------------------------------------------------

def _validate_plan_after_patch(plan_data: dict[str, Any]) -> list[str]:
    """Check the plan for common quality issues after a patch.

    Returns a list of warning strings (empty = all good).
    """
    warnings: list[str] = []
    phases = plan_data.get('phases', [])

    if not phases:
        return warnings

    # Check min steps per phase
    for idx, phase in enumerate(phases):
        steps = phase.get('steps', [])
        title = phase.get('title', f'Phase {idx}')
        if len(steps) < 2:
            warnings.append(f'Kapitel "{title}" hat nur {len(steps)} Schritt(e) (min. 2)')

    # Check for duplicate target_titles
    all_titles: list[str] = []
    for phase in phases:
        for step in phase.get('steps', []):
            t = step.get('target_title', '').strip().lower()
            if t:
                all_titles.append(t)

    seen: set[str] = set()
    for t in all_titles:
        if t in seen:
            warnings.append(f'Duplikat gefunden: "{t}"')
        seen.add(t)

    # Check total step count sanity
    total = sum(len(p.get('steps', [])) for p in phases)
    if total < 5:
        warnings.append(f'Plan hat nur {total} Schritte insgesamt (sehr wenig)')

    return warnings


# ---------------------------------------------------------------------------
# #6: Plan diff computation
# ---------------------------------------------------------------------------

def _compute_plan_diff(
    old_data: dict[str, Any], new_data: dict[str, Any],
) -> list[str]:
    """Compute human-readable diff between old and new plan_data."""
    changes: list[str] = []

    old_phases = old_data.get('phases', [])
    new_phases = new_data.get('phases', [])

    if len(new_phases) != len(old_phases):
        changes.append(
            f'Kapitel: {len(old_phases)} → {len(new_phases)}'
        )

    old_total = sum(len(p.get('steps', [])) for p in old_phases)
    new_total = sum(len(p.get('steps', [])) for p in new_phases)
    if new_total != old_total:
        changes.append(f'Schritte: {old_total} → {new_total}')

    # Detect changed phases by title
    old_titles = {i: p.get('title', '') for i, p in enumerate(old_phases)}
    new_titles = {i: p.get('title', '') for i, p in enumerate(new_phases)}

    for i, title in new_titles.items():
        old_title = old_titles.get(i)
        if old_title is None:
            changes.append(f'+ Neues Kapitel: "{title}"')
        elif old_title != title:
            changes.append(f'~ Kapitel {i+1} umbenannt: "{old_title}" → "{title}"')

    for i, title in old_titles.items():
        if i not in new_titles:
            changes.append(f'- Kapitel entfernt: "{title}"')

    # Detect step-level changes in matching phases
    for i in range(min(len(old_phases), len(new_phases))):
        old_steps = old_phases[i].get('steps', [])
        new_steps = new_phases[i].get('steps', [])
        if len(new_steps) != len(old_steps):
            phase_title = new_phases[i].get('title', f'Phase {i+1}')
            changes.append(
                f'"{phase_title}": {len(old_steps)} → {len(new_steps)} Schritte'
            )

    return changes


# ---------------------------------------------------------------------------
# #7: Undo snapshot (in-memory, keyed by plan_id)
# ---------------------------------------------------------------------------

_undo_snapshots: dict[str, dict[str, Any]] = {}


def _save_undo_snapshot(
    plan_id: str,
    plan_data: Any,
    course_meta: Any = None,
    chapters: Any = None,
) -> None:
    """Save current plan state before applying a patch."""
    snapshot: dict[str, Any] = {}
    if plan_data is not None:
        snapshot['plan_data'] = plan_data if isinstance(plan_data, dict) else json.loads(plan_data)
    if course_meta is not None:
        snapshot['course_meta'] = course_meta if isinstance(course_meta, dict) else json.loads(course_meta)
    if chapters is not None:
        snapshot['chapters'] = chapters if isinstance(chapters, list) else json.loads(chapters)
    _undo_snapshots[plan_id] = snapshot


def _load_undo_snapshot(plan_id: str) -> dict[str, Any] | None:
    """Load the most recent undo snapshot for a plan."""
    return _undo_snapshots.get(plan_id)


def _clear_undo_snapshot(plan_id: str) -> None:
    """Remove the undo snapshot after it's been used."""
    _undo_snapshots.pop(plan_id, None)


