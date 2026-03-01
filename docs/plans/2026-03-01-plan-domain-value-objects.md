# Plan Domain Value Objects — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add frozen dataclass Value Objects (CourseMeta, ChapterDraft, PlanChatMessage, PlanData) to the domain layer, wire them into PlanGeneratorPort and PlanWizardService at boundaries.

**Architecture:** Value Objects live in `app/domain/ai/models/plan.py`. They provide `from_dict()` / `to_dict()` for boundary conversion. The Port uses VOs in signatures. The Service converts dict→VO at input and VO→dict at output. Repository and API stay unchanged (dicts). The Infrastructure adapter converts its raw AI output into VOs before returning.

**Tech Stack:** Python 3.12 dataclasses, pytest

---

### Task 1: Create Domain Value Objects with tests

**Files:**
- Create: `backend/app/domain/ai/models/plan.py`
- Modify: `backend/app/domain/ai/models/__init__.py`
- Create: `backend/tests/unit/domain/ai/models/test_plan.py`

**Step 1: Write the failing tests**

```python
# backend/tests/unit/domain/ai/models/test_plan.py
"""Tests for Plan domain value objects."""
import pytest
from app.domain.ai.models.plan import CourseMeta, ChapterDraft, PlanChatMessage, PlanData

VALID_DIFFICULTIES = ('beginner', 'intermediate', 'advanced', 'expert')


class TestCourseMeta:
    def test_from_dict_valid(self):
        raw = {
            'title': 'Python Basics',
            'description': 'Learn Python',
            'target_audience': 'Beginners',
            'difficulty': 'beginner',
            'language': 'de',
        }
        meta = CourseMeta.from_dict(raw)
        assert meta.title == 'Python Basics'
        assert meta.difficulty == 'beginner'
        assert meta.language == 'de'

    def test_from_dict_with_extras(self):
        raw = {
            'title': 'Advanced ML',
            'description': 'Deep learning',
            'target_audience': 'Data Scientists',
            'difficulty': 'advanced',
            'language': 'en',
            'subtitle': 'Neural Networks',
            'prerequisites': ['Python', 'Math'],
            'estimated_duration_hours': 40,
            'tags': ['ml', 'ai'],
        }
        meta = CourseMeta.from_dict(raw)
        assert meta.subtitle == 'Neural Networks'
        assert meta.prerequisites == ['Python', 'Math']
        assert meta.estimated_duration_hours == 40
        assert meta.tags == ['ml', 'ai']

    def test_from_dict_defaults(self):
        raw = {'title': 'T', 'description': 'D', 'target_audience': 'A', 'difficulty': 'beginner'}
        meta = CourseMeta.from_dict(raw)
        assert meta.language == 'de'
        assert meta.subtitle == ''
        assert meta.prerequisites == []
        assert meta.estimated_duration_hours == 0
        assert meta.tags == []

    def test_from_dict_invalid_difficulty(self):
        raw = {'title': 'T', 'description': 'D', 'target_audience': 'A', 'difficulty': 'banane'}
        with pytest.raises(ValueError, match='difficulty'):
            CourseMeta.from_dict(raw)

    def test_from_dict_empty_title(self):
        raw = {'title': '', 'description': 'D', 'target_audience': 'A', 'difficulty': 'beginner'}
        with pytest.raises(ValueError, match='title'):
            CourseMeta.from_dict(raw)

    def test_to_dict_roundtrip(self):
        raw = {
            'title': 'Python', 'description': 'Desc', 'target_audience': 'All',
            'difficulty': 'beginner', 'language': 'de',
        }
        meta = CourseMeta.from_dict(raw)
        result = meta.to_dict()
        assert result['title'] == 'Python'
        assert result['difficulty'] == 'beginner'
        assert isinstance(result, dict)

    def test_frozen(self):
        meta = CourseMeta.from_dict({
            'title': 'T', 'description': 'D', 'target_audience': 'A', 'difficulty': 'beginner',
        })
        with pytest.raises(AttributeError):
            meta.title = 'Changed'


class TestChapterDraft:
    def test_from_dict_valid(self):
        raw = {'id': 'ch-1', 'title': 'Intro', 'description': 'Introduction', 'order': 1}
        chapter = ChapterDraft.from_dict(raw)
        assert chapter.id == 'ch-1'
        assert chapter.order == 1

    def test_from_dict_with_extras(self):
        raw = {
            'id': 'ch-1', 'title': 'Intro', 'description': 'Intro',
            'order': 1, 'estimated_lessons': 5, 'learning_goals': ['Goal 1'],
        }
        chapter = ChapterDraft.from_dict(raw)
        assert chapter.estimated_lessons == 5
        assert chapter.learning_goals == ['Goal 1']

    def test_from_dict_invalid_order(self):
        raw = {'id': 'ch-1', 'title': 'Intro', 'description': 'Desc', 'order': 0}
        with pytest.raises(ValueError, match='order'):
            ChapterDraft.from_dict(raw)

    def test_to_dict_roundtrip(self):
        raw = {'id': 'ch-1', 'title': 'Intro', 'description': 'Desc', 'order': 1}
        chapter = ChapterDraft.from_dict(raw)
        assert chapter.to_dict() == {
            'id': 'ch-1', 'title': 'Intro', 'description': 'Desc',
            'order': 1, 'estimated_lessons': 0, 'learning_goals': [],
        }


class TestPlanChatMessage:
    def test_from_dict_valid(self):
        msg = PlanChatMessage.from_dict({'role': 'user', 'content': 'Hello'})
        assert msg.role == 'user'
        assert msg.content == 'Hello'

    def test_from_dict_invalid_role(self):
        with pytest.raises(ValueError, match='role'):
            PlanChatMessage.from_dict({'role': 'system', 'content': 'X'})

    def test_to_dict(self):
        msg = PlanChatMessage.from_dict({'role': 'assistant', 'content': 'Hi', 'timestamp': '2026-01-01'})
        d = msg.to_dict()
        assert d == {'role': 'assistant', 'content': 'Hi', 'timestamp': '2026-01-01'}


class TestPlanData:
    def test_from_dict_valid(self):
        raw = {
            'course_meta': {
                'title': 'Python', 'description': 'D', 'target_audience': 'A',
                'difficulty': 'beginner',
            },
            'chapters': [
                {'id': 'ch-1', 'title': 'Intro', 'description': 'D', 'order': 1},
            ],
            'phases': [{'phase_id': 'p1', 'steps': []}],
        }
        pd = PlanData.from_dict(raw)
        assert isinstance(pd.course_meta, CourseMeta)
        assert len(pd.chapters) == 1
        assert isinstance(pd.chapters[0], ChapterDraft)

    def test_from_dict_empty(self):
        pd = PlanData.from_dict({})
        assert pd.course_meta is None
        assert pd.chapters == []
        assert pd.phases == []

    def test_to_dict_roundtrip(self):
        raw = {
            'course_meta': {
                'title': 'T', 'description': 'D', 'target_audience': 'A',
                'difficulty': 'beginner',
            },
            'chapters': [
                {'id': 'ch-1', 'title': 'C', 'description': 'D', 'order': 1},
            ],
            'phases': [],
        }
        pd = PlanData.from_dict(raw)
        result = pd.to_dict()
        assert result['course_meta']['title'] == 'T'
        assert len(result['chapters']) == 1
```

**Step 2: Run tests to verify they fail**

Run: `cd /home/pascal/Lernsystem/backend && python -m pytest tests/unit/domain/ai/models/test_plan.py -v`
Expected: FAIL with "ModuleNotFoundError" or "ImportError"

**Step 3: Implement the value objects**

```python
# backend/app/domain/ai/models/plan.py
"""
Domain Value Objects for AI Content Plan Wizard.

Immutable dataclasses representing plan data at domain boundaries.
Used by PlanGeneratorPort and PlanWizardService for type safety.
"""

from __future__ import annotations

from dataclasses import dataclass, field

VALID_DIFFICULTIES = frozenset({'beginner', 'intermediate', 'advanced', 'expert'})
VALID_CHAT_ROLES = frozenset({'user', 'assistant'})


@dataclass(frozen=True)
class CourseMeta:
    """Phase 1 output: course definition metadata."""

    title: str
    description: str
    target_audience: str
    difficulty: str
    language: str = 'de'
    subtitle: str = ''
    prerequisites: tuple[str, ...] = ()
    estimated_duration_hours: int = 0
    tags: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict) -> CourseMeta:
        title = data.get('title', '').strip()
        if not title:
            raise ValueError('CourseMeta: title must not be empty')
        difficulty = data.get('difficulty', '')
        if difficulty not in VALID_DIFFICULTIES:
            raise ValueError(
                f'CourseMeta: difficulty must be one of {sorted(VALID_DIFFICULTIES)}, got {difficulty!r}'
            )
        return cls(
            title=title,
            description=data.get('description', ''),
            target_audience=data.get('target_audience', ''),
            difficulty=difficulty,
            language=data.get('language', 'de'),
            subtitle=data.get('subtitle', ''),
            prerequisites=tuple(data.get('prerequisites') or []),
            estimated_duration_hours=int(data.get('estimated_duration_hours', 0)),
            tags=tuple(data.get('tags') or []),
        )

    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'description': self.description,
            'target_audience': self.target_audience,
            'difficulty': self.difficulty,
            'language': self.language,
            'subtitle': self.subtitle,
            'prerequisites': list(self.prerequisites),
            'estimated_duration_hours': self.estimated_duration_hours,
            'tags': list(self.tags),
        }


@dataclass(frozen=True)
class ChapterDraft:
    """Phase 2 output: a single chapter in the course structure."""

    id: str
    title: str
    description: str
    order: int
    estimated_lessons: int = 0
    learning_goals: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict) -> ChapterDraft:
        order = int(data.get('order', 0))
        if order < 1:
            raise ValueError(f'ChapterDraft: order must be >= 1, got {order}')
        return cls(
            id=data.get('id', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            order=order,
            estimated_lessons=int(data.get('estimated_lessons', 0)),
            learning_goals=tuple(data.get('learning_goals') or []),
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'order': self.order,
            'estimated_lessons': self.estimated_lessons,
            'learning_goals': list(self.learning_goals),
        }


@dataclass(frozen=True)
class PlanChatMessage:
    """A single chat message in plan refinement history."""

    role: str
    content: str
    timestamp: str = ''

    @classmethod
    def from_dict(cls, data: dict) -> PlanChatMessage:
        role = data.get('role', '')
        if role not in VALID_CHAT_ROLES:
            raise ValueError(
                f'PlanChatMessage: role must be one of {sorted(VALID_CHAT_ROLES)}, got {role!r}'
            )
        return cls(
            role=role,
            content=data.get('content', ''),
            timestamp=data.get('timestamp', ''),
        )

    def to_dict(self) -> dict:
        return {'role': self.role, 'content': self.content, 'timestamp': self.timestamp}


@dataclass
class PlanData:
    """Container for the full plan state across all phases.

    Not frozen — mutable container that holds immutable value objects.
    Phases stay as dicts (complex nested structure, low validation value).
    """

    course_meta: CourseMeta | None = None
    chapters: list[ChapterDraft] = field(default_factory=list)
    phases: list[dict] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> PlanData:
        course_meta_raw = data.get('course_meta')
        course_meta = CourseMeta.from_dict(course_meta_raw) if course_meta_raw else None

        chapters_raw = data.get('chapters') or []
        chapters = [ChapterDraft.from_dict(ch) for ch in chapters_raw]

        phases = data.get('phases') or []
        return cls(course_meta=course_meta, chapters=chapters, phases=phases)

    def to_dict(self) -> dict:
        return {
            'course_meta': self.course_meta.to_dict() if self.course_meta else {},
            'chapters': [ch.to_dict() for ch in self.chapters],
            'phases': self.phases,
        }
```

**Step 4: Update barrel export**

In `backend/app/domain/ai/models/__init__.py`:
```python
"""
AI Domain Models - Barrel Export.

Value objects and constants for AI domain.
"""

from .plan import ChapterDraft, CourseMeta, PlanChatMessage, PlanData

__all__ = ['CourseMeta', 'ChapterDraft', 'PlanChatMessage', 'PlanData']
```

**Step 5: Run tests to verify they pass**

Run: `cd /home/pascal/Lernsystem/backend && python -m pytest tests/unit/domain/ai/models/test_plan.py -v`
Expected: All 16 tests PASS

**Step 6: Verify backend starts**

Run: `cd /home/pascal/Lernsystem/backend && python -c "from app import create_app; create_app()"`
Expected: No import errors

**Step 7: Commit**

```bash
git add backend/app/domain/ai/models/plan.py backend/app/domain/ai/models/__init__.py backend/tests/unit/domain/ai/models/test_plan.py
git commit -m "feat(domain): add Plan value objects (CourseMeta, ChapterDraft, PlanChatMessage, PlanData)

Frozen dataclasses with from_dict/to_dict for boundary conversion.
Validates difficulty, order, and chat role constraints."
```

---

### Task 2: Update PlanGeneratorPort type hints

**Files:**
- Modify: `backend/app/domain/ports/plan_generator.py`

**Step 1: Update port signatures**

Replace `dict` type hints in all 4 wizard methods with domain VOs. The legacy methods (`generate_flat_plan`, `generate_plan_from_text`) stay as `dict` since they don't use the wizard flow.

Changes:
- `generate_course_definition() -> dict` becomes `-> dict` (stays dict — raw AI output, Service converts)
- `generate_chapter_structure(course_meta: dict, ...) -> dict` — parameter `course_meta` becomes `CourseMeta | dict`
- `generate_content_plan(course_meta: dict, chapters: list[dict], ...) -> dict` — `course_meta` becomes `CourseMeta | dict`, `chapters` becomes `list[ChapterDraft] | list[dict]`
- `chat_about_plan(plan_data: dict, ..., chat_history: list[dict] | None) -> dict` — `plan_data` becomes `PlanData | dict`, `chat_history` becomes `list[PlanChatMessage] | list[dict] | None`

NOTE: Use union types (`CourseMeta | dict`) so the Infrastructure adapter can accept both during transition. Return types stay `dict` because AI output is unpredictable raw JSON that gets validated at the Service layer.

Add import at top:
```python
from app.domain.ai.models.plan import CourseMeta, ChapterDraft, PlanChatMessage, PlanData
```

**Step 2: Verify backend starts**

Run: `cd /home/pascal/Lernsystem/backend && python -c "from app import create_app; create_app()"`

**Step 3: Commit**

```bash
git add backend/app/domain/ports/plan_generator.py
git commit -m "refactor(ports): add domain VO type hints to PlanGeneratorPort

Union types (CourseMeta | dict) for backward compatibility during transition."
```

---

### Task 3: Wire Value Objects into PlanWizardService

**Files:**
- Modify: `backend/app/application/services/ai/plan/plan_service_part2.py`

**Step 1: Add import and update `_extract_plan_data`**

Add import at top:
```python
from app.domain.ai.models.plan import CourseMeta, ChapterDraft, PlanChatMessage, PlanData
```

Replace `_extract_plan_data` (lines 166-172):
```python
def _extract_plan_data(plan: dict[str, Any]) -> PlanData:
    """Extract structured PlanData from a plan row for AI calls."""
    course_meta_raw = _parse_jsonb_field(plan, 'course_meta', {})
    chapters_raw = _parse_jsonb_field(plan, 'chapters', [])
    phases = _parse_jsonb_field(plan, 'plan_data', {}).get('phases', [])

    course_meta = CourseMeta.from_dict(course_meta_raw) if course_meta_raw else None
    chapters = [ChapterDraft.from_dict(ch) for ch in chapters_raw]

    return PlanData(course_meta=course_meta, chapters=chapters, phases=phases)
```

**Step 2: Update `create_phased_plan` to wrap Phase 1 output**

After `course_meta = self._generator.generate_course_definition(...)` (line 53), add validation:
```python
        course_meta_raw = self._generator.generate_course_definition(
            topic=topic, file_text=file_text, quality_level=quality_level,
            language=language,
        )
        # Validate AI output via domain VO
        try:
            course_meta_vo = CourseMeta.from_dict(course_meta_raw)
            course_meta = course_meta_vo.to_dict()
        except ValueError:
            course_meta = course_meta_raw  # Fallback: use raw dict if validation fails
```

**Step 3: Update `advance_to_phase2` similarly**

After `result = self._generator.generate_chapter_structure(...)` (line 77-79):
```python
        result = self._generator.generate_chapter_structure(
            course_meta, file_text=file_text, quality_level=quality_level,
        )
        # Validate chapters via domain VOs
        validated_chapters = []
        for ch in result.get('chapters', []):
            try:
                validated_chapters.append(ChapterDraft.from_dict(ch).to_dict())
            except ValueError:
                validated_chapters.append(ch)  # Fallback: keep raw
        result['chapters'] = validated_chapters
```

**Step 4: Update `chat_about_plan` to pass PlanData**

In `chat_about_plan` (line 114), `_extract_plan_data` now returns `PlanData`. Update the call to `self._generator.chat_about_plan`:
```python
        plan_data = _extract_plan_data(plan)
        result = self._generator.chat_about_plan(
            plan_data.to_dict(), message, current_phase,
            file_text=_load_file_text_from_plan(plan),
            quality_level=quality_level,
            chat_history=_parse_jsonb_field(plan, 'chat_history', []),
        )
```

NOTE: We call `.to_dict()` because the generator still accepts dicts internally. The VOs ensure the data was valid when it was loaded.

**Step 5: Verify backend starts and tests pass**

Run: `cd /home/pascal/Lernsystem/backend && python -c "from app import create_app; create_app()"`
Run: `cd /home/pascal/Lernsystem/backend && python -m pytest tests/unit/domain/ai/models/test_plan.py -v`
Expected: Backend starts, all tests pass

**Step 6: Commit**

```bash
git add backend/app/application/services/ai/plan/plan_service_part2.py
git commit -m "refactor(ai-editor): wire domain VOs into PlanWizardService

_extract_plan_data returns PlanData. Phase 1/2 outputs validated via
CourseMeta/ChapterDraft with dict fallback for AI edge cases."
```

---

### Task 4: Update Infrastructure adapter return types

**Files:**
- Modify: `backend/app/infrastructure/ai/plan/plan_generator.py`

**Step 1: Add import**

Add at top:
```python
from app.domain.ai.models.plan import CourseMeta, ChapterDraft
```

**Step 2: No functional changes needed**

The adapter already returns `dict` which is correct — the raw AI JSON output is validated at the Service layer (Task 3). The adapter's job is to call AI and parse JSON. Type annotations in the Port (Task 2) already document the expected shapes.

The only change is verifying that the adapter conforms to the updated Port signatures. Since we used union types (`CourseMeta | dict`), returning `dict` is still valid.

**Step 3: Verify backend starts**

Run: `cd /home/pascal/Lernsystem/backend && python -c "from app import create_app; create_app()"`

**Step 4: Commit (only if changes were needed)**

```bash
git add backend/app/infrastructure/ai/plan/plan_generator.py
git commit -m "refactor(ai-adapter): add domain VO import for type awareness"
```

---

### Task 5: Final verification

**Step 1: Run all domain tests**

Run: `cd /home/pascal/Lernsystem/backend && python -m pytest tests/unit/domain/ -v`

**Step 2: Verify full backend startup**

Run: `cd /home/pascal/Lernsystem/backend && python -c "from app import create_app; create_app()"`

**Step 3: Verify frontend still builds**

Run: `cd /home/pascal/Lernsystem/frontend && npm run build`

**Step 4: Verify barrel exports work**

Run: `cd /home/pascal/Lernsystem/backend && python -c "from app.domain.ai.models import CourseMeta, ChapterDraft, PlanChatMessage, PlanData; print('OK')"`

---

## Verification Checklist

After all tasks:
1. `python -m pytest tests/unit/domain/ai/models/test_plan.py -v` — 16+ tests pass
2. `python -c "from app import create_app; create_app()"` — No errors
3. `npm run build` — Frontend unaffected
4. `from app.domain.ai.models import CourseMeta` — Barrel export works
5. `PlanWizardService` uses VOs at boundaries (create, advance, chat)
6. Repository and API layers unchanged (still dicts)
