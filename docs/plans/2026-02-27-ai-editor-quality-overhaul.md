# AI Editor Quality Overhaul — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform the AI Editor from a single-shot generation system into a configurable, quality-aware pipeline. Users choose a Quality Level in the UI; that level controls tokens, temperature, pipeline steps, retry logic, and content validation — all dynamically.

**Architecture:** A new `QualityProfile` dataclass defines every tunable parameter. The UI sends a `quality_level` (schnell / standard / hoch / maximum) with each chat request. The backend resolves this into a profile that drives the entire generation pipeline. This replaces all hardcoded values (max_tokens=4000, temperature=0.7, 10-message history, etc.) with a single, testable configuration object.

**Tech Stack:** Python 3.12, Flask, psycopg3, OpenAI/Anthropic/Google APIs via AIAdapter

---

## Task 1: Quality Profile System (Core)

**Problem:** All generation parameters are hardcoded across multiple files. No central place to tune quality vs. speed trade-offs. No UI control.

**Files:**
- Create: `backend/app/application/services/content/course_authoring/quality_profile.py`
- Modify: `backend/app/application/services/content/course_authoring/__init__.py` (barrel export)

**Step 1: Create QualityProfile**

```python
# backend/app/application/services/content/course_authoring/quality_profile.py
"""
Quality profiles for AI Editor generation.

Each profile controls all generation parameters:
- Token budget (percentage of model's max output)
- Temperature (creativity vs precision)
- History depth and context size
- Content validation strictness
- Retry behavior
- Pipeline mode (single-shot vs multi-step)
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class QualityProfile:
    """Immutable configuration for a single generation request."""

    # --- Identity ---
    level: str                      # schnell, standard, hoch, maximum
    label: str                      # Display name for UI

    # --- Token Budget ---
    output_token_ratio: float       # Fraction of model's max_output_tokens (0.0-1.0)
    min_output_tokens: int          # Floor (never go below)
    # NO cap — user pays per token, model's own limit is the only ceiling

    # --- Temperature ---
    temperature_structure: float    # For structure operations (chapters, lessons)
    temperature_content: float      # For content generation (theory, text)
    temperature_methods: float      # For method generation (quiz, exercise)
    temperature_default: float      # Fallback when mode not specified

    # --- History Context ---
    history_message_limit: int      # Max messages from chat history
    history_char_limit: int         # Max total chars for history in prompt
    history_message_char_limit: int # Max chars per individual message

    # --- Content Validation ---
    validate_content: bool          # Run ContentValidator?
    min_raw_text_length: int        # Minimum lesson theory length (chars)
    min_quiz_questions: int         # Minimum questions per quiz
    min_flashcard_count: int        # Minimum cards per flashcard set
    require_exercise_solution: bool # Require modelAnswer for exercises?

    # --- Retry ---
    max_retries: int                # Auto-retry on validation errors (0=disabled)
    retry_temperature_drop: float   # Reduce temperature by this on retry

    # --- Pipeline ---
    pipeline_enabled: bool          # Use multi-step pipeline?
    pipeline_batch_size: int        # Chapters per pipeline step
    methods_per_lesson: int         # Target methods per lesson (for prompt)


# ============================================================================
# Predefined Levels
# ============================================================================

QUALITY_LEVELS: Dict[str, QualityProfile] = {
    'schnell': QualityProfile(
        level='schnell',
        label='Schnell',
        # Tokens: 25% of model limit, cap at 8K
        output_token_ratio=0.25,
        min_output_tokens=2000,
        max_output_tokens_cap=8000,
        # Temperature: slightly lower for speed/consistency
        temperature_structure=0.4,
        temperature_content=0.6,
        temperature_methods=0.5,
        temperature_default=0.6,
        # History: minimal
        history_message_limit=5,
        history_char_limit=2000,
        history_message_char_limit=200,
        # Validation: warnings only
        validate_content=True,
        min_raw_text_length=30,
        min_quiz_questions=1,
        min_flashcard_count=2,
        require_exercise_solution=False,
        # Retry: none
        max_retries=0,
        retry_temperature_drop=0.0,
        # Pipeline: single-shot
        pipeline_enabled=False,
        pipeline_batch_size=0,
        methods_per_lesson=1,
    ),

    'standard': QualityProfile(
        level='standard',
        label='Standard',
        # Tokens: 50% of model limit, cap at 16K
        output_token_ratio=0.50,
        min_output_tokens=4000,
        max_output_tokens_cap=16000,
        # Temperature: balanced
        temperature_structure=0.4,
        temperature_content=0.7,
        temperature_methods=0.6,
        temperature_default=0.7,
        # History: moderate
        history_message_limit=15,
        history_char_limit=5000,
        history_message_char_limit=500,
        # Validation: standard checks
        validate_content=True,
        min_raw_text_length=50,
        min_quiz_questions=2,
        min_flashcard_count=3,
        require_exercise_solution=True,
        # Retry: 1 attempt
        max_retries=1,
        retry_temperature_drop=0.15,
        # Pipeline: single-shot (but available)
        pipeline_enabled=False,
        pipeline_batch_size=3,
        methods_per_lesson=2,
    ),

    'hoch': QualityProfile(
        level='hoch',
        label='Hoch',
        # Tokens: 75% of model limit, cap at 32K
        output_token_ratio=0.75,
        min_output_tokens=8000,
        max_output_tokens_cap=32000,
        # Temperature: higher for creative content
        temperature_structure=0.3,
        temperature_content=0.75,
        temperature_methods=0.6,
        temperature_default=0.7,
        # History: deep
        history_message_limit=25,
        history_char_limit=8000,
        history_message_char_limit=800,
        # Validation: strict
        validate_content=True,
        min_raw_text_length=100,
        min_quiz_questions=3,
        min_flashcard_count=5,
        require_exercise_solution=True,
        # Retry: 1 attempt
        max_retries=1,
        retry_temperature_drop=0.2,
        # Pipeline: enabled
        pipeline_enabled=True,
        pipeline_batch_size=3,
        methods_per_lesson=2,
    ),

    'maximum': QualityProfile(
        level='maximum',
        label='Maximum',
        # Tokens: 100% of model limit, no cap
        output_token_ratio=1.0,
        min_output_tokens=16000,
        max_output_tokens_cap=999999,
        # Temperature: optimized per step
        temperature_structure=0.3,
        temperature_content=0.8,
        temperature_methods=0.6,
        temperature_default=0.7,
        # History: full
        history_message_limit=30,
        history_char_limit=12000,
        history_message_char_limit=1000,
        # Validation: strictest
        validate_content=True,
        min_raw_text_length=200,
        min_quiz_questions=5,
        min_flashcard_count=5,
        require_exercise_solution=True,
        # Retry: 2 attempts
        max_retries=2,
        retry_temperature_drop=0.2,
        # Pipeline: full multi-step
        pipeline_enabled=True,
        pipeline_batch_size=2,
        methods_per_lesson=3,
    ),
}


def get_quality_profile(level: str = 'standard') -> QualityProfile:
    """
    Get a quality profile by level name.

    Args:
        level: One of 'schnell', 'standard', 'hoch', 'maximum'

    Returns:
        QualityProfile for the given level
    """
    profile = QUALITY_LEVELS.get(level)
    if not profile:
        logger.warning(f"Unknown quality level '{level}', using 'standard'")
        return QUALITY_LEVELS['standard']
    return profile


def list_quality_levels() -> List[Dict]:
    """
    List all available quality levels for the UI.

    Returns:
        List of dicts with level info for display
    """
    return [
        {
            'level': p.level,
            'label': p.label,
            'description': _LEVEL_DESCRIPTIONS[p.level],
            'icon': _LEVEL_ICONS[p.level],
            'estimated_time': _LEVEL_TIMES[p.level],
            'token_ratio': p.output_token_ratio,
            'pipeline': p.pipeline_enabled,
            'methods_per_lesson': p.methods_per_lesson,
            'retries': p.max_retries,
        }
        for p in QUALITY_LEVELS.values()
    ]


_LEVEL_DESCRIPTIONS = {
    'schnell': 'Schnelle Generierung, Basis-Inhalte. Gut zum Ausprobieren.',
    'standard': 'Ausgewogene Qualität mit Validierung und Retry.',
    'hoch': 'Hochwertige Inhalte mit Multi-Step-Pipeline und strenger Validierung.',
    'maximum': 'Maximale Qualität. Volle Token-Kapazität, mehrere Durchläufe, strengste Prüfung.',
}

_LEVEL_ICONS = {
    'schnell': '⚡',
    'standard': '⭐',
    'hoch': '🎯',
    'maximum': '💎',
}

_LEVEL_TIMES = {
    'schnell': '~15-30s',
    'standard': '~30-60s',
    'hoch': '~1-2min',
    'maximum': '~2-5min',
}
```

**Step 2: Update barrel export**

In `__init__.py`:
```python
from .quality_profile import QualityProfile, get_quality_profile, list_quality_levels
```

**Step 3: Commit**

```bash
git add backend/app/application/services/content/course_authoring/quality_profile.py
git add backend/app/application/services/content/course_authoring/__init__.py
git commit -m "feat(ai-editor): quality profile system with 4 configurable levels"
```

---

## Task 2: Token Budget (driven by QualityProfile)

**Problem:** `max_tokens=4000` hardcoded. Must be dynamic based on model limits AND quality level.

**Files:**
- Create: `backend/app/application/services/content/course_authoring/token_budget.py`

**Step 1: Create TokenBudget**

```python
# backend/app/application/services/content/course_authoring/token_budget.py
"""
Dynamic token budget calculation for AI Editor.

Calculates optimal max_tokens based on:
1. Model's actual context_window and max_output_tokens
2. QualityProfile's output_token_ratio and caps
3. Estimated prompt size (system + user + tools)
"""

import logging
from typing import Dict

from app.application.services.content.course_authoring.quality_profile import (
    QualityProfile,
)

logger = logging.getLogger(__name__)

CHARS_PER_TOKEN = 4
SAFETY_MARGIN_RATIO = 0.10
TOOL_DEFINITION_TOKENS = 3000


class TokenBudget:
    """Calculates dynamic token budgets for AI requests."""

    @staticmethod
    def estimate_prompt_tokens(system_prompt: str, user_prompt: str) -> int:
        """Rough token estimate for input."""
        text_chars = len(system_prompt) + len(user_prompt)
        return (text_chars // CHARS_PER_TOKEN) + TOOL_DEFINITION_TOKENS

    @staticmethod
    def get_model_limits(provider: str, model: str) -> Dict[str, int]:
        """
        Get context_window and max_output_tokens for a model.
        Checks DB first, falls back to config.py.
        """
        try:
            from app.infrastructure.persistence.repositories.ai_models.query import (
                AIModelsQueryRepository,
            )
            db_model = AIModelsQueryRepository.get_by_name(model, provider)
            if db_model:
                cw = db_model.get('context_window')
                mo = db_model.get('max_output_tokens')
                if cw and mo:
                    return {'context_window': int(cw), 'max_output_tokens': int(mo)}
        except Exception:
            pass

        try:
            from app.infrastructure.ai.config import PROVIDERS
            cfg = PROVIDERS.get(provider, {}).get('models', {}).get(model, {})
            return {
                'context_window': cfg.get('context_window', 128000),
                'max_output_tokens': cfg.get('max_tokens', 32000),
            }
        except Exception:
            pass

        return {'context_window': 128000, 'max_output_tokens': 32000}

    @staticmethod
    def compute(
        provider: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        profile: QualityProfile = None
    ) -> int:
        """
        Calculate optimal max_tokens for a request.

        Uses model limits + quality profile ratio + prompt size estimation.

        Args:
            provider: AI provider name
            model: AI model name
            system_prompt: System prompt text
            user_prompt: User prompt text
            profile: Quality profile (uses standard defaults if None)

        Returns:
            Optimal max_tokens value
        """
        if profile is None:
            from app.application.services.content.course_authoring.quality_profile import (
                get_quality_profile,
            )
            profile = get_quality_profile('standard')

        limits = TokenBudget.get_model_limits(provider, model)
        estimated_input = TokenBudget.estimate_prompt_tokens(
            system_prompt, user_prompt
        )

        # Model's hard output limit
        model_max = limits['max_output_tokens']

        # Quality profile's desired ratio of that limit
        desired = int(model_max * profile.output_token_ratio)

        # Apply profile's cap
        desired = min(desired, profile.max_output_tokens_cap)

        # Ensure we don't exceed context window
        safety = int(limits['context_window'] * SAFETY_MARGIN_RATIO)
        context_available = limits['context_window'] - estimated_input - safety
        result = min(desired, context_available, model_max)

        # Never below profile's minimum
        result = max(result, profile.min_output_tokens)

        logger.info(
            f"Token budget [{profile.level}]: "
            f"model_max={model_max}, ratio={profile.output_token_ratio}, "
            f"desired={desired}, input≈{estimated_input} → "
            f"max_tokens={result}"
        )
        return result
```

**Step 2: Update barrel export, commit**

```bash
git add backend/app/application/services/content/course_authoring/token_budget.py
git add backend/app/application/services/content/course_authoring/__init__.py
git commit -m "feat(ai-editor): token budget calculator driven by quality profile"
```

---

## Task 3: Content Validator (driven by QualityProfile)

**Problem:** No validation of AI-generated content. Empty quizzes, missing theory, exercises without solutions all get finalized.

**Files:**
- Create: `backend/app/application/services/content/course_authoring/content_validator.py`

**Step 1: Create ContentValidator that reads thresholds from QualityProfile**

```python
# backend/app/application/services/content/course_authoring/content_validator.py
"""
Content schema validation for AI-generated course content.

Thresholds come from QualityProfile, so 'schnell' is lenient
and 'maximum' is strict.
"""

import logging
from typing import Dict, List, Tuple

from app.application.services.content.course_authoring.quality_profile import (
    QualityProfile,
)

logger = logging.getLogger(__name__)


class ContentValidator:
    """Validates AI-generated content completeness."""

    @classmethod
    def validate(
        cls,
        structure: Dict,
        profile: QualityProfile
    ) -> Tuple[bool, List[Dict]]:
        """
        Validate draft structure using profile thresholds.

        Returns:
            (is_valid, issues) where each issue has level/path/message
        """
        if not profile.validate_content:
            return (True, [])

        issues: List[Dict] = []

        for ch_idx, ch in enumerate(structure.get('chapters', [])):
            ch_label = f"Kap. {ch_idx+1} \"{ch.get('title', '?')}\""

            if not ch.get('title', '').strip():
                issues.append({
                    'level': 'error', 'path': ch_label,
                    'message': 'Kein Titel'
                })

            for ls_idx, ls in enumerate(ch.get('lessons', [])):
                ls_label = f"{ch_label} → Lek. {ls_idx+1} \"{ls.get('title', '?')}\""
                cls._check_lesson(ls, ls_label, profile, issues)

                for mt_idx, mt in enumerate(ls.get('methods', [])):
                    mt_label = f"{ls_label} → {mt.get('type', '?')} \"{mt.get('title', '?')}\""
                    cls._check_method(mt, mt_label, profile, issues)

        errors = [i for i in issues if i['level'] == 'error']
        return (len(errors) == 0, issues)

    @classmethod
    def _check_lesson(cls, lesson, path, profile, issues):
        content = lesson.get('content', {})
        raw_text = content.get('raw_text', '') if isinstance(content, dict) else ''

        if len(raw_text) < profile.min_raw_text_length:
            issues.append({
                'level': 'warning', 'path': path,
                'message': (
                    f'Theorieblatt zu kurz ({len(raw_text)} Zeichen, '
                    f'Minimum: {profile.min_raw_text_length})'
                )
            })

    @classmethod
    def _check_method(cls, method, path, profile, issues):
        mtype = method.get('type', '')
        content = method.get('content', {})

        if not isinstance(content, dict) or not content:
            issues.append({
                'level': 'error', 'path': path,
                'message': 'Leerer content'
            })
            return

        if mtype == 'quiz':
            qs = content.get('questions', [])
            if len(qs) < profile.min_quiz_questions:
                issues.append({
                    'level': 'error', 'path': path,
                    'message': f'{len(qs)} Fragen (Minimum: {profile.min_quiz_questions})'
                })
            for i, q in enumerate(qs):
                if not q.get('question'):
                    issues.append({'level': 'error', 'path': f'{path}[{i}]', 'message': 'Frage ohne Text'})
                if len(q.get('options', [])) < 2:
                    issues.append({'level': 'error', 'path': f'{path}[{i}]', 'message': 'Weniger als 2 Optionen'})
                if q.get('correct') is None:
                    issues.append({'level': 'error', 'path': f'{path}[{i}]', 'message': 'Kein correct-Index'})

        elif mtype == 'flashcards':
            cards = content.get('cards', [])
            if len(cards) < profile.min_flashcard_count:
                issues.append({
                    'level': 'error', 'path': path,
                    'message': f'{len(cards)} Karten (Minimum: {profile.min_flashcard_count})'
                })

        elif mtype == 'exercise':
            if not content.get('question') or len(content.get('question', '')) < 10:
                issues.append({'level': 'error', 'path': path, 'message': 'Keine/zu kurze Frage'})
            solution = method.get('solution', {})
            if profile.require_exercise_solution and not solution.get('modelAnswer'):
                issues.append({'level': 'warning', 'path': path, 'message': 'Keine Musterlösung'})
```

**Step 2: Commit**

```bash
git add backend/app/application/services/content/course_authoring/content_validator.py
git add backend/app/application/services/content/course_authoring/__init__.py
git commit -m "feat(ai-editor): content validator with profile-driven thresholds"
```

---

## Task 4: Integrate Quality Profile into Session Service

**Problem:** `session.py` has hardcoded `temperature=0.7`, `max_tokens=4000`, 10-message history. Must use QualityProfile.

**Files:**
- Modify: `backend/app/application/services/content/course_authoring/session.py`
- Modify: `backend/app/application/services/content/course_authoring/helpers.py`

**Step 1: Update `apply_chat_message` signature**

Add `quality_level` parameter:

```python
def apply_chat_message(
    self,
    session_id: str,
    user_id: str,
    message: str,
    mode: Optional[str] = None,
    file_ids: Optional[List[str]] = None,
    focus_chapter_id: Optional[str] = None,
    focus_lesson_id: Optional[str] = None,
    prompt_code: Optional[str] = None,
    quality_level: str = 'standard'       # NEW
) -> Dict[str, Any]:
```

**Step 2: Use profile throughout the method**

Replace all hardcoded values:

```python
# At top of method body:
from app.application.services.content.course_authoring.quality_profile import get_quality_profile
from app.application.services.content.course_authoring.token_budget import TokenBudget
from app.application.services.content.course_authoring.content_validator import ContentValidator

profile = get_quality_profile(quality_level)

# History context (replaces hardcoded [-10:] and 300 char truncation):
history_context = DataHelpers.format_history_for_prompt(
    chat_history[-profile.history_message_limit:],
    max_chars=profile.history_char_limit,
    message_char_limit=profile.history_message_char_limit
)

# Token budget (replaces hardcoded 4000):
max_tokens = TokenBudget.compute(
    self.provider, self.model, system_prompt, user_prompt, profile
)

# Temperature (replaces hardcoded 0.7):
temperature = profile.temperature_default
if mode == 'structure' or (mode and 'structure' in mode):
    temperature = profile.temperature_structure
elif mode == 'lesson' or (mode and 'content' in mode):
    temperature = profile.temperature_content
elif mode == 'method' or (mode and 'method' in mode):
    temperature = profile.temperature_methods

# AI Call:
result = adapter.send_messages_with_tools(
    messages=messages,
    tools=AUTHORING_TOOLS,
    temperature=temperature,
    max_tokens=max_tokens
)

# Content validation (after operations applied):
validation_result = None
if profile.validate_content and operations_applied:
    is_valid, validation_issues = ContentValidator.validate(
        draft_structure, profile
    )
    if validation_issues:
        validation_result = {
            'valid': is_valid,
            'errors': [i for i in validation_issues if i['level'] == 'error'],
            'warnings': [i for i in validation_issues if i['level'] == 'warning'],
        }

# Add to result:
result_dict['quality_level'] = profile.level
result_dict['max_tokens_used'] = max_tokens
if validation_result:
    result_dict['content_validation'] = validation_result
```

**Step 3: Update `format_history_for_prompt` in helpers.py**

```python
@staticmethod
def format_history_for_prompt(
    history: List[Dict],
    max_chars: int = 6000,
    message_char_limit: int = 500
) -> str:
    """
    Formats chat history for prompt, respecting token budget.

    Newest messages get priority. Each message capped at message_char_limit.
    Total output capped at max_chars.
    """
    if not history:
        return "Keine vorherigen Nachrichten."

    lines = []
    total_chars = 0

    for msg in reversed(history):
        role = 'Benutzer' if msg.get('role') == 'user' else 'Assistent'
        content = msg.get('content', '')[:message_char_limit]
        line = f"{role}: {content}"

        if total_chars + len(line) > max_chars:
            break

        lines.insert(0, line)
        total_chars += len(line)

    return "\n".join(lines) if lines else "Keine vorherigen Nachrichten."
```

**Step 4: Commit**

```bash
git add backend/app/application/services/content/course_authoring/session.py
git add backend/app/application/services/content/course_authoring/helpers.py
git commit -m "feat(ai-editor): integrate quality profile into session service"
```

---

## Task 5: Chat History Preservation + Model Fix

**Problem:** Auto-finalize creates new session with `chat_history=[]` and hardcoded `model_profile`.

**Files:**
- Modify: `backend/app/api/v1/panel/editor/ai/authoring.py` (auto-finalize block)
- Modify: `backend/app/application/services/content/course_authoring/session.py` (`create_session`)

**Step 1: Add `initial_chat_history` to `create_session`**

```python
def create_session(
    self,
    user_id: str,
    course_id: str,
    model_profile: str = "anthropic-claude-sonnet",
    initial_chat_history: Optional[List] = None
) -> Dict[str, Any]:
    # ...
    chat_history = initial_chat_history or []
    # Use in create_session call:
    chat_history_json=json.dumps(chat_history)
```

**Step 2: Fix auto-finalize in authoring.py**

```python
# In course_authoring_chat, after ops_count > 0:
if ops_count > 0:
    try:
        finalize_result = service.finalize_session(session_id, user_id)
        result['finalized'] = True
        result['finalize_stats'] = finalize_result.get('stats', {})

        course_id = result['draft_structure'].get('course_id')
        if course_id:
            # Carry chat history (capped by profile)
            carry_history = result.get('_chat_history', [])[-20:]

            new_session = service.create_session(
                user_id=user_id,
                course_id=course_id,
                model_profile=data.get('model_profile', 'anthropic-claude-sonnet'),
                initial_chat_history=carry_history
            )
            result['new_session_id'] = new_session['session_id']
            result['draft_structure'] = new_session['draft_structure']
```

**Step 3: Expose `_chat_history` from `apply_chat_message`**

At end of `apply_chat_message` in session.py:
```python
result['_chat_history'] = chat_history
```

**Step 4: Commit**

```bash
git add backend/app/api/v1/panel/editor/ai/authoring.py
git add backend/app/application/services/content/course_authoring/session.py
git commit -m "feat(ai-editor): preserve chat history and model choice across sessions"
```

---

## Task 6: Intelligent Retry (driven by QualityProfile)

**Problem:** Failed operations and validation errors are logged but not recovered. Profile controls retry count.

**Files:**
- Modify: `backend/app/application/services/content/course_authoring/session.py`

**Step 1: Add retry loop after content validation**

In `apply_chat_message`, after content validation:

```python
# Retry logic (controlled by profile.max_retries)
retry_count = 0
while (
    retry_count < profile.max_retries
    and validation_result
    and validation_result.get('errors')
):
    retry_count += 1
    retry_temp = max(0.2, temperature - profile.retry_temperature_drop * retry_count)
    logger.info(
        f"Session {session_id}: Retry {retry_count}/{profile.max_retries} "
        f"for {len(validation_result['errors'])} errors (temp={retry_temp})"
    )

    fix_prompt = self._build_fix_prompt(
        failed_ops, validation_result['errors'], draft_structure
    )
    if not fix_prompt:
        break

    fix_result = adapter.send_messages_with_tools(
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': fix_prompt}
        ],
        tools=AUTHORING_TOOLS,
        temperature=retry_temp,
        max_tokens=max_tokens // 2
    )

    fix_calls = fix_result.get('tool_calls', [])
    if fix_calls:
        fix_ops = ToolCallProcessor.to_operations(fix_calls)
        draft_structure, fix_applied, fix_failed = (
            StructureOperations.apply_operations(draft_structure, fix_ops)
        )
        operations_applied.extend(fix_applied)
        tokens_used += fix_result.get('total_tokens', 0)

    # Re-validate
    is_valid, validation_issues = ContentValidator.validate(draft_structure, profile)
    validation_result = {
        'valid': is_valid,
        'errors': [i for i in validation_issues if i['level'] == 'error'],
        'warnings': [i for i in validation_issues if i['level'] == 'warning'],
    }
```

**Step 2: Add `_build_fix_prompt` static method**

```python
@staticmethod
def _build_fix_prompt(
    failed_ops: List[Dict],
    errors: List[Dict],
    draft_structure: Dict
) -> Optional[str]:
    """Build targeted prompt to fix validation errors."""
    issues = []
    for op in failed_ops:
        issues.append(f"- Operation '{op.get('op')}' fehler: {op.get('error')}")
    for err in errors:
        issues.append(f"- {err['path']}: {err['message']}")
    if not issues:
        return None

    structure_summary = PromptGenerator._summarize_structure(draft_structure)
    return (
        f"FEHLER-KORREKTUR:\n"
        f"Folgende Probleme müssen behoben werden:\n"
        + "\n".join(issues)
        + f"\n\nAKTUELLE STRUKTUR:\n{structure_summary}\n\n"
        f"Korrigiere NUR die genannten Probleme mit den passenden Tools."
    )
```

**Step 3: Commit**

```bash
git add backend/app/application/services/content/course_authoring/session.py
git commit -m "feat(ai-editor): intelligent retry with profile-driven attempts"
```

---

## Task 7: Multi-Step Pipeline (driven by QualityProfile)

**Problem:** AI tries to generate everything in one turn. Quality degrades with many operations.

**Files:**
- Create: `backend/app/application/services/content/course_authoring/pipeline.py`
- Modify: `backend/app/api/v1/panel/editor/ai/authoring.py` (pipeline-status endpoint)

**Step 1: Create GenerationPipeline**

```python
# backend/app/application/services/content/course_authoring/pipeline.py
"""
Multi-step generation pipeline for course authoring.

When QualityProfile.pipeline_enabled=True, large generation tasks
are broken into focused steps.
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


STEP_PROMPTS = {
    'structure': (
        "\n\nAKTUELLER SCHRITT: NUR STRUKTUR.\n"
        "Erstelle Kapitel (add_chapter) und Lektionen (add_lesson) mit kurzem "
        "Platzhalter-Text in content.raw_text. KEINE Lernmethoden in diesem Schritt."
    ),
    'content': (
        "\n\nAKTUELLER SCHRITT: NUR THEORIE-INHALTE.\n"
        "Verwende update_lesson um content.raw_text mit vollständigem Markdown-Theorieblatt "
        "zu füllen. KEINE neuen Kapitel oder Methoden erstellen."
    ),
    'methods': (
        "\n\nAKTUELLER SCHRITT: NUR LERNMETHODEN.\n"
        "Verwende add_method für jede Lektion. KEINE neuen Kapitel oder Lektionen. "
        "IMMER vollständige Inhalte und Lösungen."
    ),
}


class GenerationPipeline:
    """Orchestrates multi-step course generation."""

    @classmethod
    def determine_step(cls, structure: Dict) -> str:
        """Auto-detect which step is needed next."""
        chapters = structure.get('chapters', [])
        if not chapters:
            return 'structure'

        total = 0
        needs_content = 0
        needs_methods = 0

        for ch in chapters:
            for ls in ch.get('lessons', []):
                total += 1
                content = ls.get('content', {})
                raw = content.get('raw_text', '') if isinstance(content, dict) else ''
                if len(raw) < 200:
                    needs_content += 1
                elif not ls.get('methods'):
                    needs_methods += 1

        if total == 0:
            return 'structure'
        if needs_content > total * 0.5:
            return 'content'
        if needs_methods > 0:
            return 'methods'
        return 'complete'

    @classmethod
    def get_step_prompt(cls, step: str) -> Optional[str]:
        """Get prompt suffix for a pipeline step."""
        return STEP_PROMPTS.get(step)

    @classmethod
    def get_focused_chapters(
        cls, structure: Dict, step: str, batch_size: int = 3
    ) -> List[str]:
        """Get chapter IDs needing work for this step."""
        result = []
        for ch in structure.get('chapters', []):
            needs = False
            for ls in ch.get('lessons', []):
                content = ls.get('content', {})
                raw = content.get('raw_text', '') if isinstance(content, dict) else ''
                if step == 'content' and len(raw) < 200:
                    needs = True
                    break
                if step == 'methods' and not ls.get('methods'):
                    needs = True
                    break
            if needs:
                result.append(ch.get('id'))
            if len(result) >= batch_size:
                break
        return result
```

**Step 2: Integrate into session.py**

In `apply_chat_message`, when pipeline_enabled and mode starts with `pipeline_`:

```python
# After building system_prompt:
if mode and mode.startswith('pipeline_'):
    step = mode.replace('pipeline_', '')
    step_suffix = GenerationPipeline.get_step_prompt(step)
    if step_suffix:
        system_prompt += step_suffix
```

**Step 3: Add API endpoints**

In `authoring.py`, add:
- `GET /sessions/<id>/pipeline-status` — Returns current step + focused chapters
- `GET /quality-levels` — Returns available quality levels for UI

```python
@ai_editor_bp.route('/quality-levels', methods=['GET'])
@check_course_permission('read')
def get_quality_levels():
    """Returns available quality levels for UI selector."""
    from app.application.services.content.course_authoring.quality_profile import (
        list_quality_levels,
    )
    return jsonify({'success': True, 'data': {'levels': list_quality_levels()}}), 200


@ai_editor_bp.route('/sessions/<session_id>/pipeline-status', methods=['GET'])
@check_course_permission('read')
def get_pipeline_status(session_id):
    """Returns current pipeline step and what needs work."""
    denied = _verify_session_access(session_id)
    if denied:
        return denied
    try:
        from app.application.services.content.course_authoring import (
            get_course_authoring_service,
        )
        from app.application.services.content.course_authoring.pipeline import (
            GenerationPipeline,
        )
        user_id = g.current_user['user_id']
        service = get_course_authoring_service()
        session_data = service.get_session(session_id, user_id)
        draft = session_data['draft_structure']

        step = GenerationPipeline.determine_step(draft)
        focused = GenerationPipeline.get_focused_chapters(draft, step)

        return jsonify({'success': True, 'data': {
            'current_step': step,
            'focused_chapter_ids': focused,
            'is_complete': step == 'complete',
        }}), 200
    except Exception as e:
        logger.error(f"Pipeline status error: {e}", exc_info=True)
        return error_response(ErrorCode.COURSE_FILE_OPERATION_FAILED, 500,
                            details={'error': 'Internal server error'})
```

**Step 4: Pass quality_level from API to service**

In `course_authoring_chat`:
```python
quality_level = data.get('quality_level', 'standard')

result = service.apply_chat_message(
    ...,
    quality_level=quality_level
)
```

**Step 5: Commit**

```bash
git add backend/app/application/services/content/course_authoring/pipeline.py
git add backend/app/application/services/content/course_authoring/session.py
git add backend/app/api/v1/panel/editor/ai/authoring.py
git add backend/app/application/services/content/course_authoring/__init__.py
git commit -m "feat(ai-editor): multi-step pipeline + quality-level API endpoint"
```

---

## Task 8: Integration Test

**Files:**
- All modified/created files

**Step 1: Import smoke test**

```bash
cd backend && python -c "
from app.application.services.content.course_authoring.quality_profile import (
    get_quality_profile, list_quality_levels, QUALITY_LEVELS
)
from app.application.services.content.course_authoring.token_budget import TokenBudget
from app.application.services.content.course_authoring.content_validator import ContentValidator
from app.application.services.content.course_authoring.pipeline import GenerationPipeline

# Test quality profiles
for level in ['schnell', 'standard', 'hoch', 'maximum']:
    p = get_quality_profile(level)
    print(f'{p.label}: ratio={p.output_token_ratio}, retries={p.max_retries}, pipeline={p.pipeline_enabled}')

# Test token budget per profile
for level in ['schnell', 'standard', 'hoch', 'maximum']:
    p = get_quality_profile(level)
    tokens = TokenBudget.compute('openai', 'gpt-4o-mini', 'x'*2000, 'y'*5000, p)
    print(f'{p.label}: max_tokens={tokens}')

# Test content validation strictness
structure = {
    'chapters': [{'title': 'Test', 'lessons': [{
        'title': 'L', 'content': {'raw_text': 'Short'},
        'methods': [{'type': 'quiz', 'title': 'Q', 'content': {'questions': []}}]
    }]}]
}
for level in ['schnell', 'maximum']:
    p = get_quality_profile(level)
    valid, issues = ContentValidator.validate(structure, p)
    print(f'{p.label}: valid={valid}, issues={len(issues)}')

# Test pipeline
step = GenerationPipeline.determine_step({'chapters': []})
assert step == 'structure'

levels = list_quality_levels()
assert len(levels) == 4

print('All OK')
"
```

**Step 2: Backend start test**

```bash
fuser -k 5000/tcp; sleep 2
cd backend && source venv/bin/activate && python run.py &
sleep 4
curl -s http://localhost:5000/health
```

**Step 3: API endpoint tests**

```bash
TOKEN=$(curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@lsx.de","password":"admin123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Quality levels
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/v1/course-editor/ai/quality-levels | python3 -m json.tool

# Prompt templates
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/v1/course-editor/ai/prompt-templates | python3 -m json.tool
```

**Step 4: Commit if fixes needed**

```bash
git add -A && git commit -m "fix(ai-editor): integration fixes for quality overhaul"
```

---

## Summary

```
                    ┌──────────────────────────┐
                    │   UI: Quality Selector    │
                    │  ⚡ Standard ⭐ Hoch 🎯 Max 💎 │
                    └────────────┬─────────────┘
                                 │ quality_level
                    ┌────────────▼─────────────┐
                    │    QualityProfile         │
                    │  (frozen dataclass)       │
                    │  • token ratio            │
                    │  • temperatures           │
                    │  • history limits         │
                    │  • validation thresholds  │
                    │  • retry config           │
                    │  • pipeline mode          │
                    └──┬───┬───┬───┬───┬───┬───┘
                       │   │   │   │   │   │
            ┌──────────┘   │   │   │   │   └──────────┐
            ▼              ▼   │   ▼   ▼              ▼
      TokenBudget    Temperature │ Retry  Validator  Pipeline
      (dynamic        (per mode) │ (auto   (schema    (multi-
       max_tokens)              │  fix)    checks)    step)
                                │
                    ┌───────────▼──────────────┐
                    │    History Context        │
                    │  (message limit + chars)  │
                    └──────────────────────────┘
```

| Task | New Files | Impact |
|------|-----------|--------|
| 1. Quality Profile | `quality_profile.py` | Central config, UI-selectable |
| 2. Token Budget | `token_budget.py` | Up to 64K output (GPT-5) |
| 3. Content Validator | `content_validator.py` | No more empty content |
| 4. Session Integration | session.py, helpers.py | Everything wired together |
| 5. History Carry-Over | authoring.py, session.py | KI erinnert sich |
| 6. Retry Logic | session.py | Auto-fix bei Fehlern |
| 7. Pipeline + API | pipeline.py, authoring.py | Multi-step + endpoints |
| 8. Integration Test | All | Verify everything works |
