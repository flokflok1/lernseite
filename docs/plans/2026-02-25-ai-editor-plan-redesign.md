# AI Editor Plan-Tab Redesign

**Datum:** 2026-02-25
**Status:** APPROVED
**Autor:** Pascal + Claude

---

## Ziel

Den Plan-Tab im AI Editor grundlegend neugestalten: Von einem Ein-Schuss-Plangenerator zu einem **4-Phasen-Wizard mit integriertem Chat**, der qualitativ hochwertige Kurse erstellt.

## Probleme mit dem aktuellen System

1. **Kein Kursname/Beschreibung** — Kurs bleibt "Neuer KI Kurs"
2. **Keine Diskussion** — Plan kann nicht per Chat angepasst werden
3. **Fehlende Theorie-Sheets** — Weder Kapitel- noch Lektions-Theorie wird generiert
4. **Qualitaet** — Ein-Schuss-Generierung ohne progressiven Kontext fuehrt zu oberflaechlichen Ergebnissen

## Design: 4-Phasen-Wizard mit Plan-Chat

### Ueberblick

```
Phase 1: Kurs-Definition    → Kursname, Beschreibung, Zielgruppe
Phase 2: Kapitelstruktur    → Kapitel mit Titeln und Beschreibungen
Phase 3: Content-Planung    → Lektionen, Theorie-Sheets, LMs, Pruefungen
Phase 4: Ausfuehrung        → Batch-Execution aller Steps → Draft
```

Jede Phase hat:
- KI-Generierung basierend auf vorherigen Phasen (progressiver Kontext)
- Integrierten Chat fuer Aenderungen und Diskussion
- Bestaetigung bevor es weitergeht

### Phase 1: Kurs-Definition

**Zwei Einstiegspfade:**
- **Thema im Kopf:** User tippt Thema → KI generiert Kurs-Definition
- **Datei-Upload:** KI erkennt vorhandene Dateien → leitet Definition ab

**KI generiert:**
- Kursname
- Kursbeschreibung (2-3 Saetze)
- Zielgruppe
- Schwierigkeitsgrad (beginner/intermediate/advanced)
- Sprache

**UI:** Editierbare Kurs-Karte + Chat-Bereich
**Chat-Beispiele:** "Mach die Beschreibung technischer", "Zielgruppe: Fortgeschrittene"

### Phase 2: Kapitelstruktur

**Input:** Bestaetigte Kurs-Definition aus Phase 1 (+ optional: Datei-Text)

**KI generiert:**
- N Kapitel mit Titeln und Kurzbeschreibungen
- Logische Reihenfolge

**UI:** Sortierbare Kapitelliste (Drag & Drop) + Chat-Bereich
**Chat-Beispiele:** "Fuege ein Kapitel ueber VLANs hinzu", "Teile Kapitel 3 auf"

### Phase 3: Content-Planung

**Input:** Bestaetigte Kurs-Definition + Kapitelstruktur

**KI generiert pro Kapitel:**
- Kapitel-Theorie (Ueberblick, 2-3 Seiten)
- N Lektionen mit:
  - Lektions-Theorie (Detail)
  - 2-3 Lernmethoden (KI waehlt basierend auf Inhalt)
- Kapitel-Pruefung (chapter_exam)

**Lernmethoden-Zuordnung (KI-gesteuert):**

| Inhaltstyp | Empfohlene LMs |
|-----------|---------------|
| Konzepte/Theorie | deep_explanation + flashcards |
| Prozesse/Ablaeufe | step_by_step + cloze_test |
| Praxis/Anwendung | example_scenario + multi_step |
| Berechnung | math_interactive + step_by_step |
| Begriffe/Definitionen | flashcards + true_false + drag_and_drop |
| Konfiguration/Setup | example_scenario + hands_on_lab |

**Theorie-Strategie:**
- Jedes Kapitel: eine Kapitel-Theorie (Ueberblick)
- Jede Lektion: eine Lektions-Theorie (Detail)

**UI:** Aufklappbare Kapitel mit Lektionen + LMs + Chat-Bereich
**Chat-Beispiele:** "Bei Subnetting lieber Step-by-Step", "Mehr Praxisuebungen in Kapitel 4"

### Phase 4: Ausfuehrung

**Input:** Bestaetigter Content-Plan

**Ablauf:**
1. Kurs-Metadaten speichern (Kursname, Beschreibung updaten)
2. Batch-Execution aller Steps (Theorie, LMs, Pruefungen)
3. Live-Fortschritt mit Polling (3s)
4. Alles als Draft gespeichert

**Nach Abschluss:**
- Hinweis: "Kurs als Draft erstellt"
- Button: "Im Manual Editor oeffnen"

## Technische Architektur (DDD-konform)

### DDD Layer-Zuordnung

```
Domain Layer (app/domain/ai/)
├── models/plan.py              → PlanEntity, CourseMeta, ChapterDraft (Value Objects)
├── configuration/skills.py     → Bestehend (Skill-Definitionen)
└── ports/plan_generator.py     → PlanGeneratorPort (ABC fuer AI-Aufrufe)

Application Layer (app/application/services/ai/)
├── plan_service.py             → PlanService (Orchestrierung, Phase-Transitions)
└── plan_chat_service.py        → PlanChatService (Chat + Plan-Patch Logik)

Infrastructure Layer (app/infrastructure/)
├── persistence/repositories/ai/
│   └── content_plans.py        → ContentPlanRepository (erweitern)
└── ai/
    └── plan_generator.py       → PlanGeneratorAdapter (implementiert Port)

API Layer (app/api/v1/panel/editor/ai/)
└── plans.py                    → Routes + Validation (erweitern)
```

### Domain Layer: Neue Value Objects

```python
# app/domain/ai/models/plan.py
@dataclass(frozen=True)
class CourseMeta:
    title: str
    description: str
    target_audience: str
    difficulty: str   # 'beginner' | 'intermediate' | 'advanced'
    language: str     # 'de' | 'en' | 'pl'

@dataclass(frozen=True)
class ChapterDraft:
    id: str
    title: str
    description: str
    order: int
```

### Domain Layer: Port (Interface)

```python
# app/domain/ports/plan_generator.py
from abc import ABC, abstractmethod

class PlanGeneratorPort(ABC):
    @abstractmethod
    def generate_course_definition(self, topic: str, file_text: str | None) -> dict: ...

    @abstractmethod
    def generate_chapter_structure(self, course_meta: dict, file_text: str | None) -> dict: ...

    @abstractmethod
    def generate_content_plan(self, course_meta: dict, chapters: list) -> dict: ...

    @abstractmethod
    def chat_about_plan(self, plan_data: dict, message: str, phase: int) -> dict: ...
```

### Application Layer: PlanService (Orchestrierung)

```python
# app/application/services/ai/plan_service.py — erweitert
class PlanService:
    # Phase 1
    generate_course_definition(topic_or_file_text, file_ids?)
    → { title, description, target_audience, difficulty, language }

    # Phase 2
    generate_chapter_structure(plan_id)
    → { chapters: [{ id, title, description, order }] }

    # Phase 3
    generate_content_plan(plan_id)
    → { phases: [{ chapter, lessons, theory_sheets, exam }] }

    # Plan-Chat (alle Phasen)
    chat_about_plan(plan_id, message)
    → { assistant_message, plan_patch? }

    # Bestehend: execute, approve, pause, resume
```

### Infrastructure Layer: AI-Adapter

```python
# app/infrastructure/ai/plan_generator.py
class PlanGeneratorAdapter(PlanGeneratorPort):
    # Implementiert alle Port-Methoden mit AIAdapter
    # Baut Prompts, ruft AI-Provider auf, parst JSON
    # Keine Business-Logik — nur AI-Kommunikation
```

### API Layer: Neue Endpoints

```
POST /plans/phase1          → generate_course_definition
POST /plans/phase2          → generate_chapter_structure
POST /plans/phase3          → generate_content_plan
POST /plans/<id>/chat       → chat_about_plan
POST /plans/<id>/execute    → execute_plan (bestehend)
```

**API-Regeln:** Nur Validation + Auth-Checks + DTO-Mapping. Keine Business-Logik.

### Frontend: Typ-Erweiterungen

```typescript
interface CourseMeta {
  title: string
  description: string
  target_audience: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  language: 'de' | 'en' | 'pl'
}

interface ChapterDraft {
  id: string
  title: string
  description: string
  order: number
}

// ContentPlan erweitert:
interface ContentPlan {
  plan_id: string
  course_id: string
  current_phase: 1 | 2 | 3 | 4     // NEU
  course_meta: CourseMeta            // NEU
  chapters: ChapterDraft[]           // NEU
  phases: PlanPhase[]
  chat_history: PlanChatMessage[]    // NEU
  // ... rest wie bisher
}
```

### Frontend: Composable-Aenderungen

```typescript
// usePlanMode.ts erweitert:
+ currentPhase: ref<1|2|3|4>
+ courseMeta: ref<CourseMeta>
+ chapters: ref<ChapterDraft[]>
+ chatMessages: ref<PlanChatMessage[]>
+ sendPlanChat(message: string): Promise<void>
+ confirmPhase(): Promise<void>
+ goBackToPhase(n: number): void
+ generatePhase1(topic?: string): Promise<void>
+ generatePhase2(): Promise<void>
+ generatePhase3(): Promise<void>
```

### Frontend: Komponenten

| Komponente | Status | Zweck |
|-----------|--------|-------|
| PlanTab.vue | Umbauen | Wizard-Phasen statt direktem PlanModePanel |
| usePlanMode.ts | Umbauen | Phasen-State, courseMeta, chapters, Chat |
| PlanModePanel.vue | Wiederverwenden | Phase 3+4 Darstellung |
| PlanEmptyState.vue | Umbauen | Phase 1 (Thema-Input / Datei-Erkennung) |
| StepDetailPanel.vue | Bleibt | Step-Details in Phase 3 |
| plan.types.ts | Erweitern | CourseMeta, ChapterDraft, currentPhase |
| plan_service.py | Umbauen | 3 Generierungs-Methoden + Chat |
| plans.py (API) | Erweitern | Neue Endpoints |
| unified.api.ts | Erweitern | Neue API-Calls |
| **NEU:** PlanPhaseWizard.vue | Neu | Wizard-Container mit Phase-Navigation |
| **NEU:** PlanCourseCard.vue | Neu | Editierbare Kurs-Karte (Phase 1) |
| **NEU:** PlanChapterList.vue | Neu | Drag-sortierbare Kapitelliste (Phase 2) |
| **NEU:** PlanChat.vue | Neu | Chat-Bereich im Plan-Tab |

## Fehlerbehandlung

| Situation | Verhalten |
|-----------|----------|
| Schlechter Kursname | Inline-Edit oder Chat-Anpassung |
| Falsche LM-Zuweisung | Chat: "Lieber Flashcards statt Quiz" |
| Step-Execution fehlgeschlagen | Als failed markieren, Rest weitermachen |
| Zurueck zu frueherer Phase | Warnung: Aenderungen an spaeteren Phasen gehen verloren |
| Token-Budget | Warnung vor Execution mit geschaetzten Kosten |
| Bestehender Kurs | Erkennung + Erweiterung statt Ueberschreibung |

## Finalisierung

- Alles wird als **Draft** in der DB gespeichert
- Kurs ist nicht veroeffentlicht
- User kann im Manual Editor nachbearbeiten
- Button "Im Manual Editor oeffnen" nach Abschluss
