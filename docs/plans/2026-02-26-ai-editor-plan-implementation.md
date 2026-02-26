# AI Editor Plan-Tab Redesign — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Den Plan-Tab von einem Ein-Schuss-Generator zu einem 4-Phasen-Wizard mit integriertem Chat umbauen, der vollstaendige Kurse erstellt (Kursname, Theorie, LMs, Pruefungen).

**Architecture:** 4-Phasen-Wizard (Kurs-Definition → Kapitelstruktur → Content-Planung → Ausfuehrung) mit Plan-Chat pro Phase. Progressiver Kontext-Aufbau ueber 3 KI-Aufrufe. DDD-konform: Domain → Infrastructure → Application → API → Frontend.

**Tech Stack:** Flask 3.0 + psycopg3 (Backend), Vue 3 Composition API + TypeScript (Frontend), PostgreSQL 16

**Design-Dokument:** `docs/plans/2026-02-25-ai-editor-plan-redesign.md`

---

## Reihenfolge nach DDD-Layern

```
Task 1-2:   Domain Layer      (Value Objects, Port)
Task 3:     Infrastructure    (Repository erweitern)
Task 4-5:   Infrastructure    (AI-Adapter: Prompts + Generator)
Task 6-7:   Application       (PlanService erweitern + PlanChatService)
Task 8:     API Layer         (Neue Endpoints)
Task 9:     Frontend Types    (plan.types.ts erweitern)
Task 10:    Frontend API      (unified.api.ts erweitern)
Task 11:    Frontend State    (usePlanMode.ts umbauen)
Task 12-15: Frontend UI       (Wizard, Kurs-Karte, Kapitel-Liste, Chat)
Task 16:    Frontend Glue     (PlanTab.vue umbauen)
Task 17:    i18n              (de, en, pl Keys)
Task 18:    Integration Test  (End-to-End Flow)
```

---

## Task 1: Domain — Value Objects fuer Plan-Phasen

**Files:**
- Create: `backend/app/domain/ai/models/plan.py`
- Modify: `backend/app/domain/ai/models/__init__.py` (Barrel Export hinzufuegen falls vorhanden, sonst erstellen)

**Step 1: Value Objects erstellen**

```python
# backend/app/domain/ai/models/plan.py
"""Domain Value Objects fuer den Plan-Phasen-Wizard."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class CourseMeta:
    """Kurs-Definition aus Phase 1."""
    title: str
    description: str
    target_audience: str
    difficulty: str  # 'beginner' | 'intermediate' | 'advanced'
    language: str  # 'de' | 'en' | 'pl'

    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'description': self.description,
            'target_audience': self.target_audience,
            'difficulty': self.difficulty,
            'language': self.language,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CourseMeta':
        return cls(
            title=data.get('title', ''),
            description=data.get('description', ''),
            target_audience=data.get('target_audience', ''),
            difficulty=data.get('difficulty', 'intermediate'),
            language=data.get('language', 'de'),
        )


@dataclass(frozen=True)
class ChapterDraft:
    """Kapitel-Entwurf aus Phase 2."""
    id: str
    title: str
    description: str
    order: int

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'order': self.order,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ChapterDraft':
        return cls(
            id=data.get('id', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            order=data.get('order', 0),
        )


VALID_DIFFICULTIES = ('beginner', 'intermediate', 'advanced')
VALID_LANGUAGES = ('de', 'en', 'pl')
VALID_PLAN_PHASES = (1, 2, 3, 4)
```

**Step 2: Barrel Export**

Pruefen ob `backend/app/domain/ai/models/__init__.py` existiert. Falls ja, Exports hinzufuegen. Falls nein, erstellen:

```python
from .plan import CourseMeta, ChapterDraft, VALID_DIFFICULTIES, VALID_LANGUAGES, VALID_PLAN_PHASES
```

**Step 3: Commit**

```bash
git add backend/app/domain/ai/models/plan.py backend/app/domain/ai/models/__init__.py
git commit -m "feat(domain): add CourseMeta and ChapterDraft value objects for plan wizard"
```

---

## Task 2: Domain — PlanGeneratorPort (Interface)

**Files:**
- Create: `backend/app/domain/ports/plan_generator.py`
- Modify: `backend/app/domain/ports/__init__.py` (Barrel Export erweitern)

**Step 1: Port definieren**

```python
# backend/app/domain/ports/plan_generator.py
"""Port fuer KI-gestuetzte Plan-Generierung."""
from abc import ABC, abstractmethod
from typing import Optional


class PlanGeneratorPort(ABC):
    """Interface fuer AI-basierte Plan-Phasen-Generierung.

    Implementierung liegt in Infrastructure Layer.
    """

    @abstractmethod
    def generate_course_definition(
        self, topic: str, file_text: Optional[str] = None
    ) -> dict:
        """Phase 1: Generiert Kurs-Definition aus Thema oder Datei-Text.

        Returns: {'title', 'description', 'target_audience', 'difficulty', 'language'}
        """
        ...

    @abstractmethod
    def generate_chapter_structure(
        self, course_meta: dict, file_text: Optional[str] = None
    ) -> dict:
        """Phase 2: Generiert Kapitelstruktur basierend auf Kurs-Definition.

        Returns: {'chapters': [{'id', 'title', 'description', 'order'}]}
        """
        ...

    @abstractmethod
    def generate_content_plan(
        self, course_meta: dict, chapters: list[dict],
        active_sf_codes: set[str] | None = None
    ) -> dict:
        """Phase 3: Generiert Content-Plan mit Lektionen, Theorie, LMs, Pruefungen.

        Returns: {'phases': [{'phase_id', 'title', 'order', 'steps': [...]}]}
        """
        ...

    @abstractmethod
    def chat_about_plan(
        self, plan_data: dict, message: str, current_phase: int
    ) -> dict:
        """Chat ueber den Plan — Strukturaenderungen und inhaltliche Diskussion.

        Returns: {'assistant_message': str, 'plan_patch': dict | None}
        """
        ...
```

**Step 2: Barrel Export in `__init__.py` erweitern**

In `backend/app/domain/ports/__init__.py` hinzufuegen:

```python
from .plan_generator import PlanGeneratorPort
```

**Step 3: Commit**

```bash
git add backend/app/domain/ports/plan_generator.py backend/app/domain/ports/__init__.py
git commit -m "feat(domain): add PlanGeneratorPort interface for phased plan generation"
```

---

## Task 3: Infrastructure — ContentPlanRepository erweitern

**Files:**
- Modify: `backend/app/infrastructure/persistence/repositories/ai/content_plans.py`

**Kontext:** Aktuell 105 Zeilen, 6 Methoden. Muss erweitert werden fuer:
- `current_phase` Feld
- `course_meta` Feld (JSONB)
- `chapters` Feld (JSONB)
- `chat_history` Feld (JSONB)

**Step 1: DB-Migration erstellen**

Pruefen welche Migration-Nummer als naechstes dran ist, dann Migration erstellen:

```sql
-- Migration: Add plan wizard phase columns
ALTER TABLE content_plans ADD COLUMN IF NOT EXISTS current_phase INTEGER DEFAULT 1;
ALTER TABLE content_plans ADD COLUMN IF NOT EXISTS course_meta JSONB DEFAULT '{}';
ALTER TABLE content_plans ADD COLUMN IF NOT EXISTS chapters JSONB DEFAULT '[]';
ALTER TABLE content_plans ADD COLUMN IF NOT EXISTS chat_history JSONB DEFAULT '[]';

-- Constraint fuer gueltige Phasen
ALTER TABLE content_plans ADD CONSTRAINT chk_plan_phase
    CHECK (current_phase >= 1 AND current_phase <= 4);
```

**Step 2: Repository-Methoden erweitern**

Neue Methoden in `ContentPlanRepository`:

```python
@classmethod
def update_phase(cls, plan_id: str, phase: int, phase_data: dict) -> Optional[dict]:
    """Aktualisiert die aktuelle Phase und zugehoerige Daten."""
    with get_db_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                UPDATE content_plans
                SET current_phase = %s,
                    course_meta = COALESCE(%s, course_meta),
                    chapters = COALESCE(%s, chapters),
                    plan_data = COALESCE(%s, plan_data),
                    updated_at = NOW()
                WHERE plan_id = %s
                RETURNING *
            """, (
                phase,
                Json(phase_data.get('course_meta')) if 'course_meta' in phase_data else None,
                Json(phase_data.get('chapters')) if 'chapters' in phase_data else None,
                Json(phase_data.get('plan_data')) if 'plan_data' in phase_data else None,
                plan_id,
            ))
            return cur.fetchone()

@classmethod
def append_chat_message(cls, plan_id: str, message: dict) -> Optional[dict]:
    """Fuegt eine Chat-Nachricht zur History hinzu."""
    with get_db_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                UPDATE content_plans
                SET chat_history = chat_history || %s::jsonb,
                    updated_at = NOW()
                WHERE plan_id = %s
                RETURNING *
            """, (Json([message]), plan_id))
            return cur.fetchone()
```

**Step 3: `find_by_id` und `create` erweitern**

In `create()`: Neue Felder `current_phase`, `course_meta`, `chapters`, `chat_history` im INSERT.
In `find_by_id()`: Sicherstellen dass neue Felder im SELECT zurueckgegeben werden (sollte mit `*` automatisch klappen).

**Step 4: Commit**

```bash
git add backend/app/infrastructure/persistence/repositories/ai/content_plans.py
git commit -m "feat(infrastructure): extend ContentPlanRepository for phased plan wizard"
```

---

## Task 4: Infrastructure — Plan-Prompts

**Files:**
- Create: `backend/app/infrastructure/ai/plan_prompts.py`

**Kontext:** Die Prompts fuer Phase 1-3 und Chat. Aktuell lebt die Prompt-Logik in `plan_service.py` (Zeilen 224-298 `_get_skill_catalog_prompt`). Diese Logik wird nach Infrastructure verschoben (DDD: Prompts = AI-Infrastruktur).

**Step 1: Prompt-Module erstellen**

```python
# backend/app/infrastructure/ai/plan_prompts.py
"""Prompts fuer die Plan-Phasen-Generierung."""


def build_phase1_prompt(topic: str, file_text: str | None = None) -> tuple[str, str]:
    """Phase 1: Kurs-Definition.

    Returns: (system_message, user_message)
    """
    system = """Du bist ein erfahrener Kursarchitekt fuer eine E-Learning-Plattform.
Deine Aufgabe: Erstelle eine praezise Kurs-Definition basierend auf dem gegebenen Thema.

Antworte NUR mit gueltigem JSON in diesem Format:
{
    "title": "Kurs-Titel (praegnant, max 60 Zeichen)",
    "description": "Kursbeschreibung (2-3 Saetze, was der Kurs vermittelt)",
    "target_audience": "Zielgruppe (1 Satz)",
    "difficulty": "beginner|intermediate|advanced",
    "language": "de"
}

Regeln:
- Der Titel soll professionell und spezifisch sein
- Die Beschreibung soll den Mehrwert klar kommunizieren
- Waehle die Schwierigkeit passend zum Thema"""

    if file_text:
        user = f"""Analysiere das folgende Dokument und leite daraus eine Kurs-Definition ab.

DOKUMENT-INHALT:
{file_text[:6000]}

Erstelle die Kurs-Definition basierend auf dem Inhalt des Dokuments."""
    else:
        user = f"""Erstelle eine Kurs-Definition fuer folgendes Thema:

THEMA: {topic}

Erstelle einen professionellen Kurstitel, eine Beschreibung, und bestimme Zielgruppe und Schwierigkeitsgrad."""

    return system, user


def build_phase2_prompt(course_meta: dict, file_text: str | None = None) -> tuple[str, str]:
    """Phase 2: Kapitelstruktur.

    Returns: (system_message, user_message)
    """
    system = """Du bist ein erfahrener Kursarchitekt. Deine Aufgabe: Erstelle eine logische Kapitelstruktur fuer den gegebenen Kurs.

Antworte NUR mit gueltigem JSON in diesem Format:
{
    "chapters": [
        {
            "title": "Kapitel-Titel",
            "description": "Kurzbeschreibung des Kapitels (1-2 Saetze)"
        }
    ]
}

Regeln:
- 5-12 Kapitel je nach Kursumfang
- Logische Reihenfolge: Grundlagen zuerst, dann aufbauend
- Jedes Kapitel behandelt ein klar abgegrenztes Thema
- Kapitel-Titel sollen praegnant und beschreibend sein
- Keine Ueberlappung zwischen Kapiteln"""

    context = f"""KURS: {course_meta.get('title', '')}
BESCHREIBUNG: {course_meta.get('description', '')}
ZIELGRUPPE: {course_meta.get('target_audience', '')}
SCHWIERIGKEIT: {course_meta.get('difficulty', 'intermediate')}"""

    if file_text:
        user = f"""{context}

DOKUMENT-INHALT (als Basis fuer die Kapitelstruktur):
{file_text[:8000]}

Erstelle eine Kapitelstruktur die den Dokumentinhalt vollstaendig abdeckt."""
    else:
        user = f"""{context}

Erstelle eine umfassende Kapitelstruktur fuer diesen Kurs."""

    return system, user


def build_phase3_prompt(
    course_meta: dict,
    chapters: list[dict],
    skill_catalog_section: str
) -> tuple[str, str]:
    """Phase 3: Content-Plan mit Lektionen, Theorie, LMs, Pruefungen.

    Returns: (system_message, user_message)
    """
    system = f"""Du bist ein erfahrener Kursarchitekt und Didaktik-Experte.
Deine Aufgabe: Erstelle einen detaillierten Content-Plan fuer jeden Kapitel des Kurses.

VERFUEGBARE SKILLS:
{skill_catalog_section}

DIDAKTISCHE RICHTLINIEN:
- Jedes Kapitel MUSS beginnen mit: generate_theory_sheet (target_type: chapter) — Kapitel-Ueberblick
- Jede Lektion MUSS beginnen mit: generate_theory_sheet (target_type: lesson) — Lektions-Detail
- Nach der Theorie: 2-3 passende Lernmethoden (LMs) pro Lektion
- Am Ende jedes Kapitels: generate_chapter_exam (falls verfuegbar)

LM-ZUORDNUNG nach Inhaltstyp:
- Konzepte/Theorie → deep_explanation + flashcards
- Prozesse/Ablaeufe → step_by_step + cloze_test
- Praxis/Anwendung → example_scenario + multi_step
- Berechnung → math_interactive + step_by_step
- Begriffe/Definitionen → flashcards + true_false + drag_and_drop
- Konfiguration/Setup → example_scenario + hands_on_lab

Antworte NUR mit gueltigem JSON:
{{
    "phases": [
        {{
            "title": "Kapitel-Titel",
            "chapter_id": "chapter-uuid",
            "steps": [
                {{
                    "skill_code": "generate_theory_sheet",
                    "target_type": "chapter",
                    "target_title": "Kapitel-Theorie: ...",
                    "parameters": {{"difficulty": "intermediate", "language": "de"}}
                }},
                {{
                    "skill_code": "generate_theory_sheet",
                    "target_type": "lesson",
                    "target_title": "Lektion: ...",
                    "parameters": {{"difficulty": "intermediate", "language": "de"}}
                }},
                {{
                    "skill_code": "generate_deep_explanation",
                    "target_type": "lesson",
                    "target_title": "Lektion: ...",
                    "parameters": {{"difficulty": "intermediate", "language": "de"}}
                }}
            ]
        }}
    ]
}}"""

    chapters_text = "\n".join(
        f"  {i+1}. {ch.get('title', '')} — {ch.get('description', '')}"
        for i, ch in enumerate(chapters)
    )

    user = f"""KURS: {course_meta.get('title', '')}
BESCHREIBUNG: {course_meta.get('description', '')}
ZIELGRUPPE: {course_meta.get('target_audience', '')}
SCHWIERIGKEIT: {course_meta.get('difficulty', 'intermediate')}

KAPITELSTRUKTUR:
{chapters_text}

Erstelle den vollstaendigen Content-Plan. Jedes Kapitel braucht:
1. Eine Kapitel-Theorie (generate_theory_sheet, target_type: chapter)
2. 2-4 Lektionen, jede mit:
   a. Lektions-Theorie (generate_theory_sheet, target_type: lesson)
   b. 2-3 passende Lernmethoden
3. Eine Kapitel-Pruefung (generate_chapter_exam) am Ende"""

    return system, user


def build_plan_chat_prompt(
    plan_data: dict, current_phase: int
) -> str:
    """System-Prompt fuer Plan-Chat.

    Returns: system_message
    """
    phase_context = {
        1: "Der User befindet sich in Phase 1 (Kurs-Definition). Du kannst title, description, target_audience, difficulty und language aendern.",
        2: "Der User befindet sich in Phase 2 (Kapitelstruktur). Du kannst Kapitel hinzufuegen, entfernen, umbenennen oder umsortieren.",
        3: "Der User befindet sich in Phase 3 (Content-Planung). Du kannst Lektionen, Lernmethoden und Pruefungen aendern.",
    }

    return f"""Du bist ein Kursarchitekt-Assistent. Du hilfst dem User seinen Kursplan zu verbessern.

AKTUELLE PHASE: {current_phase}
{phase_context.get(current_phase, '')}

AKTUELLER PLAN:
{_format_plan_for_chat(plan_data)}

Du kannst zwei Dinge tun:
1. BERATEN: Inhaltliche Fragen beantworten und Vorschlaege machen
2. AENDERN: Den Plan direkt aendern wenn der User es wuenscht

Wenn du den Plan aendern willst, antworte mit JSON:
{{
    "assistant_message": "Erklaerung was du geaendert hast",
    "plan_patch": {{ ... die geaenderten Felder ... }}
}}

Wenn du nur beraten willst (keine Aenderung):
{{
    "assistant_message": "Deine Antwort/Beratung",
    "plan_patch": null
}}

Antworte IMMER mit gueltigem JSON."""


def _format_plan_for_chat(plan_data: dict) -> str:
    """Formatiert Plan-Daten kompakt fuer den Chat-Kontext."""
    parts = []

    meta = plan_data.get('course_meta', {})
    if meta:
        parts.append(f"KURS: {meta.get('title', 'Unbenannt')}")
        parts.append(f"BESCHREIBUNG: {meta.get('description', '-')}")

    chapters = plan_data.get('chapters', [])
    if chapters:
        parts.append("\nKAPITEL:")
        for i, ch in enumerate(chapters):
            parts.append(f"  {i+1}. {ch.get('title', '')} — {ch.get('description', '')}")

    phases = plan_data.get('phases', [])
    if phases:
        parts.append("\nCONTENT-PLAN:")
        for phase in phases:
            parts.append(f"\n  Kapitel: {phase.get('title', '')}")
            for step in phase.get('steps', []):
                parts.append(f"    - {step.get('target_title', '')} [{step.get('skill_code', '')}]")

    return "\n".join(parts)
```

**Step 2: Barrel Export fuer `infrastructure/ai/`**

Pruefen ob `backend/app/infrastructure/ai/__init__.py` existiert, sonst erstellen.

**Step 3: Commit**

```bash
git add backend/app/infrastructure/ai/plan_prompts.py backend/app/infrastructure/ai/__init__.py
git commit -m "feat(infrastructure): add plan phase prompts for 4-phase wizard"
```

---

## Task 5: Infrastructure — PlanGeneratorAdapter

**Files:**
- Create: `backend/app/infrastructure/ai/plan_generator.py`

**Kontext:** Implementiert `PlanGeneratorPort`. Nutzt den bestehenden `AIAdapter` oder direkten Provider-Aufruf. Die Prompt-Logik kommt aus `plan_prompts.py`.

**Step 1: Adapter erstellen**

```python
# backend/app/infrastructure/ai/plan_generator.py
"""AI-Adapter fuer Plan-Phasen-Generierung. Implementiert PlanGeneratorPort."""
import json
import logging
import uuid
from typing import Optional

from app.domain.ports.plan_generator import PlanGeneratorPort
from app.infrastructure.ai.plan_prompts import (
    build_phase1_prompt,
    build_phase2_prompt,
    build_phase3_prompt,
    build_plan_chat_prompt,
)
from app.infrastructure.persistence.repositories.ai_models import AIModelsRepository

logger = logging.getLogger(__name__)


class PlanGeneratorAdapter(PlanGeneratorPort):
    """Implementierung des PlanGeneratorPort mit AI-Provider."""

    def __init__(self, provider_name: str | None = None, model_name: str | None = None):
        self.provider_name = provider_name
        self.model_name = model_name
        self._resolve_defaults()

    def _resolve_defaults(self):
        """Laedt Default-Provider/Model aus DB falls nicht gesetzt."""
        if not self.provider_name or not self.model_name:
            try:
                default = AIModelsRepository.get_default_model()
                if default:
                    self.provider_name = self.provider_name or default.get('provider_name', 'openai')
                    self.model_name = self.model_name or default.get('model_name', 'gpt-4o-mini')
            except Exception:
                self.provider_name = self.provider_name or 'openai'
                self.model_name = self.model_name or 'gpt-4o-mini'

    def _call_ai(self, system_msg: str, user_msg: str, max_tokens: int = 4000) -> str:
        """Ruft den AI-Provider auf und gibt die Antwort als String zurueck.

        NOTE: Muss an den bestehenden AI-Adapter/Provider-Mechanismus angebunden werden.
        Der genaue Import haengt davon ab wie der AIAdapter im Projekt strukturiert ist.
        Pruefen: app/infrastructure/ai/ oder app/application/services/ai/ fuer bestehenden Adapter.
        """
        # TODO: An bestehenden AIAdapter anbinden — Signatur aehnlich wie in
        # plan_service.py:_generate_plan_via_ai() (Zeilen 329-386)
        from app.application.services.content.course_authoring.session import CourseAuthoringService

        service = CourseAuthoringService(
            provider=self.provider_name,
            model=self.model_name
        )
        # Nutze den internen AI-Aufruf
        response = service._call_ai_provider(system_msg, user_msg, max_tokens=max_tokens)
        return response

    def generate_course_definition(self, topic: str, file_text: Optional[str] = None) -> dict:
        system, user = build_phase1_prompt(topic, file_text)
        raw = self._call_ai(system, user, max_tokens=1000)
        return self._parse_json(raw, fallback={
            'title': topic or 'Neuer Kurs',
            'description': '',
            'target_audience': '',
            'difficulty': 'intermediate',
            'language': 'de',
        })

    def generate_chapter_structure(self, course_meta: dict, file_text: Optional[str] = None) -> dict:
        system, user = build_phase2_prompt(course_meta, file_text)
        raw = self._call_ai(system, user, max_tokens=4000)
        return self._parse_json(raw, fallback={'chapters': []})

    def generate_content_plan(
        self, course_meta: dict, chapters: list[dict],
        active_sf_codes: set[str] | None = None
    ) -> dict:
        # Baue Skill-Katalog-Sektion (aus bestehender Logik in plan_service.py)
        from app.application.services.ai.plan_service import PlanService
        sf_codes = active_sf_codes or set()
        skill_catalog_section = PlanService._get_skill_catalog_prompt(sf_codes)

        system, user = build_phase3_prompt(course_meta, chapters, skill_catalog_section)
        raw = self._call_ai(system, user, max_tokens=8000)
        result = self._parse_json(raw, fallback={'phases': []})

        # UUIDs fuer Steps generieren falls fehlend
        for phase in result.get('phases', []):
            if not phase.get('phase_id'):
                phase['phase_id'] = str(uuid.uuid4())
            for i, step in enumerate(phase.get('steps', [])):
                if not step.get('step_id'):
                    step['step_id'] = str(uuid.uuid4())
                step['order'] = i + 1
                step['status'] = 'pending'

        return result

    def chat_about_plan(self, plan_data: dict, message: str, current_phase: int) -> dict:
        system = build_plan_chat_prompt(plan_data, current_phase)
        user = message
        raw = self._call_ai(system, user, max_tokens=4000)
        result = self._parse_json(raw, fallback={
            'assistant_message': 'Entschuldigung, ich konnte die Anfrage nicht verarbeiten.',
            'plan_patch': None,
        })
        return result

    def _parse_json(self, raw: str, fallback: dict) -> dict:
        """Parst JSON-Antwort der AI, mit Fallback bei Fehler."""
        try:
            # Markdown code fences entfernen
            cleaned = raw.strip()
            if cleaned.startswith('```'):
                lines = cleaned.split('\n')
                cleaned = '\n'.join(lines[1:])
                if cleaned.endswith('```'):
                    cleaned = cleaned[:-3]
            return json.loads(cleaned)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Plan AI JSON parse error: {e}, raw: {raw[:200]}")
            return fallback
```

**Step 2: Commit**

```bash
git add backend/app/infrastructure/ai/plan_generator.py
git commit -m "feat(infrastructure): add PlanGeneratorAdapter implementing PlanGeneratorPort"
```

**HINWEIS:** Der `_call_ai`-Aufruf muss beim Implementieren an den tatsaechlichen AI-Adapter angepasst werden. Pruefen wie `plan_service.py:329-386` den AI-Call macht und dasselbe Pattern nutzen.

---

## Task 6: Application — PlanService erweitern

**Files:**
- Modify: `backend/app/application/services/ai/plan_service.py` (486 Zeilen)

**Kontext:** Die bestehenden Methoden `create_plan()`, `create_plan_from_file()` bleiben fuer Rueckwaerts-Kompatibilitaet. Neue Methoden fuer den Phasen-Wizard werden hinzugefuegt.

**Step 1: Neue Phasen-Methoden hinzufuegen**

Am Ende der Klasse (vor den privaten Helpern) einfuegen:

```python
# --- Phase Wizard Methods ---

@staticmethod
def create_phased_plan(course_id: str, user_id: str, topic: str = '',
                       file_ids: list[str] | None = None) -> dict:
    """Erstellt einen neuen Plan und fuehrt Phase 1 (Kurs-Definition) aus.

    Args:
        topic: Thema fuer den Kurs (wenn kein File)
        file_ids: Datei-IDs deren Text als Basis dient
    """
    from app.infrastructure.ai.plan_generator import PlanGeneratorAdapter
    from app.infrastructure.persistence.repositories.authoring.files import AuthoringFilesRepository

    file_text = None
    if file_ids:
        for fid in file_ids:
            f = AuthoringFilesRepository.find_by_id(fid)
            if f and f.get('extracted_text'):
                file_text = (file_text or '') + '\n' + f['extracted_text']

    generator = PlanGeneratorAdapter()
    course_meta = generator.generate_course_definition(
        topic=topic or '',
        file_text=file_text
    )

    plan_data = {
        'plan_id': str(uuid.uuid4()),
        'course_id': course_id,
        'user_id': user_id,
        'status': 'draft',
        'current_phase': 1,
        'scope': 'course',
        'course_meta': course_meta,
        'chapters': [],
        'plan_data': json.dumps({'phases': []}),
        'chat_history': [],
        'estimated_total_tokens': 0,
        'actual_tokens': 0,
    }

    result = ContentPlanRepository.create(plan_data)
    return result

@staticmethod
def advance_to_phase2(plan_id: str) -> dict:
    """Phase 2: Generiert Kapitelstruktur basierend auf bestaetigter Kurs-Definition."""
    from app.infrastructure.ai.plan_generator import PlanGeneratorAdapter

    plan = ContentPlanRepository.find_by_id(plan_id)
    if not plan:
        raise ValueError(f"Plan {plan_id} not found")

    course_meta = plan.get('course_meta', {})
    if isinstance(course_meta, str):
        course_meta = json.loads(course_meta)

    # Optional: File-Text nochmal nutzen
    file_text = None  # TODO: Aus Plan-Kontext laden falls vorhanden

    generator = PlanGeneratorAdapter()
    result = generator.generate_chapter_structure(course_meta, file_text)

    chapters = result.get('chapters', [])
    # UUIDs und Order hinzufuegen
    for i, ch in enumerate(chapters):
        if not ch.get('id'):
            ch['id'] = str(uuid.uuid4())
        ch['order'] = i + 1

    ContentPlanRepository.update_phase(plan_id, {
        'chapters': chapters,
    })
    # Phase auf 2 setzen
    return ContentPlanRepository.update_phase(plan_id, {}) or plan

@staticmethod
def advance_to_phase3(plan_id: str) -> dict:
    """Phase 3: Generiert Content-Plan basierend auf bestaetigten Kapiteln."""
    from app.infrastructure.ai.plan_generator import PlanGeneratorAdapter

    plan = ContentPlanRepository.find_by_id(plan_id)
    if not plan:
        raise ValueError(f"Plan {plan_id} not found")

    course_meta = plan.get('course_meta', {})
    chapters = plan.get('chapters', [])
    if isinstance(course_meta, str):
        course_meta = json.loads(course_meta)
    if isinstance(chapters, str):
        chapters = json.loads(chapters)

    active_sf_codes = PlanService._get_active_sf_codes()
    generator = PlanGeneratorAdapter()
    result = generator.generate_content_plan(course_meta, chapters, active_sf_codes)

    plan_data = result
    estimated = PlanService._estimate_plan_tokens(plan_data)

    ContentPlanRepository.update_plan_data(plan_id, plan_data)
    ContentPlanRepository.update_phase(plan_id, {})  # Aktualisiert updated_at
    return ContentPlanRepository.find_by_id(plan_id)

@staticmethod
def chat_about_plan(plan_id: str, message: str) -> dict:
    """Chat ueber den Plan — KI antwortet und kann optional den Plan aendern."""
    from app.infrastructure.ai.plan_generator import PlanGeneratorAdapter

    plan = ContentPlanRepository.find_by_id(plan_id)
    if not plan:
        raise ValueError(f"Plan {plan_id} not found")

    current_phase = plan.get('current_phase', 1)
    plan_data = {
        'course_meta': plan.get('course_meta', {}),
        'chapters': plan.get('chapters', []),
        'phases': json.loads(plan.get('plan_data', '{}')) if isinstance(plan.get('plan_data'), str) else plan.get('plan_data', {}),
    }

    generator = PlanGeneratorAdapter()
    result = generator.chat_about_plan(plan_data, message, current_phase)

    # Chat-Nachricht speichern
    ContentPlanRepository.append_chat_message(plan_id, {
        'role': 'user',
        'content': message,
    })
    ContentPlanRepository.append_chat_message(plan_id, {
        'role': 'assistant',
        'content': result.get('assistant_message', ''),
    })

    # Plan-Patch anwenden falls vorhanden
    patch = result.get('plan_patch')
    if patch:
        update_data = {}
        if 'course_meta' in patch:
            update_data['course_meta'] = patch['course_meta']
        if 'chapters' in patch:
            update_data['chapters'] = patch['chapters']
        if 'phases' in patch:
            update_data['plan_data'] = patch['phases']
        if update_data:
            ContentPlanRepository.update_phase(plan_id, update_data)

    return {
        'assistant_message': result.get('assistant_message', ''),
        'plan_patch': patch,
        'plan': ContentPlanRepository.find_by_id(plan_id),
    }
```

**Step 2: Imports oben in der Datei hinzufuegen**

```python
import uuid
import json
```

Pruefen ob diese schon importiert sind.

**Step 3: Commit**

```bash
git add backend/app/application/services/ai/plan_service.py
git commit -m "feat(application): add phased plan wizard methods to PlanService"
```

**ACHTUNG:** Die Datei ist jetzt ~600 Zeilen. Nach G01 (>500 LOC → SPLIT) muss sie aufgeteilt werden:
- `plan_service.py` — bestehende Methoden (create, execute, approve etc.)
- `plan_service_wizard.py` — neue Phasen-Methoden
- `__init__.py` — Barrel Export

---

## Task 7: Application — PlanService aufteilen (G01: 500 LOC)

**Files:**
- Modify: `backend/app/application/services/ai/plan_service.py` (bestehende Methoden behalten, ~300 LOC)
- Create: `backend/app/application/services/ai/plan_service_wizard.py` (neue Phasen-Methoden, ~200 LOC)

**Step 1:** Private Helper und Wizard-Methoden in `plan_service_wizard.py` verschieben.

**Step 2:** In `plan_service.py` importieren:

```python
from app.application.services.ai.plan_service_wizard import PlanWizardService
```

**Step 3:** Commit

```bash
git add backend/app/application/services/ai/plan_service.py backend/app/application/services/ai/plan_service_wizard.py
git commit -m "refactor(application): split PlanService to respect 500 LOC limit (G01)"
```

---

## Task 8: API — Neue Endpoints

**Files:**
- Modify: `backend/app/api/v1/panel/editor/ai/plans.py` (187 Zeilen → ~280 Zeilen)

**Step 1: Neue Endpoints hinzufuegen**

Nach den bestehenden Endpoints (Zeile 186) einfuegen:

```python
# --- Phase Wizard Endpoints ---

@ai_plans_bp.route('/phased', methods=['POST'])
@permission_required('content.courses:write')
def create_phased_plan():
    """Phase 1: Erstellt Plan und generiert Kurs-Definition."""
    data = request.get_json()
    course_id = data.get('course_id')
    topic = data.get('topic', '')
    file_ids = data.get('file_ids', [])

    if not course_id:
        return jsonify({'success': False, 'error': 'MISSING_COURSE_ID'}), 400

    try:
        result = PlanService.create_phased_plan(
            course_id=course_id,
            user_id=g.current_user['user_id'],
            topic=topic,
            file_ids=file_ids,
        )
        return jsonify({'success': True, 'data': result}), 201
    except Exception as e:
        logger.error(f"Phase 1 error: {e}")
        return jsonify({'success': False, 'error': 'PLAN_ERROR', 'message': str(e)}), 500


@ai_plans_bp.route('/<plan_id>/phase2', methods=['POST'])
@permission_required('content.courses:write')
def advance_phase2(plan_id):
    """Phase 2: Generiert Kapitelstruktur."""
    try:
        result = PlanService.advance_to_phase2(plan_id)
        return jsonify({'success': True, 'data': result})
    except ValueError as e:
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': str(e)}), 404
    except Exception as e:
        logger.error(f"Phase 2 error: {e}")
        return jsonify({'success': False, 'error': 'PLAN_ERROR', 'message': str(e)}), 500


@ai_plans_bp.route('/<plan_id>/phase3', methods=['POST'])
@permission_required('content.courses:write')
def advance_phase3(plan_id):
    """Phase 3: Generiert Content-Plan."""
    try:
        result = PlanService.advance_to_phase3(plan_id)
        return jsonify({'success': True, 'data': result})
    except ValueError as e:
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': str(e)}), 404
    except Exception as e:
        logger.error(f"Phase 3 error: {e}")
        return jsonify({'success': False, 'error': 'PLAN_ERROR', 'message': str(e)}), 500


@ai_plans_bp.route('/<plan_id>/chat', methods=['POST'])
@permission_required('content.courses:write')
def plan_chat(plan_id):
    """Chat ueber den Plan — Strukturaenderungen und Beratung."""
    data = request.get_json()
    message = data.get('message', '').strip()

    if not message:
        return jsonify({'success': False, 'error': 'MISSING_MESSAGE'}), 400

    try:
        result = PlanService.chat_about_plan(plan_id, message)
        return jsonify({'success': True, 'data': result})
    except ValueError as e:
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': str(e)}), 404
    except Exception as e:
        logger.error(f"Plan chat error: {e}")
        return jsonify({'success': False, 'error': 'PLAN_ERROR', 'message': str(e)}), 500
```

**Step 2: Import erweitern**

Am Anfang der Datei sicherstellen dass `PlanWizardService` oder die neuen Methoden importiert werden (je nach Split aus Task 7).

**Step 3: Commit**

```bash
git add backend/app/api/v1/panel/editor/ai/plans.py
git commit -m "feat(api): add phased plan wizard endpoints (phase1, phase2, phase3, chat)"
```

---

## Task 9: Frontend Types — plan.types.ts erweitern

**Files:**
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/types/plan.types.ts` (57 Zeilen)

**Step 1: Neue Types hinzufuegen**

Am Anfang der Datei (nach bestehenden Types) einfuegen:

```typescript
// --- Phase Wizard Types ---

export type WizardPhase = 1 | 2 | 3 | 4

export interface CourseMeta {
  title: string
  description: string
  target_audience: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  language: 'de' | 'en' | 'pl'
}

export interface ChapterDraft {
  id: string
  title: string
  description: string
  order: number
}

export interface PlanChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

export interface PlanChatResponse {
  assistant_message: string
  plan_patch: Record<string, unknown> | null
  plan: ContentPlan
}
```

**Step 2: ContentPlan Interface erweitern**

In der bestehenden `ContentPlan` interface neue Felder hinzufuegen:

```typescript
interface ContentPlan {
  plan_id: string
  course_id: string
  current_phase: WizardPhase          // NEU
  course_meta: CourseMeta             // NEU
  chapters: ChapterDraft[]            // NEU
  chat_history: PlanChatMessage[]     // NEU
  scope: PlanScope
  scope_id: string | null
  status: PlanStatus
  phases: PlanPhase[]
  estimated_total_tokens: number
  actual_tokens: number
  created_at: string
  updated_at: string
}
```

**Step 3: Request DTOs hinzufuegen**

```typescript
export interface CreatePhasedPlanRequest {
  course_id: string
  topic?: string
  file_ids?: string[]
}

export interface PlanChatRequest {
  message: string
}
```

**Step 4: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/types/plan.types.ts
git commit -m "feat(frontend): extend plan types for 4-phase wizard"
```

---

## Task 10: Frontend API — unified.api.ts erweitern

**Files:**
- Modify: `frontend/src/infrastructure/api/clients/panel/editor/unified/unified.api.ts`

**Step 1: Neue API-Funktionen hinzufuegen**

Nach den bestehenden Plan-Funktionen (ca. Zeile 70):

```typescript
// --- Phase Wizard API ---

export async function createPhasedPlan(data: CreatePhasedPlanRequest): Promise<ContentPlan> {
  const response = await apiClient.post(`${BASE}/plans/phased`, data)
  return response.data.data
}

export async function advanceToPhase2(planId: string): Promise<ContentPlan> {
  const response = await apiClient.post(`${BASE}/plans/${planId}/phase2`)
  return response.data.data
}

export async function advanceToPhase3(planId: string): Promise<ContentPlan> {
  const response = await apiClient.post(`${BASE}/plans/${planId}/phase3`)
  return response.data.data
}

export async function sendPlanChat(planId: string, message: string): Promise<PlanChatResponse> {
  const response = await apiClient.post(`${BASE}/plans/${planId}/chat`, { message })
  return response.data.data
}
```

**Step 2: Imports erweitern**

```typescript
import type {
  CreatePhasedPlanRequest,
  PlanChatResponse,
  // ... bestehende Imports
} from '@/presentation/components/panel/editor/ai/unified/types/plan.types'
```

**Step 3: Commit**

```bash
git add frontend/src/infrastructure/api/clients/panel/editor/unified/unified.api.ts
git commit -m "feat(frontend): add phased plan wizard API functions"
```

---

## Task 11: Frontend State — usePlanMode.ts umbauen

**Files:**
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/composables/usePlanMode.ts` (361 Zeilen)

**Kontext:** Dies ist die groesste Frontend-Aenderung. Der Composable wird erweitert mit Phasen-State, Chat und Phase-Navigation. Die bestehende Polling-Logik und Execution bleiben.

**Step 1: Neue State-Variablen hinzufuegen**

Am Anfang der `usePlanMode()` Funktion:

```typescript
// --- Phase Wizard State ---
const currentPhase = ref<WizardPhase>(1)
const courseMeta = ref<CourseMeta | null>(null)
const chapters = ref<ChapterDraft[]>([])
const chatMessages = ref<PlanChatMessage[]>([])
const isChatting = ref(false)
```

**Step 2: Phasen-Methoden hinzufuegen**

```typescript
async function generatePhase1(topic?: string, fileIds?: string[]): Promise<void> {
  isCreating.value = true
  error.value = null
  try {
    const plan = await createPhasedPlan({
      course_id: courseId,  // injected
      topic,
      file_ids: fileIds,
    })
    currentPlan.value = plan
    courseMeta.value = plan.course_meta || null
    currentPhase.value = 1
  } catch (e: any) {
    error.value = e.message || 'Phase 1 fehlgeschlagen'
  } finally {
    isCreating.value = false
  }
}

async function confirmPhase(): Promise<void> {
  if (!currentPlan.value) return
  const planId = currentPlan.value.plan_id

  isCreating.value = true
  error.value = null
  try {
    if (currentPhase.value === 1) {
      const plan = await advanceToPhase2(planId)
      currentPlan.value = plan
      chapters.value = plan.chapters || []
      currentPhase.value = 2
    } else if (currentPhase.value === 2) {
      const plan = await advanceToPhase3(planId)
      currentPlan.value = plan
      currentPhase.value = 3
    } else if (currentPhase.value === 3) {
      // Phase 3 bestaetigt → bereit fuer Execution (Phase 4)
      await approve()
      currentPhase.value = 4
    }
  } catch (e: any) {
    error.value = e.message || 'Phase-Uebergang fehlgeschlagen'
  } finally {
    isCreating.value = false
  }
}

function goBackToPhase(phase: WizardPhase): void {
  if (phase < currentPhase.value) {
    currentPhase.value = phase
    // Spaetere Phasen-Daten nicht loeschen — User kann vorwaerts navigieren
  }
}

async function sendPlanChatMessage(message: string): Promise<string> {
  if (!currentPlan.value) return ''

  isChatting.value = true
  error.value = null
  try {
    chatMessages.value.push({ role: 'user', content: message })

    const result = await sendPlanChat(currentPlan.value.plan_id, message)

    chatMessages.value.push({
      role: 'assistant',
      content: result.assistant_message,
    })

    // Plan aktualisieren falls Patch kam
    if (result.plan) {
      currentPlan.value = result.plan
      courseMeta.value = result.plan.course_meta || courseMeta.value
      chapters.value = result.plan.chapters || chapters.value
    }

    return result.assistant_message
  } catch (e: any) {
    error.value = e.message || 'Chat fehlgeschlagen'
    return ''
  } finally {
    isChatting.value = false
  }
}
```

**Step 3: Return-Objekt erweitern**

Neue Exports zum return hinzufuegen:

```typescript
return {
  // ... bestehende Exports ...

  // Phase Wizard
  currentPhase,
  courseMeta,
  chapters,
  chatMessages,
  isChatting,
  generatePhase1,
  confirmPhase,
  goBackToPhase,
  sendPlanChatMessage,
}
```

**Step 4: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/composables/usePlanMode.ts
git commit -m "feat(frontend): add phase wizard state and methods to usePlanMode"
```

---

## Task 12: Frontend UI — PlanPhaseWizard.vue

**Files:**
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/panels/PlanPhaseWizard.vue`

**Kontext:** Container-Komponente die den Wizard steuert und die richtige Phase-Komponente rendert.

**Step 1: Wizard-Container erstellen**

```vue
<script setup lang="ts">
import { computed } from 'vue'
import type { WizardPhase, CourseMeta, ChapterDraft, PlanChatMessage, ContentPlan } from '../types'

import PlanCourseCard from './PlanCourseCard.vue'
import PlanChapterList from './PlanChapterList.vue'
import PlanModePanel from './PlanModePanel.vue'
import PlanChat from './PlanChat.vue'

interface Props {
  currentPhase: WizardPhase
  plan: ContentPlan | null
  courseMeta: CourseMeta | null
  chapters: ChapterDraft[]
  chatMessages: PlanChatMessage[]
  isCreating: boolean
  isExecuting: boolean
  isChatting: boolean
  hasFiles: boolean
  // Phase 3+4 props (durchgereicht an PlanModePanel)
  isDraft: boolean
  isApproved: boolean
  isPaused: boolean
  isCompleted: boolean
  isFailed: boolean
  totalSteps: number
  completedSteps: number
  failedSteps: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  generatePhase1: [topic?: string, fileIds?: string[]]
  confirmPhase: []
  goBack: [phase: WizardPhase]
  sendChat: [message: string]
  execute: []
  pause: []
  resume: []
  discard: []
  reorderStep: [phaseIdx: number, stepIdx: number, direction: 'up' | 'down']
  removeStep: [phaseIdx: number, stepIdx: number]
  selectStep: [stepId: string | null]
}>()

const phaseLabels = [
  { num: 1, label: 'Kurs' },
  { num: 2, label: 'Kapitel' },
  { num: 3, label: 'Content' },
  { num: 4, label: 'Generierung' },
]

const canGoBack = computed(() => props.currentPhase > 1 && props.currentPhase < 4)
const canConfirm = computed(() => {
  if (props.isCreating || props.isChatting) return false
  if (props.currentPhase === 1) return !!props.courseMeta?.title
  if (props.currentPhase === 2) return props.chapters.length > 0
  if (props.currentPhase === 3) return !!props.plan?.phases?.length
  return false
})
</script>

<template>
  <div class="plan-wizard">
    <!-- Phase Indicator -->
    <div class="phase-indicator">
      <div
        v-for="p in phaseLabels"
        :key="p.num"
        class="phase-dot"
        :class="{
          active: p.num === currentPhase,
          completed: p.num < currentPhase,
          future: p.num > currentPhase,
        }"
        @click="p.num < currentPhase ? emit('goBack', p.num as WizardPhase) : undefined"
      >
        <span class="dot-num">{{ p.num < currentPhase ? '✓' : p.num }}</span>
        <span class="dot-label">{{ p.label }}</span>
      </div>
    </div>

    <!-- Phase Content -->
    <div class="phase-content">
      <!-- Phase 1: Kurs-Definition -->
      <PlanCourseCard
        v-if="currentPhase === 1"
        :course-meta="courseMeta"
        :is-creating="isCreating"
        :has-files="hasFiles"
        @generate="(topic, fileIds) => emit('generatePhase1', topic, fileIds)"
      />

      <!-- Phase 2: Kapitelstruktur -->
      <PlanChapterList
        v-else-if="currentPhase === 2"
        :chapters="chapters"
        :is-creating="isCreating"
      />

      <!-- Phase 3: Content-Plan -->
      <PlanModePanel
        v-else-if="currentPhase === 3"
        :plan="plan"
        v-bind="$props"
        @reorder-step="(pi, si, dir) => emit('reorderStep', pi, si, dir)"
        @remove-step="(pi, si) => emit('removeStep', pi, si)"
        @select-step="(id) => emit('selectStep', id)"
      />

      <!-- Phase 4: Ausfuehrung -->
      <PlanModePanel
        v-else-if="currentPhase === 4"
        :plan="plan"
        v-bind="$props"
      />
    </div>

    <!-- Chat (Phase 1-3) -->
    <PlanChat
      v-if="currentPhase < 4 && plan"
      :messages="chatMessages"
      :is-loading="isChatting"
      :current-phase="currentPhase"
      @send="(msg) => emit('sendChat', msg)"
    />

    <!-- Navigation -->
    <div v-if="currentPhase < 4" class="phase-navigation">
      <button
        v-if="canGoBack"
        class="btn-secondary"
        @click="emit('goBack', (currentPhase - 1) as WizardPhase)"
      >
        ← Zurueck
      </button>
      <div class="spacer" />
      <button
        v-if="currentPhase === 4"
        class="btn-primary"
        :disabled="!isApproved"
        @click="emit('execute')"
      >
        Ausfuehren
      </button>
      <button
        v-else
        class="btn-primary"
        :disabled="!canConfirm"
        @click="emit('confirmPhase')"
      >
        {{ isCreating ? 'Generiert...' : 'Bestaetigen →' }}
      </button>
    </div>
  </div>
</template>
```

**Step 2: Styling (im gleichen File, <style scoped>)**

Minimal-Styling fuer Phase-Indicator, Navigation. Details beim Implementieren.

**Step 3: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/panels/PlanPhaseWizard.vue
git commit -m "feat(frontend): add PlanPhaseWizard container component"
```

---

## Task 13: Frontend UI — PlanCourseCard.vue (Phase 1)

**Files:**
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/panels/PlanCourseCard.vue`

**Kontext:** Zeigt die editierbare Kurs-Karte in Phase 1. Enthaelt auch den Thema-Input wenn noch kein Plan existiert.

**Step 1: Komponente erstellen**

Die Komponente hat zwei Zustaende:
1. **Kein Plan:** Zeigt Input-Feld "Worueber soll der Kurs sein?" + "Erstellen"-Button
2. **Plan vorhanden:** Zeigt editierbare Kurs-Karte (Titel, Beschreibung, Zielgruppe, Schwierigkeit)

Props: `courseMeta: CourseMeta | null`, `isCreating: boolean`, `hasFiles: boolean`
Emits: `generate(topic?: string, fileIds?: string[])`

**Step 2: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/panels/PlanCourseCard.vue
git commit -m "feat(frontend): add PlanCourseCard for phase 1 course definition"
```

---

## Task 14: Frontend UI — PlanChapterList.vue (Phase 2)

**Files:**
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/panels/PlanChapterList.vue`

**Kontext:** Zeigt die Kapitelstruktur in Phase 2. Kapitel koennen umsortiert und geloescht werden.

Props: `chapters: ChapterDraft[]`, `isCreating: boolean`
Emits: `reorder(id, direction)`, `remove(id)`, `update(id, data)`

Kapitel werden als nummerierte Liste mit Titel + Beschreibung angezeigt. Hover zeigt Aktions-Buttons (↑ ↓ ✕).

**Step 1: Komponente erstellen**

**Step 2: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/panels/PlanChapterList.vue
git commit -m "feat(frontend): add PlanChapterList for phase 2 chapter structure"
```

---

## Task 15: Frontend UI — PlanChat.vue

**Files:**
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/panels/PlanChat.vue`

**Kontext:** Chat-Bereich im Plan-Tab. Einfacher Chat mit Messages + Input. Kein vollstaendiger ChatPanel — leichtgewichtiger.

Props: `messages: PlanChatMessage[]`, `isLoading: boolean`, `currentPhase: WizardPhase`
Emits: `send(message: string)`

**Step 1: Komponente erstellen**

Minimaler Chat:
- Scrollbare Message-Liste (user = rechts, assistant = links)
- Input-Feld mit Send-Button
- Placeholder-Text abhaengig von Phase ("Beschreibe dein Kursthema...", "Welche Kapitel sollen geaendert werden?", etc.)

**Step 2: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/panels/PlanChat.vue
git commit -m "feat(frontend): add PlanChat component for plan discussion"
```

---

## Task 16: Frontend Glue — PlanTab.vue umbauen

**Files:**
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/tabs/PlanTab.vue` (193 Zeilen)

**Kontext:** Der PlanTab wird umgebaut um den PlanPhaseWizard zu nutzen statt direkt PlanModePanel zu rendern.

**Step 1: Template ersetzen**

Der neue PlanTab rendert `PlanPhaseWizard` und leitet alle Events an `usePlanMode` weiter.

**Wichtig:**
- Die bestehende Plan-History bleibt (fuer aeltere Plans)
- Neuer "Neuen Kurs erstellen"-Button startet den Wizard
- Alter Flow (create/execute ohne Phasen) bleibt als Fallback fuer bestehende Plans

```vue
<script setup lang="ts">
import { inject } from 'vue'
import PlanPhaseWizard from '../panels/PlanPhaseWizard.vue'

const props = defineProps<{ courseId: string }>()

const planMode = inject('planMode')!
const fileUpload = inject('fileUpload', null)

// Bestehende Plans laden
planMode.loadPlanHistory(props.courseId)
</script>

<template>
  <div class="plan-tab">
    <!-- Wizard fuer aktiven Plan -->
    <PlanPhaseWizard
      v-if="planMode.currentPlan.value"
      :current-phase="planMode.currentPhase.value"
      :plan="planMode.currentPlan.value"
      :course-meta="planMode.courseMeta.value"
      :chapters="planMode.chapters.value"
      :chat-messages="planMode.chatMessages.value"
      :is-creating="planMode.isCreating.value"
      :is-executing="planMode.isExecuting.value"
      :is-chatting="planMode.isChatting.value"
      :has-files="!!(fileUpload?.completedFiles?.length)"
      :is-draft="planMode.isDraft.value"
      :is-approved="planMode.isApproved.value"
      :is-paused="planMode.isPaused.value"
      :is-completed="planMode.isCompleted.value"
      :is-failed="planMode.isFailed.value"
      :total-steps="planMode.totalSteps.value"
      :completed-steps="planMode.completedSteps.value"
      :failed-steps="planMode.failedSteps.value"
      @generate-phase1="planMode.generatePhase1"
      @confirm-phase="planMode.confirmPhase"
      @go-back="planMode.goBackToPhase"
      @send-chat="planMode.sendPlanChatMessage"
      @execute="planMode.execute"
      @pause="planMode.pausePlan"
      @resume="planMode.resumePlan"
      @discard="planMode.clearPlan"
      @reorder-step="planMode.reorderStep"
      @remove-step="planMode.removeStep"
      @select-step="planMode.selectStep"
    />

    <!-- Empty State: Neuen Plan starten -->
    <div v-else class="plan-empty">
      <PlanCourseCard
        :course-meta="null"
        :is-creating="planMode.isCreating.value"
        :has-files="!!(fileUpload?.completedFiles?.length)"
        @generate="planMode.generatePhase1"
      />
    </div>
  </div>
</template>
```

**Step 2: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/tabs/PlanTab.vue
git commit -m "feat(frontend): rebuild PlanTab to use PlanPhaseWizard"
```

---

## Task 17: i18n — Neue Keys fuer Plan-Wizard

**Files:**
- Modify: `frontend/src/infrastructure/i18n/locales/de/panel/aiEditor/unified.json`
- Modify: `frontend/src/infrastructure/i18n/locales/en/panel/aiEditor/unified.json`
- Modify: `frontend/src/infrastructure/i18n/locales/pl/panel/aiEditor/unified.json`

**Step 1: Keys in ALLEN 3 Sprachen hinzufuegen**

Neue Keys unter `planWizard`:

```json
{
  "planWizard": {
    "phase1Title": "Kurs-Definition",
    "phase2Title": "Kapitelstruktur",
    "phase3Title": "Content-Planung",
    "phase4Title": "Generierung",
    "topicPlaceholder": "Worüber soll der Kurs sein? (z.B. 'CompTIA Network+')",
    "createFromFiles": "Aus Datei erstellen",
    "createManual": "Manuell erstellen",
    "confirm": "Bestätigen",
    "back": "Zurück",
    "generating": "Wird generiert...",
    "chatPlaceholder1": "Beschreibe dein Kursthema oder stelle Fragen...",
    "chatPlaceholder2": "Kapitel ändern, hinzufügen oder umordnen...",
    "chatPlaceholder3": "Lektionen oder Lernmethoden anpassen...",
    "courseTitle": "Kurstitel",
    "courseDescription": "Beschreibung",
    "targetAudience": "Zielgruppe",
    "difficulty": "Schwierigkeit",
    "chapterCount": "{count} Kapitel",
    "readyToExecute": "Plan bereit zur Ausführung",
    "executionComplete": "Kurs als Draft erstellt",
    "openInEditor": "Im Manual Editor öffnen",
    "tokenWarning": "Dieser Plan kostet ca. {tokens} Tokens. Fortfahren?"
  }
}
```

**Step 2: EN + PL Uebersetzungen**

Gleiche Keys mit englischen bzw. polnischen Uebersetzungen.

**Step 3: Commit**

```bash
git add frontend/src/infrastructure/i18n/locales/de/panel/aiEditor/unified.json \
        frontend/src/infrastructure/i18n/locales/en/panel/aiEditor/unified.json \
        frontend/src/infrastructure/i18n/locales/pl/panel/aiEditor/unified.json
git commit -m "feat(i18n): add plan wizard translations (de, en, pl)"
```

---

## Task 18: Integration — End-to-End Smoke Test

**Step 1: Backend starten und pruefen**

```bash
cd backend && python -c "from app import create_app; create_app()"
```

Erwartung: Keine Import-Fehler.

**Step 2: Frontend Build pruefen**

```bash
cd frontend && npm run build
```

Erwartung: Keine TypeScript-Fehler.

**Step 3: Manueller E2E-Test**

1. Einloggen als `admin@lsx.de`
2. AI Editor oeffnen
3. Kurs waehlen oder neuen Kurs erstellen
4. Plan-Tab oeffnen
5. Thema eingeben → Phase 1 generieren
6. Kurs-Karte reviewen → Bestaetigen
7. Kapitelstruktur reviewen → per Chat anpassen → Bestaetigen
8. Content-Plan reviewen → Bestaetigen
9. Execution starten → Fortschritt verfolgen
10. "Im Manual Editor oeffnen" klicken

**Step 4: Commit**

```bash
git add -A
git commit -m "feat(ai-editor): complete plan wizard integration"
```

---

## Zusammenfassung

| Task | Layer | Dateien | Geschaetzter Aufwand |
|------|-------|---------|---------------------|
| 1 | Domain | Value Objects | Klein |
| 2 | Domain | Port | Klein |
| 3 | Infrastructure | Repository + Migration | Mittel |
| 4 | Infrastructure | Prompts | Mittel |
| 5 | Infrastructure | AI-Adapter | Mittel |
| 6 | Application | PlanService erweitern | Gross |
| 7 | Application | PlanService splitten (G01) | Klein |
| 8 | API | Neue Endpoints | Mittel |
| 9 | Frontend | Types | Klein |
| 10 | Frontend | API Client | Klein |
| 11 | Frontend | usePlanMode Composable | Gross |
| 12 | Frontend | PlanPhaseWizard.vue | Mittel |
| 13 | Frontend | PlanCourseCard.vue | Mittel |
| 14 | Frontend | PlanChapterList.vue | Mittel |
| 15 | Frontend | PlanChat.vue | Mittel |
| 16 | Frontend | PlanTab.vue umbauen | Mittel |
| 17 | i18n | 3 Sprach-Dateien | Klein |
| 18 | Integration | Smoke Test | Mittel |

**Reihenfolge:** Domain → Infrastructure → Application → API → Frontend Types → Frontend API → Frontend State → Frontend UI → i18n → Test
