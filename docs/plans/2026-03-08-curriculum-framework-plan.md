# Curriculum Framework Integration — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Offizielle Rahmenpläne (IHK, Hochschule, Zertifizierungen) ins System integrieren mit AI-PDF-Import, Fragen-Mapping und erweitertem Schwächenprofil.

**Architecture:** Neue DB-Tabellen im `assessments` Schema (4 Curriculum-Tabellen + 2 Mapping-Tabellen). Repository → Service → API Pattern wie bestehende Exam Intelligence. Rahmenplan als obere Ebene über der bestehenden Topic Taxonomy.

**Tech Stack:** Flask, psycopg3 (raw SQL), Vue 3 Composition API, TypeScript, AIAdapter (Tool-Call Pattern)

**Design Doc:** `docs/plans/2026-03-08-curriculum-framework-design.md`

---

## Task 1: DB Migration — Curriculum Tables

**Files:**
- Create: `backend/migrations/02_Content/103_curriculum_framework.sql`

**Step 1: Write the migration**

```sql
-- Migration: 103_curriculum_framework.sql
-- Curriculum Framework tables for official training plans (IHK, university, certifications)

-- 1. Main framework container
CREATE TABLE IF NOT EXISTS assessments.curriculum_frameworks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    framework_type VARCHAR(50) NOT NULL DEFAULT 'custom',
    source_document VARCHAR(500),
    version VARCHAR(50),
    valid_from DATE,
    valid_until DATE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_framework_type CHECK (framework_type IN (
        'ihk_ausbildung', 'hochschule', 'zertifizierung', 'custom'
    ))
);

-- 2. Sections (e.g. Abschnitt A, B, C in IHK Rahmenplan)
CREATE TABLE IF NOT EXISTS assessments.curriculum_sections (
    id SERIAL PRIMARY KEY,
    framework_id INT NOT NULL REFERENCES assessments.curriculum_frameworks(id) ON DELETE CASCADE,
    section_code VARCHAR(10) NOT NULL,
    display_name JSONB NOT NULL DEFAULT '{}',
    description JSONB DEFAULT '{}',
    order_index INT NOT NULL DEFAULT 0,
    applies_to TEXT[],
    UNIQUE (framework_id, section_code)
);

-- 3. Positions (Berufsbildpositionen)
CREATE TABLE IF NOT EXISTS assessments.curriculum_positions (
    id SERIAL PRIMARY KEY,
    section_id INT NOT NULL REFERENCES assessments.curriculum_sections(id) ON DELETE CASCADE,
    position_number VARCHAR(10) NOT NULL,
    display_name JSONB NOT NULL DEFAULT '{}',
    description JSONB DEFAULT '{}',
    order_index INT NOT NULL DEFAULT 0,
    training_period VARCHAR(20),
    UNIQUE (section_id, position_number)
);

-- 4. Objectives (Lernziele a, b, c...)
CREATE TABLE IF NOT EXISTS assessments.curriculum_objectives (
    id SERIAL PRIMARY KEY,
    position_id INT NOT NULL REFERENCES assessments.curriculum_positions(id) ON DELETE CASCADE,
    objective_code VARCHAR(10) NOT NULL,
    description JSONB NOT NULL DEFAULT '{}',
    order_index INT NOT NULL DEFAULT 0,
    competency_level VARCHAR(20),
    UNIQUE (position_id, objective_code),
    CONSTRAINT chk_competency_level CHECK (
        competency_level IS NULL OR competency_level IN ('kennen', 'anwenden', 'beherrschen')
    )
);

-- 5. Mapping: Curriculum Objective <-> Topic Taxonomy
CREATE TABLE IF NOT EXISTS assessments.curriculum_topic_mapping (
    id SERIAL PRIMARY KEY,
    curriculum_objective_id INT NOT NULL REFERENCES assessments.curriculum_objectives(id) ON DELETE CASCADE,
    topic_id INT NOT NULL REFERENCES assessments.exam_topic_taxonomy(id) ON DELETE CASCADE,
    confidence FLOAT NOT NULL DEFAULT 0.0,
    mapped_by VARCHAR(10) NOT NULL DEFAULT 'ai',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (curriculum_objective_id, topic_id),
    CONSTRAINT chk_mapped_by CHECK (mapped_by IN ('ai', 'admin'))
);

-- 6. Mapping: Exam Question <-> Curriculum Objective
CREATE TABLE IF NOT EXISTS assessments.exam_question_curriculum_tags (
    id SERIAL PRIMARY KEY,
    question_id INT NOT NULL REFERENCES assessments.exam_questions(id) ON DELETE CASCADE,
    curriculum_objective_id INT NOT NULL REFERENCES assessments.curriculum_objectives(id) ON DELETE CASCADE,
    confidence FLOAT NOT NULL DEFAULT 0.0,
    tagged_by VARCHAR(10) NOT NULL DEFAULT 'ai',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (question_id, curriculum_objective_id),
    CONSTRAINT chk_tagged_by CHECK (tagged_by IN ('ai', 'admin'))
);

-- 7. Link exam_type_registry to curriculum framework
ALTER TABLE assessments.exam_type_registry
    ADD COLUMN IF NOT EXISTS framework_id INT REFERENCES assessments.curriculum_frameworks(id) ON DELETE SET NULL;

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_curriculum_sections_framework
    ON assessments.curriculum_sections(framework_id);
CREATE INDEX IF NOT EXISTS idx_curriculum_positions_section
    ON assessments.curriculum_positions(section_id);
CREATE INDEX IF NOT EXISTS idx_curriculum_objectives_position
    ON assessments.curriculum_objectives(position_id);
CREATE INDEX IF NOT EXISTS idx_curriculum_topic_mapping_objective
    ON assessments.curriculum_topic_mapping(curriculum_objective_id);
CREATE INDEX IF NOT EXISTS idx_curriculum_topic_mapping_topic
    ON assessments.curriculum_topic_mapping(topic_id);
CREATE INDEX IF NOT EXISTS idx_exam_question_curriculum_tags_question
    ON assessments.exam_question_curriculum_tags(question_id);
CREATE INDEX IF NOT EXISTS idx_exam_question_curriculum_tags_objective
    ON assessments.exam_question_curriculum_tags(curriculum_objective_id);
```

**Step 2: Run the migration**

```bash
cd backend && python run_migration.py
```

Expected: Migration runs without errors.

**Step 3: Verify tables exist**

```bash
psql service=devdb -c "\dt assessments.curriculum_*"
psql service=devdb -c "\dt assessments.exam_question_curriculum_tags"
psql service=devdb -c "\d assessments.exam_type_registry" | grep framework_id
```

Expected: All 6 tables listed, `framework_id` column visible.

**Step 4: Commit**

```bash
git add backend/migrations/02_Content/103_curriculum_framework.sql
git commit -m "feat(exams): add curriculum framework tables (migration 103)"
```

---

## Task 2: Domain Models — Curriculum Value Objects

**Files:**
- Create: `backend/app/domain/models/curriculum.py`
- Modify: `backend/app/domain/models/__init__.py` (add export)
- Create: `backend/tests/unit/domain/exam/test_curriculum.py`

**Step 1: Write the domain models**

```python
"""Curriculum Framework value objects.

Represents official training frameworks (IHK Ausbildungsrahmenplan,
university curricula, certification tracks) as immutable domain objects.
"""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass(frozen=True)
class CurriculumObjective:
    """A single learning objective (e.g. 'a) Auftragsunterlagen prüfen')."""

    id: int = 0
    objective_code: str = ''
    description: dict = field(default_factory=dict)
    order_index: int = 0
    competency_level: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'CurriculumObjective':
        level = data.get('competency_level')
        if level and level not in ('kennen', 'anwenden', 'beherrschen'):
            level = None
        return cls(
            id=data.get('id', 0),
            objective_code=data.get('objective_code', ''),
            description=data.get('description', {}),
            order_index=data.get('order_index', 0),
            competency_level=level,
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'objective_code': self.objective_code,
            'description': self.description,
            'order_index': self.order_index,
            'competency_level': self.competency_level,
        }


@dataclass(frozen=True)
class CurriculumPosition:
    """A training position (Berufsbildposition) containing objectives."""

    id: int = 0
    position_number: str = ''
    display_name: dict = field(default_factory=dict)
    description: dict = field(default_factory=dict)
    order_index: int = 0
    training_period: Optional[str] = None
    objectives: tuple = ()

    @classmethod
    def from_dict(cls, data: dict) -> 'CurriculumPosition':
        objectives = tuple(
            CurriculumObjective.from_dict(o)
            for o in data.get('objectives', [])
        )
        return cls(
            id=data.get('id', 0),
            position_number=data.get('position_number', ''),
            display_name=data.get('display_name', {}),
            description=data.get('description', {}),
            order_index=data.get('order_index', 0),
            training_period=data.get('training_period'),
            objectives=objectives,
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'position_number': self.position_number,
            'display_name': self.display_name,
            'description': self.description,
            'order_index': self.order_index,
            'training_period': self.training_period,
            'objectives': [o.to_dict() for o in self.objectives],
        }


@dataclass(frozen=True)
class CurriculumSection:
    """A section (Abschnitt) of the framework."""

    id: int = 0
    section_code: str = ''
    display_name: dict = field(default_factory=dict)
    description: dict = field(default_factory=dict)
    order_index: int = 0
    applies_to: tuple = ()
    positions: tuple = ()

    @classmethod
    def from_dict(cls, data: dict) -> 'CurriculumSection':
        positions = tuple(
            CurriculumPosition.from_dict(p)
            for p in data.get('positions', [])
        )
        applies = data.get('applies_to') or []
        return cls(
            id=data.get('id', 0),
            section_code=data.get('section_code', ''),
            display_name=data.get('display_name', {}),
            description=data.get('description', {}),
            order_index=data.get('order_index', 0),
            applies_to=tuple(applies),
            positions=positions,
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'section_code': self.section_code,
            'display_name': self.display_name,
            'description': self.description,
            'order_index': self.order_index,
            'applies_to': list(self.applies_to),
            'positions': [p.to_dict() for p in self.positions],
        }


@dataclass(frozen=True)
class CurriculumFramework:
    """A complete curriculum framework (e.g. IHK Ausbildungsrahmenplan)."""

    id: int = 0
    name: str = ''
    framework_type: str = 'custom'
    source_document: Optional[str] = None
    version: Optional[str] = None
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    sections: tuple = ()

    VALID_TYPES = frozenset({
        'ihk_ausbildung', 'hochschule', 'zertifizierung', 'custom',
    })

    @classmethod
    def from_dict(cls, data: dict) -> 'CurriculumFramework':
        fw_type = data.get('framework_type', 'custom')
        if fw_type not in cls.VALID_TYPES:
            fw_type = 'custom'
        sections = tuple(
            CurriculumSection.from_dict(s)
            for s in data.get('sections', [])
        )
        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            framework_type=fw_type,
            source_document=data.get('source_document'),
            version=data.get('version'),
            valid_from=str(data['valid_from']) if data.get('valid_from') else None,
            valid_until=str(data['valid_until']) if data.get('valid_until') else None,
            metadata=data.get('metadata') or {},
            sections=sections,
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'framework_type': self.framework_type,
            'source_document': self.source_document,
            'version': self.version,
            'valid_from': self.valid_from,
            'valid_until': self.valid_until,
            'metadata': self.metadata,
            'sections': [s.to_dict() for s in self.sections],
        }

    def to_prompt_context(self, language: str = 'de') -> str:
        """Format framework for AI prompt context."""
        lines = [f'Curriculum: {self.name}']
        for section in self.sections:
            s_name = section.display_name.get(language, section.section_code)
            lines.append(f'\nAbschnitt {section.section_code}: {s_name}')
            for pos in section.positions:
                p_name = pos.display_name.get(language, pos.position_number)
                lines.append(f'  Position {pos.position_number}: {p_name}')
                for obj in pos.objectives:
                    o_desc = obj.description.get(language, obj.objective_code)
                    lines.append(f'    {obj.objective_code}) {o_desc}')
        return '\n'.join(lines)
```

**Step 2: Write tests**

```python
"""Tests for Curriculum Framework domain models."""

import pytest
from app.domain.models.curriculum import (
    CurriculumObjective,
    CurriculumPosition,
    CurriculumSection,
    CurriculumFramework,
)


class TestCurriculumObjective:
    def test_from_dict_valid(self):
        obj = CurriculumObjective.from_dict({
            'id': 1,
            'objective_code': 'a',
            'description': {'de': 'Aufträge prüfen'},
            'competency_level': 'anwenden',
        })
        assert obj.objective_code == 'a'
        assert obj.competency_level == 'anwenden'

    def test_invalid_competency_defaults_to_none(self):
        obj = CurriculumObjective.from_dict({
            'competency_level': 'invalid',
        })
        assert obj.competency_level is None

    def test_immutable(self):
        obj = CurriculumObjective.from_dict({'objective_code': 'a'})
        with pytest.raises(AttributeError):
            obj.objective_code = 'b'

    def test_roundtrip(self):
        data = {
            'id': 5,
            'objective_code': 'c',
            'description': {'de': 'Test', 'en': 'Test'},
            'order_index': 2,
            'competency_level': 'kennen',
        }
        assert CurriculumObjective.from_dict(data).to_dict() == data


class TestCurriculumPosition:
    def test_from_dict_with_objectives(self):
        pos = CurriculumPosition.from_dict({
            'position_number': '1',
            'display_name': {'de': 'Arbeitsaufgaben planen'},
            'training_period': '1-18',
            'objectives': [
                {'objective_code': 'a', 'description': {'de': 'Prüfen'}},
                {'objective_code': 'b', 'description': {'de': 'Durchführen'}},
            ],
        })
        assert len(pos.objectives) == 2
        assert pos.objectives[0].objective_code == 'a'
        assert pos.training_period == '1-18'

    def test_roundtrip(self):
        data = {
            'id': 0,
            'position_number': '2',
            'display_name': {'de': 'Test'},
            'description': {},
            'order_index': 0,
            'training_period': None,
            'objectives': [],
        }
        assert CurriculumPosition.from_dict(data).to_dict() == data


class TestCurriculumSection:
    def test_applies_to(self):
        sec = CurriculumSection.from_dict({
            'section_code': 'B',
            'applies_to': ['FIAE'],
        })
        assert sec.applies_to == ('FIAE',)

    def test_applies_to_none(self):
        sec = CurriculumSection.from_dict({'section_code': 'A'})
        assert sec.applies_to == ()


class TestCurriculumFramework:
    def test_invalid_type_defaults_to_custom(self):
        fw = CurriculumFramework.from_dict({
            'name': 'Test',
            'framework_type': 'invalid',
        })
        assert fw.framework_type == 'custom'

    def test_full_hierarchy(self):
        fw = CurriculumFramework.from_dict({
            'name': 'IHK FI 2020',
            'framework_type': 'ihk_ausbildung',
            'sections': [{
                'section_code': 'A',
                'display_name': {'de': 'Berufsübergreifend'},
                'positions': [{
                    'position_number': '1',
                    'display_name': {'de': 'Planen'},
                    'objectives': [
                        {'objective_code': 'a', 'description': {'de': 'Prüfen'}},
                    ],
                }],
            }],
        })
        assert len(fw.sections) == 1
        assert len(fw.sections[0].positions) == 1
        assert len(fw.sections[0].positions[0].objectives) == 1

    def test_to_prompt_context(self):
        fw = CurriculumFramework.from_dict({
            'name': 'Test Plan',
            'sections': [{
                'section_code': 'A',
                'display_name': {'de': 'Abschnitt A'},
                'positions': [{
                    'position_number': '1',
                    'display_name': {'de': 'Position 1'},
                    'objectives': [
                        {'objective_code': 'a', 'description': {'de': 'Lernziel a'}},
                    ],
                }],
            }],
        })
        ctx = fw.to_prompt_context('de')
        assert 'Abschnitt A' in ctx
        assert 'Position 1' in ctx
        assert 'a) Lernziel a' in ctx
```

**Step 3: Run tests**

```bash
cd backend && python -m pytest tests/unit/domain/exam/test_curriculum.py -v
```

Expected: All tests pass.

**Step 4: Update domain models barrel export**

Add to `backend/app/domain/models/__init__.py`:
```python
from .curriculum import (
    CurriculumObjective,
    CurriculumPosition,
    CurriculumSection,
    CurriculumFramework,
)
```

**Step 5: Commit**

```bash
git add backend/app/domain/models/curriculum.py \
        backend/tests/unit/domain/exam/test_curriculum.py \
        backend/app/domain/models/__init__.py
git commit -m "feat(exams): add curriculum framework domain models with tests"
```

---

## Task 3: Repository — Curriculum CRUD

**Files:**
- Create: `backend/app/infrastructure/persistence/repositories/exams/curriculum.py`
- Modify: `backend/app/infrastructure/persistence/repositories/exams/__init__.py` (add export)

**Step 1: Write the repository**

```python
"""Repository for curriculum framework CRUD operations."""

import json
import logging
from typing import Dict, Any, Optional, List

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query, insert_returning,
)

logger = logging.getLogger(__name__)


class CurriculumFrameworkRepository:
    """CRUD for assessments.curriculum_frameworks and child tables."""

    # ── Framework CRUD ──

    @staticmethod
    def create_framework(data: dict) -> Dict[str, Any]:
        return insert_returning(
            """INSERT INTO assessments.curriculum_frameworks
               (name, framework_type, source_document, version,
                valid_from, valid_until, metadata)
               VALUES (%s, %s, %s, %s, %s, %s, %s)
               RETURNING *""",
            [
                data['name'],
                data.get('framework_type', 'custom'),
                data.get('source_document'),
                data.get('version'),
                data.get('valid_from'),
                data.get('valid_until'),
                json.dumps(data.get('metadata', {})),
            ],
        )

    @staticmethod
    def find_all_frameworks() -> List[Dict[str, Any]]:
        return fetch_all(
            """SELECT f.*,
                      (SELECT COUNT(*) FROM assessments.curriculum_sections
                       WHERE framework_id = f.id) AS section_count
               FROM assessments.curriculum_frameworks f
               ORDER BY f.created_at DESC"""
        )

    @staticmethod
    def find_framework_by_id(framework_id: int) -> Optional[Dict[str, Any]]:
        return fetch_one(
            "SELECT * FROM assessments.curriculum_frameworks WHERE id = %s",
            [framework_id],
        )

    @staticmethod
    def delete_framework(framework_id: int) -> bool:
        result = execute_query(
            "DELETE FROM assessments.curriculum_frameworks WHERE id = %s",
            [framework_id],
        )
        return result is not False

    # ── Section CRUD ──

    @staticmethod
    def create_section(framework_id: int, data: dict) -> Dict[str, Any]:
        return insert_returning(
            """INSERT INTO assessments.curriculum_sections
               (framework_id, section_code, display_name, description,
                order_index, applies_to)
               VALUES (%s, %s, %s, %s, %s, %s)
               RETURNING *""",
            [
                framework_id,
                data['section_code'],
                json.dumps(data.get('display_name', {})),
                json.dumps(data.get('description', {})),
                data.get('order_index', 0),
                data.get('applies_to'),
            ],
        )

    @staticmethod
    def find_sections_by_framework(framework_id: int) -> List[Dict[str, Any]]:
        return fetch_all(
            """SELECT * FROM assessments.curriculum_sections
               WHERE framework_id = %s ORDER BY order_index""",
            [framework_id],
        )

    # ── Position CRUD ──

    @staticmethod
    def create_position(section_id: int, data: dict) -> Dict[str, Any]:
        return insert_returning(
            """INSERT INTO assessments.curriculum_positions
               (section_id, position_number, display_name, description,
                order_index, training_period)
               VALUES (%s, %s, %s, %s, %s, %s)
               RETURNING *""",
            [
                section_id,
                data['position_number'],
                json.dumps(data.get('display_name', {})),
                json.dumps(data.get('description', {})),
                data.get('order_index', 0),
                data.get('training_period'),
            ],
        )

    @staticmethod
    def find_positions_by_section(section_id: int) -> List[Dict[str, Any]]:
        return fetch_all(
            """SELECT * FROM assessments.curriculum_positions
               WHERE section_id = %s ORDER BY order_index""",
            [section_id],
        )

    # ── Objective CRUD ──

    @staticmethod
    def create_objective(position_id: int, data: dict) -> Dict[str, Any]:
        return insert_returning(
            """INSERT INTO assessments.curriculum_objectives
               (position_id, objective_code, description,
                order_index, competency_level)
               VALUES (%s, %s, %s, %s, %s)
               RETURNING *""",
            [
                position_id,
                data['objective_code'],
                json.dumps(data.get('description', {})),
                data.get('order_index', 0),
                data.get('competency_level'),
            ],
        )

    @staticmethod
    def find_objectives_by_position(position_id: int) -> List[Dict[str, Any]]:
        return fetch_all(
            """SELECT * FROM assessments.curriculum_objectives
               WHERE position_id = %s ORDER BY order_index""",
            [position_id],
        )

    @staticmethod
    def find_all_objectives_by_framework(
        framework_id: int,
    ) -> List[Dict[str, Any]]:
        """Flat list of all objectives with section/position context."""
        return fetch_all(
            """SELECT o.*, p.position_number, p.display_name AS position_name,
                      s.section_code, s.display_name AS section_name
               FROM assessments.curriculum_objectives o
               JOIN assessments.curriculum_positions p ON p.id = o.position_id
               JOIN assessments.curriculum_sections s ON s.id = p.section_id
               WHERE s.framework_id = %s
               ORDER BY s.order_index, p.order_index, o.order_index""",
            [framework_id],
        )

    # ── Bulk Import (for AI PDF import) ──

    @staticmethod
    def bulk_import_framework(data: dict) -> Dict[str, Any]:
        """Import a complete framework hierarchy in one call.

        Args:
            data: Full framework dict with nested sections/positions/objectives.

        Returns:
            Created framework row with id.
        """
        framework = CurriculumFrameworkRepository.create_framework(data)
        fw_id = framework['id']

        for s_idx, section_data in enumerate(data.get('sections', [])):
            section_data['order_index'] = s_idx
            section = CurriculumFrameworkRepository.create_section(
                fw_id, section_data,
            )

            for p_idx, pos_data in enumerate(
                section_data.get('positions', []),
            ):
                pos_data['order_index'] = p_idx
                position = CurriculumFrameworkRepository.create_position(
                    section['id'], pos_data,
                )

                for o_idx, obj_data in enumerate(
                    pos_data.get('objectives', []),
                ):
                    obj_data['order_index'] = o_idx
                    CurriculumFrameworkRepository.create_objective(
                        position['id'], obj_data,
                    )

        return framework

    # ── Full Tree Load ──

    @staticmethod
    def load_framework_tree(framework_id: int) -> Optional[Dict[str, Any]]:
        """Load complete framework with all nested children."""
        framework = CurriculumFrameworkRepository.find_framework_by_id(
            framework_id,
        )
        if not framework:
            return None

        sections = CurriculumFrameworkRepository.find_sections_by_framework(
            framework_id,
        )
        for section in sections:
            positions = CurriculumFrameworkRepository.find_positions_by_section(
                section['id'],
            )
            for position in positions:
                position['objectives'] = (
                    CurriculumFrameworkRepository.find_objectives_by_position(
                        position['id'],
                    )
                )
            section['positions'] = positions
        framework['sections'] = sections
        return framework

    # ── Curriculum ↔ Topic Mapping ──

    @staticmethod
    def create_topic_mapping(
        objective_id: int, topic_id: int,
        confidence: float = 0.0, mapped_by: str = 'ai',
    ) -> Dict[str, Any]:
        return insert_returning(
            """INSERT INTO assessments.curriculum_topic_mapping
               (curriculum_objective_id, topic_id, confidence, mapped_by)
               VALUES (%s, %s, %s, %s)
               ON CONFLICT (curriculum_objective_id, topic_id) DO UPDATE
               SET confidence = EXCLUDED.confidence, mapped_by = EXCLUDED.mapped_by
               RETURNING *""",
            [objective_id, topic_id, confidence, mapped_by],
        )

    @staticmethod
    def find_topics_by_objective(objective_id: int) -> List[Dict[str, Any]]:
        return fetch_all(
            """SELECT m.*, t.topic_key, t.topic_label
               FROM assessments.curriculum_topic_mapping m
               JOIN assessments.exam_topic_taxonomy t ON t.id = m.topic_id
               WHERE m.curriculum_objective_id = %s
               ORDER BY m.confidence DESC""",
            [objective_id],
        )

    # ── Question ↔ Curriculum Mapping ──

    @staticmethod
    def tag_question(
        question_id: int, objective_id: int,
        confidence: float = 0.0, tagged_by: str = 'ai',
    ) -> Dict[str, Any]:
        return insert_returning(
            """INSERT INTO assessments.exam_question_curriculum_tags
               (question_id, curriculum_objective_id, confidence, tagged_by)
               VALUES (%s, %s, %s, %s)
               ON CONFLICT (question_id, curriculum_objective_id) DO UPDATE
               SET confidence = EXCLUDED.confidence, tagged_by = EXCLUDED.tagged_by
               RETURNING *""",
            [question_id, objective_id, confidence, tagged_by],
        )

    @staticmethod
    def find_tags_by_question(question_id: int) -> List[Dict[str, Any]]:
        return fetch_all(
            """SELECT t.*, o.objective_code, o.description AS objective_desc,
                      p.position_number, p.display_name AS position_name,
                      s.section_code, s.display_name AS section_name
               FROM assessments.exam_question_curriculum_tags t
               JOIN assessments.curriculum_objectives o
                    ON o.id = t.curriculum_objective_id
               JOIN assessments.curriculum_positions p ON p.id = o.position_id
               JOIN assessments.curriculum_sections s ON s.id = p.section_id
               WHERE t.question_id = %s
               ORDER BY s.order_index, p.order_index, o.order_index""",
            [question_id],
        )

    @staticmethod
    def find_questions_by_objective(
        objective_id: int,
    ) -> List[Dict[str, Any]]:
        return fetch_all(
            """SELECT q.id, q.question_text, q.question_type,
                      q.topics, t.confidence, t.tagged_by
               FROM assessments.exam_question_curriculum_tags t
               JOIN assessments.exam_questions q ON q.id = t.question_id
               WHERE t.curriculum_objective_id = %s
               ORDER BY t.confidence DESC""",
            [objective_id],
        )

    @staticmethod
    def remove_question_tag(
        question_id: int, objective_id: int,
    ) -> bool:
        result = execute_query(
            """DELETE FROM assessments.exam_question_curriculum_tags
               WHERE question_id = %s AND curriculum_objective_id = %s""",
            [question_id, objective_id],
        )
        return result is not False

    # ── Stats ──

    @staticmethod
    def get_curriculum_coverage_stats(
        framework_id: int,
    ) -> List[Dict[str, Any]]:
        """How many questions are mapped per curriculum position."""
        return fetch_all(
            """SELECT s.section_code, s.display_name AS section_name,
                      p.position_number, p.display_name AS position_name,
                      COUNT(DISTINCT t.question_id) AS question_count,
                      COUNT(DISTINCT o.id) AS objective_count
               FROM assessments.curriculum_sections s
               JOIN assessments.curriculum_positions p ON p.section_id = s.id
               JOIN assessments.curriculum_objectives o ON o.position_id = p.id
               LEFT JOIN assessments.exam_question_curriculum_tags t
                    ON t.curriculum_objective_id = o.id
               WHERE s.framework_id = %s
               GROUP BY s.section_code, s.display_name, s.order_index,
                        p.position_number, p.display_name, p.order_index
               ORDER BY s.order_index, p.order_index""",
            [framework_id],
        )

    # ── Link to Exam Type ──

    @staticmethod
    def link_framework_to_exam_type(
        framework_id: int, exam_type_key: str,
    ) -> bool:
        result = execute_query(
            """UPDATE assessments.exam_type_registry
               SET framework_id = %s WHERE exam_type = %s""",
            [framework_id, exam_type_key],
        )
        return result is not False

    @staticmethod
    def find_framework_for_exam_type(
        exam_type_key: str,
    ) -> Optional[Dict[str, Any]]:
        return fetch_one(
            """SELECT f.* FROM assessments.curriculum_frameworks f
               JOIN assessments.exam_type_registry r ON r.framework_id = f.id
               WHERE r.exam_type = %s""",
            [exam_type_key],
        )
```

**Step 2: Update barrel export**

Add to `backend/app/infrastructure/persistence/repositories/exams/__init__.py`:
```python
from .curriculum import CurriculumFrameworkRepository
```

And add `'CurriculumFrameworkRepository'` to `__all__`.

**Step 3: Verify import works**

```bash
cd backend && python -c "from app.infrastructure.persistence.repositories.exams.curriculum import CurriculumFrameworkRepository; print('OK')"
```

**Step 4: Commit**

```bash
git add backend/app/infrastructure/persistence/repositories/exams/curriculum.py \
        backend/app/infrastructure/persistence/repositories/exams/__init__.py
git commit -m "feat(exams): add curriculum framework repository with CRUD and mappings"
```

---

## Task 4: Application Service — Curriculum Import & Mapping

**Files:**
- Create: `backend/app/application/services/exams/curriculum_service.py`
- Modify: `backend/app/application/services/exams/__init__.py` (add export)

**Step 1: Write the service**

```python
"""Curriculum Framework service — PDF import and question mapping."""

import json
import logging
from typing import Optional, Dict, Any, List

from app.infrastructure.persistence.repositories.exams.curriculum import (
    CurriculumFrameworkRepository,
)

logger = logging.getLogger(__name__)


class CurriculumService:
    """Orchestrates curriculum framework operations."""

    # ── AI PDF Import ──

    @staticmethod
    def import_from_ai_result(
        ai_result: dict,
        source_document: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Import a framework from AI-parsed PDF structure.

        Args:
            ai_result: Structured dict from AI analysis with
                       name, framework_type, sections[].positions[].objectives[].
            source_document: Optional PDF file path.

        Returns:
            Created framework dict with id.
        """
        if source_document:
            ai_result['source_document'] = source_document

        framework = CurriculumFrameworkRepository.bulk_import_framework(
            ai_result,
        )
        logger.info(
            'Imported curriculum framework "%s" (id=%s)',
            framework.get('name'), framework.get('id'),
        )
        return framework

    @staticmethod
    def parse_pdf_with_ai(pdf_text: str) -> Dict[str, Any]:
        """Use AI to parse extracted PDF text into framework structure.

        Returns:
            Structured dict ready for import_from_ai_result().
        """
        from app.infrastructure.ai.adapter import AIAdapter

        prompt = (
            'Du bist ein Experte für Ausbildungsrahmenpläne und Curricula. '
            'Analysiere den folgenden Text und extrahiere die Struktur als JSON.\n\n'
            'Das JSON muss dieses Format haben:\n'
            '{\n'
            '  "name": "Name des Rahmenplans",\n'
            '  "framework_type": "ihk_ausbildung|hochschule|zertifizierung|custom",\n'
            '  "version": "2020",\n'
            '  "sections": [\n'
            '    {\n'
            '      "section_code": "A",\n'
            '      "display_name": {"de": "Abschnittname"},\n'
            '      "description": {"de": "Beschreibung"},\n'
            '      "applies_to": ["FIAE", "FISI"],\n'
            '      "positions": [\n'
            '        {\n'
            '          "position_number": "1",\n'
            '          "display_name": {"de": "Positionsname"},\n'
            '          "training_period": "1-18",\n'
            '          "objectives": [\n'
            '            {"objective_code": "a", "description": {"de": "Lernziel"}}\n'
            '          ]\n'
            '        }\n'
            '      ]\n'
            '    }\n'
            '  ]\n'
            '}\n\n'
            'Regeln:\n'
            '- Extrahiere ALLE Abschnitte, Positionen und Lernziele vollständig\n'
            '- applies_to: Fachrichtungskürzel oder null wenn für alle\n'
            '- training_period: Ausbildungsmonat-Bereich (z.B. "1-18", "19-36")\n'
            '- Antworte NUR mit dem JSON, kein weiterer Text\n\n'
            f'Text:\n{pdf_text}'
        )

        adapter = AIAdapter()
        response = adapter.send_request(
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=8000,
            temperature=0.1,
        )

        content = response.get('content', '')
        # Strip markdown code fences if present
        if content.startswith('```'):
            content = content.split('\n', 1)[1]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()

        return json.loads(content)

    # ── AI Question Mapping ──

    @staticmethod
    def auto_map_questions(
        exam_type_key: str,
        batch_size: int = 10,
    ) -> Dict[str, Any]:
        """AI-map unmapped questions to curriculum objectives.

        Returns:
            Stats dict with mapped_count, skipped_count, error_count.
        """
        from app.infrastructure.ai.adapter import AIAdapter
        from app.infrastructure.persistence.repositories.exams.questions import (
            ExamQuestionRepository,
        )

        # Find framework for this exam type
        framework = CurriculumFrameworkRepository.find_framework_for_exam_type(
            exam_type_key,
        )
        if not framework:
            raise ValueError(
                f'No curriculum framework linked to exam type "{exam_type_key}"',
            )

        # Load all objectives for context
        objectives = CurriculumFrameworkRepository.find_all_objectives_by_framework(
            framework['id'],
        )
        if not objectives:
            raise ValueError('Framework has no objectives')

        # Build objectives reference for AI
        obj_ref_lines = []
        for obj in objectives:
            section_name = (obj.get('section_name') or {}).get('de', obj['section_code'])
            pos_name = (obj.get('position_name') or {}).get('de', obj['position_number'])
            obj_desc = (obj.get('description') or {}).get('de', obj['objective_code'])
            obj_ref_lines.append(
                f'ID={obj["id"]} | {obj["section_code"]}.{obj["position_number"]}.{obj["objective_code"]} | '
                f'{section_name} > {pos_name} > {obj_desc}'
            )
        obj_reference = '\n'.join(obj_ref_lines)

        # Find unmapped questions for this exam type
        from app.infrastructure.persistence.database.connection import fetch_all
        unmapped = fetch_all(
            """SELECT q.id, q.question_text, q.scenario_text, q.topics
               FROM assessments.exam_questions q
               JOIN assessments.exams e ON e.id = q.exam_id
               JOIN assessments.exam_sessions es ON es.id = e.session_id
               WHERE es.exam_type_key = %s
                 AND q.id NOT IN (
                     SELECT question_id FROM assessments.exam_question_curriculum_tags
                 )
               ORDER BY q.id""",
            [exam_type_key],
        )

        stats = {'mapped_count': 0, 'skipped_count': 0, 'error_count': 0}

        # Process in batches
        for i in range(0, len(unmapped), batch_size):
            batch = unmapped[i:i + batch_size]
            CurriculumService._map_question_batch(
                batch, obj_reference, objectives, stats,
            )

        logger.info(
            'Auto-mapped questions for %s: %s', exam_type_key, stats,
        )
        return stats

    @staticmethod
    def _map_question_batch(
        questions: list,
        obj_reference: str,
        objectives: list,
        stats: dict,
    ) -> None:
        """Map a batch of questions using AI."""
        from app.infrastructure.ai.adapter import AIAdapter

        # Build batch prompt
        q_texts = []
        for q in questions:
            text = q.get('question_text', '') or ''
            scenario = q.get('scenario_text', '') or ''
            combined = f'{scenario}\n{text}'.strip() if scenario else text
            q_texts.append(f'FRAGE_ID={q["id"]}:\n{combined[:500]}')

        prompt = (
            'Ordne jede Prüfungsfrage den passenden Curriculum-Lernzielen zu.\n\n'
            'LERNZIELE:\n'
            f'{obj_reference}\n\n'
            'FRAGEN:\n'
            + '\n---\n'.join(q_texts)
            + '\n\n'
            'Antworte als JSON-Array:\n'
            '[{"question_id": 123, "objective_ids": [1, 5], "confidence": 0.85}]\n'
            '- objective_ids: 1-3 passende Lernziel-IDs\n'
            '- confidence: 0.0-1.0 wie sicher die Zuordnung ist\n'
            '- Antworte NUR mit dem JSON-Array'
        )

        try:
            adapter = AIAdapter()
            response = adapter.send_request(
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=4000,
                temperature=0.1,
            )

            content = response.get('content', '')
            if content.startswith('```'):
                content = content.split('\n', 1)[1]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()

            mappings = json.loads(content)
            valid_obj_ids = {o['id'] for o in objectives}

            for mapping in mappings:
                q_id = mapping.get('question_id')
                confidence = mapping.get('confidence', 0.5)
                for obj_id in mapping.get('objective_ids', []):
                    if obj_id in valid_obj_ids:
                        CurriculumFrameworkRepository.tag_question(
                            q_id, obj_id, confidence, 'ai',
                        )
                        stats['mapped_count'] += 1
                    else:
                        stats['skipped_count'] += 1

        except Exception:
            logger.exception('Error mapping question batch')
            stats['error_count'] += len(questions)

    # ── Stats & Coverage ──

    @staticmethod
    def get_user_curriculum_profile(
        user_id: str,
        exam_type_key: str,
    ) -> List[Dict[str, Any]]:
        """Get user performance aggregated by curriculum position.

        Extends the existing WeaknessProfile with curriculum dimension.
        """
        from app.infrastructure.persistence.database.connection import fetch_all

        framework = CurriculumFrameworkRepository.find_framework_for_exam_type(
            exam_type_key,
        )
        if not framework:
            return []

        return fetch_all(
            """SELECT s.section_code, s.display_name AS section_name,
                      p.position_number, p.display_name AS position_name,
                      COUNT(DISTINCT t.question_id) AS total_questions,
                      COALESCE(AVG(
                          CASE WHEN ea.is_correct THEN 100.0 ELSE 0.0 END
                      ), 0) AS avg_score,
                      COUNT(DISTINCT ea.id) AS attempts
               FROM assessments.curriculum_sections s
               JOIN assessments.curriculum_positions p ON p.section_id = s.id
               JOIN assessments.curriculum_objectives o ON o.position_id = p.id
               LEFT JOIN assessments.exam_question_curriculum_tags ct
                    ON ct.curriculum_objective_id = o.id
               LEFT JOIN assessments.exam_answers ea
                    ON ea.question_id = ct.question_id
                    AND ea.attempt_id IN (
                        SELECT id FROM assessments.exam_attempts
                        WHERE user_id = %s
                    )
               WHERE s.framework_id = %s
               GROUP BY s.section_code, s.display_name, s.order_index,
                        p.position_number, p.display_name, p.order_index
               ORDER BY s.order_index, p.order_index""",
            [user_id, framework['id']],
        )

    @staticmethod
    def get_exam_relevance_weights(
        framework_id: int,
    ) -> List[Dict[str, Any]]:
        """How often each curriculum position appears in exam questions."""
        return CurriculumFrameworkRepository.get_curriculum_coverage_stats(
            framework_id,
        )
```

**Step 2: Update service barrel export**

Add to `backend/app/application/services/exams/__init__.py`:
```python
from .curriculum_service import CurriculumService
```

**Step 3: Verify import**

```bash
cd backend && python -c "from app.application.services.exams.curriculum_service import CurriculumService; print('OK')"
```

**Step 4: Commit**

```bash
git add backend/app/application/services/exams/curriculum_service.py \
        backend/app/application/services/exams/__init__.py
git commit -m "feat(exams): add curriculum service with AI PDF import and question mapping"
```

---

## Task 5: API Endpoints — Admin Curriculum Management

**Files:**
- Create: `backend/app/api/v1/panel/admin/exams/curriculum.py`
- Modify: `backend/app/api/v1/panel/admin/exams/__init__.py` (register blueprint)

**Step 1: Write the API blueprint**

```python
"""Admin API for curriculum framework management."""

import logging
from flask import Blueprint, jsonify, request

from app.api.middleware.auth import admin_required
from app.infrastructure.persistence.repositories.exams.curriculum import (
    CurriculumFrameworkRepository,
)
from app.application.services.exams.curriculum_service import (
    CurriculumService,
)

logger = logging.getLogger(__name__)

curriculum_bp = Blueprint(
    'curriculum_admin',
    __name__,
    url_prefix='/admin/curriculum',
)


# ── Framework CRUD ──

@curriculum_bp.route('/frameworks', methods=['GET'])
@admin_required
def list_frameworks():
    frameworks = CurriculumFrameworkRepository.find_all_frameworks()
    return jsonify({'success': True, 'frameworks': frameworks})


@curriculum_bp.route('/frameworks/<int:framework_id>', methods=['GET'])
@admin_required
def get_framework(framework_id):
    tree = CurriculumFrameworkRepository.load_framework_tree(framework_id)
    if not tree:
        return jsonify({'success': False, 'message': 'Framework not found'}), 404
    return jsonify({'success': True, 'framework': tree})


@curriculum_bp.route('/frameworks', methods=['POST'])
@admin_required
def create_framework():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'success': False, 'message': 'Name is required'}), 400
    framework = CurriculumFrameworkRepository.create_framework(data)
    return jsonify({'success': True, 'framework': framework}), 201


@curriculum_bp.route('/frameworks/<int:framework_id>', methods=['DELETE'])
@admin_required
def delete_framework(framework_id):
    CurriculumFrameworkRepository.delete_framework(framework_id)
    return jsonify({'success': True})


# ── AI PDF Import ──

@curriculum_bp.route('/frameworks/import-pdf', methods=['POST'])
@admin_required
def import_pdf():
    """Extract curriculum structure from PDF text using AI."""
    data = request.get_json()
    pdf_text = data.get('pdf_text', '')
    if not pdf_text or len(pdf_text) < 100:
        return jsonify({
            'success': False,
            'message': 'pdf_text is required (min 100 chars)',
        }), 400

    try:
        ai_result = CurriculumService.parse_pdf_with_ai(pdf_text)
        return jsonify({'success': True, 'preview': ai_result})
    except Exception:
        logger.exception('PDF import AI parsing failed')
        return jsonify({
            'success': False,
            'message': 'AI parsing failed. Check PDF text quality.',
        }), 500


@curriculum_bp.route('/frameworks/import-confirm', methods=['POST'])
@admin_required
def import_confirm():
    """Persist a previewed AI-parsed framework structure."""
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'success': False, 'message': 'Invalid data'}), 400

    try:
        framework = CurriculumService.import_from_ai_result(data)
        return jsonify({'success': True, 'framework': framework}), 201
    except Exception:
        logger.exception('Framework import failed')
        return jsonify({
            'success': False,
            'message': 'Import failed',
        }), 500


# ── Link to Exam Type ──

@curriculum_bp.route(
    '/frameworks/<int:framework_id>/link/<exam_type_key>',
    methods=['POST'],
)
@admin_required
def link_to_exam_type(framework_id, exam_type_key):
    CurriculumFrameworkRepository.link_framework_to_exam_type(
        framework_id, exam_type_key,
    )
    return jsonify({'success': True})


# ── Question Mapping ──

@curriculum_bp.route('/auto-map/<exam_type_key>', methods=['POST'])
@admin_required
def auto_map_questions(exam_type_key):
    """AI-map unmapped questions to curriculum objectives."""
    try:
        stats = CurriculumService.auto_map_questions(exam_type_key)
        return jsonify({'success': True, 'stats': stats})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception:
        logger.exception('Auto-map failed for %s', exam_type_key)
        return jsonify({'success': False, 'message': 'Mapping failed'}), 500


@curriculum_bp.route('/questions/<int:question_id>/tags', methods=['GET'])
@admin_required
def get_question_tags(question_id):
    tags = CurriculumFrameworkRepository.find_tags_by_question(question_id)
    return jsonify({'success': True, 'tags': tags})


@curriculum_bp.route('/questions/<int:question_id>/tags', methods=['POST'])
@admin_required
def add_question_tag(question_id):
    data = request.get_json()
    objective_id = data.get('objective_id')
    if not objective_id:
        return jsonify({'success': False, 'message': 'objective_id required'}), 400
    tag = CurriculumFrameworkRepository.tag_question(
        question_id, objective_id,
        confidence=1.0, tagged_by='admin',
    )
    return jsonify({'success': True, 'tag': tag}), 201


@curriculum_bp.route(
    '/questions/<int:question_id>/tags/<int:objective_id>',
    methods=['DELETE'],
)
@admin_required
def remove_question_tag(question_id, objective_id):
    CurriculumFrameworkRepository.remove_question_tag(
        question_id, objective_id,
    )
    return jsonify({'success': True})


# ── Coverage Stats ──

@curriculum_bp.route(
    '/frameworks/<int:framework_id>/coverage',
    methods=['GET'],
)
@admin_required
def get_coverage(framework_id):
    stats = CurriculumFrameworkRepository.get_curriculum_coverage_stats(
        framework_id,
    )
    return jsonify({'success': True, 'coverage': stats})


@curriculum_bp.route(
    '/frameworks/<int:framework_id>/relevance',
    methods=['GET'],
)
@admin_required
def get_relevance(framework_id):
    weights = CurriculumService.get_exam_relevance_weights(framework_id)
    return jsonify({'success': True, 'relevance': weights})
```

**Step 2: Register blueprint**

Add to `backend/app/api/v1/panel/admin/exams/__init__.py`:
```python
from .curriculum import curriculum_bp
api_v1.register_blueprint(curriculum_bp)
```

**Step 3: Verify backend starts**

```bash
cd backend && python -c "from app import create_app; create_app()"
```

Expected: Exit 0, no import errors.

**Step 4: Commit**

```bash
git add backend/app/api/v1/panel/admin/exams/curriculum.py \
        backend/app/api/v1/panel/admin/exams/__init__.py
git commit -m "feat(exams): add admin API for curriculum framework management"
```

---

## Task 6: API Endpoints — User Curriculum Profile

**Files:**
- Modify: `backend/app/api/v1/panel/user/exam_goals.py` (add curriculum profile endpoint)

**Step 1: Add endpoint to existing exam_goals blueprint**

Add to the existing file after the weakness profile endpoint:

```python
@exam_goals_bp.route('/curriculum-profile/<exam_type_key>', methods=['GET'])
@login_required
def get_curriculum_profile(exam_type_key):
    """Get user performance aggregated by curriculum positions."""
    from app.application.services.exams.curriculum_service import CurriculumService
    user_id = get_jwt_identity()
    profile = CurriculumService.get_user_curriculum_profile(
        user_id, exam_type_key,
    )
    return jsonify({'success': True, 'profile': profile})
```

**Step 2: Verify backend starts**

```bash
cd backend && python -c "from app import create_app; create_app()"
```

**Step 3: Commit**

```bash
git add backend/app/api/v1/panel/user/exam_goals.py
git commit -m "feat(exams): add user curriculum profile endpoint"
```

---

## Task 7: Frontend — API Client & Composable

**Files:**
- Create: `frontend/src/infrastructure/api/clients/panel/admin/exams/curriculum.api.ts`
- Create: `frontend/src/presentation/components/panel/admin/assessment/composables/useCurriculum.ts`
- Modify: `frontend/src/presentation/components/panel/admin/assessment/composables/index.ts` (add export)

**Step 1: Write the API client**

```typescript
import { apiClient } from '@/infrastructure/api/apiClient'

// ── Types ──

export interface CurriculumObjective {
  id: number
  objective_code: string
  description: Record<string, string>
  order_index: number
  competency_level: string | null
}

export interface CurriculumPosition {
  id: number
  position_number: string
  display_name: Record<string, string>
  description: Record<string, string>
  order_index: number
  training_period: string | null
  objectives: CurriculumObjective[]
}

export interface CurriculumSection {
  id: number
  section_code: string
  display_name: Record<string, string>
  description: Record<string, string>
  order_index: number
  applies_to: string[] | null
  positions: CurriculumPosition[]
}

export interface CurriculumFramework {
  id: number
  name: string
  framework_type: string
  source_document: string | null
  version: string | null
  valid_from: string | null
  valid_until: string | null
  metadata: Record<string, unknown>
  sections?: CurriculumSection[]
  section_count?: number
}

export interface CoverageStats {
  section_code: string
  section_name: Record<string, string>
  position_number: string
  position_name: Record<string, string>
  question_count: number
  objective_count: number
}

export interface QuestionTag {
  id: number
  question_id: number
  curriculum_objective_id: number
  confidence: number
  tagged_by: string
  objective_code: string
  objective_desc: Record<string, string>
  position_number: string
  position_name: Record<string, string>
  section_code: string
  section_name: Record<string, string>
}

export interface AutoMapStats {
  mapped_count: number
  skipped_count: number
  error_count: number
}

// ── API Functions ──

const BASE = '/admin/curriculum'

export async function fetchFrameworks(): Promise<CurriculumFramework[]> {
  const { data } = await apiClient.get(`${BASE}/frameworks`)
  return data.frameworks
}

export async function fetchFramework(id: number): Promise<CurriculumFramework> {
  const { data } = await apiClient.get(`${BASE}/frameworks/${id}`)
  return data.framework
}

export async function createFramework(
  payload: Partial<CurriculumFramework>,
): Promise<CurriculumFramework> {
  const { data } = await apiClient.post(`${BASE}/frameworks`, payload)
  return data.framework
}

export async function deleteFramework(id: number): Promise<void> {
  await apiClient.delete(`${BASE}/frameworks/${id}`)
}

export async function importPdfPreview(
  pdfText: string,
): Promise<Record<string, unknown>> {
  const { data } = await apiClient.post(`${BASE}/frameworks/import-pdf`, {
    pdf_text: pdfText,
  })
  return data.preview
}

export async function importConfirm(
  framework: Record<string, unknown>,
): Promise<CurriculumFramework> {
  const { data } = await apiClient.post(
    `${BASE}/frameworks/import-confirm`,
    framework,
  )
  return data.framework
}

export async function linkFrameworkToExamType(
  frameworkId: number,
  examTypeKey: string,
): Promise<void> {
  await apiClient.post(
    `${BASE}/frameworks/${frameworkId}/link/${examTypeKey}`,
  )
}

export async function autoMapQuestions(
  examTypeKey: string,
): Promise<AutoMapStats> {
  const { data } = await apiClient.post(`${BASE}/auto-map/${examTypeKey}`)
  return data.stats
}

export async function fetchQuestionTags(
  questionId: number,
): Promise<QuestionTag[]> {
  const { data } = await apiClient.get(
    `${BASE}/questions/${questionId}/tags`,
  )
  return data.tags
}

export async function addQuestionTag(
  questionId: number,
  objectiveId: number,
): Promise<QuestionTag> {
  const { data } = await apiClient.post(
    `${BASE}/questions/${questionId}/tags`,
    { objective_id: objectiveId },
  )
  return data.tag
}

export async function removeQuestionTag(
  questionId: number,
  objectiveId: number,
): Promise<void> {
  await apiClient.delete(
    `${BASE}/questions/${questionId}/tags/${objectiveId}`,
  )
}

export async function fetchCoverage(
  frameworkId: number,
): Promise<CoverageStats[]> {
  const { data } = await apiClient.get(
    `${BASE}/frameworks/${frameworkId}/coverage`,
  )
  return data.coverage
}
```

**Step 2: Write the composable**

```typescript
import { ref, computed } from 'vue'
import {
  fetchFrameworks,
  fetchFramework,
  createFramework,
  deleteFramework,
  importPdfPreview,
  importConfirm,
  linkFrameworkToExamType,
  autoMapQuestions,
  fetchCoverage,
  type CurriculumFramework,
  type CoverageStats,
  type AutoMapStats,
} from '@/infrastructure/api/clients/panel/admin/exams/curriculum.api'

export function useCurriculum() {
  const frameworks = ref<CurriculumFramework[]>([])
  const selectedFramework = ref<CurriculumFramework | null>(null)
  const coverage = ref<CoverageStats[]>([])
  const loading = ref(false)
  const importing = ref(false)
  const mapping = ref(false)
  const error = ref<string | null>(null)
  const importPreview = ref<Record<string, unknown> | null>(null)
  const mapStats = ref<AutoMapStats | null>(null)

  async function loadFrameworks(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      frameworks.value = await fetchFrameworks()
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to load frameworks'
    } finally {
      loading.value = false
    }
  }

  async function loadFramework(id: number): Promise<void> {
    loading.value = true
    error.value = null
    try {
      selectedFramework.value = await fetchFramework(id)
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to load framework'
    } finally {
      loading.value = false
    }
  }

  async function handleCreate(
    data: Partial<CurriculumFramework>,
  ): Promise<CurriculumFramework | null> {
    error.value = null
    try {
      const created = await createFramework(data)
      frameworks.value.unshift(created)
      return created
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to create framework'
      return null
    }
  }

  async function handleDelete(id: number): Promise<void> {
    error.value = null
    try {
      await deleteFramework(id)
      frameworks.value = frameworks.value.filter((f) => f.id !== id)
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to delete framework'
    }
  }

  async function handleImportPreview(pdfText: string): Promise<void> {
    importing.value = true
    error.value = null
    importPreview.value = null
    try {
      importPreview.value = await importPdfPreview(pdfText)
    } catch (err: any) {
      error.value = err.response?.data?.message || 'PDF parsing failed'
    } finally {
      importing.value = false
    }
  }

  async function handleImportConfirm(): Promise<CurriculumFramework | null> {
    if (!importPreview.value) return null
    importing.value = true
    error.value = null
    try {
      const created = await importConfirm(importPreview.value)
      frameworks.value.unshift(created)
      importPreview.value = null
      return created
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Import failed'
      return null
    } finally {
      importing.value = false
    }
  }

  async function handleLinkExamType(
    frameworkId: number,
    examTypeKey: string,
  ): Promise<void> {
    error.value = null
    try {
      await linkFrameworkToExamType(frameworkId, examTypeKey)
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Linking failed'
    }
  }

  async function handleAutoMap(examTypeKey: string): Promise<void> {
    mapping.value = true
    error.value = null
    mapStats.value = null
    try {
      mapStats.value = await autoMapQuestions(examTypeKey)
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Auto-mapping failed'
    } finally {
      mapping.value = false
    }
  }

  async function loadCoverage(frameworkId: number): Promise<void> {
    error.value = null
    try {
      coverage.value = await fetchCoverage(frameworkId)
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to load coverage'
    }
  }

  return {
    frameworks,
    selectedFramework,
    coverage,
    loading,
    importing,
    mapping,
    error,
    importPreview,
    mapStats,
    loadFrameworks,
    loadFramework,
    handleCreate,
    handleDelete,
    handleImportPreview,
    handleImportConfirm,
    handleLinkExamType,
    handleAutoMap,
    loadCoverage,
  }
}
```

**Step 3: Update composables barrel export**

Add to `frontend/src/presentation/components/panel/admin/assessment/composables/index.ts`:
```typescript
export { useCurriculum } from './useCurriculum'
```

**Step 4: Verify frontend builds**

```bash
cd frontend && npm run build
```

**Step 5: Commit**

```bash
git add frontend/src/infrastructure/api/clients/panel/admin/exams/curriculum.api.ts \
        frontend/src/presentation/components/panel/admin/assessment/composables/useCurriculum.ts \
        frontend/src/presentation/components/panel/admin/assessment/composables/index.ts
git commit -m "feat(exams): add curriculum API client and composable"
```

---

## Task 8: Frontend — Admin Curriculum Manager Component

**Files:**
- Create: `frontend/src/presentation/components/panel/admin/assessment/curriculum/CurriculumManager.vue`
- Create: `frontend/src/presentation/components/panel/admin/assessment/curriculum/CurriculumTreeView.vue`
- Create: `frontend/src/presentation/components/panel/admin/assessment/curriculum/CurriculumImportDialog.vue`

**Step 1: Write CurriculumTreeView**

A reusable tree component that displays the framework hierarchy (sections → positions → objectives). Used in both the manager view and the import preview.

Props: `framework: CurriculumFramework`, `readonly: boolean`.
Emits: `select-objective(objective)` for tagging.

Render pattern: Nested `v-for` with collapsible sections. Use existing TailwindCSS classes from the codebase. Display names resolved via current locale (`$i18n.locale`).

**Step 2: Write CurriculumImportDialog**

A dialog component for the AI PDF import flow:
1. Textarea for pasting PDF text (or file upload that extracts text)
2. "Analyze" button → calls `handleImportPreview()`
3. Shows `CurriculumTreeView` with the preview (readonly)
4. "Confirm Import" button → calls `handleImportConfirm()`
5. "Link to Exam Type" dropdown after import

**Step 3: Write CurriculumManager**

Main admin view that shows:
1. List of all frameworks (cards, similar to ExamArchiveManager pattern)
2. "Import Framework" button → opens CurriculumImportDialog
3. Click framework → loads tree view with coverage stats
4. "Auto-Map Questions" button per linked exam type
5. Coverage heatmap (which positions have questions mapped)

**Step 4: Add i18n keys**

Add to all 3 locale files (`de.json`, `en.json`, `pl.json`):
```json
"curriculum": {
  "title": "Rahmenpläne",
  "frameworks": "Rahmenpläne",
  "import": "Rahmenplan importieren",
  "importPdf": "PDF-Text einfügen",
  "analyze": "Analysieren",
  "confirmImport": "Import bestätigen",
  "autoMap": "Fragen automatisch zuordnen",
  "coverage": "Abdeckung",
  "sections": "Abschnitte",
  "positions": "Positionen",
  "objectives": "Lernziele",
  "noFrameworks": "Noch keine Rahmenpläne importiert",
  "linkExamType": "Mit Prüfungstyp verknüpfen",
  "mappedQuestions": "Zugeordnete Fragen",
  "competencyLevel": "Kompetenzstufe"
}
```

**Step 5: Verify frontend builds**

```bash
cd frontend && npm run build
```

**Step 6: Commit**

```bash
git add frontend/src/presentation/components/panel/admin/assessment/curriculum/
git commit -m "feat(exams): add curriculum manager admin UI with tree view and import"
```

---

## Task 9: Integration — Extend Question Editor with Curriculum Tags

**Files:**
- Modify: `frontend/src/presentation/components/panel/admin/assessment/archive/questions/QuestionEditor.vue`

**Step 1: Add curriculum tag section**

Add a `CurriculumTagSelector` section to the QuestionEditor (similar to the existing `TopicTagSelector`). This shows:
- Current curriculum tags for the question
- Dropdown to add new tags (filtered by linked framework)
- Remove button per tag
- AI-suggested tags with confidence badge

Uses `fetchQuestionTags`, `addQuestionTag`, `removeQuestionTag` from the curriculum API client.

**Step 2: Verify frontend builds**

```bash
cd frontend && npm run build
```

**Step 3: Commit**

```bash
git add frontend/src/presentation/components/panel/admin/assessment/archive/questions/QuestionEditor.vue
git commit -m "feat(exams): add curriculum tags to question editor"
```

---

## Task 10: Integration — Extend User Weakness Profile

**Files:**
- Modify: `frontend/src/presentation/components/panel/user/exam-goals/ExamGoalsManager.vue`
- Create: `frontend/src/infrastructure/api/clients/panel/user/exams/curriculum.api.ts`

**Step 1: Write user API client**

```typescript
import { apiClient } from '@/infrastructure/api/apiClient'

export interface CurriculumProfileEntry {
  section_code: string
  section_name: Record<string, string>
  position_number: string
  position_name: Record<string, string>
  total_questions: number
  avg_score: number
  attempts: number
}

export async function fetchCurriculumProfile(
  examTypeKey: string,
): Promise<CurriculumProfileEntry[]> {
  const { data } = await apiClient.get(
    `/user/exam-goals/curriculum-profile/${examTypeKey}`,
  )
  return data.profile
}
```

**Step 2: Add curriculum profile section to ExamGoalsManager**

Below the existing weakness profile bars, add a "Rahmenplan-Profil" section that shows:
- Performance per curriculum position (progress bars, color-coded)
- Grouped by section
- "Kurs erstellen" button per weak position (links to course generator)

**Step 3: Verify frontend builds**

```bash
cd frontend && npm run build
```

**Step 4: Commit**

```bash
git add frontend/src/infrastructure/api/clients/panel/user/exams/curriculum.api.ts \
        frontend/src/presentation/components/panel/user/exam-goals/ExamGoalsManager.vue
git commit -m "feat(exams): add curriculum profile to user exam goals view"
```

---

## Verification Checklist

After all tasks:

```bash
# Backend starts
cd backend && python -c "from app import create_app; create_app()"

# Tests pass
cd backend && python -m pytest tests/ -v

# Frontend builds
cd frontend && npm run build

# Migration runs clean
cd backend && python run_migration.py

# API smoke test (after starting backend)
curl -s http://localhost:5000/admin/curriculum/frameworks | python -m json.tool
```
