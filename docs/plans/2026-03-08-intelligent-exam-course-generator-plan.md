# Intelligent Exam Course Generator — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Exam Course Generator mit intelligenter Topic-Hierarchie, AI Editor Integration und Pruefungsmodus als einheitliches System

**Architecture:** Drei-Phasen-Ansatz: (A) Taxonomie-Bootstrap befuellt `exam_topic_taxonomy` via KI-Gruppierung der 54 existierenden Topics, (B) Course Generator nutzt Hierarchie fuer Kapitelstruktur und delegiert Content-Generierung an die existierende AI Editor Pipeline (statt eigener LM-Generierung), (C) Pruefungsmodus als Flag auf Kursen mit Zeitlimit/Punkte.

**Tech Stack:** Flask 3.0, psycopg3, Celery, Redis, AI Editor Pipeline (`plan_execution.py`), Vue 3 Composition API

**Design Doc:** `docs/plans/2026-03-08-intelligent-exam-course-generator-design.md`

---

## Task 1: Taxonomy Bootstrap Service

**Goal:** Populate `exam_topic_taxonomy` from existing 54 topics via AI grouping call.

**Files:**
- Create: `backend/app/application/services/exams/taxonomy_bootstrap_service.py`
- Modify: `backend/app/infrastructure/persistence/repositories/exams/topic_taxonomy.py`
- Modify: `backend/app/api/v1/panel/admin/exams/taxonomy.py` (create if not exists)

### Step 1: Extend TopicTaxonomyRepository with bulk insert + find roots

**File:** `backend/app/infrastructure/persistence/repositories/exams/topic_taxonomy.py`

Add methods:

```python
@staticmethod
def find_roots_by_exam_type(exam_type: str) -> List[Dict]:
    """Find all root topics (parent_topic_id IS NULL) for an exam type."""
    return fetch_all(
        """SELECT * FROM assessments.exam_topic_taxonomy
           WHERE exam_type = %s AND parent_topic_id IS NULL
           ORDER BY weight DESC""",
        [exam_type],
    )

@staticmethod
def find_children(parent_topic_id: str) -> List[Dict]:
    """Find all child topics of a parent."""
    return fetch_all(
        """SELECT * FROM assessments.exam_topic_taxonomy
           WHERE parent_topic_id = %s
           ORDER BY topic_key""",
        [parent_topic_id],
    )

@staticmethod
def find_all_by_exam_type(exam_type: str) -> List[Dict]:
    """Find all topics (roots + children) for an exam type."""
    return fetch_all(
        """SELECT * FROM assessments.exam_topic_taxonomy
           WHERE exam_type = %s
           ORDER BY parent_topic_id NULLS FIRST, topic_key""",
        [exam_type],
    )

@staticmethod
def bulk_create(records: List[Dict]) -> int:
    """Insert multiple taxonomy records. Returns count inserted."""
    if not records:
        return 0
    from app.infrastructure.persistence.database.connection import get_db_connection
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for r in records:
                cur.execute(
                    """INSERT INTO assessments.exam_topic_taxonomy
                       (exam_type, topic_key, topic_label, parent_topic_id, weight)
                       VALUES (%s, %s, %s, %s, %s)
                       ON CONFLICT (exam_type, topic_key) DO NOTHING""",
                    [r['exam_type'], r['topic_key'], r.get('topic_label', '{}'),
                     r.get('parent_topic_id'), r.get('weight', 1.0)],
                )
            conn.commit()
    return len(records)

@staticmethod
def find_by_topic_key(exam_type: str, topic_key: str) -> Optional[Dict]:
    """Find a single topic by exam_type + topic_key."""
    return fetch_one(
        """SELECT * FROM assessments.exam_topic_taxonomy
           WHERE exam_type = %s AND topic_key = %s""",
        [exam_type, topic_key],
    )
```

### Step 2: Create TaxonomyBootstrapService

**File:** `backend/app/application/services/exams/taxonomy_bootstrap_service.py`

```python
"""
Taxonomy Bootstrap Service — Application Layer.

Populates exam_topic_taxonomy from existing question topics via AI grouping.
One AI call per exam_type to group flat topics into 6-10 parent categories.
"""
import json
import logging
from typing import Dict, List, Optional

from app.infrastructure.persistence.repositories.exams.topic_taxonomy import (
    TopicTaxonomyRepository,
)
from app.infrastructure.persistence.repositories.exams.questions import (
    ExamQuestionRepository,
)

logger = logging.getLogger(__name__)

# Prompt template for grouping topics
GROUPING_PROMPT = """Du bekommst eine Liste von Pruefungs-Topics fuer den Pruefungstyp "{exam_type}".
Gruppiere sie in 6-10 sinnvolle Oberkategorien.

Topics: {topics}

Antworte NUR als JSON-Array:
[
  {{
    "parent": "oberkategorie_key",
    "parent_label": {{"de": "Deutsch", "en": "English"}},
    "children": ["topic1", "topic2"]
  }}
]

Regeln:
- Jeder Topic muss genau einer Oberkategorie zugeordnet sein
- Oberkategorie-Keys in snake_case
- Jede Oberkategorie sollte 3-10 Topics enthalten
- Topics die nicht gut passen: eigene Kategorie "allgemein"
"""


class TaxonomyBootstrapService:
    """Bootstrap exam_topic_taxonomy from existing question data."""

    @staticmethod
    def bootstrap_exam_type(
        exam_type: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict:
        """
        Bootstrap taxonomy for one exam type.

        1. Read distinct topics from exam_questions
        2. Check if taxonomy already populated
        3. AI call to group into parent categories
        4. Write to exam_topic_taxonomy

        Returns: {exam_type, parents_created, children_created, skipped}
        """
        existing = TopicTaxonomyRepository.find_all_by_exam_type(exam_type)
        if existing:
            logger.info(
                "Taxonomy already populated for %s (%d entries), skipping",
                exam_type, len(existing),
            )
            return {
                'exam_type': exam_type,
                'parents_created': 0,
                'children_created': 0,
                'skipped': True,
            }

        topics = _get_distinct_topics(exam_type)
        if not topics:
            logger.warning("No topics found for exam_type=%s", exam_type)
            return {
                'exam_type': exam_type,
                'parents_created': 0,
                'children_created': 0,
                'skipped': False,
            }

        grouping = _ai_group_topics(exam_type, topics, provider, model)
        parents, children = _write_taxonomy(exam_type, grouping)

        logger.info(
            "Taxonomy bootstrap for %s: %d parents, %d children",
            exam_type, parents, children,
        )
        return {
            'exam_type': exam_type,
            'parents_created': parents,
            'children_created': children,
            'skipped': False,
        }

    @staticmethod
    def classify_orphan_topic(
        exam_type: str,
        topic_key: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Optional[str]:
        """
        Classify a new topic into an existing parent category.

        Returns parent_topic_id or None if no parents exist.
        """
        roots = TopicTaxonomyRepository.find_roots_by_exam_type(exam_type)
        if not roots:
            return None

        parent_keys = [r['topic_key'] for r in roots]
        parent_id = _ai_classify_topic(
            exam_type, topic_key, parent_keys, provider, model,
        )

        if parent_id:
            # Insert the orphan topic with parent
            TopicTaxonomyRepository.create({
                'exam_type': exam_type,
                'topic_key': topic_key,
                'topic_label': json.dumps({'de': topic_key.replace('_', ' ').title()}),
                'parent_topic_id': parent_id,
                'weight': 1.0,
            })

        return parent_id


def _get_distinct_topics(exam_type: str) -> List[str]:
    """Get all distinct topic keys from exam_questions for an exam_type."""
    from app.infrastructure.persistence.database.connection import fetch_all
    rows = fetch_all(
        """SELECT DISTINCT unnest(topics) AS topic
           FROM assessments.exam_questions eq
           JOIN assessments.exams e ON eq.exam_id = e.exam_id
           JOIN assessments.exam_sessions es ON e.session_id = es.session_id
           WHERE es.exam_type = %s AND eq.status = 'ready'
           ORDER BY topic""",
        [exam_type],
    )
    return [r['topic'] for r in rows]


def _ai_group_topics(
    exam_type: str,
    topics: List[str],
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> List[Dict]:
    """Call AI to group topics into parent categories."""
    from app.infrastructure.ai.adapter import AIAdapter

    prompt = GROUPING_PROMPT.format(
        exam_type=exam_type,
        topics=', '.join(topics),
    )

    kwargs = {}
    if provider:
        kwargs['provider'] = provider
    if model:
        kwargs['model'] = model

    adapter = AIAdapter(**kwargs)
    response = adapter.send_request(
        prompt=prompt,
        temperature=0.3,
        max_tokens=4000,
    )

    raw = response.get('output_text', '[]')
    # Strip markdown code fences if present
    if '```' in raw:
        raw = raw.split('```')[1]
        if raw.startswith('json'):
            raw = raw[4:]

    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        logger.error("Failed to parse AI grouping response: %s", raw[:200])
        return []


def _ai_classify_topic(
    exam_type: str,
    topic_key: str,
    parent_keys: List[str],
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> Optional[str]:
    """Classify a single topic into one of the existing parent categories."""
    from app.infrastructure.ai.adapter import AIAdapter

    prompt = (
        f'Zu welcher Oberkategorie gehoert das Topic "{topic_key}" '
        f'fuer den Pruefungstyp "{exam_type}"?\n\n'
        f'Oberkategorien: {", ".join(parent_keys)}\n\n'
        f'Antworte NUR mit dem Key der Oberkategorie.'
    )

    kwargs = {}
    if provider:
        kwargs['provider'] = provider
    if model:
        kwargs['model'] = model

    try:
        adapter = AIAdapter(**kwargs)
        response = adapter.send_request(
            prompt=prompt,
            temperature=0.1,
            max_tokens=100,
        )
        answer = response.get('output_text', '').strip().lower()

        # Find matching parent
        from app.infrastructure.persistence.repositories.exams.topic_taxonomy import (
            TopicTaxonomyRepository,
        )
        parent = TopicTaxonomyRepository.find_by_topic_key(exam_type, answer)
        return str(parent['topic_id']) if parent else None

    except Exception:
        logger.exception("Failed to classify topic %s", topic_key)
        return None


def _write_taxonomy(
    exam_type: str,
    grouping: List[Dict],
) -> tuple:
    """Write AI grouping result to exam_topic_taxonomy. Returns (parents, children)."""
    import uuid

    parents_created = 0
    children_created = 0

    for group in grouping:
        parent_key = group.get('parent', 'allgemein')
        parent_label = group.get('parent_label', {'de': parent_key.replace('_', ' ').title()})

        parent_id = str(uuid.uuid4())
        TopicTaxonomyRepository.create({
            'topic_id': parent_id,
            'exam_type': exam_type,
            'topic_key': parent_key,
            'topic_label': json.dumps(parent_label) if isinstance(parent_label, dict) else parent_label,
            'parent_topic_id': None,
            'weight': len(group.get('children', [])),
        })
        parents_created += 1

        for child_key in group.get('children', []):
            TopicTaxonomyRepository.create({
                'exam_type': exam_type,
                'topic_key': child_key,
                'topic_label': json.dumps({'de': child_key.replace('_', ' ').title()}),
                'parent_topic_id': parent_id,
                'weight': 1.0,
            })
            children_created += 1

    return parents_created, children_created
```

### Step 3: Add Bootstrap Admin Endpoint

**File:** `backend/app/api/v1/panel/admin/exams/taxonomy.py` (create if not exists, extend if exists)

Add a bootstrap endpoint:

```python
@taxonomy_bp.route('/bootstrap', methods=['POST'])
@permission_required('admin.system:write')
def bootstrap_taxonomy():
    """Bootstrap taxonomy for an exam type from existing question data."""
    data = request.get_json() or {}
    exam_type = data.get('exam_type')
    if not exam_type:
        return error_response(ErrorCode.VALIDATION_FAILED, 400,
            details={'message': 'exam_type required'})

    result = TaxonomyBootstrapService.bootstrap_exam_type(
        exam_type=exam_type,
        provider=data.get('provider'),
        model=data.get('model'),
    )
    return jsonify({'success': True, 'data': result}), 200
```

### Step 4: Verify

```bash
# Backend starts without errors
cd backend && python -c "from app.application.services.exams.taxonomy_bootstrap_service import TaxonomyBootstrapService; print('OK')"

# Repository methods importable
python -c "from app.infrastructure.persistence.repositories.exams.topic_taxonomy import TopicTaxonomyRepository; print('OK')"
```

### Step 5: Commit

```bash
git add backend/app/application/services/exams/taxonomy_bootstrap_service.py
git add backend/app/infrastructure/persistence/repositories/exams/topic_taxonomy.py
git add backend/app/api/v1/panel/admin/exams/taxonomy.py
git commit -m "feat(exams): add taxonomy bootstrap service with AI grouping"
```

---

## Task 2: Dynamic ANALYSIS_PROMPT

**Goal:** Replace hardcoded 27 topics in ANALYSIS_PROMPT with dynamic list from taxonomy.

**Files:**
- Modify: `backend/app/infrastructure/tasks/exam_archive_tasks.py` (lines 30-44)
- Modify: `backend/app/infrastructure/tasks/exam_archive_tasks.py` (after analysis: auto-classify new topics)

### Step 1: Extract prompt builder function

**File:** `backend/app/infrastructure/tasks/exam_archive_tasks.py`

Replace the hardcoded ANALYSIS_PROMPT topic list with a dynamic builder:

```python
def _build_topic_list(exam_type: str) -> str:
    """Build topic list for ANALYSIS_PROMPT from taxonomy, with fallback."""
    from app.infrastructure.persistence.repositories.exams.topic_taxonomy import (
        TopicTaxonomyRepository,
    )
    topics = TopicTaxonomyRepository.find_all_by_exam_type(exam_type)
    if topics:
        topic_keys = sorted(set(t['topic_key'] for t in topics))
        return ', '.join(topic_keys)

    # Fallback: hardcoded list (used when taxonomy is empty)
    return (
        'subnetting, kalkulation, sql, erm, schutzbedarfsanalyse, '
        'osi_modell, dhcp, wlan, programmierung, itil, rechtsformen, '
        'organisationsformen, raid, virtualisierung, datenschutz, '
        'netzwerk, backup, it_sicherheit, projektmanagement, '
        'qualitaetsmanagement, datenbanken, hardware, software, '
        'cloud, verschluesselung, firewall, routing'
    )
```

Update ANALYSIS_PROMPT to use the dynamic list:

```python
def _build_analysis_prompt(exam_type: str) -> str:
    """Build the full analysis prompt with dynamic topic list."""
    topic_list = _build_topic_list(exam_type)
    return f"""Analysiere die folgende Pruefungsaufgabe...
    ...
    4. Tagge Topics aus dieser Liste (mehrere moeglich, neue Topics erlaubt):
       {topic_list}
    ..."""
```

### Step 2: Auto-classify orphan topics after analysis

In the analysis result handling (after topics are extracted from AI response), add orphan classification:

```python
def _register_new_topics(exam_type: str, extracted_topics: List[str]) -> None:
    """Check for new topics not in taxonomy and auto-classify them."""
    from app.infrastructure.persistence.repositories.exams.topic_taxonomy import (
        TopicTaxonomyRepository,
    )
    from app.application.services.exams.taxonomy_bootstrap_service import (
        TaxonomyBootstrapService,
    )

    known = TopicTaxonomyRepository.find_all_by_exam_type(exam_type)
    known_keys = {t['topic_key'] for t in known}

    for topic in extracted_topics:
        normalized = normalize_topic(topic)
        if normalized not in known_keys:
            logger.info("New topic discovered: %s for %s", normalized, exam_type)
            TaxonomyBootstrapService.classify_orphan_topic(
                exam_type=exam_type,
                topic_key=normalized,
            )
```

Call `_register_new_topics()` after question records are created in `analyze_exam_pdf_task`.

### Step 3: Verify

```bash
cd backend && python -c "
from app.infrastructure.tasks.exam_archive_tasks import _build_topic_list
topics = _build_topic_list('IHK_FISI_AP1')
print(f'Topic count: {len(topics.split(\",\"))}')
print('OK')
"
```

### Step 4: Commit

```bash
git add backend/app/infrastructure/tasks/exam_archive_tasks.py
git commit -m "feat(exams): dynamic ANALYSIS_PROMPT from taxonomy with auto-classify"
```

---

## Task 3: Course Generator — Taxonomy-Based Hierarchy

**Goal:** Rewrite course generator to group questions by taxonomy parent categories instead of flat topic list. Reduces 33 chapters to 8-10.

**Files:**
- Modify: `backend/app/domain/models/exam_course_plan.py`
- Modify: `backend/app/application/services/exams/course_generator_service.py`

### Step 1: Extend ChapterPlan with parent_topic

**File:** `backend/app/domain/models/exam_course_plan.py`

```python
@dataclass(frozen=True)
class ChapterPlan:
    """Immutable chapter plan within an exam course."""
    topic: str
    question_ids: List[str]
    lm_types: List[int]
    point_weight: float = 0
    question_count: int = 0
    parent_topic: Optional[str] = None      # NEW: parent category key
    parent_label: Optional[Dict] = None     # NEW: i18n label {"de": "...", "en": "..."}
    child_topics: Optional[List[str]] = None  # NEW: child topics in this chapter
```

### Step 2: Rewrite `_group_by_topic` to use taxonomy hierarchy

**File:** `backend/app/application/services/exams/course_generator_service.py`

Replace `_group_by_topic()` and `_merge_small_topics()` with a single `_group_by_taxonomy()`:

```python
def _group_by_taxonomy(
    questions: List[Dict],
    exam_type: str,
) -> Dict[str, Dict]:
    """Group questions by taxonomy parent categories.

    Returns: {parent_key: {'questions': [...], 'label': {...}, 'children': [...]}}

    Strategy:
    1. If taxonomy exists: group by parent_topic
    2. If no taxonomy: fall back to primary-topic grouping
    """
    from app.infrastructure.persistence.repositories.exams.topic_taxonomy import (
        TopicTaxonomyRepository,
    )

    all_topics = TopicTaxonomyRepository.find_all_by_exam_type(exam_type)
    if not all_topics:
        # Fallback: flat grouping (legacy behavior)
        return _group_flat(questions)

    # Build lookup: child_key -> parent info
    child_to_parent = {}
    parent_info = {}
    for t in all_topics:
        if t.get('parent_topic_id') is None:
            # This is a root/parent
            parent_info[t['topic_key']] = {
                'label': t.get('topic_label', {}),
                'topic_id': t['topic_id'],
            }
        else:
            # Find parent key
            parent = next(
                (p for p in all_topics
                 if str(p['topic_id']) == str(t['parent_topic_id'])),
                None,
            )
            if parent:
                child_to_parent[t['topic_key']] = parent['topic_key']

    # Group questions by parent category
    groups: Dict[str, Dict] = {}
    seen_ids: set = set()

    for q in questions:
        qid = q['question_id']
        if qid in seen_ids:
            continue
        seen_ids.add(qid)

        topics = q.get('topics') or []
        primary = normalize_topic(topics[0]) if topics else 'allgemein'

        # Resolve to parent
        parent_key = child_to_parent.get(primary, primary)
        # If topic itself is a parent, use it directly
        if parent_key not in parent_info and primary in parent_info:
            parent_key = primary

        if parent_key not in groups:
            info = parent_info.get(parent_key, {})
            groups[parent_key] = {
                'questions': [],
                'label': info.get('label', {'de': parent_key.replace('_', ' ').title()}),
                'children': set(),
            }

        groups[parent_key]['questions'].append(q)
        groups[parent_key]['children'].add(primary)

    # Convert children sets to sorted lists
    for g in groups.values():
        g['children'] = sorted(g['children'])

    return groups


def _group_flat(questions: List[Dict]) -> Dict[str, Dict]:
    """Legacy flat grouping when no taxonomy exists."""
    groups: Dict[str, Dict] = {}
    seen_ids: set = set()

    for q in questions:
        qid = q['question_id']
        if qid in seen_ids:
            continue
        seen_ids.add(qid)

        topics = q.get('topics') or []
        primary = normalize_topic(topics[0]) if topics else 'allgemein'

        if primary not in groups:
            groups[primary] = {
                'questions': [],
                'label': {'de': primary.replace('_', ' ').title()},
                'children': [],
            }
        groups[primary]['questions'].append(q)

    return groups
```

### Step 3: Update `preview()` to use new grouping

**File:** `backend/app/application/services/exams/course_generator_service.py`

Update `preview()` method to use `_group_by_taxonomy()` and populate new ChapterPlan fields:

```python
@staticmethod
def preview(
    exam_type_key: str,
    region: str = 'alle',
    language: str = 'de',
) -> ExamCoursePlan:
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

    topic_groups = _group_by_taxonomy(questions, exam_type_key)

    chapters = []
    for parent_key, group_data in sorted(
        topic_groups.items(),
        key=lambda x: sum(q.get('points', 0) for q in x[1]['questions']),
        reverse=True,
    ):
        topic_questions = group_data['questions']
        lm_types = LMContentMapper.select_lm_types(topic_questions)
        total_points = sum(q.get('points', 0) for q in topic_questions)

        chapters.append(ChapterPlan(
            topic=parent_key,
            question_ids=[q['question_id'] for q in topic_questions],
            lm_types=lm_types,
            point_weight=total_points,
            question_count=len(topic_questions),
            parent_topic=parent_key,
            parent_label=group_data.get('label'),
            child_topics=group_data.get('children', []),
        ))

    simulation_exam_ids = _find_simulation_exams(exam_type_key, region)
    title = _build_title(exam_type_key, region, language)

    return ExamCoursePlan(
        title=title,
        exam_type=exam_type_key,
        region=region,
        chapters=chapters,
        simulation_exam_ids=simulation_exam_ids,
    )
```

### Step 4: Remove old `_group_by_topic` and `_merge_small_topics`

Delete both functions (they are replaced by `_group_by_taxonomy` and `_group_flat`).

### Step 5: Update builder to use parent_label for chapter title

**File:** `backend/app/application/services/exams/course_generator_builder.py` (line 155)

```python
# In _build_chapter():
# Old:
#   'title': chapter_plan.topic.replace('_', ' ').title(),
# New:
label = chapter_plan.parent_label or {}
if isinstance(label, str):
    import json
    try:
        label = json.loads(label)
    except (json.JSONDecodeError, TypeError):
        label = {}
chapter_title = label.get(language, chapter_plan.topic.replace('_', ' ').title())
```

### Step 6: Verify

```bash
cd backend && python -c "
from app.domain.models.exam_course_plan import ChapterPlan
cp = ChapterPlan(topic='netzwerk', question_ids=[], lm_types=[0],
                 parent_topic='netzwerk', parent_label={'de': 'Netzwerktechnik'},
                 child_topics=['subnetting', 'dhcp', 'routing'])
print(f'parent={cp.parent_topic}, children={cp.child_topics}')
print('OK')
"
```

### Step 7: Commit

```bash
git add backend/app/domain/models/exam_course_plan.py
git add backend/app/application/services/exams/course_generator_service.py
git add backend/app/application/services/exams/course_generator_builder.py
git commit -m "feat(exams): taxonomy-based chapter grouping in course generator"
```

---

## Task 4: AI Editor Pipeline Integration

**Goal:** Replace duplicate AI generation in builder (`_generate_deep_explanation`, `_generate_step_by_step`) with AI Editor pipeline via plan creation. Content generation for LM0 and LM1 runs through the existing `plan_execution.py` infrastructure.

**Files:**
- Modify: `backend/app/application/services/exams/course_generator_builder.py`
- Create: `backend/app/application/services/exams/course_plan_factory.py`

### Step 1: Create plan factory for exam courses

**File:** `backend/app/application/services/exams/course_plan_factory.py`

This factory creates AI Editor plans from ExamCoursePlan chapters.

```python
"""
Course Plan Factory — Creates AI Editor plans for exam course chapters.

Bridges the Exam Course Generator (structure) with the AI Editor Pipeline (content).
Instead of generating LM content directly, we create an AI Editor plan per chapter
and let the existing pipeline handle content generation.
"""
import json
import logging
from typing import Dict, Any, List, Optional

from app.domain.models.exam_course_plan import ChapterPlan

logger = logging.getLogger(__name__)

# Skills that need AI generation (LM types that require the pipeline)
AI_GENERATED_LM_TYPES = {0, 1}  # Deep Explanation, Step by Step

# Skill codes for AI-generated LM types
LM_SKILL_MAP = {
    0: 'generate_deep_explanation',
    1: 'generate_step_by_step',
}


class CoursePlanFactory:
    """Creates AI Editor plans from exam course structure."""

    @staticmethod
    def create_chapter_plan(
        course_id: str,
        chapter_id: str,
        chapter_plan: ChapterPlan,
        questions: List[Dict],
        language: str = 'de',
    ) -> Dict[str, Any]:
        """
        Create an AI Editor plan for a single chapter.

        Only creates steps for LM types that need AI generation (0, 1).
        Static LM types (5-11) are handled directly by LMContentMapper.

        Returns: plan_data dict compatible with plan_execution.py
        """
        steps = []
        step_idx = 0

        # Build context from questions for the AI
        question_context = _build_question_context(questions)

        for lm_type in chapter_plan.lm_types:
            if lm_type not in AI_GENERATED_LM_TYPES:
                continue

            skill_code = LM_SKILL_MAP.get(lm_type)
            if not skill_code:
                continue

            topic_label = chapter_plan.topic.replace('_', ' ').title()
            if chapter_plan.parent_label:
                label = chapter_plan.parent_label
                if isinstance(label, str):
                    try:
                        label = json.loads(label)
                    except (json.JSONDecodeError, TypeError):
                        label = {}
                topic_label = label.get(language, topic_label)

            steps.append({
                'step_id': f'0-{step_idx}',
                'skill_code': skill_code,
                'target_title': topic_label,
                'target_type': 'chapter',
                'target_id': chapter_id,
                'learning_methods': [lm_type],
                'parameters': {
                    'difficulty': 'medium',
                    'topic': chapter_plan.topic,
                    'topic_label': topic_label,
                    'language': language,
                    'question_context': question_context,
                    'child_topics': chapter_plan.child_topics or [],
                },
                'status': 'pending',
                'tokens_used': 0,
            })
            step_idx += 1

        plan_data = {
            'course_id': course_id,
            'source': 'exam_course_generator',
            'phases': [
                {
                    'phase_idx': 0,
                    'title': chapter_plan.topic.replace('_', ' ').title(),
                    'chapter_id': chapter_id,
                    'steps': steps,
                }
            ],
        }

        return plan_data

    @staticmethod
    def needs_ai_generation(chapter_plan: ChapterPlan) -> bool:
        """Check if any LM types in this chapter need AI generation."""
        return any(lm in AI_GENERATED_LM_TYPES for lm in chapter_plan.lm_types)


def _build_question_context(questions: List[Dict], max_questions: int = 10) -> str:
    """Build a text context from exam questions for AI generation."""
    lines = []
    for q in questions[:max_questions]:
        text = q.get('question_text', '')
        if isinstance(text, dict):
            text = text.get('de', str(text))
        if text:
            lines.append(f"- {text[:200]}")

    return '\n'.join(lines) if lines else ''
```

### Step 2: Modify builder to use plan factory for AI-generated LMs

**File:** `backend/app/application/services/exams/course_generator_builder.py`

Replace `_build_lm_data()` for LM types 0 and 1: instead of calling `_generate_deep_explanation()` and `_generate_step_by_step()` directly, the builder creates static LMs immediately and queues AI-generated LMs via the plan factory.

The key change is in `CourseGeneratorBuilder.build()`:

```python
class CourseGeneratorBuilder:
    """Builds and persists course structure from ExamCoursePlan."""

    @staticmethod
    def build(
        plan: ExamCoursePlan,
        creator_user_id: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create course + chapters + static LM instances from plan.
        AI-generated LMs are created via AI Editor pipeline (async).

        Returns:
            {course_id, chapters_count, lm_count, tokens_used, ai_plan_ids}
        """
        options = options or {}
        language = options.get('language', 'de')

        course_id = _create_course(plan, creator_user_id, language)

        total_lm_count, total_tokens, ai_plan_ids = _build_all_chapters(
            course_id, plan, creator_user_id, options, language,
        )

        logger.info(
            "Course generation complete: %s — %d chapters, %d LMs, %d AI plans queued",
            course_id, len(plan.chapters), total_lm_count, len(ai_plan_ids),
        )

        return {
            'course_id': course_id,
            'chapters_count': (
                len(plan.chapters) + len(plan.simulation_exam_ids)
            ),
            'lm_count': total_lm_count,
            'tokens_used': total_tokens,
            'ai_plan_ids': ai_plan_ids,
            'status': 'generating' if ai_plan_ids else 'ready',
        }
```

Update `_build_all_chapters` to collect AI plan IDs:

```python
def _build_all_chapters(
    course_id: str,
    plan: ExamCoursePlan,
    creator_user_id: str,
    options: Dict[str, Any],
    language: str,
) -> tuple:
    """Build topic chapters + simulation chapters. Returns (lm_count, tokens, ai_plan_ids)."""
    total_lm = 0
    total_tokens = 0
    ai_plan_ids = []

    for idx, chapter_plan in enumerate(plan.chapters):
        result = _build_chapter(
            course_id, chapter_plan, idx, creator_user_id, options, language,
        )
        total_lm += result['lm_count']
        total_tokens += result.get('tokens_used', 0)
        if result.get('ai_plan_id'):
            ai_plan_ids.append(result['ai_plan_id'])

    for sim_exam_id in plan.simulation_exam_ids:
        sim = _build_simulation_chapter(course_id, sim_exam_id)
        total_lm += sim['lm_count']

    return total_lm, total_tokens, ai_plan_ids
```

Update `_build_chapter` to create AI plans for LM 0/1:

```python
def _build_chapter(
    course_id: str,
    chapter_plan: ChapterPlan,
    order_index: int,
    creator_user_id: str,
    options: Dict[str, Any],
    language: str = 'de',
) -> Dict[str, Any]:
    """Build a single topic chapter with static LMs + AI plan for generated LMs."""
    from app.application.services.exams.course_plan_factory import CoursePlanFactory

    # ... (chapter creation stays the same) ...

    questions = _fetch_chapter_questions(chapter_plan.question_ids)

    # Create static LM instances (types 5-11)
    result = _create_static_lm_instances(
        chapter_id, chapter_plan, questions, options, language,
    )

    # Queue AI-generated LMs (types 0, 1) via AI Editor pipeline
    ai_plan_id = None
    if CoursePlanFactory.needs_ai_generation(chapter_plan):
        ai_plan_id = _queue_ai_generation(
            course_id, chapter_id, chapter_plan,
            questions, creator_user_id, language,
        )

    result['ai_plan_id'] = ai_plan_id
    return result
```

New function to queue AI generation:

```python
def _queue_ai_generation(
    course_id: str,
    chapter_id: str,
    chapter_plan: ChapterPlan,
    questions: List[Dict],
    user_id: str,
    language: str,
) -> Optional[str]:
    """Create an AI Editor plan for AI-generated LMs and queue for execution."""
    from app.application.services.exams.course_plan_factory import CoursePlanFactory
    from app.infrastructure.persistence.repositories.ai.content_plans import (
        ContentPlanRepository,
    )

    plan_data = CoursePlanFactory.create_chapter_plan(
        course_id=course_id,
        chapter_id=chapter_id,
        chapter_plan=chapter_plan,
        questions=questions,
        language=language,
    )

    if not plan_data['phases'][0]['steps']:
        return None

    plan = ContentPlanRepository.create({
        'course_id': course_id,
        'scope': 'chapter',
        'scope_id': chapter_id,
        'user_id': user_id,
        'status': 'approved',  # Auto-approved for exam courses
        'plan_data': plan_data,
    })

    return str(plan['plan_id'])
```

### Step 3: Rename `_create_lm_instances` to `_create_static_lm_instances`

Remove LM types 0 and 1 from the static creation flow (they go through AI Editor):

```python
def _create_static_lm_instances(
    chapter_id: str,
    chapter_plan: ChapterPlan,
    questions: List[Dict],
    options: Dict[str, Any],
    language: str,
) -> Dict[str, Any]:
    """Create static LM instances (types 5-11) from question data mapping."""
    lm_count = 0

    for lm_order, lm_type in enumerate(chapter_plan.lm_types):
        # Skip AI-generated types (handled by AI Editor pipeline)
        if lm_type in (0, 1):
            continue

        mapper = LM_MAPPER.get(lm_type)
        if not mapper:
            continue

        map_fn = getattr(LMContentMapper, mapper, None)
        if not map_fn:
            continue

        lm_data = map_fn(questions)
        items_key = list(lm_data.keys())[0] if lm_data else None
        if items_key and len(lm_data.get(items_key, [])) == 0:
            continue

        title = _lm_title(chapter_plan.topic, lm_type, language)
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

    return {'lm_count': lm_count, 'tokens_used': 0}
```

### Step 4: Delete duplicate AI generation functions

Remove from `course_generator_builder.py`:
- `_generate_deep_explanation()` (lines 306-342)
- `_generate_step_by_step()` (lines 345-379)
- `_create_ai_adapter()` (lines 295-303)
- The LM 0/1 branches in `_build_lm_data()` (lines 274-279)

Also remove `course_generator_prompts.py` if it exists and is only used by these deleted functions.

### Step 5: Verify

```bash
cd backend && python -c "
from app.application.services.exams.course_plan_factory import CoursePlanFactory
from app.domain.models.exam_course_plan import ChapterPlan
cp = ChapterPlan(topic='netzwerk', question_ids=['q1'], lm_types=[0, 1, 6, 10],
                 parent_topic='netzwerk')
print(f'Needs AI: {CoursePlanFactory.needs_ai_generation(cp)}')
plan = CoursePlanFactory.create_chapter_plan('c1', 'ch1', cp, [{'question_text': 'Test'}])
print(f'Steps: {len(plan[\"phases\"][0][\"steps\"])}')
print('OK')
"
```

### Step 6: Commit

```bash
git add backend/app/application/services/exams/course_plan_factory.py
git add backend/app/application/services/exams/course_generator_builder.py
git commit -m "feat(exams): integrate AI Editor pipeline, remove duplicate content generation"
```

---

## Task 5: Background Course Generation with Progress

**Goal:** Create a Celery task that orchestrates multi-chapter AI generation with Redis progress tracking.

**Files:**
- Create: `backend/app/infrastructure/tasks/course_generation_tasks.py`
- Modify: `backend/app/infrastructure/tasks/__init__.py` (barrel export)
- Modify: `backend/app/application/services/exams/course_generator_builder.py` (trigger task)

### Step 1: Create course generation Celery task

**File:** `backend/app/infrastructure/tasks/course_generation_tasks.py`

```python
"""
Course Generation Tasks — Celery background tasks for exam course content.

Orchestrates AI Editor plan execution for all chapters in an exam course.
Tracks progress in Redis for real-time frontend updates.
"""
import logging
import json
from typing import List

from app.core.bootstrap.extensions import celery, redis_client

logger = logging.getLogger(__name__)

PROGRESS_KEY = 'course_generation:{course_id}'
PROGRESS_TTL = 3600  # 1 hour


@celery.task(bind=True, max_retries=1, default_retry_delay=60)
def generate_course_content_task(
    self,
    course_id: str,
    ai_plan_ids: List[str],
    user_id: str,
) -> dict:
    """
    Execute AI Editor plans for all chapters in a course.

    Progress is tracked in Redis:
    - course_generation:{course_id} = {total, completed, failed, status}
    """
    from app.application.services.ai.plan.plan_execution import (
        execute_plan_background,
    )
    from app.infrastructure.persistence.repositories.ai.content_plans import (
        ContentPlanRepository,
    )

    total = len(ai_plan_ids)
    completed = 0
    failed = 0

    _update_progress(course_id, total, completed, failed, 'generating')

    for plan_id in ai_plan_ids:
        try:
            plan = ContentPlanRepository.find_by_id(plan_id)
            if not plan:
                logger.error("Plan %s not found, skipping", plan_id)
                failed += 1
                _update_progress(course_id, total, completed, failed, 'generating')
                continue

            # Execute plan synchronously within Celery worker
            execute_plan_background(plan_id, plan, user_id)
            completed += 1

        except Exception:
            logger.exception("Failed to execute plan %s", plan_id)
            failed += 1

        _update_progress(course_id, total, completed, failed, 'generating')

    status = 'ready' if failed == 0 else 'partial'
    _update_progress(course_id, total, completed, failed, status)

    logger.info(
        "Course %s generation complete: %d/%d chapters, %d failed",
        course_id, completed, total, failed,
    )

    return {
        'course_id': course_id,
        'total': total,
        'completed': completed,
        'failed': failed,
        'status': status,
    }


def get_generation_progress(course_id: str) -> dict:
    """Read generation progress from Redis."""
    key = PROGRESS_KEY.format(course_id=course_id)
    raw = redis_client.get(key)
    if not raw:
        return {'total': 0, 'completed': 0, 'failed': 0, 'status': 'unknown'}
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {'total': 0, 'completed': 0, 'failed': 0, 'status': 'unknown'}


def _update_progress(
    course_id: str,
    total: int,
    completed: int,
    failed: int,
    status: str,
) -> None:
    """Update generation progress in Redis."""
    key = PROGRESS_KEY.format(course_id=course_id)
    data = {
        'total': total,
        'completed': completed,
        'failed': failed,
        'status': status,
    }
    redis_client.setex(key, PROGRESS_TTL, json.dumps(data))
```

### Step 2: Update tasks barrel export

**File:** `backend/app/infrastructure/tasks/__init__.py`

Add:
```python
from .course_generation_tasks import generate_course_content_task, get_generation_progress
```

### Step 3: Trigger Celery task from builder

**File:** `backend/app/application/services/exams/course_generator_builder.py`

At the end of `CourseGeneratorBuilder.build()`, after structure is created:

```python
# After all chapters are built, trigger async content generation
if ai_plan_ids:
    from app.infrastructure.tasks.course_generation_tasks import (
        generate_course_content_task,
    )
    generate_course_content_task.delay(
        course_id, ai_plan_ids, creator_user_id,
    )
```

### Step 4: Add progress endpoint

**File:** `backend/app/api/v1/panel/admin/exams/courses.py` (or appropriate endpoint file)

```python
@bp.route('/courses/<course_id>/generation-progress', methods=['GET'])
@permission_required('admin.content:read')
def get_course_generation_progress(course_id: str):
    """Get real-time generation progress for an exam course."""
    from app.infrastructure.tasks.course_generation_tasks import (
        get_generation_progress,
    )
    progress = get_generation_progress(course_id)
    return jsonify({'success': True, 'data': progress}), 200
```

### Step 5: Verify

```bash
cd backend && python -c "
from app.infrastructure.tasks.course_generation_tasks import get_generation_progress
print(get_generation_progress('nonexistent'))
print('OK')
"
```

### Step 6: Commit

```bash
git add backend/app/infrastructure/tasks/course_generation_tasks.py
git add backend/app/infrastructure/tasks/__init__.py
git add backend/app/application/services/exams/course_generator_builder.py
git commit -m "feat(exams): Celery background course generation with Redis progress"
```

---

## Task 6: Exam Mode (Database + Backend)

**Goal:** Add exam_mode flag and exam_config to courses for Pruefungsmodus support.

**Files:**
- Create: `backend/migrations/02_Content/102_exam_mode_on_courses.sql`
- Modify: `backend/app/application/services/exams/course_generator_builder.py`

### Step 1: Create migration

**File:** `backend/migrations/02_Content/102_exam_mode_on_courses.sql`

```sql
-- Exam Mode: Pruefungsmodus fuer generierte Pruefungskurse
-- Adds exam_mode flag and exam_config JSONB to courses

ALTER TABLE courses.courses
    ADD COLUMN IF NOT EXISTS exam_mode BOOLEAN DEFAULT FALSE;

ALTER TABLE courses.courses
    ADD COLUMN IF NOT EXISTS exam_config JSONB DEFAULT NULL;

-- Index for quick filtering
CREATE INDEX IF NOT EXISTS idx_courses_exam_mode
    ON courses.courses (exam_mode) WHERE exam_mode = TRUE;

COMMENT ON COLUMN courses.courses.exam_mode IS 'Whether this course is an exam simulation course';
COMMENT ON COLUMN courses.courses.exam_config IS 'Exam configuration: time_limit_minutes, total_points, passing_percentage, source_exam_type, source_region';
```

### Step 2: Run migration

```bash
cd backend && python run_migration.py
```

### Step 3: Update course creation in builder

**File:** `backend/app/application/services/exams/course_generator_builder.py`

In `_create_course()`, add exam_mode fields:

```python
def _create_course(
    plan: ExamCoursePlan, creator_user_id: str, language: str,
) -> str:
    """Create the course record with exam_mode enabled."""
    descriptions = {
        'de': f'Automatisch generiert aus {plan.total_questions} '
              f'echten Pruefungsaufgaben.',
        'en': f'Auto-generated from {plan.total_questions} '
              f'real exam questions.',
    }
    course = CourseRepositoryCRUD.create({
        'title': plan.title,
        'creator_id': creator_user_id,
        'description': descriptions.get(language, descriptions['de']),
        'tags': ['exam-based', 'auto-generated', plan.exam_type.lower()],
        'level': 'intermediate',
        'exam_mode': True,
        'exam_config': {
            'time_limit_minutes': 90,
            'total_points': sum(c.point_weight for c in plan.chapters),
            'passing_percentage': 50,
            'source_exam_type': plan.exam_type,
            'source_region': plan.region,
            'simulation_exam_ids': plan.simulation_exam_ids,
        },
    })
    course_id = str(course['course_id'])
    logger.info("Created exam course %s: %s", course_id, plan.title)
    return course_id
```

### Step 4: Verify migration

```bash
psql service=devdb -c "
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_schema = 'courses' AND table_name = 'courses'
  AND column_name IN ('exam_mode', 'exam_config');
"
```

### Step 5: Commit

```bash
git add backend/migrations/02_Content/102_exam_mode_on_courses.sql
git add backend/app/application/services/exams/course_generator_builder.py
git commit -m "feat(exams): add exam_mode + exam_config to courses table"
```

---

## Task 7: Frontend — Hierarchical Preview + Generation Progress

**Goal:** Update ExamCourseGenerator.vue to show taxonomy-based chapter hierarchy and generation progress.

**Files:**
- Modify: `frontend/src/presentation/components/panel/admin/assessment/exams/ExamCourseGenerator.vue`
- Create: `frontend/src/infrastructure/api/clients/panel/admin/exams/generation.api.ts` (progress polling)

### Step 1: Add generation progress API client

**File:** `frontend/src/infrastructure/api/clients/panel/admin/exams/generation.api.ts`

```typescript
import { apiClient } from '@/infrastructure/api/client'

export interface GenerationProgress {
  total: number
  completed: number
  failed: number
  status: 'generating' | 'ready' | 'partial' | 'unknown'
}

export interface GenerateResult {
  course_id: string
  chapters_count: number
  lm_count: number
  status: 'generating' | 'ready'
  ai_plan_ids: string[]
}

export const examGenerationApi = {
  getProgress(courseId: string): Promise<GenerationProgress> {
    return apiClient
      .get(`/panel/admin/exam-courses/courses/${courseId}/generation-progress`)
      .then(res => res.data.data)
  },
}
```

### Step 2: Update ExamCourseGenerator.vue preview display

In the template, update the chapter list to show hierarchy information:

```vue
<!-- Chapter preview with hierarchy -->
<div v-for="chapter in previewPlan.chapters" :key="chapter.topic" class="border rounded-lg p-4 mb-3">
  <div class="flex items-center justify-between">
    <div>
      <h4 class="font-semibold text-lg">
        {{ chapter.parent_label?.[locale] || chapter.topic.replace(/_/g, ' ') }}
      </h4>
      <p class="text-sm text-gray-500">
        {{ chapter.question_count }} {{ $t('exam.questions') }},
        {{ Math.round(chapter.point_weight) }} {{ $t('exam.points') }}
      </p>
      <!-- Child topics -->
      <div v-if="chapter.child_topics?.length" class="mt-1 flex flex-wrap gap-1">
        <span
          v-for="child in chapter.child_topics"
          :key="child"
          class="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded"
        >
          {{ child.replace(/_/g, ' ') }}
        </span>
      </div>
    </div>
    <div class="text-right text-sm text-gray-400">
      {{ chapter.lm_types.length }} LMs
    </div>
  </div>
</div>
```

### Step 3: Add generation progress tracking

In the script setup, add polling for generation progress after course is created:

```typescript
const generationProgress = ref<GenerationProgress | null>(null)
const generatingCourseId = ref<string | null>(null)
let progressInterval: ReturnType<typeof setInterval> | null = null

async function pollProgress() {
  if (!generatingCourseId.value) return
  try {
    generationProgress.value = await examGenerationApi.getProgress(generatingCourseId.value)
    if (generationProgress.value.status !== 'generating') {
      stopPolling()
    }
  } catch {
    // Ignore polling errors
  }
}

function startPolling(courseId: string) {
  generatingCourseId.value = courseId
  progressInterval = setInterval(pollProgress, 3000)
  pollProgress() // immediate first poll
}

function stopPolling() {
  if (progressInterval) {
    clearInterval(progressInterval)
    progressInterval = null
  }
}

onUnmounted(() => stopPolling())
```

Update the generate handler:

```typescript
async function handleGenerate() {
  const result = await examCourseApi.generate(previewPlan.value)
  if (result.status === 'generating') {
    startPolling(result.course_id)
  }
}
```

### Step 4: Add progress UI in template

```vue
<!-- Generation progress -->
<div v-if="generationProgress" class="mt-4 border rounded-lg p-4 bg-blue-50">
  <div class="flex items-center justify-between mb-2">
    <span class="font-medium">{{ $t('exam.generating') }}</span>
    <span class="text-sm">
      {{ generationProgress.completed }}/{{ generationProgress.total }}
      {{ $t('exam.chaptersReady') }}
    </span>
  </div>
  <div class="w-full bg-gray-200 rounded-full h-2">
    <div
      class="bg-blue-600 h-2 rounded-full transition-all duration-500"
      :style="{ width: `${(generationProgress.completed / Math.max(generationProgress.total, 1)) * 100}%` }"
    />
  </div>
  <p v-if="generationProgress.status === 'ready'" class="mt-2 text-green-600 text-sm">
    {{ $t('exam.generationComplete') }}
  </p>
  <p v-if="generationProgress.failed > 0" class="mt-2 text-amber-600 text-sm">
    {{ generationProgress.failed }} {{ $t('exam.chaptersFailed') }}
  </p>
</div>
```

### Step 5: Add i18n keys

**Files:** `frontend/src/infrastructure/i18n/locales/{de,en,pl}/exam.json` (or appropriate namespace)

```json
// de
{
  "generating": "Kurs wird generiert...",
  "chaptersReady": "Kapitel fertig",
  "generationComplete": "Alle Kapitel erfolgreich generiert!",
  "chaptersFailed": "Kapitel fehlgeschlagen"
}

// en
{
  "generating": "Generating course...",
  "chaptersReady": "chapters ready",
  "generationComplete": "All chapters generated successfully!",
  "chaptersFailed": "chapters failed"
}

// pl
{
  "generating": "Generowanie kursu...",
  "chaptersReady": "rozdzialy gotowe",
  "generationComplete": "Wszystkie rozdzialy wygenerowane pomyslnie!",
  "chaptersFailed": "rozdzialy nie powiodly sie"
}
```

### Step 6: Verify build

```bash
cd frontend && npm run build
```

### Step 7: Commit

```bash
git add frontend/src/infrastructure/api/clients/panel/admin/exams/generation.api.ts
git add frontend/src/presentation/components/panel/admin/assessment/exams/ExamCourseGenerator.vue
git add frontend/src/infrastructure/i18n/locales/
git commit -m "feat(exams): hierarchical preview + generation progress in frontend"
```

---

## Verification Checklist

After all tasks are complete:

```bash
# 1. Backend starts
cd backend && python -c "from app import create_app; create_app()"

# 2. Frontend builds
cd frontend && npm run build

# 3. Taxonomy bootstrap works (manual test)
# POST /api/v1/admin/exam-courses/taxonomy/bootstrap
# Body: {"exam_type": "IHK_FISI_AP1"}

# 4. Preview shows 8-10 chapters (not 33)
# GET /api/v1/admin/exam-courses/preview?exam_type=IHK_FISI_AP1

# 5. Generate creates course with exam_mode = true
# POST /api/v1/admin/exam-courses/generate

# 6. Progress endpoint returns status
# GET /api/v1/admin/exam-courses/courses/{id}/generation-progress

# 7. DB verification
psql service=devdb -c "
SELECT topic_key, parent_topic_id IS NOT NULL as has_parent
FROM assessments.exam_topic_taxonomy
WHERE exam_type = 'IHK_FISI_AP1'
LIMIT 20;
"
```

---

## Summary

| Task | Files | Action | LOC Delta |
|------|-------|--------|-----------|
| 1 | `taxonomy_bootstrap_service.py`, `topic_taxonomy.py`, `taxonomy.py` | New service + repo extension | ~+250 |
| 2 | `exam_archive_tasks.py` | Dynamic prompt + auto-classify | ~+50 -10 |
| 3 | `exam_course_plan.py`, `course_generator_service.py`, `course_generator_builder.py` | Taxonomy-based grouping | ~+80 -60 |
| 4 | `course_plan_factory.py`, `course_generator_builder.py` | AI Editor integration | ~+120 -90 |
| 5 | `course_generation_tasks.py`, `__init__.py`, builder | Celery + Redis progress | ~+100 |
| 6 | Migration, builder | Exam mode flag | ~+20 |
| 7 | Vue component, API client, i18n | Frontend hierarchy + progress | ~+100 |

**Netto:** ~+560 new LOC across 10+ files, ~-160 removed (duplicate AI generation). All files stay under 500 LOC limit (G01).
