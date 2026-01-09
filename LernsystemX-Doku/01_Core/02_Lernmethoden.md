# 02 – Lernmethoden (12 Content-Methoden)

**Version:** 6.0
**Stand:** 2026-01-02
**Status:** Master-Dokument für Content-Lernmethoden (Clean Separation + Agent Intelligence)

---

## Einleitung

Das LernSystemX (LSX) nutzt **12 Content-Lernmethoden** als didaktische Bausteine, die sich inhaltlich vollständig an unterschiedliche Kurse, Zielgruppen und Prüfungsformate anpassen lassen.

Jede Lernmethode beschreibt ein **Aufgabenformat** (z.B. Flashcards, Lückentext, Freitext-Prüfung), während die konkreten Inhalte pro Kurs und Kapitel frei definiert werden.

**Clean Separation (2026-01-02):**
System-Features (Tools/Services mit eigener Infrastruktur) wurden aus den Content-LMs entfernt und sind nun in `02a_System-Features.md` dokumentiert.

**Agent Intelligence (2026-01-02):**
Content-LMs nutzen ein intelligentes Agent-System, das DB-Wissen mit KI-Unterstützung kombiniert (siehe Migration `066_agent_global_knowledge.sql`).

---

## Didaktische Rollen der 12 Methoden

| Gruppe | Name | IDs | Anzahl | Fokus |
|--------|------|-----|--------|-------|
| **A** | Erklärend | lm00-lm04 | 5 | Verständnis aufbauen |
| **B** | Praxis | lm05-lm08 | 4 | Anwenden & Üben |
| **C** | Prüfung | lm09-lm11 | 3 | Kompetenz nachweisen |

**Ehemalige LMs (jetzt System-Features):**
- lm05 (Whiteboard) → `whiteboard_engine`
- lm10 (Hands-on Lab) → `it_sandbox`
- lm14 (Zeitlimit) → `timer_wrapper`
- lm17 (Mündliche Erklärung) → `speech_to_text`
- **NEU (2026-01-02):**
  - lm10 (IHK-Stil) → `ihk_exam_system`
  - lm11 (Multi-Step Praxis) → `practical_exam_engine`
  - lm13 (Verständnis-Checks) → `comprehension_checker`
  - lm14 (Kapitel-Endprüfung) → `chapter_completion_system`

---

## Technische Grundlage – Format vs. Inhalt

Die 12 Lernmethoden sind technisch als **Methodentypen** umgesetzt; jede konkrete Aufgabe im Kurs ist eine **Instanz eines Typs**.

### Datenbankstruktur

```sql
-- Tabelle für Instanzen von Lernmethoden in Kapiteln
CREATE TABLE learning_methods.learning_method_instances (
    instance_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chapter_id UUID REFERENCES courses.chapters(chapter_id) ON DELETE CASCADE,
    method_type INTEGER NOT NULL REFERENCES learning_methods.learning_method_types(method_type),
    title VARCHAR(255) NOT NULL,
    instructions TEXT,
    content JSONB NOT NULL,
    solution JSONB,
    metadata JSONB DEFAULT '{}',
    order_index INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Methodentypen (12 Content-LMs)
CREATE TABLE learning_methods.learning_method_types (
    method_type INTEGER PRIMARY KEY CHECK (method_type BETWEEN 0 AND 11),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    group_code CHAR(1) CHECK (group_code IN ('A', 'B', 'C')),
    tier VARCHAR(20) CHECK (tier IN ('basic', 'premium')),
    icon VARCHAR(50),
    prompt_template VARCHAR(100),
    default_config JSONB DEFAULT '{}'
);
```

- **`method_type`** legt nur das **Format** fest (0-11 für Content-LMs)
- **`content`** enthält die **individuellen Inhalte** der Aufgabe (JSONB)
- **Foreign Key** statt hardcoded Constraint → flexibel erweiterbar

### Agent-basierte Intelligenz

Seit Version 6.0 nutzen Content-LMs ein intelligentes Agent-System:

```python
@dataclass
class AgentSupport:
    agent_can_handle: bool          # Agent kann ohne AI antworten?
    requires_fresh_ai: bool          # Immer frische AI-Generierung?
    knowledge_domains: List[str]     # Wissensdomänen (networking, math, etc.)
    knowledge_cacheable: bool        # Antworten cachebar?
    complexity_threshold: int        # 1-5: Wann zu AI eskalieren?
```

**Agent-Flow:**
1. User stellt Frage
2. Agent prüft **lokale** Knowledge Base (kurs-spezifisch)
3. Agent prüft **globale** Knowledge Base (cross-course)
4. Falls nicht gefunden → AI-Call + Wissen speichern
5. Nächste ähnliche Frage → aus Cache (Token-Ersparnis!)

---

## Übersicht – 12 Content-Lernmethoden

| LM-ID | Name | Gruppe | Agent-Support | Tier | Didaktisches Ziel |
|-------|------|--------|---------------|------|-------------------|
| **Gruppe A – Erklärend (5 Methoden)** ||||||
| lm00 | Tiefgehende Erklärung | A | ✅ Yes (general) | basic | Komplexe Konzepte verstehen |
| lm01 | Schritt-für-Schritt | A | ✅ Yes (general) | basic | Prozeduren sicher nachvollziehen |
| lm02 | Interaktive Theorie | A | ✅ Yes (general) | basic | Theorie aktiv verarbeiten |
| lm03 | Diagramm/Visualisierung | A | ✅ Yes (general) | basic | Strukturen/Prozesse begreifen |
| lm04 | Beispiel-Szenario | A | ✅ Yes (general) | basic | Transfer in reale Situationen |
| **Gruppe B – Praxis (4 Methoden)** ||||||
| lm05 | Mathe-Interaktiv | B | ✅ Yes (math) | basic | Rechnen/Logik schrittweise beherrschen |
| lm06 | Flashcards | B | ❌ No | basic | Fakten/Wissen langfristig behalten |
| lm07 | Drag & Drop | B | ❌ No | basic | Begriffe/Strukturen sicher zuordnen |
| lm08 | Lückentext | B | ❌ No | basic | Fachbegriffe gezielt anwenden |
| **Gruppe C – Prüfung (3 Methoden)** ||||||
| lm09 | Freitext-Langantwort | C | ✅ Yes (general) | premium | Zusammenhängend schreiben/argumentieren |
| lm10 | Multiple-Choice Quiz | C | ❌ No | basic | Wissensstand schnell checken |
| lm11 | True/False | C | ❌ No | basic | Aussagen bewerten (Richtig/Falsch) |

**Agent-Support Legende:**
- ✅ Yes = Agent entscheidet eigenständig: DB-Wissen vs. AI-Call
- ❌ No = Rein format-basiert, keine Agent-Unterstützung nötig

---

## Gruppe A – Erklärend (lm00-lm04)

**Didaktische Rolle:** Lernende verstehen neue Inhalte, bauen ein tragfähiges mentales Modell auf.

### lm00 – Tiefgehende Erklärung

- **Didaktisches Ziel:** Komplexe Themen systematisch verständlich machen mit Beispielen & Analogien
- **Agent-Support:** ✅ Ja (general knowledge, cacheable, threshold=2)
- **Einsatzszenarien:**
  - Einführung OSI-Modell
  - Subnetting-Konzepte
  - Datenbank-Normalformen
- **Content-Struktur:**
  ```json
  {
    "concept": "Konzeptname",
    "explanation": "Detaillierte Erklärung...",
    "examples": ["Beispiel 1", "Beispiel 2"],
    "analogies": ["Analogie 1"]
  }
  ```
- **Agent-Flow:** Agent prüft DB → bei Bedarf AI → speichert Erklärung

### lm01 – Schritt-für-Schritt

- **Didaktisches Ziel:** Prozedurales Wissen aufbauen; Abläufe reproduzieren
- **Agent-Support:** ✅ Ja (general knowledge, cacheable, threshold=2)
- **Einsatzszenarien:**
  - „Webserver installieren"
  - „Linux-Benutzer anlegen"
  - „Lineare Gleichung lösen"
- **Content-Struktur:**
  ```json
  {
    "process_title": "Titel",
    "introduction": "Einleitung",
    "steps": [
      {"title": "Schritt 1", "description": "...", "hint": "..."},
      {"title": "Schritt 2", "description": "..."}
    ],
    "summary": "Zusammenfassung"
  }
  ```

### lm02 – Interaktive Theorie

- **Didaktisches Ziel:** Theorie mit eingebetteten Verständnisfragen
- **Agent-Support:** ✅ Ja (general knowledge, cacheable, threshold=2)
- **Content-Struktur:**
  ```json
  {
    "topic": "Thema",
    "sections": [
      {
        "title": "Abschnitt 1",
        "theory": "Theorietext...",
        "question": "Verständnisfrage?"
      }
    ]
  }
  ```

### lm03 – Diagramm/Visualisierung

- **Didaktisches Ziel:** Abstrakte Strukturen visuell greifbar machen
- **Agent-Support:** ✅ Ja (general knowledge, cacheable, threshold=3)
- **Einsatzszenarien:**
  - Netzwerk-Topologie
  - ER-Diagramm
  - Ablaufdiagramm
- **Content-Struktur:**
  ```json
  {
    "diagram_title": "Titel",
    "diagram_type": "network|flowchart|uml|er",
    "description": "Kontext",
    "diagram_code": "Mermaid/PlantUML code (optional)",
    "elements": [{"name": "Element", "description": "..."}],
    "learning_goal": "Lernziel"
  }
  ```

### lm04 – Beispiel-Szenario

- **Didaktisches Ziel:** Theorie in realistischen Situationen anwenden
- **Agent-Support:** ✅ Ja (general knowledge, cacheable, threshold=3)
- **Einsatzszenarien:**
  - „Netzwerk langsam – Troubleshooting"
  - „Server-Ausfall vor Prüfung"
- **Content-Struktur:**
  ```json
  {
    "topic": "Thema",
    "industry_context": "IT|BWL|...",
    "scenarios": [
      {
        "title": "Szenario",
        "situation": "Ausgangssituation",
        "challenge": "Problem",
        "solution": "Lösung",
        "takeaway": "Lernerkenntnis"
      }
    ],
    "complexity": "simple|moderate|complex"
  }
  ```

---

## Gruppe B – Praxis (lm05-lm08)

**Didaktische Rolle:** Wissen wird aktiv angewendet und in praktische Fertigkeiten überführt.

### lm05 – Mathe-Interaktiv

- **Didaktisches Ziel:** Rechenwege verstehen, nicht nur Ergebnisse
- **Agent-Support:** ✅ Ja (math domain, cacheable, threshold=3)
- **Einsatzszenarien:**
  - Subnetting
  - Prozentrechnung
  - Algebra
- **Content-Struktur:**
  ```json
  {
    "instruction": "Aufgabenstellung",
    "math_area": "arithmetic|algebra|geometry|calculus|statistics|linear_algebra",
    "formula": "LaTeX formula",
    "solution_steps": ["Schritt 1", "Schritt 2"],
    "final_answer": "x = 5",
    "step_by_step": true,
    "show_hints": true
  }
  ```
- **Agent-Flow:** Agent kennt mathematische Lösungswege → cached für ähnliche Aufgaben

### lm06 – Flashcards

- **Didaktisches Ziel:** Fakten/Wissen langfristig behalten (Spaced Repetition)
- **Agent-Support:** ❌ Nein (rein format-basiert, keine Bewertung nötig)
- **Content-Struktur:**
  ```json
  {
    "cards": [
      {"front": "Frage", "back": "Antwort"},
      {"front": "Begriff", "back": "Definition"}
    ],
    "shuffle": true,
    "spaced_repetition": true
  }
  ```

### lm07 – Drag & Drop

- **Didaktisches Ziel:** Begriffe/Strukturen sicher zuordnen
- **Agent-Support:** ❌ Nein (exakte Zuordnung, kein Bewertungsspielraum)
- **Content-Struktur:**
  ```json
  {
    "instruction": "Ordne zu...",
    "items": ["Item 1", "Item 2"],
    "targets": ["Ziel A", "Ziel B"],
    "correct_mapping": {"Item 1": "Ziel A", "Item 2": "Ziel B"},
    "randomize": true,
    "show_hints": false
  }
  ```

### lm08 – Lückentext

- **Didaktisches Ziel:** Fachbegriffe gezielt anwenden
- **Agent-Support:** ❌ Nein (exakte String-Matching)
- **Content-Struktur:**
  ```json
  {
    "text": "Text mit {{Lücke1}} und {{Lücke2}}...",
    "blanks": {
      "Lücke1": {"answer": "Antwort1", "alternatives": []},
      "Lücke2": {"answer": "Antwort2", "alternatives": ["Alt"]}
    },
    "case_sensitive": false,
    "show_hints": true,
    "show_word_bank": false
  }
  ```

---

## Gruppe C – Prüfung (lm09-lm11)

**Didaktische Rolle:** Kompetenz nachweisen, Lernfortschritt prüfen.

### lm09 – Freitext-Langantwort

- **Didaktisches Ziel:** Zusammenhängend schreiben/argumentieren mit Agent-Bewertung
- **Agent-Support:** ✅ Ja (general knowledge, cacheable, threshold=4)
- **Content-Struktur:**
  ```json
  {
    "exam_topic": "Thema",
    "questions": [
      {
        "question_text": "Offene Frage...",
        "expected_points": "Kernpunkte, die erwartet werden",
        "max_points": 10,
        "min_words": 100
      }
    ],
    "criteria": {
      "content_accuracy": true,
      "completeness": true,
      "structure": false,
      "terminology": false
    },
    "show_detailed_feedback": true,
    "show_model_answer": false
  }
  ```
- **Agent-Flow:**
  1. User gibt Antwort ab
  2. Agent prüft Knowledge Base: "Haben wir ähnliche Freitext-Fragen bewertet?"
  3. Falls ja → nutzt gelerntes Bewertungsmuster
  4. Falls nein → AI-Call für Bewertung → speichert Bewertungsmuster
  5. Gibt konstruktives Feedback

### lm10 – Multiple-Choice Quiz

- **Didaktisches Ziel:** Wissensstand schnell checken
- **Agent-Support:** ❌ Nein (vordefinierte Antworten, kein Bewertungsspielraum)
- **Content-Struktur:**
  ```json
  {
    "questions": [
      {
        "question_text": "Frage...",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answers": [0, 2]
      }
    ],
    "randomize": true,
    "questions_per_set": 20
  }
  ```

### lm11 – True/False

- **Didaktisches Ziel:** Aussagen bewerten (Richtig/Falsch)
- **Agent-Support:** ❌ Nein (binäre Entscheidung, keine Interpretation)
- **Content-Struktur:**
  ```json
  {
    "statements": [
      {
        "text": "Aussage...",
        "is_true": true,
        "explanation": "Erklärung warum richtig/falsch..."
      }
    ],
    "randomize": true,
    "show_explanations": true
  }
  ```

---

## Backend-Integration

### Python Mapping (mit Agent-Support)

```python
# backend/app/ki/learning_method_mapping.py

@dataclass
class AgentSupport:
    agent_can_handle: bool
    requires_fresh_ai: bool
    knowledge_domains: List[str]
    knowledge_cacheable: bool
    complexity_threshold: int

LEARNING_METHODS = {
    0: LearningMethodDefinition(
        lm_id=0,
        name="Tiefgehende Erklärung",
        agent_support=AgentSupport(
            agent_can_handle=True,
            requires_fresh_ai=False,
            knowledge_domains=["general"],
            knowledge_cacheable=True,
            complexity_threshold=2
        )
    ),
    # ... lm01-04 (agent_can_handle=True)
    5: LearningMethodDefinition(
        lm_id=5,
        name="Mathe-Interaktiv",
        agent_support=AgentSupport(
            agent_can_handle=True,
            knowledge_domains=["math"],
            ...
        )
    ),
    # ... lm06-08 (agent_can_handle=False)
    9: LearningMethodDefinition(
        lm_id=9,
        name="Freitext-Langantwort",
        agent_support=AgentSupport(
            agent_can_handle=True,
            complexity_threshold=4,
            ...
        )
    ),
    # ... lm10-11 (agent_can_handle=False)
}

ACTIVE_LEARNING_METHODS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

GROUP_A_EXPLAINING = [0, 1, 2, 3, 4]  # 5 LMs
GROUP_B_PRACTICE = [5, 6, 7, 8]       # 4 LMs
GROUP_C_EXAM = [9, 10, 11]            # 3 LMs
```

### Frontend-Komponenten

```
frontend/src/components/learning-methods/
├── DeepExplanation.vue        (lm00)
├── StepByStep.vue             (lm01)
├── InteractiveTheory.vue      (lm02)
├── DiagramVisualization.vue   (lm03)
├── ExampleScenario.vue        (lm04)
├── MathInteractive.vue        (lm05) ← aus system-features verschoben
├── Flashcards.vue             (lm06)
├── DragDrop.vue               (lm07)
├── FillBlanks.vue             (lm08)
├── LongAnswer.vue             (lm09)
├── MultipleChoiceQuiz.vue     (lm10) ← renummeriert
└── TrueFalse.vue              (lm11) ← NEU
```

### i18n-Struktur (DE/EN/PL)

```json
// de/windows/learningMethods.json
{
  "lm00": { "conceptLabel": "Konzept *", ... },
  "lm01": { "processTitleLabel": "Prozess *", ... },
  "lm02": { "topicLabel": "Thema *", ... },
  "lm03": { "diagramTitleLabel": "Diagramm-Titel *", ... },
  "lm04": { "topicLabel": "Thema / Konzept *", ... },
  "lm05": { "title": "Mathe-Interaktiv", ... },
  "lm06": { "title": "Flashcards (Karteikarten)", ... },
  "lm07": { "title": "Drag & Drop", ... },
  "lm08": { "title": "Lückentext-Aufgaben", ... },
  "lm09": { "title": "Freitext-Langantwort", ... },
  "lm10": { "title": "Multiple-Choice Quiz", ... },
  "lm11": { "title": "True/False", ... }
}
```

---

## Agent Intelligence System (Migration 066)

### Cross-Course Knowledge Sharing

**Schema:** `agent_intelligence`

**Kernidee:** Agents lernen nicht nur kurs-spezifisch, sondern teilen Wissen system-weit.

**Tabellen:**
- `domain_taxonomy` - Wissensdomänen (networking, programming, math, business...)
- `global_knowledge_pool` - Kurs-übergreifende Wissensbasis
- `agent_learning_events` - Lernhistorie
- `cross_agent_sync_status` - Sync zwischen lokaler & globaler Wissensbasis

**Flow:**
1. Agent in Kurs A lernt: "Was ist TCP?"
2. Agent speichert Antwort in **lokale** Knowledge Base
3. Bei hoher Qualität: Agent teilt in **globale** Knowledge Base
4. Agent in Kurs B fragt: "Was ist TCP?"
5. Agent findet Antwort in **globaler** Knowledge Base → **kein AI-Call!**
6. Token-Ersparnis + schnellere Antwort

**Confidence-Mechanismus:**
- Agent 1 beantwortet "Was ist OSI-Modell?" → Confidence 0.5
- Agent 2 bestätigt gleiche Antwort → Confidence 0.6
- Agent 3 bestätigt → Confidence 0.7
- Ab Confidence 0.8 → "verified" Status

**Funktionen:**
- `contribute_to_global_knowledge()` - Teilt lokales Wissen
- `import_global_knowledge()` - Importiert globales Wissen
- `find_global_knowledge()` - Sucht mit Full-Text Search
- `sync_agent_knowledge()` - Sync zwischen lokal & global

---

## Abgrenzung zu System-Features

**Content-LMs** = Aufgabenformate, die mit Inhalt gefüllt werden:
- Flashcards, Quiz, Lückentext, Freitext → pro Kapitel individualisiert
- Keine eigene Infrastruktur (nur JSONB-Content)
- **KÖNNEN** Agent-Support nutzen (lm00-05, lm09)

**System-Features** = Tools/Services mit eigener Infrastruktur:
- Whiteboard-Engine, IT-Sandbox, IHK-Prüfungssystem → kurs-übergreifend
- Benötigen externe Services (Container, KI-APIs, WebRTC)
- **MÜSSEN** immer eigene Logik/Infrastruktur haben

**Siehe:** `02a_System-Features.md` für ausgelagerte Features

---

## Changelog

### Version 6.0 (2026-01-02) - Agent Intelligence System
- ✅ Reduziert von 15 auf **12 Content-Lernmethoden**
- ✅ 4 weitere LMs ausgelagert zu System-Features:
  - lm10 (IHK-Stil) → `ihk_exam_system`
  - lm11 (Multi-Step Praxis) → `practical_exam_engine`
  - lm13 (Verständnis-Checks) → `comprehension_checker`
  - lm14 (Kapitel-Endprüfung) → `chapter_completion_system`
- ✅ Neue Gruppe C: lm09-lm11 (nur 3 LMs)
- ✅ **Agent-System integriert:**
  - `AgentSupport` Dataclass statt `ki_usage` String
  - Cross-Course Knowledge Sharing (Migration 066)
  - Global Knowledge Pool (domain_taxonomy, agent_intelligence)
- ✅ 7 LMs mit Agent-Support: lm00-05, lm09
- ✅ 5 LMs ohne Agent-Support: lm06-08, lm10-11
- ✅ i18n: DE/EN/PL für 12 LMs aktualisiert
- ✅ Frontend: Komponenten renummeriert, `TrueFalse.vue` neu

### Version 5.0 (2026-01-02) - Clean Separation
- Reduziert von 19 auf 15 Content-Lernmethoden
- 4 LMs ausgelagert zu System-Features (Whiteboard, IT-Sandbox, Timer, Speech-to-Text)

### Version 4.0 (2025-12-28)
- Dokumentation zu 12 Content-LMs (vor Clean Separation)

---

*Stand: 2026-01-02 - Clean Separation + Agent Intelligence Complete*
