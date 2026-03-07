# Exam-to-Course Integration — Phase 1 Implementation Plan (Kurs-Generator)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Admin kann einen IHK-Pruefungskurs automatisch generieren lassen — aus 442 echten IHK-Fragen werden strukturierte Kapitel mit 12 Lernmethoden erstellt, die im bestehenden Editor editierbar sind.

**Architecture:** Neuer ExamCourseGeneratorService im Application Layer. Liest Exam-Questions, gruppiert nach Topic, mappt question_types auf passende Lernmethoden, ruft KI fuer Deep Explanations auf, erstellt echte `courses.*` + `learning_methods.*` Records. DDD-konform: Domain VOs → Application Service → Infrastructure Repos.

**Tech Stack:** Flask 3.0, psycopg3 (fetch_one/fetch_all/insert_returning), Vue 3 Composition API, bestehender AIAdapter, bestehender CourseRepository/ChapterRepository/LMInstanceRepository.

---

## Context

### Design Document
Full design: `docs/plans/2026-03-06-exam-course-integration-design.md`

### Relevant Existing Code

| File | Purpose |
|------|---------|
| `app/infrastructure/persistence/repositories/courses/management/crud.py` | `CourseRepository.create(course_data)` — needs `title`, `creator_user_id` |
| `app/infrastructure/persistence/repositories/courses/content/chapters.py` | `ChapterRepository.create(chapter_data)` — needs `course_id`, `title`, auto-orders |
| `app/infrastructure/persistence/repositories/learning_method/execution/instances.py` | `LearningMethodInstanceRepository.create(data)` — needs `chapter_id`, `method_type` (0-11), `title`, `data` (JSONB) |
| `app/infrastructure/persistence/repositories/exams/core_part2.py` | `ExamQuestionRepository.find_by_topics(topics)` — uses `&&` overlap |
| `app/infrastructure/ai/adapter.py` | `AIAdapter(provider, model).send_request(prompt, ...)` → `{output_text, total_tokens, ...}` |
| `app/api/v1/panel/admin/exams/__init__.py` | Blueprint registration pattern: import + `api_v1.register_blueprint(bp)` |
| `app/domain/ports/ai/ports.py` | ABC port pattern with `@abstractmethod` |
| `frontend/src/infrastructure/api/clients/panel/admin/exams/archive.api.ts` | Frontend API client pattern |

### LM Type Mapping (from design)

| exam question_type | Target LM | method_type |
|---|---|---|
| `mcq` | Flashcards | 6 |
| `mcq` (zuordnung) | Drag & Drop | 7 |
| `fill_blank` | Cloze Test | 8 |
| `essay` | IHK-Style Tasks | 10 |
| `calculation` | Math Interactive | 5 |
| `code` | IHK-Style Tasks | 10 |
| `case_study` | Multi-Step Practical | 11 |
| (alle Topics) | Deep Explanation | 0 |

### DB Helpers

```python
from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query, insert_returning
```

- `fetch_one(query, params)` → `Dict | None`
- `fetch_all(query, params)` → `List[Dict]`
- `insert_returning(table, params_dict, returning_columns)` → `Dict`

---

## Task 1: Domain VOs — ExamCoursePlan + LMMapping

**Files:**
- Create: `backend/app/domain/models/exam_course_plan.py`

**Step 1: Write the Value Objects**

```python
"""
Exam Course Plan — Domain Value Objects.

Describes the structure of an auto-generated IHK exam course
before it's persisted to the database.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class LMMapping:
    """Maps a question_type to a target learning method."""
    question_type: str
    target_lm_type: int
    transform_fn: str


@dataclass(frozen=True)
class ChapterPlan:
    """Plan for a single chapter (= one topic)."""
    topic: str
    question_ids: List[str]
    lm_types: List[int]
    point_weight: float
    question_count: int


@dataclass(frozen=True)
class ExamCoursePlan:
    """Complete plan for an auto-generated exam course."""
    title: str
    exam_type: str
    region: str
    chapters: List[ChapterPlan] = field(default_factory=list)
    simulation_exam_ids: List[str] = field(default_factory=list)

    @property
    def total_questions(self) -> int:
        return sum(ch.question_count for ch in self.chapters)

    @property
    def total_points(self) -> float:
        return sum(ch.point_weight for ch in self.chapters)

    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'exam_type': self.exam_type,
            'region': self.region,
            'total_questions': self.total_questions,
            'total_points': self.total_points,
            'chapters': [
                {
                    'topic': ch.topic,
                    'question_count': ch.question_count,
                    'lm_types': ch.lm_types,
                    'point_weight': ch.point_weight,
                }
                for ch in self.chapters
            ],
            'simulation_exam_ids': self.simulation_exam_ids,
        }
```

**Step 2: Verify import**

```bash
cd backend && python -c "from app.domain.models.exam_course_plan import ExamCoursePlan, ChapterPlan, LMMapping; print('OK')"
```

Expected: `OK`

**Step 3: Commit**

```bash
git add backend/app/domain/models/exam_course_plan.py
git commit -m "feat(exams): add ExamCoursePlan, ChapterPlan, LMMapping domain VOs"
```

---

## Task 2: Domain Service — LMContentMapper

**Files:**
- Create: `backend/app/domain/services/lm_content_mapper.py`

**Step 1: Write the domain service**

This is the core mapping logic: given exam questions for a topic, decide which LMs to create and transform question data into LM-compatible JSONB format.

```python
"""
LM Content Mapper — Domain Service.

Maps exam question_types to learning method types and transforms
question data into LM-compatible JSONB format.

Pure domain logic — no Flask, no SQL, no AI imports.
"""
import hashlib
import json
from typing import Dict, List, Any, Set


# question_type → List of suitable LM types
QUESTION_TYPE_TO_LM: Dict[str, List[int]] = {
    'mcq':         [6, 7],   # Flashcards, Drag & Drop
    'fill_blank':  [8],      # Cloze Test
    'essay':       [10],     # IHK-Style Tasks
    'calculation': [5],      # Math Interactive
    'code':        [10],     # IHK-Style Tasks
    'case_study':  [11],     # Multi-Step Practical
}

# Always included in every chapter
ALWAYS_INCLUDE = [0]  # Deep Explanation


class LMContentMapper:
    """Maps exam questions to learning method content."""

    @staticmethod
    def select_lm_types(questions: List[Dict]) -> List[int]:
        """Select 3-5 LM types based on question types in the topic."""
        lm_set: Set[int] = set(ALWAYS_INCLUDE)

        for q in questions:
            q_type = q.get('question_type', 'essay')
            for lm_type in QUESTION_TYPE_TO_LM.get(q_type, [10]):
                lm_set.add(lm_type)

        return sorted(lm_set)

    @staticmethod
    def question_hash(question_id: str) -> str:
        """SHA-256 hash of question_id — survives course regeneration."""
        return hashlib.sha256(question_id.encode()).hexdigest()

    @staticmethod
    def map_to_flashcards(questions: List[Dict]) -> Dict[str, Any]:
        """MCQ questions → Flashcard JSONB format."""
        cards = []
        for q in questions:
            if q.get('question_type') != 'mcq':
                continue
            renderer = q.get('data', {})
            q_items = renderer.get('questions', [])
            for item in q_items:
                cards.append({
                    'front': item.get('question', q.get('question_text', '')),
                    'back': _extract_correct_answer(item),
                    'source_question_id': q.get('question_id'),
                })
        return {'cards': cards}

    @staticmethod
    def map_to_cloze(questions: List[Dict]) -> Dict[str, Any]:
        """fill_blank questions → Cloze JSONB format."""
        sentences = []
        for q in questions:
            if q.get('question_type') != 'fill_blank':
                continue
            renderer = q.get('data', {})
            for s in renderer.get('sentences', []):
                sentences.append({
                    'text': s.get('text', ''),
                    'answers': s.get('answers', []),
                    'source_question_id': q.get('question_id'),
                })
        return {'sentences': sentences}

    @staticmethod
    def map_to_drag_drop(questions: List[Dict]) -> Dict[str, Any]:
        """MCQ with assignment pattern → Drag & Drop JSONB format."""
        items = []
        for q in questions:
            if q.get('question_type') != 'mcq':
                continue
            renderer = q.get('data', {})
            q_items = renderer.get('questions', [])
            for item in q_items:
                options = item.get('options', [])
                correct = item.get('correctAnswers', [])
                if len(options) >= 3 and len(correct) >= 1:
                    items.append({
                        'question': item.get('question', ''),
                        'answer': options[correct[0]] if correct[0] < len(options) else '',
                        'source_question_id': q.get('question_id'),
                    })
        return {'pairs': items}

    @staticmethod
    def map_to_math_interactive(questions: List[Dict]) -> Dict[str, Any]:
        """Calculation questions → Math Interactive JSONB format."""
        problems = []
        for q in questions:
            if q.get('question_type') != 'calculation':
                continue
            renderer = q.get('data', {})
            for p in renderer.get('problems', []):
                problems.append({
                    'question': p.get('question', q.get('question_text', '')),
                    'answer': p.get('answer', ''),
                    'hint': p.get('hint', ''),
                    'source_question_id': q.get('question_id'),
                })
        return {'problems': problems}

    @staticmethod
    def map_to_ihk_tasks(questions: List[Dict]) -> Dict[str, Any]:
        """Essay/Code/CaseStudy → IHK-Style Tasks JSONB format."""
        tasks = []
        for q in questions:
            if q.get('question_type') not in ('essay', 'code', 'case_study'):
                continue
            tasks.append({
                'question': q.get('question_text', ''),
                'points': q.get('points', 5),
                'solution': q.get('solution_text', ''),
                'question_type': q.get('question_type'),
                'source_question_id': q.get('question_id'),
            })
        return {'tasks': tasks}

    @staticmethod
    def map_to_multi_step(questions: List[Dict]) -> Dict[str, Any]:
        """Case study questions → Multi-Step Practical JSONB format."""
        steps = []
        for q in questions:
            if q.get('question_type') != 'case_study':
                continue
            renderer = q.get('data', {})
            scenario = renderer.get('scenario', q.get('scenario_text', ''))
            sub_qs = renderer.get('questions', [])
            steps.append({
                'scenario': scenario,
                'questions': sub_qs,
                'source_question_id': q.get('question_id'),
            })
        return {'steps': steps}


def _extract_correct_answer(item: Dict) -> str:
    """Extract the correct answer text from MCQ options."""
    options = item.get('options', [])
    correct_indices = item.get('correctAnswers', [])
    if correct_indices and options:
        idx = correct_indices[0]
        if idx < len(options):
            return options[idx]
    return item.get('explanation', '')
```

**Step 2: Verify import**

```bash
cd backend && python -c "from app.domain.services.lm_content_mapper import LMContentMapper; print('OK')"
```

Expected: `OK`

**Step 3: Commit**

```bash
git add backend/app/domain/services/lm_content_mapper.py
git commit -m "feat(exams): add LMContentMapper domain service for question→LM mapping"
```

---

## Task 3: Application Service — ExamCourseGeneratorService.preview()

**Files:**
- Create: `backend/app/application/services/exams/course_generator_service.py`

**Step 1: Write the preview service**

This service orchestrates: fetch questions → group by topic → select LMs → build ExamCoursePlan VO.

```python
"""
Exam Course Generator Service — Application Layer.

Orchestrates course generation from exam archive questions.
Two phases: preview() returns a plan, generate() persists it.
"""
import logging
from typing import Dict, Any, Optional, List

from app.domain.models.exam_course_plan import ExamCoursePlan, ChapterPlan
from app.domain.services.lm_content_mapper import LMContentMapper
from app.infrastructure.persistence.database.connection import fetch_all

logger = logging.getLogger(__name__)


class ExamCourseGeneratorService:
    """Generates structured courses from real IHK exam questions."""

    @staticmethod
    def preview(
        exam_type_key: str,
        region: str = 'alle',
    ) -> ExamCoursePlan:
        """
        Build a course plan without persisting anything.

        1. Fetch all ready exam questions for the given type + region
        2. Group by topic
        3. For each topic: determine LM types
        4. Return ExamCoursePlan VO

        Args:
            exam_type_key: e.g. 'IHK_FISI'
            region: e.g. 'bw' or 'alle'

        Returns:
            ExamCoursePlan value object with chapter plans
        """
        # 1. Fetch questions with region filter
        questions = _fetch_questions_for_course(exam_type_key, region)

        if not questions:
            logger.warning(
                "No questions found for type=%s region=%s",
                exam_type_key, region,
            )
            return ExamCoursePlan(
                title=f'{exam_type_key} — {region}',
                exam_type=exam_type_key,
                region=region,
            )

        # 2. Group by topic
        topic_groups = _group_by_topic(questions)

        # 3. Build chapter plans (sorted by total points descending)
        chapters = []
        for topic, topic_questions in sorted(
            topic_groups.items(),
            key=lambda x: sum(q.get('points', 0) for q in x[1]),
            reverse=True,
        ):
            lm_types = LMContentMapper.select_lm_types(topic_questions)
            total_points = sum(q.get('points', 0) for q in topic_questions)

            chapters.append(ChapterPlan(
                topic=topic,
                question_ids=[q['question_id'] for q in topic_questions],
                lm_types=lm_types,
                point_weight=total_points,
                question_count=len(topic_questions),
            ))

        # 4. Find simulation exams (distinct exam_ids for mock chapters)
        simulation_exam_ids = _find_simulation_exams(exam_type_key, region)

        title = _build_title(exam_type_key, region)

        return ExamCoursePlan(
            title=title,
            exam_type=exam_type_key,
            region=region,
            chapters=chapters,
            simulation_exam_ids=simulation_exam_ids,
        )

    @staticmethod
    def generate(
        plan: ExamCoursePlan,
        creator_user_id: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Persist the plan as a real course.
        Delegated to CourseGeneratorBuilder.

        Args:
            plan: ExamCoursePlan from preview()
            creator_user_id: Admin user ID
            options: {provider, model} for AI content generation

        Returns:
            {course_id, chapters_count, lm_count, tokens_used}
        """
        from app.application.services.exams.course_generator_builder import (
            CourseGeneratorBuilder,
        )

        return CourseGeneratorBuilder.build(plan, creator_user_id, options)


def _fetch_questions_for_course(
    exam_type_key: str, region: str
) -> List[Dict]:
    """Fetch all ready exam questions for given type + region."""
    query = """
        SELECT eq.question_id, eq.question_text, eq.question_type,
               eq.points, eq.topics, eq.data, eq.solution_text,
               eq.scenario_title, eq.scenario_text, eq.question_number,
               e.year, e.season, e.part
        FROM assessments.exam_questions eq
        JOIN assessments.exams e ON eq.exam_id = e.exam_id
        LEFT JOIN assessments.exam_sessions s ON e.session_id = s.session_id
        WHERE e.analysis_status = 'ready'
          AND (
              s.exam_type_key = %s
              OR e.exam_type_key = %s
          )
          AND (
              COALESCE(s.region, 'alle') = %s
              OR COALESCE(s.region, 'alle') = 'alle'
          )
        ORDER BY eq.topics, e.year DESC, eq.order_index
    """
    return fetch_all(query, (exam_type_key, exam_type_key, region))


def _group_by_topic(questions: List[Dict]) -> Dict[str, List[Dict]]:
    """Group questions by their topics (a question can belong to multiple topics)."""
    groups: Dict[str, List[Dict]] = {}
    for q in questions:
        topics = q.get('topics') or []
        if not topics:
            topics = ['allgemein']
        for topic in topics:
            if topic not in groups:
                groups[topic] = []
            groups[topic].append(q)
    return groups


def _find_simulation_exams(
    exam_type_key: str, region: str
) -> List[str]:
    """Find distinct exam IDs that can serve as simulation chapters."""
    query = """
        SELECT DISTINCT e.exam_id
        FROM assessments.exams e
        LEFT JOIN assessments.exam_sessions s ON e.session_id = s.session_id
        WHERE e.analysis_status = 'ready'
          AND (s.exam_type_key = %s OR e.exam_type_key = %s)
          AND (COALESCE(s.region, 'alle') = %s OR COALESCE(s.region, 'alle') = 'alle')
        ORDER BY e.exam_id
        LIMIT 6
    """
    rows = fetch_all(query, (exam_type_key, exam_type_key, region))
    return [r['exam_id'] for r in rows]


def _build_title(exam_type_key: str, region: str) -> str:
    """Build a human-readable course title."""
    type_labels = {
        'IHK_FISI': 'IHK Fachinformatiker Systemintegration AP1',
        'IHK_FIAE': 'IHK Fachinformatiker Anwendungsentwicklung AP1',
    }
    region_labels = {
        'alle': 'Alle Bundeslaender',
        'bw': 'Baden-Wuerttemberg',
        'bayern': 'Bayern',
        'nrw': 'Nordrhein-Westfalen',
    }
    type_label = type_labels.get(exam_type_key, exam_type_key)
    region_label = region_labels.get(region, region)
    return f'{type_label} — {region_label}'
```

**Step 2: Verify import**

```bash
cd backend && python -c "from app.application.services.exams.course_generator_service import ExamCourseGeneratorService; print('OK')"
```

Expected: `OK`

**Step 3: Commit**

```bash
git add backend/app/application/services/exams/course_generator_service.py
git commit -m "feat(exams): add ExamCourseGeneratorService with preview() and generate()"
```

---

## Task 4: Application Builder — CourseGeneratorBuilder

**Files:**
- Create: `backend/app/application/services/exams/course_generator_builder.py`

**Step 1: Write the builder**

This handles the actual persistence: create course, chapters, and LM instances.

```python
"""
Course Generator Builder — Application Layer.

Persists an ExamCoursePlan as real course/chapter/LM records.
Separated from the service to keep both under 300 LOC.
"""
import json
import logging
from typing import Dict, Any, Optional, List

from app.domain.models.exam_course_plan import ExamCoursePlan, ChapterPlan
from app.domain.services.lm_content_mapper import LMContentMapper
from app.infrastructure.persistence.repositories.courses.management.crud import (
    CourseRepository,
)
from app.infrastructure.persistence.repositories.courses.content.chapters import (
    ChapterRepository,
)
from app.infrastructure.persistence.repositories.learning_method.execution.instances import (
    LearningMethodInstanceRepository,
)
from app.infrastructure.persistence.repositories.exams.core_part2 import (
    ExamQuestionRepository,
)

logger = logging.getLogger(__name__)

# LM type → mapper function name
LM_MAPPER: Dict[int, str] = {
    5: 'map_to_math_interactive',
    6: 'map_to_flashcards',
    7: 'map_to_drag_drop',
    8: 'map_to_cloze',
    10: 'map_to_ihk_tasks',
    11: 'map_to_multi_step',
}

# LM type → human-readable title template
LM_TITLES: Dict[int, str] = {
    0: '{topic} — Erklaerung',
    1: '{topic} — Schritt fuer Schritt',
    5: '{topic} — Rechenaufgaben',
    6: '{topic} — Karteikarten',
    7: '{topic} — Zuordnungen',
    8: '{topic} — Lueckentexte',
    10: '{topic} — Pruefungsaufgaben',
    11: '{topic} — Fallstudien',
}


class CourseGeneratorBuilder:
    """Builds and persists course structure from ExamCoursePlan."""

    @staticmethod
    def build(
        plan: ExamCoursePlan,
        creator_user_id: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create course + chapters + LM instances from plan.

        Returns:
            {course_id, chapters_count, lm_count, tokens_used}
        """
        options = options or {}
        total_lm_count = 0
        total_tokens = 0

        # 1. Create course
        course = CourseRepository.create({
            'title': plan.title,
            'creator_user_id': creator_user_id,
            'description': f'Automatisch generiert aus {plan.total_questions} echten Pruefungsaufgaben.',
            'tags': ['ihk', 'auto-generated', plan.exam_type.lower()],
            'level': 'intermediate',
        })
        course_id = str(course['course_id'])
        logger.info("Created course %s: %s", course_id, plan.title)

        # 2. Build chapters
        for idx, chapter_plan in enumerate(plan.chapters):
            chapter_result = CourseGeneratorBuilder._build_chapter(
                course_id, chapter_plan, idx, options,
            )
            total_lm_count += chapter_result['lm_count']
            total_tokens += chapter_result.get('tokens_used', 0)

        # 3. Build simulation chapters
        for sim_exam_id in plan.simulation_exam_ids:
            sim_result = CourseGeneratorBuilder._build_simulation_chapter(
                course_id, sim_exam_id,
            )
            total_lm_count += sim_result['lm_count']

        logger.info(
            "Course generation complete: %s — %d chapters, %d LMs, %d tokens",
            course_id, len(plan.chapters), total_lm_count, total_tokens,
        )

        return {
            'course_id': course_id,
            'chapters_count': len(plan.chapters) + len(plan.simulation_exam_ids),
            'lm_count': total_lm_count,
            'tokens_used': total_tokens,
        }

    @staticmethod
    def _build_chapter(
        course_id: str,
        chapter_plan: ChapterPlan,
        order_index: int,
        options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build a single topic chapter with its LM instances."""
        # Create chapter
        chapter = ChapterRepository.create({
            'course_id': course_id,
            'title': chapter_plan.topic.replace('_', ' ').title(),
            'description': f'{chapter_plan.question_count} Aufgaben, {int(chapter_plan.point_weight)} Punkte',
            'order_index': order_index + 1,
        })
        chapter_id = str(chapter['chapter_id'])

        # Fetch full question data for this chapter
        questions = []
        for qid in chapter_plan.question_ids:
            q = ExamQuestionRepository.find_by_id(qid)
            if q:
                questions.append(q)

        # Create LM instances for each selected type
        lm_count = 0
        tokens_used = 0

        for lm_order, lm_type in enumerate(chapter_plan.lm_types):
            lm_data, used_tokens = _build_lm_data(
                lm_type, chapter_plan.topic, questions, options,
            )

            if lm_data is None:
                continue

            title = LM_TITLES.get(lm_type, '{topic}').format(
                topic=chapter_plan.topic.replace('_', ' ').title(),
            )

            LearningMethodInstanceRepository.create({
                'chapter_id': chapter_id,
                'method_type': lm_type,
                'title': title,
                'data': lm_data,
                'order_index': lm_order + 1,
                'published': True,
                'difficulty': 'medium',
            })
            lm_count += 1
            tokens_used += used_tokens

        return {'lm_count': lm_count, 'tokens_used': tokens_used}

    @staticmethod
    def _build_simulation_chapter(
        course_id: str,
        exam_id: str,
    ) -> Dict[str, Any]:
        """Build a simulation chapter from a full exam."""
        questions = ExamQuestionRepository.find_by_exam(exam_id)
        if not questions:
            return {'lm_count': 0}

        first_q = questions[0]
        title = f"Simulation — {first_q.get('exam_title', 'Pruefung')}"

        chapter = ChapterRepository.create({
            'course_id': course_id,
            'title': title,
            'description': f'Pruefungssimulation mit {len(questions)} Aufgaben',
            'has_exam': True,
        })
        chapter_id = str(chapter['chapter_id'])

        # Create one IHK-Style Tasks (LM10) with all questions
        tasks = LMContentMapper.map_to_ihk_tasks(questions)
        LearningMethodInstanceRepository.create({
            'chapter_id': chapter_id,
            'method_type': 10,
            'title': title,
            'data': tasks,
            'published': True,
            'difficulty': 'hard',
        })

        return {'lm_count': 1}


def _build_lm_data(
    lm_type: int,
    topic: str,
    questions: List[Dict],
    options: Dict[str, Any],
) -> tuple:
    """
    Build JSONB data for a specific LM type.

    Returns:
        (data_dict, tokens_used) — data_dict is None if no content could be generated
    """
    mapper = LM_MAPPER.get(lm_type)

    # LM 0 (Deep Explanation) — needs AI generation
    if lm_type == 0:
        return _generate_deep_explanation(topic, questions, options)

    # LM 1 (Step by Step) — needs AI generation
    if lm_type == 1:
        return _generate_step_by_step(topic, questions, options)

    # Static mapping from exam data
    if mapper:
        map_fn = getattr(LMContentMapper, mapper, None)
        if map_fn:
            data = map_fn(questions)
            # Skip if no content was mapped
            items_key = list(data.keys())[0] if data else None
            if items_key and len(data.get(items_key, [])) == 0:
                return None, 0
            return data, 0

    return None, 0


def _generate_deep_explanation(
    topic: str,
    questions: List[Dict],
    options: Dict[str, Any],
) -> tuple:
    """Generate Deep Explanation content via AI."""
    from app.application.services.exams.course_generator_prompts import (
        build_deep_explanation_prompt,
    )
    from app.infrastructure.ai.adapter import AIAdapter

    prompt = build_deep_explanation_prompt(topic, questions)
    provider = options.get('provider', 'openai')
    model = options.get('model', 'gpt-4o-mini')

    try:
        adapter = AIAdapter(provider=provider, model=model)
        response = adapter.send_request(
            prompt=prompt,
            language='de',
            temperature=0.5,
            max_tokens=4000,
        )
        explanation = response.get('output_text', '')
        tokens = response.get('total_tokens', 0)

        return {
            'content': explanation,
            'topic': topic,
            'source_questions': len(questions),
        }, tokens

    except Exception as e:
        logger.error("AI generation failed for %s: %s", topic, e)
        return {
            'content': f'Thema: {topic.replace("_", " ").title()}',
            'topic': topic,
            'source_questions': len(questions),
        }, 0


def _generate_step_by_step(
    topic: str,
    questions: List[Dict],
    options: Dict[str, Any],
) -> tuple:
    """Generate Step-by-Step content via AI."""
    from app.application.services.exams.course_generator_prompts import (
        build_step_by_step_prompt,
    )
    from app.infrastructure.ai.adapter import AIAdapter

    prompt = build_step_by_step_prompt(topic, questions)
    provider = options.get('provider', 'openai')
    model = options.get('model', 'gpt-4o-mini')

    try:
        adapter = AIAdapter(provider=provider, model=model)
        response = adapter.send_request(
            prompt=prompt,
            language='de',
            temperature=0.5,
            max_tokens=4000,
        )
        content = response.get('output_text', '')
        tokens = response.get('total_tokens', 0)

        return {
            'content': content,
            'topic': topic,
            'source_questions': len(questions),
        }, tokens

    except Exception as e:
        logger.error("AI step-by-step generation failed for %s: %s", topic, e)
        return None, 0
```

**Step 2: Verify import**

```bash
cd backend && python -c "from app.application.services.exams.course_generator_builder import CourseGeneratorBuilder; print('OK')"
```

Expected: `OK`

**Step 3: Commit**

```bash
git add backend/app/application/services/exams/course_generator_builder.py
git commit -m "feat(exams): add CourseGeneratorBuilder for persisting exam course plans"
```

---

## Task 5: KI-Prompt Templates

**Files:**
- Create: `backend/app/application/services/exams/course_generator_prompts.py`

**Step 1: Write prompt templates**

Separated per G07 (no hardcoded AI models/prompts inline).

```python
"""
Course Generator Prompts — KI-Prompt Templates.

Separated from service logic per G07 (no hardcoded AI config inline).
"""
from typing import List, Dict


def build_deep_explanation_prompt(topic: str, questions: List[Dict]) -> str:
    """Build prompt for Deep Explanation (LM00) content generation."""
    topic_label = topic.replace('_', ' ').title()

    # Extract sample questions for context
    sample_texts = []
    for q in questions[:8]:
        text = q.get('question_text', '')[:200]
        if text:
            sample_texts.append(f"- {text}")
    samples = '\n'.join(sample_texts)

    return f"""Du bist ein erfahrener IT-Dozent fuer IHK-Pruefungsvorbereitung.

Erstelle eine ausfuehrliche Erklaerung zum Thema "{topic_label}" fuer die IHK Fachinformatiker AP1 Pruefung.

## Kontext: Echte Pruefungsaufgaben zu diesem Thema
{samples}

## Anforderungen:
1. Erklaere das Thema von Grund auf — stelle dir einen Azubi im 2. Lehrjahr vor
2. Verwende konkrete Beispiele aus der IT-Praxis
3. Beziehe dich auf typische IHK-Pruefungsaufgaben
4. Strukturiere mit Ueberschriften (## und ###)
5. Nutze Aufzaehlungen und Tabellen wo sinnvoll
6. Laenge: 800-1500 Woerter
7. Sprache: Deutsch, fachlich korrekt aber verstaendlich

## Ausgabeformat:
Markdown-Text (kein JSON, kein Code-Block drumherum).
Beginne direkt mit der Erklaerung."""


def build_step_by_step_prompt(topic: str, questions: List[Dict]) -> str:
    """Build prompt for Step-by-Step (LM01) content generation."""
    topic_label = topic.replace('_', ' ').title()

    # Find calculation or complex questions for step-by-step
    complex_qs = [
        q for q in questions
        if q.get('question_type') in ('calculation', 'code', 'case_study')
    ][:5]

    if not complex_qs:
        complex_qs = questions[:5]

    examples = []
    for q in complex_qs:
        text = q.get('question_text', '')[:300]
        solution = q.get('solution_text', '')[:200]
        examples.append(f"Aufgabe: {text}\nLoesungshinweis: {solution}")
    examples_text = '\n\n'.join(examples)

    return f"""Du bist ein erfahrener IT-Dozent.

Erstelle eine Schritt-fuer-Schritt Anleitung zum Thema "{topic_label}" fuer die IHK AP1 Pruefung.

## Beispiel-Aufgaben aus echten Pruefungen:
{examples_text}

## Anforderungen:
1. Zeige den Loesungsweg Schritt fuer Schritt
2. Erklaere WARUM jeder Schritt notwendig ist
3. Nutze nummerierte Schritte (1., 2., 3. ...)
4. Bei Berechnungen: zeige Zwischenergebnisse
5. Bei Code/SQL: zeige Teilloesungen die aufeinander aufbauen
6. Gib am Ende Tipps fuer die Pruefung
7. Laenge: 600-1000 Woerter

## Ausgabeformat:
Markdown-Text. Beginne direkt mit der Anleitung."""
```

**Step 2: Verify import**

```bash
cd backend && python -c "from app.application.services.exams.course_generator_prompts import build_deep_explanation_prompt; print('OK')"
```

Expected: `OK`

**Step 3: Commit**

```bash
git add backend/app/application/services/exams/course_generator_prompts.py
git commit -m "feat(exams): add KI prompt templates for course content generation"
```

---

## Task 6: API Blueprint — course_generator.py

**Files:**
- Create: `backend/app/api/v1/panel/admin/exams/course_generator.py`
- Modify: `backend/app/api/v1/panel/admin/exams/__init__.py`

**Step 1: Write the API blueprint**

```python
"""
Exam Course Generator API — Admin endpoints for auto-generating
structured courses from real IHK exam questions.
"""
from flask import Blueprint, request, jsonify

from app.infrastructure.security.auth.core import admin_required, get_jwt_identity
from app.application.services.exams.course_generator_service import (
    ExamCourseGeneratorService,
)

course_gen_bp = Blueprint(
    'exam_course_generator',
    __name__,
    url_prefix='/admin/exam-courses',
)


@course_gen_bp.route('/preview', methods=['POST'])
@admin_required
def preview_course():
    """
    Preview course plan without creating anything.

    Body: {exam_type: str, region?: str}
    Returns: {plan: {...chapters, total_questions, total_points}}
    """
    data = request.get_json() or {}
    exam_type = data.get('exam_type')
    if not exam_type:
        return jsonify({'error': 'exam_type is required'}), 400

    region = data.get('region', 'alle')

    plan = ExamCourseGeneratorService.preview(exam_type, region)

    return jsonify({
        'success': True,
        'plan': plan.to_dict(),
    }), 200


@course_gen_bp.route('/generate', methods=['POST'])
@admin_required
def generate_course():
    """
    Generate a full course from exam questions.

    Body: {exam_type: str, region?: str, options?: {provider, model}}
    Returns: {course_id, chapters_count, lm_count, tokens_used}
    """
    data = request.get_json() or {}
    exam_type = data.get('exam_type')
    if not exam_type:
        return jsonify({'error': 'exam_type is required'}), 400

    region = data.get('region', 'alle')
    options = data.get('options', {})
    user_id = get_jwt_identity()

    # First generate the plan
    plan = ExamCourseGeneratorService.preview(exam_type, region)

    if not plan.chapters:
        return jsonify({
            'error': 'No questions found for given type and region',
        }), 404

    # Then persist it
    result = ExamCourseGeneratorService.generate(
        plan=plan,
        creator_user_id=user_id,
        options=options,
    )

    return jsonify({
        'success': True,
        **result,
    }), 201
```

**Step 2: Register blueprint in `__init__.py`**

Add to `backend/app/api/v1/panel/admin/exams/__init__.py`:

```python
from .course_generator import course_gen_bp

api_v1.register_blueprint(course_gen_bp)
```

Add `'course_gen_bp'` to `__all__`.

**Step 3: Verify app starts**

```bash
cd backend && python -c "from app import create_app; create_app(); print('OK')"
```

Expected: `OK` (no import errors)

**Step 4: Commit**

```bash
git add backend/app/api/v1/panel/admin/exams/course_generator.py
git add backend/app/api/v1/panel/admin/exams/__init__.py
git commit -m "feat(exams): add /admin/exam-courses/preview and /generate API endpoints"
```

---

## Task 7: Frontend API Client

**Files:**
- Create: `frontend/src/infrastructure/api/clients/panel/admin/exams/course-generator.api.ts`

**Step 1: Write the API client**

```typescript
import http from '@/infrastructure/api/http'

export interface ChapterPreview {
  topic: string
  question_count: number
  lm_types: number[]
  point_weight: number
}

export interface CoursePlan {
  title: string
  exam_type: string
  region: string
  total_questions: number
  total_points: number
  chapters: ChapterPreview[]
  simulation_exam_ids: string[]
}

export interface GenerateResult {
  course_id: string
  chapters_count: number
  lm_count: number
  tokens_used: number
}

export async function previewExamCourse(
  examType: string,
  region: string = 'alle'
): Promise<CoursePlan> {
  const response = await http.post<{ success: boolean; plan: CoursePlan }>(
    '/admin/exam-courses/preview',
    { exam_type: examType, region }
  )
  return response.data.plan
}

export async function generateExamCourse(
  examType: string,
  region: string = 'alle',
  options?: { provider?: string; model?: string }
): Promise<GenerateResult> {
  const response = await http.post<{ success: boolean } & GenerateResult>(
    '/admin/exam-courses/generate',
    { exam_type: examType, region, options }
  )
  return {
    course_id: response.data.course_id,
    chapters_count: response.data.chapters_count,
    lm_count: response.data.lm_count,
    tokens_used: response.data.tokens_used,
  }
}
```

**Step 2: Commit**

```bash
git add frontend/src/infrastructure/api/clients/panel/admin/exams/course-generator.api.ts
git commit -m "feat(exams): add course generator API client"
```

---

## Task 8: Frontend — ExamCourseGenerator.vue

**Files:**
- Create: `frontend/src/presentation/components/panel/admin/assessment/exams/ExamCourseGenerator.vue`

**Step 1: Write the component**

```vue
<!--
  ExamCourseGenerator — Admin UI for auto-generating IHK exam courses.
  Workflow: Select exam type + region → Preview plan → Generate course.
-->

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-[var(--color-text-primary)]">
        {{ t('panel.examCourseGenerator.title') }}
      </h2>
    </div>

    <!-- Config Form -->
    <div class="bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)] p-4 space-y-4">
      <div class="grid grid-cols-2 gap-4">
        <!-- Exam Type -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
            {{ t('panel.examCourseGenerator.selectType') }}
          </label>
          <select
            v-model="examType"
            class="w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-sm"
          >
            <option value="IHK_FISI">IHK Fachinformatiker SI (AP1)</option>
            <option value="IHK_FIAE">IHK Fachinformatiker AE (AP1)</option>
          </select>
        </div>

        <!-- Region -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
            {{ t('panel.examCourseGenerator.selectRegion') }}
          </label>
          <select
            v-model="region"
            class="w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-sm"
          >
            <option value="alle">Alle Bundeslaender</option>
            <option value="bw">Baden-Wuerttemberg</option>
            <option value="bayern">Bayern</option>
            <option value="nrw">Nordrhein-Westfalen</option>
          </select>
        </div>
      </div>

      <button
        @click="handlePreview"
        :disabled="previewing"
        class="px-4 py-2 text-sm rounded text-white transition-colors disabled:opacity-50"
        style="background-color: var(--color-primary, #7c3aed);"
      >
        {{ previewing ? '...' : t('panel.examCourseGenerator.preview') }}
      </button>
    </div>

    <!-- Preview Plan -->
    <div
      v-if="plan"
      class="bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)] p-4 space-y-4"
    >
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold text-[var(--color-text-primary)]">
          {{ plan.title }}
        </h3>
        <div class="flex items-center gap-3 text-xs text-[var(--color-text-secondary)]">
          <span>{{ plan.total_questions }} {{ t('panel.examCourseGenerator.questions') }}</span>
          <span>{{ plan.chapters.length }} {{ t('panel.examCourseGenerator.chapters') }}</span>
          <span>{{ Math.round(plan.total_points) }} {{ t('panel.examCourseGenerator.points') }}</span>
        </div>
      </div>

      <!-- Chapter List -->
      <div class="space-y-2">
        <div
          v-for="(ch, idx) in plan.chapters"
          :key="ch.topic"
          class="flex items-center justify-between px-3 py-2 rounded bg-[var(--color-bg)] border border-[var(--color-border)]"
        >
          <div class="flex items-center gap-3">
            <span class="text-xs font-mono text-[var(--color-text-secondary)] w-6">
              {{ idx + 1 }}
            </span>
            <span class="text-sm font-medium text-[var(--color-text-primary)]">
              {{ formatTopic(ch.topic) }}
            </span>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-xs text-[var(--color-text-secondary)]">
              {{ ch.question_count }} {{ t('panel.examCourseGenerator.questions') }}
            </span>
            <div class="flex gap-1">
              <span
                v-for="lm in ch.lm_types"
                :key="lm"
                class="px-1.5 py-0.5 text-xs rounded bg-[var(--color-primary-bg,#ede9fe)] text-[var(--color-primary-text,#6d28d9)]"
              >
                LM{{ lm }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Simulations -->
      <div v-if="plan.simulation_exam_ids.length > 0" class="text-xs text-[var(--color-text-secondary)]">
        + {{ plan.simulation_exam_ids.length }} {{ t('panel.examCourseGenerator.simulations') }}
      </div>

      <!-- Generate Button -->
      <div class="flex items-center gap-3">
        <button
          @click="handleGenerate"
          :disabled="generating"
          class="px-4 py-2 text-sm rounded text-white transition-colors disabled:opacity-50"
          style="background-color: var(--color-primary, #7c3aed);"
        >
          {{ generating ? t('panel.examCourseGenerator.generating') : t('panel.examCourseGenerator.generate') }}
        </button>
        <div v-if="generating" class="flex items-center gap-2">
          <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-[var(--color-primary)]" />
          <span class="text-xs text-[var(--color-text-secondary)]">
            {{ t('panel.examCourseGenerator.generatingHint') }}
          </span>
        </div>
      </div>
    </div>

    <!-- Success Result -->
    <div
      v-if="result"
      class="bg-[var(--color-success-bg,#dcfce7)] rounded-lg border border-[var(--color-success-text,#15803d)] p-4"
    >
      <p class="text-sm font-medium text-[var(--color-success-text,#15803d)]">
        {{ t('panel.examCourseGenerator.success') }}
      </p>
      <p class="text-xs text-[var(--color-success-text,#15803d)] mt-1">
        {{ result.chapters_count }} Kapitel, {{ result.lm_count }} Lernmethoden, {{ result.tokens_used }} Tokens
      </p>
      <a
        :href="`/panel/courses/${result.course_id}/edit`"
        class="inline-block mt-2 text-sm underline text-[var(--color-primary)]"
      >
        {{ t('panel.examCourseGenerator.openInEditor') }}
      </a>
    </div>

    <!-- Error -->
    <div
      v-if="error"
      class="bg-[var(--color-error-bg,#fee2e2)] rounded-lg border border-[var(--color-error-text,#dc2626)] p-4"
    >
      <p class="text-sm text-[var(--color-error-text,#dc2626)]">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { CoursePlan, GenerateResult } from '@/infrastructure/api/clients/panel/admin/exams/course-generator.api'
import { previewExamCourse, generateExamCourse } from '@/infrastructure/api/clients/panel/admin/exams/course-generator.api'

const { t } = useI18n()

const examType = ref('IHK_FISI')
const region = ref('alle')
const previewing = ref(false)
const generating = ref(false)
const plan = ref<CoursePlan | null>(null)
const result = ref<GenerateResult | null>(null)
const error = ref<string | null>(null)

function formatTopic(topic: string): string {
  return topic.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

async function handlePreview() {
  previewing.value = true
  error.value = null
  result.value = null
  try {
    plan.value = await previewExamCourse(examType.value, region.value)
  } catch (err: any) {
    error.value = err?.response?.data?.error || 'Preview failed'
  } finally {
    previewing.value = false
  }
}

async function handleGenerate() {
  generating.value = true
  error.value = null
  try {
    result.value = await generateExamCourse(examType.value, region.value)
  } catch (err: any) {
    error.value = err?.response?.data?.error || 'Generation failed'
  } finally {
    generating.value = false
  }
}
</script>
```

**Step 2: Commit**

```bash
git add frontend/src/presentation/components/panel/admin/assessment/exams/ExamCourseGenerator.vue
git commit -m "feat(exams): add ExamCourseGenerator.vue admin component"
```

---

## Task 9: i18n Keys (de/en/pl)

**Files:**
- Modify: `frontend/src/infrastructure/i18n/locales/de/panel/shared.json`
- Modify: `frontend/src/infrastructure/i18n/locales/en/panel/shared.json`
- Modify: `frontend/src/infrastructure/i18n/locales/pl/panel/shared.json`

**Step 1: Add keys to all 3 locales**

Under `examCourseGenerator`:

**German (de):**
```json
"examCourseGenerator": {
  "title": "Pruefungskurs generieren",
  "selectType": "Pruefungstyp",
  "selectRegion": "Region / Bundesland",
  "preview": "Vorschau",
  "generate": "Kurs generieren",
  "generating": "Generiere...",
  "generatingHint": "KI erstellt Erklaerungen — das kann 1-2 Minuten dauern",
  "success": "Kurs erfolgreich generiert!",
  "openInEditor": "Im Editor oeffnen",
  "questions": "Fragen",
  "chapters": "Kapitel",
  "points": "Punkte",
  "simulations": "Pruefungssimulationen"
}
```

**English (en):**
```json
"examCourseGenerator": {
  "title": "Generate Exam Course",
  "selectType": "Exam Type",
  "selectRegion": "Region / State",
  "preview": "Preview",
  "generate": "Generate Course",
  "generating": "Generating...",
  "generatingHint": "AI is creating explanations — this may take 1-2 minutes",
  "success": "Course generated successfully!",
  "openInEditor": "Open in Editor",
  "questions": "Questions",
  "chapters": "Chapters",
  "points": "Points",
  "simulations": "Exam Simulations"
}
```

**Polish (pl):**
```json
"examCourseGenerator": {
  "title": "Generuj kurs egzaminacyjny",
  "selectType": "Typ egzaminu",
  "selectRegion": "Region / Kraj",
  "preview": "Podglad",
  "generate": "Generuj kurs",
  "generating": "Generowanie...",
  "generatingHint": "AI tworzy wyjasnienia — moze to potrwac 1-2 minuty",
  "success": "Kurs wygenerowany pomyslnie!",
  "openInEditor": "Otworz w edytorze",
  "questions": "Pytania",
  "chapters": "Rozdzialy",
  "points": "Punkty",
  "simulations": "Symulacje egzaminu"
}
```

**Step 2: Commit**

```bash
git add frontend/src/infrastructure/i18n/locales/de/panel/shared.json
git add frontend/src/infrastructure/i18n/locales/en/panel/shared.json
git add frontend/src/infrastructure/i18n/locales/pl/panel/shared.json
git commit -m "feat(i18n): add exam course generator translations (de/en/pl)"
```

---

## Task 10: Integration — Barrel Exports + ExamArchiveManager Link

**Files:**
- Modify: `backend/app/application/services/exams/__init__.py` (barrel export)
- Modify: `frontend/src/presentation/components/panel/admin/assessment/exams/index.ts` (barrel export)
- Modify: `frontend/src/presentation/components/panel/admin/assessment/archive/ExamArchiveManager.vue` (add generator link)

**Step 1: Backend barrel export**

Add to `backend/app/application/services/exams/__init__.py`:

```python
from app.application.services.exams.course_generator_service import ExamCourseGeneratorService
```

**Step 2: Frontend barrel export**

Add to `frontend/src/presentation/components/panel/admin/assessment/exams/index.ts`:

```typescript
export { default as ExamCourseGenerator } from './ExamCourseGenerator.vue'
```

**Step 3: Add "Generate Course" button to ExamArchiveManager**

In `ExamArchiveManager.vue`, add a button/link that opens the generator. This is a minimal integration — just a tab or button that shows/hides the `ExamCourseGenerator` component.

```vue
<!-- Add to existing header area -->
<button
  @click="showGenerator = !showGenerator"
  class="px-3 py-1.5 text-sm rounded border border-[var(--color-primary)] text-[var(--color-primary)] hover:bg-[var(--color-primary-bg)]"
>
  {{ t('panel.examCourseGenerator.title') }}
</button>

<!-- Add below existing content, conditionally -->
<ExamCourseGenerator v-if="showGenerator" />
```

Add in `<script setup>`:
```typescript
import { ExamCourseGenerator } from '../exams'
const showGenerator = ref(false)
```

**Step 4: Verify full build**

```bash
cd backend && python -c "from app import create_app; create_app(); print('Backend OK')"
cd frontend && npm run build
```

Expected: Both succeed without errors.

**Step 5: Commit**

```bash
git add backend/app/application/services/exams/__init__.py
git add frontend/src/presentation/components/panel/admin/assessment/exams/index.ts
git add frontend/src/presentation/components/panel/admin/assessment/archive/ExamArchiveManager.vue
git commit -m "feat(exams): integrate course generator into ExamArchiveManager + barrel exports"
```

---

## Verification

### Backend

```bash
# 1. App starts without errors
cd backend && python -c "from app import create_app; create_app()"

# 2. Preview endpoint (requires auth token)
curl -s -X POST http://localhost:5000/api/v1/admin/exam-courses/preview \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"exam_type": "IHK_FISI", "region": "alle"}' | python -m json.tool

# Expected: {success: true, plan: {title: "...", chapters: [...], total_questions: 442, ...}}

# 3. Generate endpoint (creates real course)
curl -s -X POST http://localhost:5000/api/v1/admin/exam-courses/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"exam_type": "IHK_FISI", "region": "alle"}' | python -m json.tool

# Expected: {success: true, course_id: "...", chapters_count: ~20, lm_count: ~60, tokens_used: ~X}
```

### Frontend

```bash
cd frontend && npm run build   # Compiles without errors

# Browser: /panel/exam-archive
# → "Pruefungskurs generieren" Button
# → Select IHK FISI + Alle Bundeslaender
# → Preview → shows chapters with LM types
# → Generate → creates course
# → "Im Editor oeffnen" → opens course in editor
```

### Quality Gate Check

| Gate | Status |
|------|--------|
| G01 (<500 LOC) | All files < 300 LOC |
| G02 (<50 LOC/fn) | All functions < 50 LOC |
| G03 (No circular imports) | Clean layer separation |
| G05 (No duplicates) | Reuses existing repos |
| G07 (No hardcoded AI) | Prompts in separate file |
| G09 (No cross-layer) | Domain → Application → Infrastructure |

---

## Not in Scope (Phase 2-4)

- Spaced Repetition (SM-2 cards, daily review) — Phase 2
- Elaborative Interrogation + KI-Feedback — Phase 3
- Trainer deprecation + dashboard widget — Phase 4
- Exam simulation timer — Phase 4
