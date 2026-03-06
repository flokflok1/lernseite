# IHK AP1 Exam-to-Course Integration — Design Document

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:writing-plans to create the implementation plan from this design.

**Goal:** 442 echte IHK-Pruefungsfragen automatisch in einen strukturierten Kurs mit 12 Lernmethoden transformieren, ergaenzt um wissenschaftlich fundiertes Spaced Repetition + Elaborative Interrogation + Successive Relearning.

**Architecture:** Ansatz A — Kurs-Generator Service erstellt echte `courses.*` Records die im bestehenden Editor editierbar sind. Kein Breaking Change an bestehender Infrastruktur.

**Tech Stack:** Flask 3.0, psycopg3 (fetch_one/fetch_all), Vue 3 Composition API, bestehender AIAdapter, bestehendes smart_agents Cache-Schema.

---

## 1. Problemstellung

### IST-Zustand

Zwei getrennte Lernsysteme die nichts voneinander wissen:

```
KURSSYSTEM (12 LMs)                 PRUEFUNGSARCHIV
├── Deep Explanation (LM00)          ├── 442 echte IHK-Fragen
├── Flashcards (LM06)                ├── 30 Exams (2017-2024)
├── Drag & Drop (LM07)               ├── Einfacher QuestionCard
├── Cloze Test (LM08)                ├── MCQ / Text / Zahl Input
├── IHK-Style Tasks (LM10)           ├── Kein Spaced Repetition
├── + 7 weitere LMs                  ├── Kein Fortschritt-Tracking
│                                     └── Kein Lernpfad
├── Enrollments + Progress
├── Streaks + Achievements
└── Editor fuer Anpassung
```

### SOLL-Zustand

Ein integrierter Kurs der alle 12 LMs mit echtem IHK-Material nutzt:

```
IHK FISI AP1 — Baden-Wuerttemberg (courses.courses)
│
├── Kap 1: Kalkulation (82 Fragen, 493 Punkte)
│   ├── Deep Explanation (LM00)  — KI-generierte Themenuebersicht
│   ├── Step-by-Step (LM01)      — Rechenweg-Erklaerungen
│   ├── Math Interactive (LM05)  — Interaktive Uebungen
│   ├── Flashcards (LM06)        — Formel-Karten
│   ├── IHK-Style Tasks (LM10)   — Original-Pruefungsaufgaben
│   └── Kapitelpruefung          — 10 gemischte Fragen
│
├── Kap 2: Netzwerktechnik (85 Fragen, 455 Punkte)
│   ├── Deep Explanation (LM00)
│   ├── Flashcards (LM06)        — Begriffe + Protokolle
│   ├── Drag & Drop (LM07)       — OSI-Zuordnungen
│   ├── Cloze Test (LM08)        — Lueckentexte Subnetting
│   ├── IHK-Style Tasks (LM10)   — Original-Aufgaben
│   └── Kapitelpruefung
│
├── ... (20 Topics = 20 Kapitel, sortiert nach Punkte-Gewichtung)
│
├── Kap N-2: Pruefungssimulation GA1 (90 min Mock)
├── Kap N-1: Pruefungssimulation GA2 (90 min Mock)
└── Kap N:   Pruefungssimulation WK (60 min Mock)

ZUSAETZLICH (kursuebergreifend):
└── Taegliche Wiederholung (Spaced Repetition + Interleaving)
    └── 10-20 Fragen/Tag, Topic-gemischt, mit Elaboration
```

---

## 2. Wissenschaftliche Grundlage

### 5-Phasen Lern-Loop (evidenzbasiert)

| Phase | Technik | Studie | Effekt |
|-------|---------|--------|--------|
| 1. VERSTEHEN | Deep Explanation + Dual Coding | Paivio (1986) | Grundverstaendnis |
| 2. ABRUFEN | Active Recall (Flashcards, Cloze, Tasks) | Karpicke & Blunt (2011) | +50% Retention vs. Lesen |
| 3. VERTIEFEN | Elaborative Interrogation ("Warum?") | Pressley et al. (1987) | Verdoppelt Fakten-Retention |
| 4. MEISTERN | Successive Relearning | Rawson & Dunlosky (2013) | Effektivste bekannte Methode |
| 5. BEHALTEN | Spaced Repetition (SM-2) | Cepeda et al. (2008) | Langzeit-Retention |

**Zusaetzlich:** Interleaving (Rohrer et al. 2019) — Topics mischen statt blockweise, +43% bessere Ergebnisse.

### Konkurrenz-Analyse

| Plattform | Recall | SR | Interleaving | Elaboration | Successive RL | KI-Feedback |
|-----------|:---:|:---:|:---:|:---:|:---:|:---:|
| Anki | Ja | Ja | Nein | Nein | Nein | Nein |
| Duolingo | Ja | Ja | Teilw. | Nein | Nein | Nein |
| Cerego | Ja | Ja | Nein | Nein | Ja | Nein |
| **LSX (Ziel)** | **Ja** | **Ja** | **Ja** | **Ja** | **Ja** | **Ja** |

Quellen: [Cerego](https://www.cerego.com/why-cerego), [Dunlosky et al. 2013](https://www.academia.edu/13564364/), [APA Successive Relearning](https://www.apa.org/pubs/journals/features/stl-0000024.pdf)

---

## 3. Architektur-Entscheidungen

### Ansatz A: Kurs-Generator Service (GEWAEHLT)

Neuer `ExamCourseGeneratorService` im Application Layer. Admin klickt "Kurs generieren" → Service liest Exam-Questions, gruppiert nach Topic, ruft KI auf, erstellt echte `courses.*` + `learning_methods.*` Records.

**Warum:**
- Null Breaking Changes — alles sind normale Kurs-Records
- Bestehender Editor sofort nutzbar fuer Anpassungen
- Alle Features geschenkt — Enrollments, Progress, Streaks, Achievements
- DDD-sauber — neuer Service im Application Layer

**Verworfen:**
- Ansatz B (Virtuelle Kurs-View) — Neues Frontend noetig, kein Editor nutzbar
- Ansatz C (Hybrid mit source FK) — Breaking Change an LM-Architektur

### Region-Filter

Kurs wird pro Region generiert. Admin waehlt:
- Pruefungstyp: IHK FISI AP1 (aus `exam_type_registry`)
- Region: Baden-Wuerttemberg (aus `exam_regions`)

Filter: `WHERE s.region = %s OR s.region = 'alle'` — regionsspezifische + bundesweite Pruefungen.

### Trainer-Ersetzung

Der bestehende `/exam-trainer` wird durch den generierten Kurs ersetzt:
- Pruefungssimulationen werden Kapitel im Kurs (GA1, GA2, WK Mocks)
- Topic-Heatmap wird durch Kurs-Fortschritt ersetzt
- Taegliche Wiederholung ersetzt das Topic-basierte Ueben

---

## 4. DDD-Layer Architektur

### 4.1 Domain Layer

Reine Logik. Kein Flask, kein SQL, kein AI-Import.

```
app/domain/
├── models/
│   ├── exam_course_plan.py              ~80 LOC
│   │   ├── ChapterPlan (VO)
│   │   │   - topic: str
│   │   │   - question_ids: List[str]
│   │   │   - lm_types: List[int]       # z.B. [0, 6, 8, 10]
│   │   │   - point_weight: float
│   │   │   - question_count: int
│   │   │
│   │   ├── ExamCoursePlan (VO)
│   │   │   - title: str
│   │   │   - exam_type: str
│   │   │   - region: str
│   │   │   - chapters: List[ChapterPlan]
│   │   │   - simulation_exams: List[str]  # exam_ids fuer Mocks
│   │   │
│   │   └── LMMapping (VO)
│   │       - question_type: str
│   │       - target_lm_type: int
│   │       - transform_fn: str           # Name der Mapping-Funktion
│   │
│   └── spaced_repetition.py             ~100 LOC
│       ├── SM2Card (VO)
│       │   - question_hash: str          # SHA256 — ueberlebt Regenerierung
│       │   - ease_factor: float          # Default 2.5
│       │   - interval_days: int
│       │   - repetitions: int
│       │   - next_review: date
│       │
│       ├── SM2Result (VO)
│       │   - new_ease: float
│       │   - new_interval: int
│       │   - new_repetitions: int
│       │   - next_review: date
│       │
│       ├── sm2_calculate(card, quality) → SM2Result
│       │   # Reiner SM-2 Algorithmus, keine Side Effects
│       │
│       ├── ReviewSession (VO)
│       │   - cards: List[SM2Card]
│       │   - interleaved: bool
│       │   - estimated_minutes: int
│       │
│       └── ElaborationPrompt (VO)
│           - type: str                   # 'why' | 'self_explanation'
│           - template: str
│
├── services/
│   └── lm_content_mapper.py             ~150 LOC
│       └── LMContentMapper (Domain Service)
│           ├── QUESTION_TYPE_TO_LM: Dict[str, List[int]]
│           │   # mcq → [6, 7], fill_blank → [8], essay → [10],
│           │   # calculation → [5], code → [10], case_study → [11]
│           │
│           ├── select_lm_types(topic, questions) → List[int]
│           │   # Waehlt 3-5 passende LMs basierend auf question_types
│           │   # im Topic. Immer LM00 (Deep Explanation) dazu.
│           │
│           ├── map_to_flashcards(questions) → Dict (JSONB)
│           │   # MCQ options+correctAnswers → Flashcard-Karten
│           │
│           ├── map_to_cloze(questions) → Dict (JSONB)
│           │   # fill_blank sentences → Cloze-Format
│           │
│           ├── map_to_drag_drop(questions) → Dict (JSONB)
│           │   # Zuordnungs-MCQs → Drag&Drop Items
│           │
│           ├── map_to_math_interactive(questions) → Dict (JSONB)
│           │   # Calculation problems → Math-Steps
│           │
│           └── map_to_ihk_tasks(questions) → Dict (JSONB)
│               # Essay/Code/CaseStudy → IHK-Task Format
│
└── ports/
    └── learning/
        ├── spaced_repetition_port.py    ~30 LOC
        │   └── SpacedRepetitionPort (ABC)
        │       ├── find_due_cards(user_id, limit) → List[Dict]
        │       ├── upsert_card(data) → Dict
        │       └── find_cards_by_chapter(user_id, chapter_id) → List
        │
        └── ai_feedback_port.py          ~20 LOC
            └── AIFeedbackPort (ABC)
                └── evaluate_answer(question, user_answer, solution) → Dict
```

### 4.2 Application Layer

Orchestrierung + Transaktionen. Importiert Domain + ruft Infrastructure ueber Ports/Repos.

```
app/application/services/
├── exams/
│   ├── course_generator_service.py      ~200 LOC
│   │   └── ExamCourseGeneratorService
│   │       ├── preview(exam_type, region) → ExamCoursePlan
│   │       │   1. ExamQuestionRepo → alle Fragen nach Topics gruppiert
│   │       │   2. LMContentMapper.select_lm_types() pro Topic
│   │       │   3. ExamCoursePlan VO zusammenbauen
│   │       │   4. Return (kein DB-Write)
│   │       │
│   │       ├── generate(plan, options) → course_id
│   │       │   1. CourseRepo.create() → course Record
│   │       │   2. Delegiert an CourseGeneratorBuilder
│   │       │   3. Return course_id
│   │       │
│   │       └── regenerate_chapter(course_id, chapter_id) → None
│   │
│   ├── course_generator_builder.py      ~150 LOC
│   │   └── CourseGeneratorBuilder
│   │       ├── build_chapter(plan, chapter_plan) → chapter_id
│   │       │   1. ChapterRepo.create()
│   │       │   2. LMContentMapper.map_to_X() pro LM-Typ
│   │       │   3. AIAdapter → Deep Explanation generieren
│   │       │   4. LMInstanceRepo.create() pro LM
│   │       │
│   │       └── build_simulation_chapters(plan) → List[chapter_id]
│   │           # GA1, GA2, WK Mock-Pruefungen als Kapitel
│   │
│   └── course_generator_prompts.py      ~150 LOC
│       # KI-Prompt Templates (getrennt, G07 konform)
│       ├── DEEP_EXPLANATION_PROMPT
│       ├── STEP_BY_STEP_PROMPT
│       └── ELABORATION_FEEDBACK_PROMPT
│
└── learning/
    ├── spaced_repetition_service.py     ~250 LOC
    │   └── SpacedRepetitionService
    │       ├── get_daily_review(user_id) → ReviewSession
    │       │   1. SR-Repo.find_due_cards(user_id)
    │       │   2. Interleaving: nie 2x gleiches Topic hintereinander
    │       │   3. Successive Relearning: falsche ans Queue-Ende
    │       │   4. Return ReviewSession VO
    │       │
    │       ├── process_answer(user_id, card_hash, quality) → SM2Result
    │       │   1. Card laden (by question_hash)
    │       │   2. Domain sm2_calculate() aufrufen
    │       │   3. SR-Repo.upsert_card() speichern
    │       │   4. Return neues Intervall
    │       │
    │       ├── create_cards_for_chapter(user_id, chapter_id) → int
    │       │   # Beim Kapitel-Start: SR-Cards fuer alle LM-Instances
    │       │
    │       └── get_stats(user_id) → Dict
    │           # Streak, due_count, mastered_count, weak_topics
    │
    └── elaboration_service.py           ~200 LOC
        └── ElaborationService
            ├── get_prompt(question, answer_result) → ElaborationPrompt
            │   # Domain-VO entscheidet: "why" oder "self_explanation"
            │   # Basierend auf question_type + ob richtig/falsch
            │
            ├── evaluate(question, user_elaboration) → Dict
            │   1. Cache-Check: KnowledgeCacheRepo
            │      (question_hash = SHA256(question_id + answer_pattern))
            │   2. Cache-Hit → gespeichertes Feedback
            │   3. Cache-Miss → AIFeedbackPort.evaluate_answer()
            │   4. Cache-Write → KnowledgeCacheRepo.create()
            │   5. Log → agent_query_log (tokens_used/tokens_saved)
            │   6. Return {feedback, quality_score, missing_points[]}
            │
            └── compute_auto_quality(answer_correct, elab_score) → int
                # SM-2 quality (0-5) aus Antwort + Elaboration
                # richtig + gute Elaboration = 5
                # richtig + schwache Elaboration = 3
                # falsch = 0-1
```

### 4.3 Infrastructure Layer

DB-Zugriff, KI-Aufrufe. Alle SQL NUR hier. psycopg3, parameterized queries.

```
app/infrastructure/persistence/repositories/
├── learning/
│   ├── spaced_repetition.py             ~120 LOC
│   │   └── SpacedRepetitionRepository (implements SpacedRepetitionPort)
│   │       ├── find_due_cards(user_id, limit=20) → List[Dict]
│   │       │   SELECT ... FROM learning_methods.spaced_repetition_cards
│   │       │   WHERE user_id = %s AND next_review <= CURRENT_DATE
│   │       │   ORDER BY ease_factor ASC
│   │       │   LIMIT %s
│   │       │
│   │       ├── upsert_card(data) → Dict
│   │       │   INSERT ... ON CONFLICT (user_id, question_hash, chapter_id)
│   │       │   DO UPDATE SET ...
│   │       │
│   │       ├── find_cards_by_chapter(user_id, chapter_id) → List
│   │       ├── bulk_create_cards(cards) → int
│   │       └── get_user_stats(user_id) → Dict
│   │
│   └── elaboration.py                   ~80 LOC
│       └── ElaborationRepository
│           ├── save_response(data) → Dict
│           │   INSERT INTO learning_methods.elaboration_responses ...
│           │
│           └── find_by_user_method(user_id, method_id) → List
│
│ BESTEHEND — KEINE AENDERUNG:
├── exams/core.py                    # ExamRepository
├── exams/core_part2.py              # ExamQuestionRepository
├── courses/management/crud.py       # CourseRepository
├── knowledge/cache.py               # KnowledgeCacheRepository ← WIEDERVERWENDEN
│
│ BESTEHEND — AIAdapter:
app/infrastructure/ai/adapter.py     # AIAdapter ← WIEDERVERWENDEN
    └── implements AIFeedbackPort fuer Elaboration-Feedback
```

### 4.4 API Layer

Nur Routing, Auth, Validation. Kein SQL, keine Business-Logik.

```
app/api/v1/
├── panel/admin/exams/
│   └── course_generator.py              ~120 LOC
│       └── course_gen_bp Blueprint('/admin/exam-courses')
│
│       POST /admin/exam-courses/preview
│         @admin_required
│         Body: {exam_type: str, region: str}
│         → ExamCourseGeneratorService.preview()
│         → 200: {plan: {title, chapters: [{topic, lm_types, question_count, points}]}}
│
│       POST /admin/exam-courses/generate
│         @admin_required
│         Body: {exam_type: str, region: str, options?: {provider, model}}
│         → ExamCourseGeneratorService.generate()
│         → 201: {course_id, chapters_count, lm_count, tokens_used}
│
│       POST /admin/exam-courses/<course_id>/regenerate/<chapter_id>
│         @admin_required
│         → ExamCourseGeneratorService.regenerate_chapter()
│         → 200: {chapter_id, lm_count}
│
└── panel/user/learning/
    └── review.py                        ~100 LOC
        └── review_bp Blueprint('/user/daily-review')

        GET /user/daily-review
          @token_required
          → SpacedRepetitionService.get_daily_review(user_id)
          → 200: {cards: [...], total, estimated_minutes, streak}

        POST /user/daily-review/answer
          @token_required
          Body: {card_id: str, answer: any, elaboration?: str}
          → SpacedRepetitionService.process_answer()
          → ElaborationService.evaluate() (wenn elaboration vorhanden)
          → 200: {result, feedback?, next_review, cards_remaining}

        GET /user/daily-review/stats
          @token_required
          → SpacedRepetitionService.get_stats(user_id)
          → 200: {due_today, mastered, streak, weak_topics[]}
```

---

## 5. Datenbank-Erweiterungen

### Neue Migration: `101_spaced_repetition.sql`

```sql
-- Spaced Repetition Cards
-- question_hash statt method_id FK → ueberlebt Kurs-Regenerierung
CREATE TABLE IF NOT EXISTS learning_methods.spaced_repetition_cards (
    card_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    question_hash   VARCHAR(64) NOT NULL,
    chapter_id      UUID REFERENCES courses.chapters(chapter_id) ON DELETE SET NULL,
    topic           VARCHAR(100),
    -- SM-2 Algorithmus State
    ease_factor     NUMERIC(4,2) NOT NULL DEFAULT 2.5,
    interval_days   INTEGER NOT NULL DEFAULT 0,
    repetitions     INTEGER NOT NULL DEFAULT 0,
    next_review     DATE NOT NULL DEFAULT CURRENT_DATE,
    last_review     TIMESTAMPTZ,
    -- Statistik
    total_reviews   INTEGER NOT NULL DEFAULT 0,
    correct_count   INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, question_hash, chapter_id)
);

CREATE INDEX idx_sr_cards_due
    ON learning_methods.spaced_repetition_cards(user_id, next_review)
    WHERE next_review <= CURRENT_DATE;
CREATE INDEX idx_sr_cards_topic
    ON learning_methods.spaced_repetition_cards(user_id, topic);

-- Elaboration-Antworten (Lernfortschritt)
CREATE TABLE IF NOT EXISTS learning_methods.elaboration_responses (
    response_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    method_id       UUID REFERENCES learning_methods.learning_method_instances(method_id)
                    ON DELETE SET NULL,
    question_hash   VARCHAR(64) NOT NULL,
    elaboration_type VARCHAR(20) NOT NULL
                    CHECK (elaboration_type IN ('why', 'self_explanation')),
    user_response   TEXT NOT NULL,
    quality_score   NUMERIC(3,2),
    -- FK zum bestehenden Cache-System
    knowledge_id    UUID REFERENCES smart_agents.agent_knowledge_base(knowledge_id)
                    ON DELETE SET NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_elab_user
    ON learning_methods.elaboration_responses(user_id, question_hash);
```

### Bestehende Tabellen die WIEDERVERWENDET werden (kein Schema-Change)

| Tabelle | Zweck in diesem Feature |
|---------|------------------------|
| `courses.courses` | Generierter Kurs |
| `courses.chapters` | Kapitel pro Topic |
| `courses.course_enrollments` | User-Enrollment + Fortschritt |
| `courses.chapter_progress` | Kapitel-Fortschritt |
| `learning_methods.learning_method_instances` | LM-Content pro Kapitel |
| `learning_methods.learning_method_progress` | LM-Fortschritt |
| `learning_methods.learning_streaks` | Streak-Tracking |
| `smart_agents.agent_knowledge_base` | KI-Feedback Cache |
| `smart_agents.agent_query_log` | Token-Tracking |
| `ai_pipeline.ki_requests` | KI-Request Logging |

---

## 6. Frontend-Architektur

### Neue Komponenten

```
src/presentation/
├── components/panel/admin/assessment/exams/
│   └── ExamCourseGenerator.vue          ~250 LOC
│       # Admin-UI: Pruefungstyp + Region Dropdown
│       # → Preview (Kapitel-Liste mit LM-Counts)
│       # → "Kurs generieren" Button
│       # → Fortschrittsanzeige waehrend Generierung
│       # → Link zum generierten Kurs im Editor
│
├── components/panel/user/learning/daily-review/
│   ├── DailyReviewSession.vue           ~200 LOC
│   │   # Session-Flow:
│   │   # 1. Frage anzeigen (bestehender LM-Renderer)
│   │   # 2. User antwortet aktiv (kein "Antwort zeigen")
│   │   # 3. Ergebnis + Musterloesunge
│   │   # 4. ElaborationPrompt einblenden
│   │   # 5. KI-Feedback auf Elaboration
│   │   # 6. Naechste Frage (interleaved)
│   │   # 7. Falsche → Queue-Ende (Successive Relearning)
│   │
│   ├── ElaborationPrompt.vue            ~100 LOC
│   │   # "Warum ist das die Antwort?"
│   │   # oder "Erklaere deinen Denkweg"
│   │   # Textarea + KI-Feedback-Anzeige
│   │
│   ├── ReviewStats.vue                  ~80 LOC
│   │   # Streak, Due Today, Mastered Count, Weak Topics
│   │
│   └── index.ts                         # Barrel Export
│
├── pages/panel/user/learning/
│   └── DailyReviewPage.vue              ~30 LOC
│
├── composables/
│   └── useDailyReview.ts                ~150 LOC
│       # State: cards, currentIndex, sessionComplete
│       # Actions: loadReview, submitAnswer, submitElaboration
│
└── infrastructure/api/clients/panel/
    ├── admin/exams/course-generator.api.ts   ~40 LOC
    │   # previewExamCourse(), generateExamCourse()
    │
    └── user/learning/review.api.ts           ~50 LOC
        # getDailyReview(), submitReviewAnswer(), getReviewStats()
```

### i18n Keys (de/en/pl)

Unter `panel.dailyReview`:
- `title`, `subtitle`, `dueToday`, `startReview`
- `elaboration.why`, `elaboration.selfExplanation`
- `elaboration.placeholder`, `elaboration.feedback`
- `stats.streak`, `stats.mastered`, `stats.weakTopics`
- `complete.title`, `complete.summary`

Unter `panel.examCourseGenerator`:
- `title`, `selectType`, `selectRegion`
- `preview`, `generate`, `generating`
- `success`, `openInEditor`

---

## 7. LM-Mapping: question_type → Lernmethode

| exam question_type | Ziel-LM | method_type | Transformation |
|---|---|---|---|
| `mcq` | Flashcards | 6 | options + correctAnswers → Karten mit Vorder-/Rueckseite |
| `mcq` (Zuordnung) | Drag & Drop | 7 | Wenn Zuordnungsmuster erkennbar → Paare |
| `fill_blank` | Cloze Test | 8 | sentences + answers → Lueckentexte direkt |
| `essay` | IHK-Style Tasks | 10 | Frage + solution_text → Aufgabe mit Musterloesunge |
| `calculation` | Math Interactive | 5 | problems + steps → Interaktive Rechenschritte |
| `code` | IHK-Style Tasks | 10 | Code-Aufgabe + Solution → Programmieraufgabe |
| `case_study` | Multi-Step Practical | 11 | Szenario + Teilfragen → Mehrstufige Aufgabe |
| (alle Topics) | Deep Explanation | 0 | KI generiert Themen-Erklaerung aus Frageppool |
| (alle Topics) | Step-by-Step | 1 | KI generiert Schritt-fuer-Schritt fuer komplexe Themen |

---

## 8. Spaced Repetition Engine

### SM-2 Algorithmus (Domain Layer, reine Funktion)

```python
def sm2_calculate(card: SM2Card, quality: int) -> SM2Result:
    """
    SuperMemo-2 Algorithmus.
    quality: 0=falsch, 1=falsch+erkannt, 2=schwer,
             3=richtig+schwer, 4=richtig, 5=leicht
    """
    new_ease = card.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ease = max(1.3, new_ease)

    if quality >= 3:  # richtig
        if card.repetitions == 0:
            new_interval = 1
        elif card.repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(card.interval_days * new_ease)
        new_repetitions = card.repetitions + 1
    else:  # falsch
        new_interval = 1
        new_repetitions = 0

    return SM2Result(
        new_ease=new_ease,
        new_interval=new_interval,
        new_repetitions=new_repetitions,
        next_review=date.today() + timedelta(days=new_interval),
    )
```

### Quality-Berechnung (automatisch, keine Selbstbewertung)

```
answer_correct + elaboration_quality → SM-2 quality

richtig + gute Elaboration (score >= 0.8)     → quality = 5
richtig + mittlere Elaboration (0.5-0.8)      → quality = 4
richtig + schwache Elaboration (< 0.5)        → quality = 3
richtig + keine Elaboration                    → quality = 3
falsch + gute Elaboration (verstand warum)     → quality = 2
falsch + schwache Elaboration                  → quality = 1
falsch + keine Elaboration                     → quality = 0
```

### Successive Relearning Queue

```
Session mit 12 Fragen:
  Queue: [F1, F2, F3, ..., F12]

  F1: richtig → raus, SR-Update
  F2: falsch  → ans Ende: Queue = [F3, ..., F12, F2]
  F3: richtig → raus
  ...
  F2 (2. Versuch): richtig → raus, aber next_review = morgen (nicht SR-Intervall)

Erst wenn in dieser Session korrekt → naechster Tag nochmal
Erst wenn am naechsten Tag korrekt → SM-2 Intervall startet
```

### Interleaving-Logik

```
Input: 12 faellige Cards mit Topics [netz, netz, kalk, kalk, sql, sql, ...]
Output: [netz, kalk, sql, netz, kalk, sql, ...]  — nie 2x gleiches Topic

Algorithmus:
1. Gruppiere nach Topic
2. Round-Robin ueber Topic-Gruppen
3. Innerhalb Gruppe: ease_factor ASC (schwache zuerst)
```

---

## 9. KI-Feedback Caching (bestehendes Schema)

### Flow

```
User beantwortet Frage → Elaboration eingegeben

1. Cache-Key berechnen:
   question_hash = SHA256(question_id)
   answer_pattern = normalize(user_answer)  # lowercase, keywords extrahieren

2. Cache-Check:
   smart_agents.agent_knowledge_base
   WHERE question_hash = %s
   AND similarity(answer_text, answer_pattern) > 0.8

3a. Cache-HIT:
    → Gespeichertes Feedback zurueckgeben
    → agent_query_log: response_source='cache_hit', tokens_saved=X
    → knowledge_base: usage_count += 1

3b. Cache-MISS:
    → AIFeedbackPort.evaluate_answer()
    → Feedback in agent_knowledge_base speichern
    → agent_query_log: response_source='ai_generated', tokens_used=X

Erwartete Cache-Hit-Rate: 60-70% nach 50 Usern pro Frage
```

---

## 10. Datei-Uebersicht (alle neuen Dateien)

| Layer | Datei | LOC | Aendert Bestehendes? |
|-------|-------|:---:|:---:|
| Domain | `app/domain/models/exam_course_plan.py` | ~80 | Nein |
| Domain | `app/domain/models/spaced_repetition.py` | ~100 | Nein |
| Domain | `app/domain/services/lm_content_mapper.py` | ~150 | Nein |
| Domain | `app/domain/ports/learning/spaced_repetition_port.py` | ~30 | Nein |
| Domain | `app/domain/ports/learning/ai_feedback_port.py` | ~20 | Nein |
| Application | `app/application/services/exams/course_generator_service.py` | ~200 | Nein |
| Application | `app/application/services/exams/course_generator_builder.py` | ~150 | Nein |
| Application | `app/application/services/exams/course_generator_prompts.py` | ~150 | Nein |
| Application | `app/application/services/learning/spaced_repetition_service.py` | ~250 | Nein |
| Application | `app/application/services/learning/elaboration_service.py` | ~200 | Nein |
| Infrastructure | `app/infrastructure/persistence/repositories/learning/spaced_repetition.py` | ~120 | Nein |
| Infrastructure | `app/infrastructure/persistence/repositories/learning/elaboration.py` | ~80 | Nein |
| API | `app/api/v1/panel/admin/exams/course_generator.py` | ~120 | Nein |
| API | `app/api/v1/panel/user/learning/review.py` | ~100 | Nein |
| Migration | `migrations/02_Content/101_spaced_repetition.sql` | ~60 | Nein |
| Frontend | `ExamCourseGenerator.vue` | ~250 | Nein |
| Frontend | `DailyReviewSession.vue` | ~200 | Nein |
| Frontend | `ElaborationPrompt.vue` | ~100 | Nein |
| Frontend | `ReviewStats.vue` | ~80 | Nein |
| Frontend | `DailyReviewPage.vue` | ~30 | Nein |
| Frontend | `useDailyReview.ts` | ~150 | Nein |
| Frontend | `course-generator.api.ts` | ~40 | Nein |
| Frontend | `review.api.ts` | ~50 | Nein |
| i18n | de/en/pl JSON | +50 Keys | Erweitern |

**Gesamt: ~2.760 LOC neuer Code, 0 Breaking Changes**

### Bestehende Dateien die minimal erweitert werden

| Datei | Aenderung |
|-------|-----------|
| `app/__init__.py` | 2 neue Blueprint-Registrierungen |
| `repositories/learning/__init__.py` | Barrel Exports |
| `repositories/exams/__init__.py` | ggf. Barrel Export |
| `frontend/router/index.ts` | 1 neue Route `/daily-review` |
| `frontend/layouts/BaseLayout.vue` | Menu-Item "Taegliche Wiederholung" |
| `i18n/locales/{de,en,pl}/panel/shared.json` | Neue Keys |

---

## 11. Quality Gate Compliance

| Gate | Regel | Status |
|------|-------|:---:|
| G01 | Max 500 LOC pro Datei | Alle < 300 ✅ |
| G02 | Max 50 LOC pro Funktion | Ja ✅ |
| G03 | Keine Circular Imports | Ja ✅ |
| G05 | Keine Duplikate — Cache wiederverwendet | Ja ✅ |
| G06 | Keine hardcoded Secrets | Ja ✅ |
| G07 | KI-Prompts in eigener Datei | `course_generator_prompts.py` ✅ |
| G08 | Kein Silent Exception Swallowing | Ja ✅ |
| G09 | Keine Cross-Layer Shortcuts | AIFeedbackPort ✅ |
| G10 | Kein Dead Code | Ja ✅ |

---

## 12. Phasen-Aufteilung (Implementation)

### Phase 1: Kurs-Generator (Kern-Feature)
- Domain: ExamCoursePlan, LMContentMapper
- Application: CourseGeneratorService + Builder
- API: /admin/exam-courses/*
- Frontend: ExamCourseGenerator.vue
- **Ergebnis:** Admin kann IHK-Kurs generieren und im Editor anpassen

### Phase 2: Spaced Repetition + Successive Relearning
- Migration: spaced_repetition_cards
- Domain: SM2Card, sm2_calculate, ReviewSession
- Application: SpacedRepetitionService
- API: /user/daily-review/*
- Frontend: DailyReviewSession.vue + ReviewStats.vue
- **Ergebnis:** Taegliche Wiederholung mit SR + Successive Relearning

### Phase 3: Elaborative Interrogation + KI-Feedback
- Migration: elaboration_responses
- Domain: ElaborationPrompt, AIFeedbackPort
- Application: ElaborationService (mit Cache)
- Frontend: ElaborationPrompt.vue
- **Ergebnis:** "Warum?"-Fragen nach jeder Antwort mit KI-Feedback

### Phase 4: Trainer-Deprecation + Polish
- /exam-trainer Route → Redirect zum Kurs
- Dashboard-Widget: "X Fragen faellig"
- Streak-Integration
- **Ergebnis:** Saubere Migration, ein Lernort

---

## 13. Nicht in Scope

- Gamification-Erweiterungen (XP fuer Reviews)
- Peer-Learning (andere User-Antworten sehen)
- Pruefungs-Kalender (Countdown zum IHK-Termin)
- Mobil-optimierte Review-UI (kommt spaeter)
- Weitere Pruefungstypen (FIAE, Systemkaufleute) — Architektur ist vorbereitet
