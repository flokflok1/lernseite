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
from app.infrastructure.ai.plan.plan_prompts import (
    build_phase1_prompt,
    build_phase2_prompt,
    build_phase3_prompt,
)
from app.infrastructure.ai.plan.plan_prompts_part2 import (
    build_plan_chat_prompt,
    build_flat_plan_prompt,
    build_flat_plan_from_text_prompt,
)
from app.infrastructure.persistence.repositories.ai_models import (
    AIModelsRepository,
)

logger = logging.getLogger(__name__)


def _resolve_model_defaults() -> tuple[str, str]:
    """Resolve provider/model from task defaults (category='content').

    Falls back to global default if no task-specific config exists.
    Raises ValueError if nothing is configured.
    """
    from app.infrastructure.ai.task_model_resolver import resolve_model_for_task
    provider, model = resolve_model_for_task('content')
    if not provider or not model:
        raise ValueError(
            'No default AI model configured. '
            'Please configure a default model in AI Settings (Admin > AI).'
        )
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
    max_tokens: Optional[int] = None,
    timeout: int = 120,
    temperature: float = 0.0,
) -> str:
    """Send a system/user message pair via AIAdapter and return raw text."""
    adapter = AIAdapter(provider=provider_name, model=model_name, timeout=timeout)
    messages = [
        {'role': 'system', 'content': system_msg},
        {'role': 'user', 'content': user_msg},
    ]
    response = adapter.send_messages(
        messages=messages, max_tokens=max_tokens, temperature=temperature,
    )
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
        provider_name: str | None = None,
        model_name: str | None = None,
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
        file_text: str | None = None,
        quality_level: str = 'standard',
        language: str = 'de',
    ) -> dict:
        """Phase 1: generate course metadata from a topic description."""
        system_msg, user_msg = build_phase1_prompt(
            topic=topic, file_text=file_text, language=language,
        )
        fallback = _phase1_fallback(topic)

        raw = _safe_call_ai(
            self._provider, self._model, system_msg, user_msg,
            quality_level=quality_level,
        )
        if raw is None:
            return fallback

        return _parse_json_safe(raw, fallback)

    # -- Phase 2 ---------------------------------------------------------

    def generate_chapter_structure(
        self,
        course_meta: dict,
        file_text: str | None = None,
        quality_level: str = 'standard',
    ) -> dict:
        """Phase 2: generate chapter structure from course metadata."""
        system_msg, user_msg = build_phase2_prompt(
            course_meta=course_meta, file_text=file_text,
        )
        fallback: dict[str, Any] = {'chapters': []}

        raw = _safe_call_ai(
            self._provider, self._model, system_msg, user_msg,
            quality_level=quality_level,
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
        skill_catalog_section: str = '',
        quality_level: str = 'standard',
    ) -> dict:
        """Phase 3: generate detailed content plan with skills per lesson."""
        system_msg, user_msg = build_phase3_prompt(
            course_meta=course_meta,
            chapters=chapters,
            skill_catalog_section=skill_catalog_section,
        )
        fallback: dict[str, Any] = {'phases': []}

        raw = _safe_call_ai(
            self._provider, self._model, system_msg, user_msg,
            timeout=300,
            quality_level=quality_level,
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
        file_text: str | None = None,
        quality_level: str = 'standard',
        chat_history: list[dict] | None = None,
    ) -> dict:
        """Refine a plan phase via multi-turn conversational interaction."""
        system_msg = build_plan_chat_prompt(
            plan_data=plan_data,
            current_phase=current_phase,
            file_text=file_text,
        )
        fallback = {
            'response': '[PLAN_CHAT_UNAVAILABLE]',
            'updated_data': None,
            'phase': current_phase,
        }

        raw = _safe_call_ai_multi_turn(
            self._provider, self._model, system_msg, message,
            chat_history=chat_history,
            quality_level=quality_level,
        )
        if raw is None:
            return fallback

        parsed = _parse_json_safe(raw, fallback)
        return _normalize_chat_response(parsed, current_phase, fallback)

    # -- Flat Plan (legacy single-shot) ------------------------------------

    def generate_flat_plan(
        self,
        course_title: str,
        scope: str,
        chapters: list[dict],
        language: str = 'de',
        skill_catalog_section: str = '',
    ) -> dict:
        """Generate a flat content plan in a single AI call."""
        system_msg, user_msg = build_flat_plan_prompt(
            course_title=course_title,
            scope=scope,
            chapters=chapters,
            language=language,
            skill_catalog_section=skill_catalog_section,
        )
        fallback: dict[str, Any] = {'phases': []}

        raw = _safe_call_ai(self._provider, self._model, system_msg, user_msg)
        if raw is None:
            return fallback

        result = _parse_json_safe(raw, fallback)
        if 'phases' not in result:
            result = {'phases': []}
        return _add_step_ids(result)

    def generate_plan_from_text(
        self,
        extracted_text: str,
        language: str = 'de',
        skill_catalog_section: str = '',
    ) -> dict:
        """Generate a content plan from uploaded file text."""
        system_msg, user_msg = build_flat_plan_from_text_prompt(
            extracted_text=extracted_text,
            language=language,
            skill_catalog_section=skill_catalog_section,
        )
        fallback: dict[str, Any] = {'phases': []}

        raw = _safe_call_ai(
            self._provider, self._model, system_msg, user_msg,
            timeout=300,
        )
        if raw is None:
            return fallback

        result = _parse_json_safe(raw, fallback)
        if 'phases' not in result:
            result = {'phases': []}
        return _add_step_ids(result)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _resolve_quality_tokens(quality_level: str, base_tokens: Optional[int]) -> Optional[int]:
    """Scale base_tokens by quality level profile's output_token_ratio.

    If base_tokens is None, returns None so the adapter resolves dynamically.
    """
    if base_tokens is None:
        return None
    try:
        from app.application.services.content.course_authoring.quality_profile import (
            get_quality_profile,
        )
        profile = get_quality_profile(quality_level)
        return max(profile.min_output_tokens, int(base_tokens * profile.output_token_ratio / 0.75))
    except Exception:
        return base_tokens


def _safe_call_ai(
    provider: str,
    model: str,
    system_msg: str,
    user_msg: str,
    max_tokens: Optional[int] = None,
    timeout: int = 120,
    quality_level: str = 'standard',
    temperature: float = 0.0,
) -> str | None:
    """Wrap _call_ai with exception handling; returns None on failure."""
    scaled_tokens = _resolve_quality_tokens(quality_level, max_tokens)
    try:
        return _call_ai(
            provider, model, system_msg, user_msg,
            scaled_tokens, timeout, temperature=temperature,
        )
    except Exception as exc:
        logger.error("AI call failed in plan generator: %s", exc)
        return None


def _call_ai_multi_turn(
    provider_name: str,
    model_name: str,
    system_msg: str,
    user_msg: str,
    chat_history: list[dict] | None = None,
    max_tokens: Optional[int] = None,
    timeout: int = 120,
    temperature: float = 0.0,
) -> str:
    """Send a multi-turn conversation via AIAdapter.

    Builds: system → history (user/assistant pairs) → new user message.
    """
    adapter = AIAdapter(provider=provider_name, model=model_name, timeout=timeout)
    messages: list[dict[str, str]] = [
        {'role': 'system', 'content': system_msg},
    ]

    if chat_history:
        # Limit to last 20 messages to stay within context limits
        recent = chat_history[-20:]
        for msg in recent:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role in ('user', 'assistant') and content:
                messages.append({'role': role, 'content': content})

    messages.append({'role': 'user', 'content': user_msg})
    response = adapter.send_messages(
        messages=messages, max_tokens=max_tokens, temperature=temperature,
    )
    return response.get('output_text', '').strip()


def _safe_call_ai_multi_turn(
    provider: str,
    model: str,
    system_msg: str,
    user_msg: str,
    chat_history: list[dict] | None = None,
    max_tokens: Optional[int] = None,
    timeout: int = 120,
    quality_level: str = 'standard',
    temperature: float = 0.0,
) -> str | None:
    """Wrap _call_ai_multi_turn with exception handling."""
    scaled_tokens = _resolve_quality_tokens(quality_level, max_tokens)
    try:
        return _call_ai_multi_turn(
            provider, model, system_msg, user_msg,
            chat_history=chat_history,
            max_tokens=scaled_tokens, timeout=timeout,
            temperature=temperature,
        )
    except Exception as exc:
        logger.error("AI multi-turn call failed in plan generator: %s", exc)
        return None


def _phase1_fallback(topic: str) -> dict:
    """Minimal fallback for Phase 1 when AI is unavailable."""
    return {
        'title': topic[:80] if topic else '',
        'description': '',
        'target_audience': '',
        'difficulty': 'intermediate',
        'language': 'de',
    }


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
