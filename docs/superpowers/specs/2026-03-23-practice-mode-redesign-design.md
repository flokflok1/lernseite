# Freies Ueben - Practice Mode Redesign

**Datum:** 2026-03-23
**Status:** APPROVED
**Ziel:** Den "Freies Ueben"-Modus zum vollwertigen intelligenten Pruefungstrainer ausbauen

---

## 1. Uebersicht

Der statische "Freies Ueben"-Button (10 Fragen, keine Optionen) wird zu einem konfigurierbaren
Uebungssystem mit 5 Dimensionen, 3 Lernmodi und 4 intelligenten Features.

### 5 Konfigurations-Dimensionen

| Dimension | Optionen |
|-----------|----------|
| Fragenanzahl | 10, 20, 40, 100, Alle, Endlos |
| Reihenfolge | Sequentiell (1.1->1.2->...) oder Gemischt |
| Lernmodus | Entdecken, Festigen, Pruefungsreif (nur bei Gemischt) |
| Zeitlimit | Ohne, 30min, 45min, 90min |
| Filter | Optional: bestimmte Pruefungen / Themen |

### 3 Lernmodi (nur bei Gemischt)

- **Entdecken** - 70% ungesehen, 20% Review, 10% schwach. Gleichmaessige Themen-Verteilung.
- **Festigen** - 50% schwach, 30% Review, 20% ungesehen. Schwache Themen leicht uebergewichtet.
- **Pruefungsreif** - Gewichtung nach Pruefungswahrscheinlichkeit x Schwaeche-Score.

### 4 Intelligente Features (immer aktiv)

1. **Spaced Repetition** - Falsche Fragen kommen nach 3->10->30 Fragen wieder
2. **Adaptive Schwierigkeit** - 5x richtig -> schwerer, 3x falsch -> leichter
3. **Themen-Streak-Erkennung** - 3x falsch in einem Thema -> Angebot fuer Extra-Uebung
4. **Session-Zusammenfassung** - Themen-Aufschluesselung, Staerken/Schwaechen, Empfehlung

---

## 2. DDD-Layer-Architektur

### 2.1 Domain Layer (app/domain/)

**Neue Datei: `app/domain/models/practice_session.py`** (~60 Zeilen)

Value Objects und Enums fuer die Practice-Konfiguration:

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional

class PracticeMode(Enum):
    DISCOVER = "discover"
    STRENGTHEN = "strengthen"
    EXAM_READY = "exam_ready"

class PracticeOrder(Enum):
    SEQUENTIAL = "sequential"
    MIXED = "mixed"

class QuestionBucket(Enum):
    UNSEEN = "unseen"
    WEAK = "weak"
    REVIEW = "review"
    SPACED_REPEAT = "spaced_repeat"

class DifficultyShift(Enum):
    UP = "up"
    DOWN = "down"
    STAY = "stay"

@dataclass(frozen=True)
class SpacedRepetitionEntry:
    question_id: str
    wrong_count: int
    next_appearance_offset: int  # 3 -> 10 -> 30

@dataclass(frozen=True)
class StreakAlert:
    topic: str
    consecutive_wrong: int
    suggested_extra_count: int  # default 5

@dataclass(frozen=True)
class PracticeConfig:
    mode: PracticeMode
    order: PracticeOrder
    question_count: Optional[int] = None  # None = Endlos
    time_limit_minutes: Optional[int] = None
    exam_filter: list[str] = field(default_factory=list)
    topic_filter: list[str] = field(default_factory=list)
```

Keine Business-Logik. Keine Flask/DB/Infrastructure-Imports.

### 2.2 Application Layer (app/application/services/exams/)

#### Erweitern: `rotation_service.py` (+170 Zeilen -> ~350 gesamt)

Neue Methode neben der bestehenden `generate_adaptive_exam()`:

```
generate_practice_session(user_id, config: PracticeConfig) -> dict
    |-- _resolve_bucket_ratios(mode: PracticeMode) -> dict
    |       DISCOVER:   {unseen: 0.7, review: 0.2, weak: 0.1}
    |       STRENGTHEN: {weak: 0.5, review: 0.3, unseen: 0.2}
    |       EXAM_READY: dynamic (see below)
    |
    |-- _apply_topic_balance(questions, mode, topic_stats) -> list
    |       DISCOVER/STRENGTHEN: equal distribution across topics
    |       EXAM_READY: weighted by prognosis * weakness
    |
    |-- _apply_exam_probability_weight(questions, prognosis) -> list
    |       Only for EXAM_READY mode
    |       Weight = topic_probability * (1 - user_correct_rate)
    |
    |-- _order_questions(questions, order: PracticeOrder) -> list
    |       SEQUENTIAL: ORDER BY exam.year DESC, exam.season, question_number
    |       MIXED: random.shuffle with topic-interleave
    |
    |-- _apply_adaptive_difficulty(questions, user_recent) -> list
    |       Adjusts question selection based on recent streak
```

Bestehende `generate_adaptive_exam()` bleibt unveraendert (kein Breaking Change).

**EXAM_READY Gewichtung:**
```
topic_weight = prognosis_probability * (1.0 + weakness_score)
weakness_score = 1.0 - (times_correct / max(times_seen, 1))
```
Topics mit hoher Pruefungswahrscheinlichkeit UND niedrigem Wissen bekommen das meiste Gewicht.

#### Neue Datei: `app/application/services/exams/practice_intelligence.py` (~200 Zeilen)

4 Engines fuer die intelligenten Features:

```
class SpacedRepetitionEngine:
    INTERVALS = [3, 10, 30, 75]  # Fibonacci-aehnlich

    schedule_repeat(question_id, wrong_count) -> int
        # Gibt next_appearance_offset zurueck basierend auf wrong_count
        # wrong_count=1 -> 3, wrong_count=2 -> 10, etc.

    get_due_repeats(spaced_queue, current_position) -> list[str]
        # Welche Fragen jetzt faellig sind

class AdaptiveDifficultyEngine:
    check_adjustment(recent_results: list[bool]) -> DifficultyShift
        # Letzte 5-8 Antworten pruefen
        # 5+ richtig hintereinander -> UP (hoehere Punkte-Fragen)
        # 3+ falsch hintereinander -> DOWN (niedrigere Punkte-Fragen)
        # Sonst -> STAY

    apply_to_query(shift: DifficultyShift, avg_points: float) -> tuple[float, float]
        # Gibt (min_points, max_points) Range zurueck fuer naechste Frage
        # UP: avg_points * 1.3 bis max
        # DOWN: 0 bis avg_points * 0.7

class StreakDetector:
    check_topic_streak(answers_by_topic: dict) -> Optional[StreakAlert]
        # Pro Thema: letzte N Antworten pruefen
        # 3+ falsch hintereinander -> StreakAlert(topic, count, suggested=5)

class SessionSummaryBuilder:
    build_summary(attempt_id, all_answers) -> dict
        # Returns structured data (NO hardcoded language strings):
        #   topics: [{name, total, correct, percentage}]
        #   strongest_topic: str  (topic key)
        #   weakest_topic: str    (topic key)
        #   recommendation: {     (structured, frontend renders via i18n)
        #       "type": "strengthen_focus" | "discover_more" | "exam_ready",
        #       "topic": "Netzwerktechnik"
        #   }
        #   overall_score: float
        #   time_spent: int (seconds)
```

### 2.3 Infrastructure Layer (app/infrastructure/persistence/repositories/exams/)

**ACHTUNG Zeilenstaende:** `trainer.py` (Part 1) ist bei ~452 Zeilen — KEINE neuen Methoden dort!
`trainer_part2.py` ist bei ~287 Zeilen. Neue Methoden kommen alle in Part 2.
Falls Part 2 nach Erweiterung >450 Zeilen: sofort `trainer_part3.py` + Barrel Export.

#### Erweitern: `trainer_part2.py` (+100 Zeilen -> ~387 gesamt)

Neue Query-Methoden im bestehenden `ExamTrainerRepository`:

```
find_questions_sequential(exam_filter, topic_filter, offset, limit)
    # Alle Fragen sortiert nach Pruefung + Fragennummer
    # WHERE e.analysis_status = 'ready' AND e.published = true
    # Optional: AND e.exam_id IN (exam_filter)
    # Optional: AND topic = ANY(topic_filter)
    # ORDER BY e.year DESC, e.season DESC, eq.question_number ASC
    # OFFSET + LIMIT fuer Batch-Loading

find_questions_by_topic_balanced(user_id, topic_weights: dict, limit)
    # Pro Thema: anteilig Fragen holen (gewichtet nach topic_weights)
    # Innerhalb jedes Themas: Bucket-Logik (unseen/weak/review)
    # Returns gemischte Liste mit Topic-Balance

find_topic_prognosis_weights()
    # SELECT topic, COUNT(DISTINCT exam_id)::float / total_exams AS probability
    # FROM assessments.exam_questions eq
    # JOIN assessments.exams e ON ...
    # WHERE e.analysis_status = 'ready' AND e.published = true
    # GROUP BY topic

find_user_topic_weakness(user_id)
    # SELECT eq.topics[1] AS topic,
    #        1.0 - (SUM(uqs.times_correct)::float / GREATEST(SUM(uqs.times_seen), 1))
    #        AS weakness_score
    # FROM assessments.exam_questions eq
    # LEFT JOIN assessments.user_question_stats uqs ON ...
    # GROUP BY topic

count_available_questions(exam_filter, topic_filter)
    # COUNT(*) mit optionalen Filtern, fuer "Alle X Fragen" Anzeige
```

Falls `trainer_part2.py` ueber 500 Zeilen kommt -> `trainer_part3.py` + Barrel Export in `__init__.py`.

### 2.4 API Layer (app/api/v1/panel/user/exams/)

**ACHTUNG:** `trainer_part2.py` (API) ist bereits bei ~435 Zeilen. Neue Endpoints MUESSEN
in eine neue Datei: `app/api/v1/panel/user/exams/practice.py` mit eigenem Blueprint-Fragment.
Registrierung via `register_practice_routes(bp)` aufgerufen aus `trainer.py`.

#### Neue Datei: `app/api/v1/panel/user/exams/practice.py` (~120 Zeilen)

**Neuer Endpoint: Practice Session starten**
```
POST /user/exam-trainer/practice-session
Body:
{
    "mode": "discover" | "strengthen" | "exam_ready",
    "order": "sequential" | "mixed",
    "question_count": 20 | null,         // null = endlos
    "time_limit_minutes": 0 | null,
    "exam_filter": ["uuid-1", "uuid-2"], // optional
    "topic_filter": ["Netzwerktechnik"]  // optional
}
Response 200:
{
    "success": true,
    "attempt_id": "uuid",
    "questions": [...],           // Erste Batch (max 50)
    "total_available": 409,
    "has_more": true,             // true bei Endlos/Alle wenn mehr da
    "config": { mode, order, ... }
}
```

**Neuer Endpoint: Naechste Batch laden (fuer Endlos/Alle)**
```
POST /user/exam-trainer/practice-session/<attempt_id>/next-batch
Body:
{
    "recent_results": [           // Fuer Spaced Repetition + Adaptive
        {"question_id": "...", "correct": true},
        {"question_id": "...", "correct": false}
    ]
}
Response 200:
{
    "success": true,
    "questions": [...],           // Naechste Batch (max 50)
    "has_more": true,
    "spaced_repeats": ["q-id-1"], // Fragen die jetzt wiederholt werden
    "streak_alert": null | {      // Wenn Themen-Streak erkannt
        "topic": "Netzwerktechnik",
        "consecutive_wrong": 3,
        "suggested_extra": 5
    },
    "difficulty_shift": "up" | "down" | "stay"
}
```

**Neuer Endpoint: Session-Zusammenfassung**
```
GET /user/exam-trainer/practice-session/<attempt_id>/summary
Response 200:
{
    "success": true,
    "summary": {
        "total_questions": 40,
        "correct": 28,
        "overall_score": 70.0,
        "time_spent_seconds": 2700,
        "topics": [
            {"name": "Netzwerktechnik", "total": 8, "correct": 5, "pct": 62.5},
            {"name": "Datenbanken", "total": 6, "correct": 6, "pct": 100.0},
            ...
        ],
        "strongest_topic": "Datenbanken",
        "weakest_topic": "Recht & Gesetz",
        "recommendation": {
            "type": "strengthen_focus",
            "topic": "Recht & Gesetz"
        }
    }
}
```

Bestehende Endpoints (`/generate-exam`, `/start-exam`, etc.) bleiben unveraendert.

### 2.5 Frontend (src/presentation/components/panel/user/exam-trainer/)

#### Neue Datei: `PracticeConfigPanel.vue` (~150 Zeilen)

Aufklappbares Konfigurations-Panel das den alten "Freies Ueben"-Button ersetzt:

```
Freies Ueben
+-- Fragenanzahl: [10] [20] [40] [100] [Alle (409)] [Endlos]
+-- Reihenfolge:  [Sequentiell] [Gemischt]
+-- Lernmodus:    [Entdecken] [Festigen] [Pruefungsreif]  <- nur bei Gemischt sichtbar
+-- Zeitlimit:    [Ohne] [30m] [45m] [90m]
+-- Filter:       [Alle Pruefungen v] [Alle Themen v]     <- aufklappbar
+-- [Uebung starten]
```

Emits: `start-practice(config: PracticeConfig)`
Props: `totalQuestions: number` (fuer "Alle (409)" Label)

#### Neue Datei: `SessionSummary.vue` (~200 Zeilen)

Wird nach Session-Ende angezeigt statt direkt zum Dashboard zurueckzukehren:

- Balkendiagramm pro Thema (correct/total)
- Staerkstes/Schwaechstes Thema hervorgehoben
- Gesamtscore + Zeit
- Empfehlung als CTA-Button: "Festigen mit Fokus X starten"
- Button: "Zurueck zum Dashboard"

#### Erweitern: `ExamTrainer.vue` (+30 Zeilen)

- Import PracticeConfigPanel
- Ersetze den statischen "practice" examMode-Eintrag
- Neuer Handler `onStartPractice(config)` der den neuen API-Endpoint aufruft
- Nach Session-Ende: SessionSummary anzeigen statt direkt Dashboard

#### Erweitern: `SimulationMode.vue` (+50 Zeilen)

- **Batch-Loading**: Wenn `questions.length - currentIndex < 5` und `hasMore` -> naechsten Batch laden
- **Streak-Alert**: Toast/Banner wenn Backend `streak_alert` zurueckgibt
  - "3x falsch bei Netzwerktechnik - 5 Extra-Fragen dazu?" [Ja] [Nein]
- **Difficulty-Indikator**: Dezenter Badge "Schwierigkeit +/-" (optional)
- **Spaced Repeat Marker**: Kleine Markierung wenn eine Frage eine Wiederholung ist

#### Neue Datei: `practice.api.ts` (~80 Zeilen)

Eigene API-Datei statt `trainer.api.ts` zu erweitern (bereits bei ~360 Zeilen):

```typescript
// Interfaces
interface PracticeSessionConfig { mode, order, question_count, ... }
interface PracticeSessionResponse { attempt_id, questions, total_available, has_more, config }
interface BatchResponse { questions, has_more, spaced_repeats, streak_alert, difficulty_shift }
interface SessionSummary { total_questions, correct, overall_score, topics, recommendation }

// API functions
practiceStartSession(config: PracticeSessionConfig): Promise<PracticeSessionResponse>
practiceLoadNextBatch(attemptId: string, recentResults: AnswerResult[]): Promise<BatchResponse>
practiceGetSummary(attemptId: string): Promise<SessionSummary>
```

Re-export via `src/infrastructure/api/clients/panel/user/exams/index.ts`.

---

## 3. Datei-Uebersicht

| Aktion | Datei | Aktuell | +Zeilen | Gesamt |
|--------|-------|---------|---------|--------|
| NEU | `app/domain/models/practice_session.py` | 0 | 60 | 60 |
| NEU | `app/application/services/exams/practice_intelligence.py` | 0 | 200 | 200 |
| ERWEITERN | `app/application/services/exams/rotation_service.py` | ~181 | +170 | ~350 |
| ERWEITERN | `app/infrastructure/.../exams/trainer_part2.py` | ~287 | +100 | ~387 |
| NEU | `app/api/v1/panel/user/exams/practice.py` | 0 | 120 | 120 |
| NEU | `src/.../exam-trainer/PracticeConfigPanel.vue` | 0 | 150 | 150 |
| NEU | `src/.../exam-trainer/SessionSummary.vue` | 0 | 200 | 200 |
| ERWEITERN | `src/.../exam-trainer/ExamTrainer.vue` | ~300 | +30 | ~330 |
| ERWEITERN | `src/.../exam-trainer/SimulationMode.vue` | ~350 | +50 | ~400 |
| NEU | `src/.../api/.../practice.api.ts` | 0 | 80 | 80 |

Dateien die NICHT erweitert werden duerfen (zu voll):
- `app/infrastructure/.../exams/trainer.py` (Part 1): ~452 Zeilen
- `app/api/v1/panel/user/exams/trainer_part2.py`: ~435 Zeilen
- `src/.../api/.../trainer.api.ts`: ~360 Zeilen

Barrel Exports aktualisieren:
- `app/api/v1/panel/user/exams/__init__.py` -> `register_practice_routes` registrieren
- `src/.../exam-trainer/index.ts` -> `PracticeConfigPanel` + `SessionSummary` exportieren
- `src/.../api/.../exams/index.ts` -> `practice.api.ts` re-exportieren

Keine Datei ueber 500 Zeilen. Keine Duplikate. Keine Breaking Changes an bestehenden Endpoints.

---

## 4. i18n Keys (PFLICHT: de/en/pl)

Namespace: `panel.examTrainer.practice.*`

```
# Modi
panel.examTrainer.practice.modeDiscover       = "Entdecken" / "Discover" / "Odkrywaj"
panel.examTrainer.practice.modeStrengthen     = "Festigen" / "Strengthen" / "Utrwalaj"
panel.examTrainer.practice.modeExamReady      = "Pruefungsreif" / "Exam Ready" / "Gotowy na egzamin"

# Reihenfolge
panel.examTrainer.practice.orderSequential    = "Sequentiell" / "Sequential" / "Sekwencyjny"
panel.examTrainer.practice.orderMixed         = "Gemischt" / "Mixed" / "Losowy"

# Fragenanzahl
panel.examTrainer.practice.countAll           = "Alle ({count})" / "All ({count})" / "Wszystkie ({count})"
panel.examTrainer.practice.countEndless       = "Endlos" / "Endless" / "Bez konca"

# Streak Alert
panel.examTrainer.practice.streakAlert        = "{count}x falsch bei {topic} — {extra} Extra-Fragen?"
                                                / "{count}x wrong at {topic} — {extra} extra questions?"
                                                / "{count}x blednie w {topic} — {extra} dodatkowych pytan?"
panel.examTrainer.practice.streakAccept       = "Ja" / "Yes" / "Tak"
panel.examTrainer.practice.streakDecline      = "Nein" / "No" / "Nie"

# Session Summary
panel.examTrainer.practice.summary.title         = "Zusammenfassung"
panel.examTrainer.practice.summary.strongestTopic = "Staerkstes Thema"
panel.examTrainer.practice.summary.weakestTopic   = "Schwaechstes Thema"
panel.examTrainer.practice.summary.overallScore   = "Gesamtergebnis"
panel.examTrainer.practice.summary.timeSpent      = "Dauer"
panel.examTrainer.practice.summary.backToDashboard = "Zurueck zum Dashboard"

# Recommendations (structured, rendered by frontend)
panel.examTrainer.practice.recommendation.strengthenFocus = "Naechstes Mal: Festigen mit Fokus {topic}"
panel.examTrainer.practice.recommendation.discoverMore    = "Naechstes Mal: Neue Themen entdecken"
panel.examTrainer.practice.recommendation.examReady       = "Pruefungsreif-Training empfohlen"

# Difficulty
panel.examTrainer.practice.difficultyUp   = "Schwierigkeit gestiegen"
panel.examTrainer.practice.difficultyDown = "Schwierigkeit gesenkt"

# Spaced Repeat
panel.examTrainer.practice.spacedRepeat   = "Wiederholung"
```

Keys MUESSEN in ALLEN 3 Dateien existieren:
- `src/infrastructure/i18n/locales/de/panel/shared.json`
- `src/infrastructure/i18n/locales/en/panel/shared.json`
- `src/infrastructure/i18n/locales/pl/panel/shared.json`

---

## 5. Error Handling

| Endpoint | Fehler | HTTP | Response |
|----------|--------|------|----------|
| POST /practice-session | Ungueltige mode/order | 400 | `{"error": "INVALID_CONFIG", "detail": "..."}` |
| POST /practice-session | Filter ergibt 0 Fragen | 400 | `{"error": "NO_QUESTIONS", "total_available": 0}` |
| POST /practice-session | User nicht authentifiziert | 401 | Standard auth error |
| POST /next-batch | attempt_id ungueltig | 404 | `{"error": "ATTEMPT_NOT_FOUND"}` |
| POST /next-batch | attempt gehoert anderem User | 403 | `{"error": "ACCESS_DENIED"}` |
| POST /next-batch | Session bereits beendet | 409 | `{"error": "SESSION_COMPLETED"}` |
| GET /summary | attempt_id ungueltig | 404 | `{"error": "ATTEMPT_NOT_FOUND"}` |

---

## 6. State Persistence

Spaced Repetition Queue, Adaptive Difficulty und Streak-Tracking State werden im
`exam_attempts.settings` JSONB-Feld gespeichert (bereits vorhanden):

```json
{
    "practice_state": {
        "spaced_queue": [
            {"question_id": "...", "wrong_count": 1, "due_at_position": 15}
        ],
        "adaptive": {
            "recent_results": [true, true, false, true, true],
            "current_shift": "stay",
            "avg_points": 5.2
        },
        "streak_tracking": {
            "Netzwerktechnik": {"consecutive_wrong": 0, "alerted": false},
            "Datenbanken": {"consecutive_wrong": 2, "alerted": false}
        },
        "current_position": 12,
        "batch_offset": 0
    }
}
```

Bei jedem `/next-batch` Call wird der State gelesen, aktualisiert und zurueckgeschrieben.
Bei Browser-Refresh: Frontend laedt `attempt_id` aus localStorage, Backend liefert State
aus `exam_attempts.settings` — kein Datenverlust.

Keine neuen DB-Tabellen oder Migrationen noetig.

---

## 7. Implementierungs-Reihenfolge

**Sequentiell zuerst** (damit Claude Cowork sofort damit arbeiten kann):

### Phase 1: Sequentieller Modus (Backend + Frontend)
1. Domain models (practice_session.py)
2. Repository: `find_questions_sequential()` + `count_available_questions()`
3. API: `POST /practice-session` (nur sequential support)
4. Frontend: PracticeConfigPanel.vue + Integration in ExamTrainer.vue
5. Test: Sequentiell alle 409 Fragen durchgehen

### Phase 2: Gemischte Modi (Entdecken/Festigen/Pruefungsreif)
6. Repository: `find_topic_prognosis_weights()` + `find_user_topic_weakness()`
7. Repository: `find_questions_by_topic_balanced()`
8. RotationService: `generate_practice_session()` mit 3 Modi
9. Frontend: Lernmodus-Auswahl in PracticeConfigPanel
10. Test: Alle 3 Modi mit verschiedenen Fragenanzahlen

### Phase 3: Intelligente Features
11. practice_intelligence.py: SpacedRepetitionEngine + AdaptiveDifficultyEngine
12. practice_intelligence.py: StreakDetector + SessionSummaryBuilder
13. API: `POST /next-batch` mit Intelligence-Integration
14. Frontend SimulationMode: Batch-Loading + Streak-Alerts
15. Frontend SessionSummary.vue
16. Test: Endlos-Modus mit allen Features aktiv

### Phase 4: Endlos-Modus + Polish
17. Batch-Loading komplett (Frontend + Backend)
18. Endlos-Modus: kein festes Ende, Fortschritt pro Antwort gespeichert
19. Filter-UI (Pruefungen + Themen Dropdowns)
20. Gesamttest aller Kombinationen

---

## 8. Abhaengigkeiten

- Keine externen Abhaengigkeiten
- Bestehende exam_questions + user_question_stats Tabellen genuegen
- Keine DB-Migrationen noetig
- Keine neuen npm-Pakete noetig

---

## 9. Nicht im Scope

- Neue Datenbank-Tabellen (alles mit bestehenden Tabellen + In-Memory State)
- Aenderungen an der AI-Analyse Pipeline
- Aenderungen an bestehenden Pruefungsmodi (Schnell/Halb/Voll)
- Mobile-spezifische UI
