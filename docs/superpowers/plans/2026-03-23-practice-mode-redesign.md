# Practice Mode Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the static "Freies Ueben" button into a configurable practice system with sequential/mixed modes, 3 learning strategies, spaced repetition, adaptive difficulty, streak detection, and session summaries.

**Architecture:** DDD layers (Domain -> Application -> Infrastructure -> API -> Frontend). All new practice endpoints go in a new `practice.py` route file. Intelligence engines live in a new `practice_intelligence.py` service. Domain models are pure dataclasses with zero framework imports. Existing files are extended only where they have room (<500 LOC).

**Tech Stack:** Python 3.12 / Flask 3.0 / psycopg3 / Vue 3 Composition API / TypeScript / Pinia / TailwindCSS

**Spec:** `docs/superpowers/specs/2026-03-23-practice-mode-redesign-design.md`

---

## File Map

| Action | File | Current LOC | Target LOC |
|--------|------|-------------|------------|
| CREATE | `backend/app/domain/models/practice_session.py` | 0 | ~60 |
| CREATE | `backend/app/application/services/exams/practice_intelligence.py` | 0 | ~200 |
| EXTEND | `backend/app/application/services/exams/rotation_service.py` | 182 | ~350 |
| EXTEND | `backend/app/infrastructure/persistence/repositories/exams/trainer_part2.py` | 288 | ~390 |
| CREATE | `backend/app/api/v1/panel/user/exams/practice.py` | 0 | ~120 |
| MODIFY | `backend/app/api/v1/panel/user/exams/trainer.py` | 333 | ~336 |
| CREATE | `frontend/src/infrastructure/api/clients/panel/user/exams/practice.api.ts` | 0 | ~80 |
| MODIFY | `frontend/src/infrastructure/api/clients/panel/user/exams/index.ts` | 4 | ~5 |
| CREATE | `frontend/src/presentation/components/panel/user/exam-trainer/PracticeConfigPanel.vue` | 0 | ~150 |
| CREATE | `frontend/src/presentation/components/panel/user/exam-trainer/SessionSummary.vue` | 0 | ~200 |
| MODIFY | `frontend/src/presentation/components/panel/user/exam-trainer/ExamTrainer.vue` | 340 | ~370 |
| MODIFY | `frontend/src/presentation/components/panel/user/exam-trainer/SimulationMode.vue` | 327 | ~380 |
| MODIFY | `frontend/src/presentation/components/panel/user/exam-trainer/index.ts` | 4 | ~6 |
| MODIFY | `frontend/src/infrastructure/i18n/locales/de/panel/shared.json` | — | +30 keys |
| MODIFY | `frontend/src/infrastructure/i18n/locales/en/panel/shared.json` | — | +30 keys |
| MODIFY | `frontend/src/infrastructure/i18n/locales/pl/panel/shared.json` | — | +30 keys |

**DO NOT modify** (too full):
- `backend/app/infrastructure/persistence/repositories/exams/trainer.py` (452 LOC)
- `backend/app/api/v1/panel/user/exams/trainer_part2.py` (436 LOC)
- `frontend/src/infrastructure/api/clients/panel/user/exams/trainer.api.ts` (360 LOC)

---

## Phase 1: Sequential Mode (Backend + Frontend)

Priority: highest — enables Claude Cowork to test all 409 questions immediately.

---

### Task 1: Domain Models

**Files:**
- Create: `backend/app/domain/models/practice_session.py`

- [ ] **Step 1: Create the domain models file**

```python
"""
Practice Session Domain Models

Value Objects and Enums for the configurable practice system.
DDD Layer: Domain — NO Flask, DB, or Infrastructure imports.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class PracticeMode(Enum):
    """Learning strategy for mixed-mode practice."""
    DISCOVER = "discover"
    STRENGTHEN = "strengthen"
    EXAM_READY = "exam_ready"


class PracticeOrder(Enum):
    """Question ordering strategy."""
    SEQUENTIAL = "sequential"
    MIXED = "mixed"


class QuestionBucket(Enum):
    """Source bucket for question selection."""
    UNSEEN = "unseen"
    WEAK = "weak"
    REVIEW = "review"
    SPACED_REPEAT = "spaced_repeat"


class DifficultyShift(Enum):
    """Adaptive difficulty adjustment direction."""
    UP = "up"
    DOWN = "down"
    STAY = "stay"


@dataclass(frozen=True)
class SpacedRepetitionEntry:
    """Tracks a question scheduled for spaced repetition."""
    question_id: str
    wrong_count: int
    due_at_position: int


@dataclass(frozen=True)
class StreakAlert:
    """Alert when user gets multiple wrong answers in one topic."""
    topic: str
    consecutive_wrong: int
    suggested_extra_count: int = 5


@dataclass(frozen=True)
class PracticeConfig:
    """User-selected practice session configuration."""
    mode: PracticeMode
    order: PracticeOrder
    question_count: Optional[int] = None  # None = endless
    time_limit_minutes: Optional[int] = None
    exam_filter: list[str] = field(default_factory=list)
    topic_filter: list[str] = field(default_factory=list)
```

- [ ] **Step 2: Verify no import violations**

Run: `cd /home/pascal/Lernsystem/backend && python -c "from app.domain.models.practice_session import PracticeConfig, PracticeMode, PracticeOrder; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/app/domain/models/practice_session.py
git commit -m "feat(domain): add practice session value objects and enums"
```

---

### Task 2: Repository — Sequential Query + Count

**Files:**
- Modify: `backend/app/infrastructure/persistence/repositories/exams/trainer_part2.py` (append after line 287)

- [ ] **Step 1: Add `find_questions_sequential` and `count_available_questions` to ExamTrainerRotationMixin**

Append these two methods at the end of the `ExamTrainerRotationMixin` class in `trainer_part2.py` (after the existing `get_topic_frequency` method at line 287):

```python
    @staticmethod
    def find_questions_sequential(
        exam_filter: list | None = None,
        topic_filter: list | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list:
        """
        Fetch questions in sequential order (by exam year desc, season, question number).

        Used for sequential practice mode — user works through exams one by one.
        Supports pagination via offset/limit for batch loading.
        """
        conditions = [
            "e.analysis_status = 'ready'",
            "e.published = true",
        ]
        params: list = []

        if exam_filter:
            conditions.append("e.exam_id = ANY(%s)")
            params.append(exam_filter)

        if topic_filter:
            conditions.append("eq.topics && %s")
            params.append(topic_filter)

        where = " AND ".join(conditions)
        query = f"""
            SELECT eq.question_id, eq.exam_id, eq.question_number,
                   eq.question_text, eq.question_type, eq.points,
                   eq.topics, eq.data, eq.scenario_title, eq.scenario_text,
                   e.title AS exam_title, e.year, e.season, e.semester
            FROM assessments.exam_questions eq
            JOIN assessments.exams e ON e.exam_id = eq.exam_id
            WHERE {where}
            ORDER BY e.year DESC, e.season DESC, eq.question_number ASC
            OFFSET %s LIMIT %s
        """
        params.extend([offset, limit])
        return fetch_all(query, params)

    @staticmethod
    def count_available_questions(
        exam_filter: list | None = None,
        topic_filter: list | None = None,
    ) -> int:
        """Count total available questions matching optional filters."""
        conditions = [
            "e.analysis_status = 'ready'",
            "e.published = true",
        ]
        params: list = []

        if exam_filter:
            conditions.append("e.exam_id = ANY(%s)")
            params.append(exam_filter)

        if topic_filter:
            conditions.append("eq.topics && %s")
            params.append(topic_filter)

        where = " AND ".join(conditions)
        query = f"""
            SELECT COUNT(*) AS cnt
            FROM assessments.exam_questions eq
            JOIN assessments.exams e ON e.exam_id = eq.exam_id
            WHERE {where}
        """
        row = fetch_one(query, params)
        return row['cnt'] if row else 0
```

- [ ] **Step 2: Verify the queries work**

Run: `cd /home/pascal/Lernsystem/backend && python -c "
from app import create_app
app = create_app()
with app.app_context():
    from app.infrastructure.persistence.repositories.exams.trainer import ExamTrainerRepository
    count = ExamTrainerRepository.count_available_questions()
    print(f'Total questions: {count}')
    first = ExamTrainerRepository.find_questions_sequential(limit=3)
    for q in first:
        print(f'  {q[\"question_number\"]} - {q[\"exam_title\"]}')
"`
Expected: Total questions count > 0, and 3 questions printed in order.

- [ ] **Step 3: Commit**

```bash
git add backend/app/infrastructure/persistence/repositories/exams/trainer_part2.py
git commit -m "feat(repo): add sequential question query and count method"
```

---

### Task 3: Application Service — Sequential Practice Session

**Files:**
- Modify: `backend/app/application/services/exams/rotation_service.py` (add method after line 181)

- [ ] **Step 1: Add `generate_practice_session` to RotationService**

Add this method to the `RotationService` class. Import the domain models at the top of the file (after existing imports around line 12):

```python
from app.domain.models.practice_session import (
    PracticeConfig, PracticeOrder, PracticeMode,
)
```

Then append this method to the class (after `_select_from_buckets` around line 181):

```python
    @classmethod
    def generate_practice_session(
        cls, user_id: int, config: PracticeConfig,
    ) -> dict:
        """
        Create a practice session based on user configuration.

        For SEQUENTIAL order: fetches questions sorted by exam + question number.
        For MIXED order: uses bucket-based selection with topic balancing (Phase 2).

        Returns:
            Dict with attempt_id, questions, total_available, has_more, config.
        """
        total = ExamTrainerRepository.count_available_questions(
            exam_filter=config.exam_filter or None,
            topic_filter=config.topic_filter or None,
        )

        if total == 0:
            return {
                'attempt_id': None,
                'questions': [],
                'total_available': 0,
                'has_more': False,
                'config': {
                    'mode': config.mode.value,
                    'order': config.order.value,
                },
            }

        # Determine batch size
        if config.question_count is None:
            # Endless mode — first batch of 50
            batch_size = min(50, total)
        else:
            batch_size = min(config.question_count, total, 50)

        if config.order == PracticeOrder.SEQUENTIAL:
            questions = ExamTrainerRepository.find_questions_sequential(
                exam_filter=config.exam_filter or None,
                topic_filter=config.topic_filter or None,
                offset=0,
                limit=batch_size,
            )
        else:
            # Phase 2: mixed mode with topic balancing
            # For now, fall back to sequential
            questions = ExamTrainerRepository.find_questions_sequential(
                exam_filter=config.exam_filter or None,
                topic_filter=config.topic_filter or None,
                offset=0,
                limit=batch_size,
            )

        # Strip solutions from questions
        from app.api.v1.panel.user.exams.trainer_helpers import strip_solutions
        clean_questions = strip_solutions(questions)

        # Create attempt record
        duration = config.time_limit_minutes or 0
        total_points = sum(q.get('points', 0) for q in questions)
        attempt = ExamTrainerRepository.create_adaptive_attempt(
            user_id=user_id,
            question_count=config.question_count or total,
            duration_minutes=duration,
            total_points=total_points,
        )
        attempt_id = str(attempt['attempt_id']) if attempt else None

        # Store practice state in attempt settings
        if attempt_id:
            from app.infrastructure.persistence.repositories.exams.core import ExamRepository
            ExamRepository.update_exam_attempt_settings(attempt_id, {
                'practice_state': {
                    'config': {
                        'mode': config.mode.value,
                        'order': config.order.value,
                        'question_count': config.question_count,
                        'exam_filter': config.exam_filter,
                        'topic_filter': config.topic_filter,
                    },
                    'current_position': 0,
                    'batch_offset': batch_size,
                    'spaced_queue': [],
                    'adaptive': {
                        'recent_results': [],
                        'current_shift': 'stay',
                        'avg_points': 0,
                    },
                    'streak_tracking': {},
                },
            })

        effective_count = config.question_count or total
        has_more = batch_size < effective_count and batch_size < total

        return {
            'attempt_id': attempt_id,
            'questions': clean_questions,
            'total_available': total,
            'has_more': has_more,
            'config': {
                'mode': config.mode.value,
                'order': config.order.value,
                'question_count': config.question_count,
            },
        }
```

- [ ] **Step 2: Check that `update_exam_attempt_settings` exists in ExamRepository**

Run: `cd /home/pascal/Lernsystem/backend && grep -n "def update_exam_attempt_settings\|def update_attempt" app/infrastructure/persistence/repositories/exams/core.py | head -5`

If it does NOT exist, add it to `ExamRepository` in `core.py`:

```python
    @classmethod
    def update_exam_attempt_settings(cls, attempt_id: str, settings: dict) -> None:
        """Update the settings JSONB field on an exam attempt."""
        import json
        execute_query(
            """UPDATE assessments.exam_attempts
               SET settings = COALESCE(settings, '{}'::jsonb) || %s::jsonb
               WHERE attempt_id = %s""",
            [json.dumps(settings), attempt_id],
        )
```

- [ ] **Step 3: Verify the service creates a session**

Run: `cd /home/pascal/Lernsystem/backend && python -c "
from app import create_app
app = create_app()
with app.app_context():
    from app.application.services.exams.rotation_service import RotationService
    from app.domain.models.practice_session import PracticeConfig, PracticeMode, PracticeOrder
    config = PracticeConfig(mode=PracticeMode.DISCOVER, order=PracticeOrder.SEQUENTIAL, question_count=5)
    result = RotationService.generate_practice_session(user_id=1, config=config)
    print(f'attempt_id: {result[\"attempt_id\"]}')
    print(f'questions: {len(result[\"questions\"])}')
    print(f'total: {result[\"total_available\"]}')
    print(f'has_more: {result[\"has_more\"]}')
"`
Expected: attempt_id is a UUID, 5 questions returned, total > 5, has_more is True.

- [ ] **Step 4: Commit**

```bash
git add backend/app/application/services/exams/rotation_service.py backend/app/infrastructure/persistence/repositories/exams/core.py
git commit -m "feat(service): add generate_practice_session for sequential mode"
```

---

### Task 4: API Endpoint — POST /practice-session

**Files:**
- Create: `backend/app/api/v1/panel/user/exams/practice.py`
- Modify: `backend/app/api/v1/panel/user/exams/trainer.py` (add 3 lines to register routes)

- [ ] **Step 1: Create the practice routes file**

```python
"""
Practice Session API — configurable practice mode with sequential/mixed ordering.

DDD Layer: API — delegates to RotationService, no business logic here.
"""

import logging
from flask import jsonify, request
from app.api.middleware.auth import token_required, get_current_user
from app.application.services.exams.rotation_service import RotationService
from app.domain.models.practice_session import (
    PracticeConfig, PracticeMode, PracticeOrder,
)

logger = logging.getLogger(__name__)

VALID_MODES = {m.value for m in PracticeMode}
VALID_ORDERS = {o.value for o in PracticeOrder}


def register_practice_routes(bp):
    """Register practice session routes on the exam trainer blueprint."""

    @bp.route('/practice-config/count', methods=['GET'])
    @token_required
    def practice_question_count():
        """Get available question count for practice config panel."""
        from app.infrastructure.persistence.repositories.exams.trainer import (
            ExamTrainerRepository,
        )
        exam_filter = request.args.getlist('exam_filter')
        topic_filter = request.args.getlist('topic_filter')
        count = ExamTrainerRepository.count_available_questions(
            exam_filter=exam_filter or None,
            topic_filter=topic_filter or None,
        )
        return jsonify({'success': True, 'count': count})

    @bp.route('/practice-session', methods=['POST'])
    @token_required
    def start_practice_session():
        """
        Start a configurable practice session.

        Body: {mode, order, question_count, time_limit_minutes, exam_filter, topic_filter}
        """
        user = get_current_user()
        data = request.get_json(silent=True) or {}

        mode_str = data.get('mode', 'discover')
        order_str = data.get('order', 'sequential')

        if mode_str not in VALID_MODES:
            return jsonify({
                'success': False, 'error': 'INVALID_CONFIG',
                'detail': f'Invalid mode: {mode_str}',
            }), 400

        if order_str not in VALID_ORDERS:
            return jsonify({
                'success': False, 'error': 'INVALID_CONFIG',
                'detail': f'Invalid order: {order_str}',
            }), 400

        config = PracticeConfig(
            mode=PracticeMode(mode_str),
            order=PracticeOrder(order_str),
            question_count=data.get('question_count'),
            time_limit_minutes=data.get('time_limit_minutes'),
            exam_filter=data.get('exam_filter', []),
            topic_filter=data.get('topic_filter', []),
        )

        try:
            result = RotationService.generate_practice_session(
                user_id=user['user_id'], config=config,
            )
        except Exception:
            logger.exception("Practice session creation failed for user=%s", user['user_id'])
            return jsonify({'success': False, 'error': 'SESSION_CREATION_FAILED'}), 500

        if not result.get('questions'):
            return jsonify({
                'success': False, 'error': 'NO_QUESTIONS',
                'total_available': result.get('total_available', 0),
            }), 400

        return jsonify({'success': True, **result})
```

- [ ] **Step 2: Register practice routes in trainer.py**

In `backend/app/api/v1/panel/user/exams/trainer.py`, after line 49 (`register_advanced_routes(trainer_bp)`), add:

```python
from app.api.v1.panel.user.exams.practice import register_practice_routes
register_practice_routes(trainer_bp)
```

- [ ] **Step 3: Test the endpoint manually**

Run: `cd /home/pascal/Lernsystem/backend && python -c "from app import create_app; create_app()" 2>&1 | tail -3`
Expected: No import errors.

Then test via curl (requires active backend):
```bash
curl -s -X POST http://localhost:5000/api/v1/user/exam-trainer/practice-session \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"mode":"discover","order":"sequential","question_count":5}' | python3 -m json.tool | head -20
```
Expected: JSON with `success: true`, `attempt_id`, and 5 questions.

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/v1/panel/user/exams/practice.py backend/app/api/v1/panel/user/exams/trainer.py
git commit -m "feat(api): add POST /practice-session endpoint"
```

---

### Task 5: i18n Keys (de/en/pl)

**Files:**
- Modify: `frontend/src/infrastructure/i18n/locales/de/panel/shared.json`
- Modify: `frontend/src/infrastructure/i18n/locales/en/panel/shared.json`
- Modify: `frontend/src/infrastructure/i18n/locales/pl/panel/shared.json`

- [ ] **Step 1: Add practice keys to all 3 locale files**

Add the following keys under the `examTrainer` object in each file. The exact JSON structure depends on the existing file layout — find the `examTrainer` key and add a `practice` sub-object.

**German (de):**
```json
"practice": {
  "title": "Freies Ueben",
  "modeDiscover": "Entdecken",
  "modeStrengthen": "Festigen",
  "modeExamReady": "Pruefungsreif",
  "orderSequential": "Sequentiell",
  "orderMixed": "Gemischt",
  "questionCount": "Fragenanzahl",
  "countAll": "Alle ({count})",
  "countEndless": "Endlos",
  "timeLimit": "Zeitlimit",
  "timeLimitNone": "Ohne",
  "filter": "Filter",
  "allExams": "Alle Pruefungen",
  "allTopics": "Alle Themen",
  "startButton": "Uebung starten",
  "learningMode": "Lernmodus",
  "streakAlert": "{count}x falsch bei {topic} — {extra} Extra-Fragen dazu?",
  "streakAccept": "Ja",
  "streakDecline": "Nein",
  "spacedRepeat": "Wiederholung",
  "difficultyUp": "Schwierigkeit gestiegen",
  "difficultyDown": "Schwierigkeit gesenkt",
  "summary": {
    "title": "Zusammenfassung",
    "strongestTopic": "Staerkstes Thema",
    "weakestTopic": "Schwaechstes Thema",
    "overallScore": "Gesamtergebnis",
    "timeSpent": "Dauer",
    "backToDashboard": "Zurueck zum Dashboard",
    "topicBreakdown": "Themen-Aufschluesselung",
    "correct": "Richtig",
    "total": "Gesamt"
  },
  "recommendation": {
    "strengthenFocus": "Naechstes Mal: Festigen mit Fokus {topic}",
    "discoverMore": "Naechstes Mal: Neue Themen entdecken",
    "examReady": "Pruefungsreif-Training empfohlen"
  }
}
```

**English (en):**
```json
"practice": {
  "title": "Free Practice",
  "modeDiscover": "Discover",
  "modeStrengthen": "Strengthen",
  "modeExamReady": "Exam Ready",
  "orderSequential": "Sequential",
  "orderMixed": "Mixed",
  "questionCount": "Question Count",
  "countAll": "All ({count})",
  "countEndless": "Endless",
  "timeLimit": "Time Limit",
  "timeLimitNone": "None",
  "filter": "Filter",
  "allExams": "All Exams",
  "allTopics": "All Topics",
  "startButton": "Start Practice",
  "learningMode": "Learning Mode",
  "streakAlert": "{count}x wrong at {topic} — {extra} extra questions?",
  "streakAccept": "Yes",
  "streakDecline": "No",
  "spacedRepeat": "Repeat",
  "difficultyUp": "Difficulty increased",
  "difficultyDown": "Difficulty decreased",
  "summary": {
    "title": "Summary",
    "strongestTopic": "Strongest Topic",
    "weakestTopic": "Weakest Topic",
    "overallScore": "Overall Score",
    "timeSpent": "Duration",
    "backToDashboard": "Back to Dashboard",
    "topicBreakdown": "Topic Breakdown",
    "correct": "Correct",
    "total": "Total"
  },
  "recommendation": {
    "strengthenFocus": "Next time: Strengthen with focus on {topic}",
    "discoverMore": "Next time: Discover new topics",
    "examReady": "Exam Ready training recommended"
  }
}
```

**Polish (pl):**
```json
"practice": {
  "title": "Wolna praktyka",
  "modeDiscover": "Odkrywaj",
  "modeStrengthen": "Utrwalaj",
  "modeExamReady": "Gotowy na egzamin",
  "orderSequential": "Sekwencyjny",
  "orderMixed": "Losowy",
  "questionCount": "Liczba pytan",
  "countAll": "Wszystkie ({count})",
  "countEndless": "Bez konca",
  "timeLimit": "Limit czasu",
  "timeLimitNone": "Brak",
  "filter": "Filtr",
  "allExams": "Wszystkie egzaminy",
  "allTopics": "Wszystkie tematy",
  "startButton": "Rozpocznij cwiczenie",
  "learningMode": "Tryb nauki",
  "streakAlert": "{count}x zle w {topic} — {extra} dodatkowych pytan?",
  "streakAccept": "Tak",
  "streakDecline": "Nie",
  "spacedRepeat": "Powtorka",
  "difficultyUp": "Trudnosc wzrosla",
  "difficultyDown": "Trudnosc spadla",
  "summary": {
    "title": "Podsumowanie",
    "strongestTopic": "Najmocniejszy temat",
    "weakestTopic": "Najslabszy temat",
    "overallScore": "Wynik ogolny",
    "timeSpent": "Czas trwania",
    "backToDashboard": "Powrot do pulpitu",
    "topicBreakdown": "Podzial tematow",
    "correct": "Poprawne",
    "total": "Razem"
  },
  "recommendation": {
    "strengthenFocus": "Nastepnym razem: Utrwalaj z naciskiem na {topic}",
    "discoverMore": "Nastepnym razem: Odkryj nowe tematy",
    "examReady": "Zalecany trening Gotowy na egzamin"
  }
}
```

- [ ] **Step 2: Verify i18n loads without errors**

Run: `cd /home/pascal/Lernsystem/frontend && npx vue-tsc --noEmit 2>&1 | tail -5`
Expected: No errors related to i18n keys.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/infrastructure/i18n/locales/
git commit -m "feat(i18n): add practice mode keys for de/en/pl"
```

---

### Task 6: Frontend API Client

**Files:**
- Create: `frontend/src/infrastructure/api/clients/panel/user/exams/practice.api.ts`
- Modify: `frontend/src/infrastructure/api/clients/panel/user/exams/index.ts`

- [ ] **Step 1: Create practice API client**

```typescript
/**
 * Practice Session API Client
 *
 * Configurable practice mode with sequential/mixed ordering,
 * learning strategies, and intelligent features.
 */

import http from '@/infrastructure/api/http'

export interface PracticeSessionConfig {
  mode: 'discover' | 'strengthen' | 'exam_ready'
  order: 'sequential' | 'mixed'
  question_count?: number | null
  time_limit_minutes?: number | null
  exam_filter?: string[]
  topic_filter?: string[]
}

export interface PracticeSessionResponse {
  success: boolean
  attempt_id: string
  questions: PracticeQuestion[]
  total_available: number
  has_more: boolean
  config: {
    mode: string
    order: string
    question_count: number | null
  }
}

export interface PracticeQuestion {
  question_id: string
  exam_id: string
  question_number: string
  question_text: string
  question_type: string
  points: number
  topics: string[]
  data: Record<string, unknown>
  scenario_title: string | null
  scenario_text: string | null
  exam_title: string
  year: number
  season: string
  semester: string
}

export interface BatchResponse {
  success: boolean
  questions: PracticeQuestion[]
  has_more: boolean
  spaced_repeats: string[]
  streak_alert: StreakAlert | null
  difficulty_shift: 'up' | 'down' | 'stay'
}

export interface StreakAlert {
  topic: string
  consecutive_wrong: number
  suggested_extra: number
}

export interface PracticeSummary {
  total_questions: number
  correct: number
  overall_score: number
  time_spent_seconds: number
  topics: TopicResult[]
  strongest_topic: string
  weakest_topic: string
  recommendation: {
    type: 'strengthen_focus' | 'discover_more' | 'exam_ready'
    topic?: string
  }
}

export interface TopicResult {
  name: string
  total: number
  correct: number
  pct: number
}

export async function practiceGetQuestionCount(
  examFilter?: string[],
  topicFilter?: string[],
): Promise<number> {
  const params = new URLSearchParams()
  examFilter?.forEach(id => params.append('exam_filter', id))
  topicFilter?.forEach(t => params.append('topic_filter', t))
  const response = await http.get<{ success: boolean; count: number }>(
    `/user/exam-trainer/practice-config/count?${params}`,
  )
  return response.data.count
}

export async function practiceStartSession(
  config: PracticeSessionConfig,
): Promise<PracticeSessionResponse> {
  const response = await http.post<PracticeSessionResponse>(
    '/user/exam-trainer/practice-session',
    config,
  )
  return response.data
}

export async function practiceLoadNextBatch(
  attemptId: string,
  recentResults: Array<{ question_id: string; correct: boolean }>,
): Promise<BatchResponse> {
  const response = await http.post<BatchResponse>(
    `/user/exam-trainer/practice-session/${attemptId}/next-batch`,
    { recent_results: recentResults },
  )
  return response.data
}

export async function practiceGetSummary(
  attemptId: string,
): Promise<PracticeSummary> {
  const response = await http.get<{ success: boolean; summary: PracticeSummary }>(
    `/user/exam-trainer/practice-session/${attemptId}/summary`,
  )
  return response.data.summary
}
```

- [ ] **Step 2: Update barrel export**

In `frontend/src/infrastructure/api/clients/panel/user/exams/index.ts`, add:

```typescript
export * from './practice.api'
```

- [ ] **Step 3: Verify TypeScript compiles**

Run: `cd /home/pascal/Lernsystem/frontend && npx vue-tsc --noEmit 2>&1 | grep -i practice | head -5`
Expected: No errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/infrastructure/api/clients/panel/user/exams/practice.api.ts frontend/src/infrastructure/api/clients/panel/user/exams/index.ts
git commit -m "feat(api-client): add practice session API client with types"
```

---

### Task 7: Frontend — PracticeConfigPanel Component

**Files:**
- Create: `frontend/src/presentation/components/panel/user/exam-trainer/PracticeConfigPanel.vue`

- [ ] **Step 1: Create the config panel component**

This replaces the static "Freies Ueben" button card. It shows an expandable panel with all configuration options. When "Sequentiell" is selected, the learning mode row is hidden.

```vue
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { practiceGetQuestionCount } from '@/infrastructure/api/clients/panel/user/exams'
import type { PracticeSessionConfig } from '@/infrastructure/api/clients/panel/user/exams'

const props = defineProps<{
  disabled?: boolean
}>()

const emit = defineEmits<{
  start: [config: PracticeSessionConfig]
}>()

const { t } = useI18n()

const isExpanded = ref(false)
const totalQuestions = ref(0)

// Config state
const mode = ref<'discover' | 'strengthen' | 'exam_ready'>('discover')
const order = ref<'sequential' | 'mixed'>('sequential')
const questionCount = ref<number | null>(10)
const timeLimit = ref<number | null>(null)

const questionOptions = computed(() => [
  { value: 10, label: '10' },
  { value: 20, label: '20' },
  { value: 40, label: '40' },
  { value: 100, label: '100' },
  { value: -1, label: t('panel.examTrainer.practice.countAll', { count: totalQuestions.value }) },
  { value: null, label: t('panel.examTrainer.practice.countEndless') },
])

const timeLimitOptions = [
  { value: null, label: '' },
  { value: 30, label: '30min' },
  { value: 45, label: '45min' },
  { value: 90, label: '90min' },
]

const modeOptions = computed(() => [
  { value: 'discover' as const, icon: '\uD83D\uDD0D', label: t('panel.examTrainer.practice.modeDiscover') },
  { value: 'strengthen' as const, icon: '\uD83D\uDCAA', label: t('panel.examTrainer.practice.modeStrengthen') },
  { value: 'exam_ready' as const, icon: '\uD83C\uDFAF', label: t('panel.examTrainer.practice.modeExamReady') },
])

onMounted(async () => {
  totalQuestions.value = await practiceGetQuestionCount()
})

// When switching to sequential, reset mode (not applicable)
watch(order, (val) => {
  if (val === 'sequential') mode.value = 'discover'
})

function startPractice() {
  const effectiveCount = questionCount.value === -1 ? totalQuestions.value : questionCount.value
  emit('start', {
    mode: mode.value,
    order: order.value,
    question_count: effectiveCount,
    time_limit_minutes: timeLimit.value,
  })
}
</script>

<template>
  <div class="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] overflow-hidden">
    <!-- Header (always visible) -->
    <button
      class="w-full flex items-center gap-3 px-5 py-4 text-left hover:bg-[var(--color-background)] transition-colors"
      @click="isExpanded = !isExpanded"
    >
      <span class="text-2xl">📖</span>
      <div class="flex-1">
        <div class="font-semibold text-[var(--color-text)]">{{ t('panel.examTrainer.practice.title') }}</div>
        <div class="text-sm text-[var(--color-text-secondary)]">
          {{ totalQuestions }} {{ t('panel.examTrainer.practice.questionCount') }}
        </div>
      </div>
      <span class="text-[var(--color-text-secondary)] transition-transform" :class="{ 'rotate-180': isExpanded }">
        ▼
      </span>
    </button>

    <!-- Expandable config -->
    <div v-if="isExpanded" class="px-5 pb-5 space-y-4 border-t border-[var(--color-border)]">
      <!-- Question count -->
      <div>
        <label class="text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider mb-2 block">
          {{ t('panel.examTrainer.practice.questionCount') }}
        </label>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="opt in questionOptions" :key="String(opt.value)"
            class="px-3 py-1.5 text-sm rounded-lg border transition-colors"
            :class="questionCount === opt.value
              ? 'border-blue-500 bg-blue-500/10 text-blue-400'
              : 'border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-blue-500/50'"
            @click="questionCount = opt.value"
          >{{ opt.label }}</button>
        </div>
      </div>

      <!-- Order -->
      <div>
        <label class="text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider mb-2 block">
          {{ t('panel.examTrainer.practice.orderSequential') }} / {{ t('panel.examTrainer.practice.orderMixed') }}
        </label>
        <div class="flex gap-2">
          <button
            class="flex-1 px-3 py-2 text-sm rounded-lg border transition-colors"
            :class="order === 'sequential'
              ? 'border-blue-500 bg-blue-500/10 text-blue-400'
              : 'border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-blue-500/50'"
            @click="order = 'sequential'"
          >{{ t('panel.examTrainer.practice.orderSequential') }}</button>
          <button
            class="flex-1 px-3 py-2 text-sm rounded-lg border transition-colors"
            :class="order === 'mixed'
              ? 'border-blue-500 bg-blue-500/10 text-blue-400'
              : 'border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-blue-500/50'"
            @click="order = 'mixed'"
          >{{ t('panel.examTrainer.practice.orderMixed') }}</button>
        </div>
      </div>

      <!-- Learning mode (only when mixed) -->
      <div v-if="order === 'mixed'">
        <label class="text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider mb-2 block">
          {{ t('panel.examTrainer.practice.learningMode') }}
        </label>
        <div class="flex gap-2">
          <button
            v-for="m in modeOptions" :key="m.value"
            class="flex-1 px-3 py-2 text-sm rounded-lg border transition-colors text-center"
            :class="mode === m.value
              ? 'border-blue-500 bg-blue-500/10 text-blue-400'
              : 'border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-blue-500/50'"
            @click="mode = m.value"
          >{{ m.icon }} {{ m.label }}</button>
        </div>
      </div>

      <!-- Time limit -->
      <div>
        <label class="text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider mb-2 block">
          {{ t('panel.examTrainer.practice.timeLimit') }}
        </label>
        <div class="flex gap-2">
          <button
            v-for="opt in timeLimitOptions" :key="String(opt.value)"
            class="px-3 py-1.5 text-sm rounded-lg border transition-colors"
            :class="timeLimit === opt.value
              ? 'border-blue-500 bg-blue-500/10 text-blue-400'
              : 'border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-blue-500/50'"
            @click="timeLimit = opt.value"
          >{{ opt.label || t('panel.examTrainer.practice.timeLimitNone') }}</button>
        </div>
      </div>

      <!-- Start button -->
      <button
        class="w-full py-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold transition-colors disabled:opacity-50"
        :disabled="disabled || totalQuestions === 0"
        @click="startPractice"
      >{{ t('panel.examTrainer.practice.startButton') }}</button>
    </div>
  </div>
</template>
```

- [ ] **Step 2: Update barrel export**

In `frontend/src/presentation/components/panel/user/exam-trainer/index.ts`, add:

```typescript
export { default as PracticeConfigPanel } from './PracticeConfigPanel.vue'
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/presentation/components/panel/user/exam-trainer/PracticeConfigPanel.vue frontend/src/presentation/components/panel/user/exam-trainer/index.ts
git commit -m "feat(frontend): add PracticeConfigPanel component"
```

---

### Task 8: Frontend — Integrate PracticeConfigPanel into ExamTrainer

**Files:**
- Modify: `frontend/src/presentation/components/panel/user/exam-trainer/ExamTrainer.vue`

- [ ] **Step 1: Import and wire up PracticeConfigPanel**

In `ExamTrainer.vue`:

1. Add import (after line 9):
```typescript
import PracticeConfigPanel from './PracticeConfigPanel.vue'
import { practiceStartSession, type PracticeSessionConfig } from '@/infrastructure/api/clients/panel/user/exams'
```

2. Add handler function (after `startAdaptiveExam` function, around line 107):
```typescript
const startPracticeSession = async (config: PracticeSessionConfig) => {
  isGenerating.value = true
  try {
    const result = await practiceStartSession(config)
    if (!result.attempt_id) return
    simQuestions.value = result.questions as unknown as TrainerQuestion[]
    simAttemptId.value = result.attempt_id
    simDuration.value = config.time_limit_minutes || 0
    // Load anlagen from source exams
    const examIds = [...new Set(result.questions.map(q => q.exam_id))]
    const anlagenArrays = await Promise.all(examIds.map(id => trainerGetAnlagen(id)))
    simAnlagen.value = anlagenArrays.flat()
    view.value = 'simulation'
  } catch (e) {
    logger.error('Practice session failed:', e)
  } finally {
    isGenerating.value = false
  }
}
```

3. In the template, replace the first `examModes` card (the one with `key: 'practice'`) with the PracticeConfigPanel component. Find the section that renders exam mode cards and add before or replace:
```vue
<PracticeConfigPanel :disabled="isGenerating" @start="startPracticeSession" />
```

- [ ] **Step 2: Verify it renders**

Start frontend dev server and navigate to the Pruefungstrainer tab. The "Freies Ueben" section should show an expandable panel instead of a simple button.

- [ ] **Step 3: Test sequential mode end-to-end**

1. Expand "Freies Ueben"
2. Select "10" questions, "Sequentiell", no time limit
3. Click "Uebung starten"
4. Verify questions load in sequential order (1.1, 1.2, 1.3...)

- [ ] **Step 4: Commit**

```bash
git add frontend/src/presentation/components/panel/user/exam-trainer/ExamTrainer.vue
git commit -m "feat(frontend): integrate PracticeConfigPanel into ExamTrainer"
```

---

## Phase 2: Mixed Modes (Discover / Strengthen / Exam Ready)

---

### Task 9: Repository — Topic Prognosis & Weakness Queries

**Files:**
- Modify: `backend/app/infrastructure/persistence/repositories/exams/trainer_part2.py` (append)

- [ ] **Step 1: Add topic weight and weakness queries**

Append to `ExamTrainerRotationMixin` class:

```python
    @staticmethod
    def find_topic_prognosis_weights() -> list:
        """
        Calculate how likely each topic is to appear in an exam.

        Returns list of {topic, probability, exam_count} sorted by probability desc.
        """
        return fetch_all("""
            WITH total AS (
                SELECT COUNT(DISTINCT exam_id) AS cnt
                FROM assessments.exams
                WHERE analysis_status = 'ready' AND published = true
            )
            SELECT eq.topics[1] AS topic,
                   COUNT(DISTINCT eq.exam_id) AS exam_count,
                   COUNT(DISTINCT eq.exam_id)::float / GREATEST(t.cnt, 1) AS probability
            FROM assessments.exam_questions eq
            JOIN assessments.exams e ON e.exam_id = eq.exam_id
            CROSS JOIN total t
            WHERE e.analysis_status = 'ready' AND e.published = true
              AND array_length(eq.topics, 1) > 0
            GROUP BY eq.topics[1], t.cnt
            ORDER BY probability DESC
        """)

    @staticmethod
    def find_user_topic_weakness(user_id: int) -> list:
        """
        Calculate weakness score per topic for a user.

        weakness_score = 1.0 - (correct / seen). Higher = weaker.
        Returns list of {topic, weakness_score, times_seen, times_correct}.
        """
        return fetch_all("""
            SELECT eq.topics[1] AS topic,
                   COALESCE(SUM(uqs.times_seen), 0) AS times_seen,
                   COALESCE(SUM(uqs.times_correct), 0) AS times_correct,
                   CASE WHEN COALESCE(SUM(uqs.times_seen), 0) = 0 THEN 1.0
                        ELSE 1.0 - (SUM(uqs.times_correct)::float
                                     / GREATEST(SUM(uqs.times_seen), 1))
                   END AS weakness_score
            FROM assessments.exam_questions eq
            JOIN assessments.exams e ON e.exam_id = eq.exam_id
            LEFT JOIN assessments.user_question_stats uqs
                ON uqs.question_id = eq.question_id AND uqs.user_id = %s
            WHERE e.analysis_status = 'ready' AND e.published = true
              AND array_length(eq.topics, 1) > 0
            GROUP BY eq.topics[1]
            ORDER BY weakness_score DESC
        """, (user_id,))
```

- [ ] **Step 2: Verify queries return data**

Run: `cd /home/pascal/Lernsystem/backend && python -c "
from app import create_app
app = create_app()
with app.app_context():
    from app.infrastructure.persistence.repositories.exams.trainer import ExamTrainerRepository
    prognosis = ExamTrainerRepository.find_topic_prognosis_weights()
    print(f'Topics with prognosis: {len(prognosis)}')
    for p in prognosis[:3]:
        print(f'  {p[\"topic\"]}: {p[\"probability\"]:.2%}')
    weakness = ExamTrainerRepository.find_user_topic_weakness(1)
    print(f'Topics with weakness: {len(weakness)}')
    for w in weakness[:3]:
        print(f'  {w[\"topic\"]}: weakness={w[\"weakness_score\"]:.2f}')
"`

- [ ] **Step 3: Commit**

```bash
git add backend/app/infrastructure/persistence/repositories/exams/trainer_part2.py
git commit -m "feat(repo): add topic prognosis and user weakness queries"
```

---

### Task 10: Application Service — Mixed Mode Selection Logic

**Files:**
- Modify: `backend/app/application/services/exams/rotation_service.py`

- [ ] **Step 1: Add mixed-mode helper functions**

Add these private methods to `RotationService` and update the `generate_practice_session` method's `else` branch (the Phase 2 placeholder) to use them:

```python
    @staticmethod
    def _resolve_bucket_ratios(mode: PracticeMode) -> dict:
        """Return target ratios for each question bucket based on learning mode."""
        if mode == PracticeMode.DISCOVER:
            return {'unseen': 0.7, 'review': 0.2, 'weak': 0.1}
        elif mode == PracticeMode.STRENGTHEN:
            return {'weak': 0.5, 'review': 0.3, 'unseen': 0.2}
        else:  # EXAM_READY
            return {'weak': 0.4, 'review': 0.3, 'unseen': 0.3}

    @classmethod
    def _build_topic_weights(cls, mode: PracticeMode, user_id: int) -> dict:
        """Build topic weights based on mode. Returns {topic: weight}."""
        prognosis = ExamTrainerRepository.find_topic_prognosis_weights()
        weakness = ExamTrainerRepository.find_user_topic_weakness(user_id)
        weakness_map = {w['topic']: w['weakness_score'] for w in weakness}

        weights = {}
        for p in prognosis:
            topic = p['topic']
            prob = p['probability']
            weak = weakness_map.get(topic, 1.0)
            if mode == PracticeMode.EXAM_READY:
                weights[topic] = prob * (1.0 + weak)
            elif mode == PracticeMode.STRENGTHEN:
                weights[topic] = 1.0 + weak * 0.5
            else:  # DISCOVER
                weights[topic] = 1.0  # equal weight
        return weights

    @classmethod
    def _select_mixed_questions(
        cls, user_id: int, config: PracticeConfig, limit: int,
    ) -> list:
        """Select questions for mixed mode with topic balancing."""
        ratios = cls._resolve_bucket_ratios(config.mode)
        topic_weights = cls._build_topic_weights(config.mode, user_id)

        # Normalize weights
        total_w = sum(topic_weights.values()) or 1.0
        topic_weights = {t: w / total_w for t, w in topic_weights.items()}

        # Collect from buckets
        target_unseen = round(limit * ratios.get('unseen', 0.3))
        target_weak = round(limit * ratios.get('weak', 0.3))
        target_review = limit - target_unseen - target_weak

        unseen = ExamTrainerRepository.find_unseen_questions(user_id, limit=target_unseen + 10)
        weak = ExamTrainerRepository.find_weak_questions(user_id, limit=target_weak + 10)
        review = ExamTrainerRepository.find_review_questions(user_id, limit=target_review + 10)

        selected = []
        selected.extend(unseen[:target_unseen])
        selected.extend(weak[:target_weak])
        selected.extend(review[:target_review])

        # Redistribute if buckets were short
        if len(selected) < limit:
            remaining = limit - len(selected)
            seen_ids = {q['question_id'] for q in selected}
            for pool in [unseen, weak, review]:
                for q in pool:
                    if q['question_id'] not in seen_ids and remaining > 0:
                        selected.append(q)
                        seen_ids.add(q['question_id'])
                        remaining -= 1

        # Topic-interleaved shuffle
        import random
        random.shuffle(selected)
        return selected[:limit]
```

Then replace the Phase 2 placeholder in `generate_practice_session`:

```python
        else:
            # Mixed mode with topic balancing
            questions = cls._select_mixed_questions(
                user_id, config, batch_size,
            )
```

- [ ] **Step 2: Test all 3 modes**

Run quick Python test:
```python
from app.domain.models.practice_session import PracticeConfig, PracticeMode, PracticeOrder
for m in PracticeMode:
    config = PracticeConfig(mode=m, order=PracticeOrder.MIXED, question_count=10)
    result = RotationService.generate_practice_session(user_id=1, config=config)
    print(f'{m.value}: {len(result["questions"])} questions')
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/application/services/exams/rotation_service.py
git commit -m "feat(service): add mixed mode question selection with topic balancing"
```

---

## Phase 3: Intelligent Features

---

### Task 11: Practice Intelligence — Spaced Repetition & Adaptive Difficulty

**Files:**
- Create: `backend/app/application/services/exams/practice_intelligence.py`

- [ ] **Step 1: Create the intelligence engines file**

```python
"""
Practice Intelligence — Spaced Repetition, Adaptive Difficulty,
Streak Detection, Session Summary.

DDD Layer: Application (use cases).
All engines are stateless — they receive state and return decisions.
State is persisted in exam_attempts.settings JSONB by the caller.
"""

import logging
from typing import Optional

from app.domain.models.practice_session import (
    DifficultyShift, SpacedRepetitionEntry, StreakAlert,
)

logger = logging.getLogger(__name__)


class SpacedRepetitionEngine:
    """Schedules wrong answers for later repetition at increasing intervals."""

    INTERVALS = [3, 10, 30, 75]

    @classmethod
    def schedule_repeat(
        cls, question_id: str, wrong_count: int, current_position: int,
    ) -> SpacedRepetitionEntry:
        """Create a repeat entry for a wrong answer."""
        idx = min(wrong_count - 1, len(cls.INTERVALS) - 1)
        offset = cls.INTERVALS[idx]
        return SpacedRepetitionEntry(
            question_id=question_id,
            wrong_count=wrong_count,
            due_at_position=current_position + offset,
        )

    @staticmethod
    def get_due_repeats(
        spaced_queue: list[dict], current_position: int,
    ) -> list[str]:
        """Return question_ids that are due for repetition at current position."""
        return [
            entry['question_id']
            for entry in spaced_queue
            if entry.get('due_at_position', 0) <= current_position
        ]

    @staticmethod
    def remove_completed(
        spaced_queue: list[dict], current_position: int,
    ) -> list[dict]:
        """Remove entries that have been served (past their due position)."""
        return [
            entry for entry in spaced_queue
            if entry.get('due_at_position', 0) > current_position
        ]


class AdaptiveDifficultyEngine:
    """Adjusts question difficulty based on recent answer streaks."""

    CORRECT_STREAK_THRESHOLD = 5
    WRONG_STREAK_THRESHOLD = 3

    @classmethod
    def check_adjustment(cls, recent_results: list[bool]) -> DifficultyShift:
        """
        Check if difficulty should shift based on recent results.

        5+ correct in a row -> UP (harder questions)
        3+ wrong in a row -> DOWN (easier questions)
        Otherwise -> STAY
        """
        if not recent_results:
            return DifficultyShift.STAY

        # Check trailing correct streak
        correct_streak = 0
        for r in reversed(recent_results):
            if r:
                correct_streak += 1
            else:
                break

        if correct_streak >= cls.CORRECT_STREAK_THRESHOLD:
            return DifficultyShift.UP

        # Check trailing wrong streak
        wrong_streak = 0
        for r in reversed(recent_results):
            if not r:
                wrong_streak += 1
            else:
                break

        if wrong_streak >= cls.WRONG_STREAK_THRESHOLD:
            return DifficultyShift.DOWN

        return DifficultyShift.STAY

    @staticmethod
    def apply_to_query(
        shift: DifficultyShift, avg_points: float,
    ) -> tuple[float, float]:
        """
        Return (min_points, max_points) range for next question selection.

        UP: harder questions (above average points)
        DOWN: easier questions (below average points)
        STAY: full range
        """
        if avg_points <= 0:
            return (0, 100)

        if shift == DifficultyShift.UP:
            return (avg_points * 1.3, 100)
        elif shift == DifficultyShift.DOWN:
            return (0, avg_points * 0.7)
        return (0, 100)


class StreakDetector:
    """Detects when a user struggles with a specific topic."""

    ALERT_THRESHOLD = 3

    @classmethod
    def check_topic_streak(
        cls, streak_tracking: dict,
    ) -> Optional[StreakAlert]:
        """
        Check if any topic has a streak of wrong answers.

        streak_tracking: {topic: {consecutive_wrong: int, alerted: bool}}
        Returns StreakAlert if threshold met and not already alerted.
        """
        for topic, data in streak_tracking.items():
            consecutive = data.get('consecutive_wrong', 0)
            alerted = data.get('alerted', False)
            if consecutive >= cls.ALERT_THRESHOLD and not alerted:
                return StreakAlert(
                    topic=topic,
                    consecutive_wrong=consecutive,
                    suggested_extra_count=5,
                )
        return None

    @staticmethod
    def update_tracking(
        streak_tracking: dict, topic: str, correct: bool,
    ) -> dict:
        """Update streak tracking after an answer."""
        if topic not in streak_tracking:
            streak_tracking[topic] = {'consecutive_wrong': 0, 'alerted': False}

        if correct:
            streak_tracking[topic]['consecutive_wrong'] = 0
            streak_tracking[topic]['alerted'] = False
        else:
            streak_tracking[topic]['consecutive_wrong'] += 1

        return streak_tracking


class SessionSummaryBuilder:
    """Builds a structured summary after a practice session."""

    @staticmethod
    def build_summary(answers: list[dict]) -> dict:
        """
        Build session summary from answer records.

        answers: list of {question_id, topics, correct, points, points_earned}
        Returns structured dict (no hardcoded language strings).
        """
        topic_stats: dict = {}
        total_correct = 0
        total_points = 0
        total_earned = 0

        for a in answers:
            topics = a.get('topics', [])
            topic = topics[0] if topics else 'unknown'
            correct = a.get('correct', False)
            points = a.get('points', 0)
            earned = a.get('points_earned', 0)

            if topic not in topic_stats:
                topic_stats[topic] = {'total': 0, 'correct': 0}
            topic_stats[topic]['total'] += 1
            if correct:
                topic_stats[topic]['correct'] += 1
                total_correct += 1
            total_points += points
            total_earned += earned

        topics_list = [
            {
                'name': t,
                'total': s['total'],
                'correct': s['correct'],
                'pct': round(s['correct'] / max(s['total'], 1) * 100, 1),
            }
            for t, s in sorted(topic_stats.items(), key=lambda x: x[0])
        ]

        strongest = max(topics_list, key=lambda x: x['pct']) if topics_list else None
        weakest = min(topics_list, key=lambda x: x['pct']) if topics_list else None

        # Recommendation logic
        if weakest and weakest['pct'] < 50:
            recommendation = {
                'type': 'strengthen_focus',
                'topic': weakest['name'],
            }
        elif total_correct / max(len(answers), 1) > 0.8:
            recommendation = {'type': 'exam_ready'}
        else:
            recommendation = {'type': 'discover_more'}

        return {
            'total_questions': len(answers),
            'correct': total_correct,
            'overall_score': round(
                total_correct / max(len(answers), 1) * 100, 1
            ),
            'topics': topics_list,
            'strongest_topic': strongest['name'] if strongest else None,
            'weakest_topic': weakest['name'] if weakest else None,
            'recommendation': recommendation,
        }
```

- [ ] **Step 2: Verify imports work**

Run: `cd /home/pascal/Lernsystem/backend && python -c "
from app.application.services.exams.practice_intelligence import (
    SpacedRepetitionEngine, AdaptiveDifficultyEngine, StreakDetector, SessionSummaryBuilder
)
from app.domain.models.practice_session import DifficultyShift
# Quick smoke test
shift = AdaptiveDifficultyEngine.check_adjustment([True]*6)
assert shift == DifficultyShift.UP
shift = AdaptiveDifficultyEngine.check_adjustment([False]*4)
assert shift == DifficultyShift.DOWN
print('All intelligence engines OK')
"`

- [ ] **Step 3: Commit**

```bash
git add backend/app/application/services/exams/practice_intelligence.py
git commit -m "feat(service): add practice intelligence engines (spaced rep, adaptive, streak, summary)"
```

---

### Task 12: API — Next-Batch & Summary Endpoints

**Files:**
- Modify: `backend/app/api/v1/panel/user/exams/practice.py`

- [ ] **Step 1: Add next-batch and summary endpoints**

Add these routes inside `register_practice_routes(bp)` in `practice.py`, after the existing `start_practice_session` route:

```python
    @bp.route('/practice-session/<attempt_id>/next-batch', methods=['POST'])
    @token_required
    def practice_next_batch(attempt_id):
        """
        Load next batch of questions with intelligence applied.

        Reads practice_state from attempt settings, applies spaced repetition,
        adaptive difficulty, and streak detection, then returns next questions.
        """
        from app.infrastructure.persistence.repositories.exams.core import ExamRepository
        from app.application.services.exams.practice_intelligence import (
            SpacedRepetitionEngine, AdaptiveDifficultyEngine, StreakDetector,
        )
        user = get_current_user()

        # Load attempt and verify ownership
        attempt = ExamRepository.find_attempt_by_id(attempt_id)
        if not attempt:
            return jsonify({'success': False, 'error': 'ATTEMPT_NOT_FOUND'}), 404
        if str(attempt.get('user_id')) != str(user['user_id']):
            return jsonify({'success': False, 'error': 'ACCESS_DENIED'}), 403
        if attempt.get('status') == 'completed':
            return jsonify({'success': False, 'error': 'SESSION_COMPLETED'}), 409

        settings = attempt.get('settings') or {}
        state = settings.get('practice_state', {})
        config_data = state.get('config', {})

        data = request.get_json(silent=True) or {}
        recent_results = data.get('recent_results', [])

        # Update intelligence state
        adaptive_state = state.get('adaptive', {'recent_results': [], 'current_shift': 'stay', 'avg_points': 0})
        streak_state = state.get('streak_tracking', {})
        spaced_queue = state.get('spaced_queue', [])
        position = state.get('current_position', 0)

        for r in recent_results:
            adaptive_state['recent_results'].append(r.get('correct', False))
            # Keep last 10 results
            adaptive_state['recent_results'] = adaptive_state['recent_results'][-10:]
            position += 1

            # Update streak tracking per topic
            q_topic = r.get('topic', 'unknown')
            StreakDetector.update_tracking(streak_state, q_topic, r.get('correct', False))

            # Schedule spaced repetition for wrong answers
            if not r.get('correct', False):
                wrong_count = sum(
                    1 for e in spaced_queue if e.get('question_id') == r['question_id']
                ) + 1
                entry = SpacedRepetitionEngine.schedule_repeat(
                    r['question_id'], wrong_count, position,
                )
                spaced_queue.append({
                    'question_id': entry.question_id,
                    'wrong_count': entry.wrong_count,
                    'due_at_position': entry.due_at_position,
                })

        # Check intelligence outputs
        difficulty = AdaptiveDifficultyEngine.check_adjustment(adaptive_state['recent_results'])
        streak_alert_obj = StreakDetector.check_topic_streak(streak_state)
        due_repeats = SpacedRepetitionEngine.get_due_repeats(spaced_queue, position)
        spaced_queue = SpacedRepetitionEngine.remove_completed(spaced_queue, position)

        # Mark streak as alerted
        if streak_alert_obj:
            streak_state[streak_alert_obj.topic]['alerted'] = True

        # Load next batch
        batch_offset = state.get('batch_offset', 0)
        from app.infrastructure.persistence.repositories.exams.trainer import ExamTrainerRepository
        questions = ExamTrainerRepository.find_questions_sequential(
            exam_filter=config_data.get('exam_filter') or None,
            topic_filter=config_data.get('topic_filter') or None,
            offset=batch_offset,
            limit=50,
        )
        from app.api.v1.panel.user.exams.trainer_helpers import strip_solutions
        clean = strip_solutions(questions)

        has_more = len(questions) == 50

        # Persist updated state
        state['current_position'] = position
        state['batch_offset'] = batch_offset + len(questions)
        state['spaced_queue'] = spaced_queue
        state['adaptive'] = {
            'recent_results': adaptive_state['recent_results'],
            'current_shift': difficulty.value,
            'avg_points': adaptive_state.get('avg_points', 0),
        }
        state['streak_tracking'] = streak_state
        ExamRepository.update_exam_attempt_settings(attempt_id, {'practice_state': state})

        return jsonify({
            'success': True,
            'questions': clean,
            'has_more': has_more,
            'spaced_repeats': due_repeats,
            'streak_alert': {
                'topic': streak_alert_obj.topic,
                'consecutive_wrong': streak_alert_obj.consecutive_wrong,
                'suggested_extra': streak_alert_obj.suggested_extra_count,
            } if streak_alert_obj else None,
            'difficulty_shift': difficulty.value,
        })

    @bp.route('/practice-session/<attempt_id>/summary', methods=['GET'])
    @token_required
    def practice_summary(attempt_id):
        """Get session summary with topic breakdown and recommendation."""
        from app.infrastructure.persistence.repositories.exams.core import ExamRepository
        from app.application.services.exams.practice_intelligence import SessionSummaryBuilder

        user = get_current_user()
        attempt = ExamRepository.find_attempt_by_id(attempt_id)
        if not attempt:
            return jsonify({'success': False, 'error': 'ATTEMPT_NOT_FOUND'}), 404
        if str(attempt.get('user_id')) != str(user['user_id']):
            return jsonify({'success': False, 'error': 'ACCESS_DENIED'}), 403

        # Load answers for this attempt
        from app.infrastructure.persistence.repositories.exams.questions import ExamQuestionRepository
        answers = ExamQuestionRepository.find_answers_by_attempt(attempt_id)

        summary = SessionSummaryBuilder.build_summary(answers)
        return jsonify({'success': True, 'summary': summary})
```

- [ ] **Step 2: Check that `find_attempt_by_id` and `find_answers_by_attempt` exist**

Run: `cd /home/pascal/Lernsystem/backend && grep -n "def find_attempt_by_id\|def find_answers_by_attempt" app/infrastructure/persistence/repositories/exams/core.py app/infrastructure/persistence/repositories/exams/questions.py`

If `find_attempt_by_id` does not exist in ExamRepository, add it. If `find_answers_by_attempt` does not exist in ExamQuestionRepository, add it. These are standard repository lookups.

- [ ] **Step 3: Verify the file stays under 500 LOC**

Run: `wc -l backend/app/api/v1/panel/user/exams/practice.py`
Expected: Under 250 lines.

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/v1/panel/user/exams/practice.py
git commit -m "feat(api): add next-batch and summary endpoints with intelligence"
```

---

### Task 13: Frontend — Batch Loading & Streak Alerts in SimulationMode

**Files:**
- Modify: `frontend/src/presentation/components/panel/user/exam-trainer/SimulationMode.vue`

- [ ] **Step 1: Add batch loading and streak alert support**

Add these to SimulationMode.vue:

1. New props:
```typescript
hasMore?: boolean
attemptId?: string
```

2. Import practice API:
```typescript
import { practiceLoadNextBatch, type StreakAlert } from '@/infrastructure/api/clients/panel/user/exams'
```

3. Add state for streak alert and batch loading:
```typescript
const streakAlert = ref<StreakAlert | null>(null)
const isLoadingBatch = ref(false)
const recentResults = ref<Array<{ question_id: string; correct: boolean; topic: string }>>([])
```

4. Add batch loading watcher — when `currentIndex` approaches end of questions array and `hasMore` is true, load more:
```typescript
watch(currentIndex, async (idx) => {
  if (props.hasMore && props.attemptId && !isLoadingBatch.value
      && idx >= props.questions.length - 5) {
    isLoadingBatch.value = true
    try {
      const batch = await practiceLoadNextBatch(props.attemptId, recentResults.value)
      recentResults.value = []
      if (batch.questions.length) {
        emit('append-questions', batch.questions)
      }
      if (batch.streak_alert) {
        streakAlert.value = batch.streak_alert
      }
    } finally {
      isLoadingBatch.value = false
    }
  }
})
```

5. Add emit for appending questions:
```typescript
'append-questions': [questions: TrainerQuestion[]]
```

6. After each answer submission, track result for batch loading:
```typescript
// In the answer submit handler, after grading:
recentResults.value.push({
  question_id: currentQuestion.value.question_id,
  correct: result.is_correct,
  topic: currentQuestion.value.topics?.[0] || 'unknown',
})
```

7. Add streak alert template (shown as dismissible banner):
```vue
<div v-if="streakAlert" class="mx-4 mb-3 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/30 flex items-center gap-3">
  <span class="text-xl">⚠️</span>
  <span class="flex-1 text-sm text-yellow-200">
    {{ $t('panel.examTrainer.practice.streakAlert', {
      count: streakAlert.consecutive_wrong,
      topic: streakAlert.topic,
      extra: streakAlert.suggested_extra
    }) }}
  </span>
  <button class="text-xs px-2 py-1 rounded bg-yellow-500/20 text-yellow-300" @click="streakAlert = null">
    {{ $t('panel.examTrainer.practice.streakDecline') }}
  </button>
</div>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/presentation/components/panel/user/exam-trainer/SimulationMode.vue
git commit -m "feat(frontend): add batch loading and streak alerts to SimulationMode"
```

---

### Task 14: Frontend — SessionSummary Component

**Files:**
- Create: `frontend/src/presentation/components/panel/user/exam-trainer/SessionSummary.vue`
- Modify: `frontend/src/presentation/components/panel/user/exam-trainer/index.ts`

- [ ] **Step 1: Create SessionSummary component**

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { practiceGetSummary, type PracticeSummary } from '@/infrastructure/api/clients/panel/user/exams'

const props = defineProps<{
  attemptId: string
}>()

const emit = defineEmits<{
  'back-to-dashboard': []
  'start-recommended': [config: { mode: string; topic?: string }]
}>()

const { t } = useI18n()
const summary = ref<PracticeSummary | null>(null)
const isLoading = ref(true)

onMounted(async () => {
  try {
    summary.value = await practiceGetSummary(props.attemptId)
  } finally {
    isLoading.value = false
  }
})

function getRecommendationText(rec: PracticeSummary['recommendation']): string {
  if (rec.type === 'strengthen_focus' && rec.topic) {
    return t('panel.examTrainer.practice.recommendation.strengthenFocus', { topic: rec.topic })
  }
  if (rec.type === 'exam_ready') {
    return t('panel.examTrainer.practice.recommendation.examReady')
  }
  return t('panel.examTrainer.practice.recommendation.discoverMore')
}
</script>

<template>
  <div class="max-w-3xl mx-auto p-6">
    <div v-if="isLoading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
    </div>

    <div v-else-if="summary" class="space-y-6">
      <!-- Header -->
      <div class="text-center">
        <h2 class="text-2xl font-bold text-[var(--color-text)]">
          {{ t('panel.examTrainer.practice.summary.title') }}
        </h2>
        <div class="mt-2 text-4xl font-bold" :class="summary.overall_score >= 70 ? 'text-green-400' : summary.overall_score >= 50 ? 'text-yellow-400' : 'text-red-400'">
          {{ summary.overall_score }}%
        </div>
        <div class="text-sm text-[var(--color-text-secondary)]">
          {{ summary.correct }} / {{ summary.total_questions }} {{ t('panel.examTrainer.practice.summary.correct') }}
        </div>
      </div>

      <!-- Strongest / Weakest -->
      <div class="grid grid-cols-2 gap-4">
        <div class="p-4 rounded-lg bg-green-500/10 border border-green-500/30 text-center">
          <div class="text-xs uppercase text-green-400 mb-1">{{ t('panel.examTrainer.practice.summary.strongestTopic') }}</div>
          <div class="font-semibold text-green-300">{{ summary.strongest_topic }}</div>
        </div>
        <div class="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-center">
          <div class="text-xs uppercase text-red-400 mb-1">{{ t('panel.examTrainer.practice.summary.weakestTopic') }}</div>
          <div class="font-semibold text-red-300">{{ summary.weakest_topic }}</div>
        </div>
      </div>

      <!-- Topic breakdown bars -->
      <div>
        <h3 class="text-sm font-semibold text-[var(--color-text-secondary)] uppercase mb-3">
          {{ t('panel.examTrainer.practice.summary.topicBreakdown') }}
        </h3>
        <div class="space-y-2">
          <div v-for="topic in summary.topics" :key="topic.name" class="flex items-center gap-3">
            <span class="w-40 text-sm text-[var(--color-text)] truncate">{{ topic.name }}</span>
            <div class="flex-1 h-5 bg-gray-700 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all"
                :class="topic.pct >= 70 ? 'bg-green-500' : topic.pct >= 50 ? 'bg-yellow-500' : 'bg-red-500'"
                :style="{ width: topic.pct + '%' }"
              />
            </div>
            <span class="w-20 text-right text-sm text-[var(--color-text-secondary)]">
              {{ topic.correct }}/{{ topic.total }} ({{ topic.pct }}%)
            </span>
          </div>
        </div>
      </div>

      <!-- Recommendation -->
      <div class="p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
        <div class="text-sm text-blue-300">{{ getRecommendationText(summary.recommendation) }}</div>
      </div>

      <!-- Actions -->
      <div class="flex gap-3">
        <button
          class="flex-1 py-3 rounded-lg border border-[var(--color-border)] text-[var(--color-text)] hover:bg-[var(--color-background)] transition-colors"
          @click="emit('back-to-dashboard')"
        >{{ t('panel.examTrainer.practice.summary.backToDashboard') }}</button>
        <button
          class="flex-1 py-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold transition-colors"
          @click="emit('start-recommended', summary.recommendation)"
        >{{ getRecommendationText(summary.recommendation) }}</button>
      </div>
    </div>
  </div>
</template>
```

- [ ] **Step 2: Update barrel export**

Add to `frontend/src/presentation/components/panel/user/exam-trainer/index.ts`:

```typescript
export { default as SessionSummary } from './SessionSummary.vue'
```

- [ ] **Step 3: Wire SessionSummary into ExamTrainer.vue**

In ExamTrainer.vue, add a `'summary'` option to the `View` type and add the component render:

```typescript
type View = 'dashboard' | 'simulation' | 'review' | 'summary'
const summaryAttemptId = ref<string | null>(null)
```

After simulation completes (when `view` changes back from simulation), show summary:
```typescript
const onSimulationComplete = () => {
  summaryAttemptId.value = simAttemptId.value
  view.value = 'summary'
}
```

Template addition:
```vue
<SessionSummary
  v-else-if="view === 'summary' && summaryAttemptId"
  :attempt-id="summaryAttemptId"
  @back-to-dashboard="view = 'dashboard'; summaryAttemptId = null"
  @start-recommended="(rec) => { /* start new practice based on recommendation */ }"
/>
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/presentation/components/panel/user/exam-trainer/SessionSummary.vue frontend/src/presentation/components/panel/user/exam-trainer/index.ts frontend/src/presentation/components/panel/user/exam-trainer/ExamTrainer.vue
git commit -m "feat(frontend): add SessionSummary component and wire into ExamTrainer"
```

---

## Phase 4: Integration Testing & Polish

---

### Task 15: End-to-End Test — All Modes

- [ ] **Step 1: Test sequential mode with "All" questions**

Navigate to Pruefungstrainer, expand Freies Ueben, select "Alle (409)", "Sequentiell", start.
Verify: Questions load in order, batch loading works when scrolling past first 50.

- [ ] **Step 2: Test mixed mode — Discover**

Select 20 questions, "Gemischt", "Entdecken", start.
Verify: Questions are shuffled, topics are balanced.

- [ ] **Step 3: Test mixed mode — Pruefungsreif**

Select 20 questions, "Gemischt", "Pruefungsreif", start.
Verify: Topics weighted by prognosis + weakness.

- [ ] **Step 4: Test Endless mode**

Select "Endlos", "Gemischt", start.
Answer some questions, verify batch loading, then manually stop.
Verify: SessionSummary shows after completion.

- [ ] **Step 5: Test streak alert**

Answer 3+ questions wrong in the same topic.
Verify: Streak alert banner appears.

- [ ] **Step 6: Build verification**

```bash
cd /home/pascal/Lernsystem/frontend && npm run build
cd /home/pascal/Lernsystem/backend && python -c "from app import create_app; create_app()"
```
Expected: Both pass without errors.

- [ ] **Step 7: Final commit**

```bash
git add -A
git commit -m "feat(exam-trainer): complete practice mode redesign with all features"
```

---

## Summary

| Phase | Tasks | What it delivers |
|-------|-------|-----------------|
| 1 | Tasks 1-8 | Sequential mode working end-to-end, Claude Cowork can test all 409 questions |
| 2 | Tasks 9-10 | Mixed mode with 3 learning strategies and topic balancing |
| 3 | Tasks 11-14 | Spaced repetition, adaptive difficulty, streak alerts, session summary |
| 4 | Task 15 | Integration testing and build verification |
