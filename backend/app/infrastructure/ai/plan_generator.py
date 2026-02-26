"""
PlanGeneratorAdapter — Infrastructure implementation of PlanGeneratorPort.

Calls the configured AI provider (via AIAdapter) to generate course plans
in three phases, plus a chat refinement endpoint. Uses the same AI call
mechanism as the existing plan_service.py.
"""

import json
import logging
import uuid
from typing import Any, Optional

from app.domain.ports.plan_generator import PlanGeneratorPort
from app.infrastructure.ai.adapter import AIAdapter
from app.infrastructure.ai.plan_prompts import (
    build_phase1_prompt,
    build_phase2_prompt,
    build_phase3_prompt,
    build_plan_chat_prompt,
)
from app.infrastructure.persistence.repositories.ai_models import (
    AIModelsRepository,
)

logger = logging.getLogger(__name__)


def _resolve_model_defaults() -> tuple[str, str]:
    """Resolve provider/model from the DB default, with safe fallbacks."""
    default_model = AIModelsRepository.get_default_model()
    if default_model:
        provider = default_model.get('provider_name', 'openai')
        model = default_model.get('model_name', 'gpt-4o-mini')
    else:
        provider = 'openai'
        model = 'gpt-4o-mini'
    return provider, model


def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences (```json ... ```) from AI output."""
    if not text.startswith('```'):
        return text
    lines = text.split('\n')
    lines = [line for line in lines if not line.strip().startswith('```')]
    return '\n'.join(lines).strip()


def _parse_json_safe(raw: str, fallback: dict) -> dict:
    """Parse JSON from AI output, returning fallback on any error."""
    cleaned = _strip_code_fences(raw.strip())
    if not cleaned:
        logger.warning("AI returned empty output for plan generation")
        return fallback
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.error(
            "Plan generator — invalid JSON: %s, output: %.200s",
            exc,
            cleaned,
        )
        return fallback


def _call_ai(
    provider_name: str,
    model_name: str,
    system_msg: str,
    user_msg: str,
    max_tokens: int = 4000,
) -> str:
    """Send a system/user message pair via AIAdapter and return raw text."""
    adapter = AIAdapter(provider=provider_name, model=model_name)
    messages = [
        {'role': 'system', 'content': system_msg},
        {'role': 'user', 'content': user_msg},
    ]
    response = adapter.send_messages(messages=messages, max_tokens=max_tokens)
    return response.get('output_text', '').strip()


def _add_chapter_ids(data: dict) -> dict:
    """Ensure every chapter in 'chapters' has a unique id and order."""
    chapters = data.get('chapters', [])
    for idx, chapter in enumerate(chapters):
        if 'id' not in chapter:
            chapter['id'] = str(uuid.uuid4())
        if 'order' not in chapter:
            chapter['order'] = idx + 1
    return data


def _add_step_ids(data: dict) -> dict:
    """Ensure every step in every phase has id, order, and status."""
    phases = data.get('phases', [])
    for phase in phases:
        steps = phase.get('steps', [])
        for step_idx, step in enumerate(steps):
            if 'step_id' not in step:
                step['step_id'] = str(uuid.uuid4())
            if 'order' not in step:
                step['order'] = step_idx + 1
            if 'status' not in step:
                step['status'] = 'pending'
        if 'phase_id' not in phase:
            phase['phase_id'] = str(uuid.uuid4())
    return data


# ---------------------------------------------------------------------------
# Adapter class
# ---------------------------------------------------------------------------

class PlanGeneratorAdapter(PlanGeneratorPort):
    """Infrastructure adapter that calls AIAdapter to generate course plans."""

    def __init__(
        self,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        if provider_name and model_name:
            self._provider = provider_name
            self._model = model_name
        else:
            self._provider, self._model = _resolve_model_defaults()

    # -- Phase 1 ---------------------------------------------------------

    def generate_course_definition(
        self,
        topic: str,
        file_text: Optional[str] = None,
    ) -> dict:
        """Phase 1: generate course metadata from a topic description."""
        system_msg, user_msg = build_phase1_prompt(
            topic=topic, file_text=file_text,
        )
        fallback = _phase1_fallback(topic)

        raw = _safe_call_ai(
            self._provider, self._model, system_msg, user_msg,
        )
        if raw is None:
            return fallback

        return _parse_json_safe(raw, fallback)

    # -- Phase 2 ---------------------------------------------------------

    def generate_chapter_structure(
        self,
        course_meta: dict,
        file_text: Optional[str] = None,
    ) -> dict:
        """Phase 2: generate chapter structure from course metadata."""
        system_msg, user_msg = build_phase2_prompt(
            course_meta=course_meta, file_text=file_text,
        )
        fallback: dict[str, Any] = {'chapters': []}

        raw = _safe_call_ai(
            self._provider, self._model, system_msg, user_msg,
        )
        if raw is None:
            return fallback

        result = _parse_json_safe(raw, fallback)
        return _add_chapter_ids(result)

    # -- Phase 3 ---------------------------------------------------------

    def generate_content_plan(
        self,
        course_meta: dict,
        chapters: list[dict],
        active_sf_codes: Optional[set[str]] = None,
    ) -> dict:
        """Phase 3: generate detailed content plan with skills per lesson."""
        skill_catalog = _get_skill_catalog_section(active_sf_codes)

        system_msg, user_msg = build_phase3_prompt(
            course_meta=course_meta,
            chapters=chapters,
            skill_catalog_section=skill_catalog,
        )
        fallback: dict[str, Any] = {'phases': []}

        raw = _safe_call_ai(
            self._provider, self._model, system_msg, user_msg,
            max_tokens=8000,
        )
        if raw is None:
            return fallback

        result = _parse_json_safe(raw, fallback)
        if 'phases' not in result:
            result = {'phases': []}
        return _add_step_ids(result)

    # -- Plan Chat -------------------------------------------------------

    def chat_about_plan(
        self,
        plan_data: dict,
        message: str,
        current_phase: int,
    ) -> dict:
        """Refine a plan phase via conversational interaction."""
        system_msg = build_plan_chat_prompt(
            plan_data=plan_data,
            current_phase=current_phase,
        )
        user_msg = message
        fallback = {
            'response': 'Entschuldigung, ich konnte die Anfrage nicht verarbeiten.',
            'updated_data': None,
            'phase': current_phase,
        }

        raw = _safe_call_ai(
            self._provider, self._model, system_msg, user_msg,
        )
        if raw is None:
            return fallback

        parsed = _parse_json_safe(raw, fallback)
        return _normalize_chat_response(parsed, current_phase, fallback)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _safe_call_ai(
    provider: str,
    model: str,
    system_msg: str,
    user_msg: str,
    max_tokens: int = 4000,
) -> Optional[str]:
    """Wrap _call_ai with exception handling; returns None on failure."""
    try:
        return _call_ai(provider, model, system_msg, user_msg, max_tokens)
    except Exception as exc:
        logger.error("AI call failed in plan generator: %s", exc)
        return None


def _phase1_fallback(topic: str) -> dict:
    """Minimal fallback for Phase 1 when AI is unavailable."""
    return {
        'title': topic[:80] if topic else 'Neuer Kurs',
        'description': '',
        'target_audience': '',
        'difficulty': 'intermediate',
        'language': 'de',
    }


def _get_skill_catalog_section(
    active_sf_codes: Optional[set[str]] = None,
) -> str:
    """Import and call the skill catalog builder from plan_service."""
    try:
        from app.application.services.ai.plan_service import (
            _get_skill_catalog_prompt,
        )
        return _get_skill_catalog_prompt(active_sf_codes=active_sf_codes)
    except ImportError:
        logger.warning(
            "Could not import _get_skill_catalog_prompt; using empty catalog"
        )
        return ''


def _normalize_chat_response(
    parsed: dict,
    current_phase: int,
    fallback: dict,
) -> dict:
    """Ensure the chat response has the expected shape."""
    assistant_msg = parsed.get('assistant_message') or parsed.get('response')
    if not assistant_msg:
        return fallback

    return {
        'response': assistant_msg,
        'updated_data': parsed.get('plan_patch') or parsed.get('updated_data'),
        'phase': parsed.get('phase', current_phase),
    }
