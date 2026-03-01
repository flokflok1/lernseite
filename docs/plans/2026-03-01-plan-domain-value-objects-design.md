# Plan Domain Value Objects — Design

**Datum:** 2026-03-01
**Status:** APPROVED
**Ziel:** Typ-sichere Domain Value Objects fuer den Plan-Wizard, die rohe Dicts an den Service-Boundaries ersetzen.

---

## Problem

`PlanWizardService` und `PlanGeneratorPort` arbeiten komplett mit `dict[str, Any]`. Keine Validierung, keine Type-Safety, keine IDE-Unterstuetzung. Verstoesst gegen DDD-Regel: Domain-Layer soll Entities/Value Objects definieren.

## Loesung: Boundaries-Only Value Objects

Value Objects werden an den **Service-Boundaries** genutzt — nicht ueberall:

```
API (dict) -> Service (dict -> ValueObject -> Logik -> dict) -> Repository (dict)
                        |
              PlanGeneratorPort (ValueObject)
```

Repository und API bleiben unveraendert (arbeiten weiter mit Dicts).

## Value Objects

### CourseMeta (frozen dataclass)

```python
@dataclass(frozen=True)
class CourseMeta:
    title: str
    description: str
    target_audience: str
    difficulty: str          # beginner | intermediate | advanced | expert
    language: str = 'de'
    subtitle: str = ''
    prerequisites: list[str] = field(default_factory=list)
    estimated_duration_hours: int = 0
    tags: list[str] = field(default_factory=list)
```

Validierung: difficulty in VALID_DIFFICULTIES, title nicht leer.

### ChapterDraft (frozen dataclass)

```python
@dataclass(frozen=True)
class ChapterDraft:
    id: str
    title: str
    description: str
    order: int
    estimated_lessons: int = 0
    learning_goals: list[str] = field(default_factory=list)
```

Validierung: order > 0.

### PlanChatMessage (frozen dataclass)

```python
@dataclass(frozen=True)
class PlanChatMessage:
    role: str                # user | assistant
    content: str
    timestamp: str = ''
```

Validierung: role in ('user', 'assistant').

### PlanData (Container)

```python
@dataclass
class PlanData:
    course_meta: CourseMeta
    chapters: list[ChapterDraft]
    phases: list[dict]       # Phases bleiben dicts (zu komplex, wenig Gewinn)
```

Factory: `PlanData.from_dict(raw)` und `.to_dict()`.

## Aenderungen

| Datei | Aenderung |
|-------|-----------|
| `domain/ai/models/plan.py` | NEU — 4 Value Objects |
| `domain/ai/models/__init__.py` | Barrel Export |
| `domain/ports/plan_generator.py` | Type Hints: dict -> CourseMeta/ChapterDraft |
| `application/services/ai/plan/plan_service_part2.py` | from_dict/to_dict an Boundaries |
| `infrastructure/ai/plan/plan_generator.py` | Return types anpassen |

## Nicht betroffen

- Frontend (TypeScript-Interfaces bleiben)
- API-Endpoints (JSON rein/raus)
- Repository (arbeitet weiter mit Dicts)
- Database Schema (keine Aenderungen)
