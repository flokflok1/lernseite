# 02a – System-Features

**Version:** 2.0
**Stand:** 2026-01-02
**Status:** System-Features (Tools/Services separate from Content-LMs)

---

## Zweck dieses Dokuments

Dieses Dokument beschreibt **System-Features**, die **keine Content-Lernmethoden** sind. Sie erweitern das LernSystemX (LSX) um Tools, Services und Infrastruktur, die kurs-übergreifend genutzt werden.

---

## Abgrenzung zu Content-Lernmethoden

**Content-Lernmethoden** (`02_Lernmethoden.md`):
- Aufgabenformate (Flashcards, Quiz, Lückentext)
- Pro Kapitel individualisiert mit Inhalt gefüllt
- Keine eigene Infrastruktur (nur JSONB-Content)
- **Task-Fokus:** WAS der Lernende macht

**System-Features** (dieses Dokument):
- Tools/Services mit eigener Infrastruktur
- Kurs-übergreifend konfigurierbar
- Benötigen oft externe Services (Container, KI-APIs, WebRTC)
- **Runtime-Fokus:** WELCHE Features während der Ausführung aktiv sind

> ⚠️ **Wichtig:** System-Features sind KEINE Aufgaben/Tasks. Sie sind Runtime-Erweiterungen, die eine LM-Instanz anreichern können.
> - Timer ist kein Task → Timer ist ein SF, das zu MCQ (lm03) hinzugefügt wird
> - Proctoring ist kein Task → Proctoring ist ein SF für Exam-Runner
> - Whiteboard ist ein Tool → User zeichnet in LM-Instanz, Whiteboard-SF wertet aus

**📌 Backend-Integration:** Siehe `05_Technical/05_Backend-Struktur.md` **Abschnitt 1.5** für die detaillierte Backend-Implementierung und Flask-Blueprint-Struktur aller System-Features.

---

## Überblick – 25 System-Features

| Kategorie | Features | Anzahl |
|-----------|----------|--------|
| **Interactive Tools** | whiteboard_engine, it_sandbox, speech_to_text | 3 |
| **Exam & Assessment** | ihk_exam_system, practical_exam_engine, comprehension_checker, chapter_completion_system | 4 |
| **Meta Features** | timer_wrapper | 1 |
| **Visualization** | mindmap_generator | 1 |
| **Tutor & Coaching** | npc_tutor, socratic_dialog | 2 |
| **Gamification** | adaptive_difficulty, xp_quest_system, daily_recall | 3 |
| **Learning Paths** | learning_path_generator | 1 |
| **Collaboration** | peer_instruction, team_case, peer_review, learning_journal, project_portfolio, project_based_learning, inverted_classroom | 7 |
| **IT Environments** | code_sandbox, network_simulation, terminal_access | 3 |

**Total:** 25 System-Features (davon 15 aus früheren LMs ausgelagert)

---

## Runner/Experience Layer Integration

System-Features werden vom **Runner/Experience Layer** orchestriert. Der Runner bestimmt, WELCHE SF für einen bestimmten Modus aktiv sind:

| Runner-Modus | Aktive System-Features | Beschreibung |
|--------------|------------------------|--------------|
| `learn.default` | Keine SF erforderlich | Standard-Lernen ohne Extras |
| `learn.guided` | `npc_tutor`, `adaptive_difficulty` | KI-geführtes Lernen mit Hints |
| `exam.practice` | `timer_wrapper`, `chapter_completion_system` | Übungsprüfung mit Timer |
| `exam.simulation` | `timer_wrapper`, `ihk_exam_system`, `practical_exam_engine` | IHK/CompTIA-Prüfungssimulation |
| `game.quiz_battle` | `xp_quest_system`, `peer_instruction` | Multiplayer-Wettbewerb |

**Wichtig:** Der Runner aktiviert SF automatisch basierend auf dem gewählten Modus. Creators können zusätzliche SF manuell pro Kurs/Kapitel aktivieren.

---

## Datenbankstruktur

```sql
-- Registry aller System-Features
CREATE TABLE support_systems.system_features (
    feature_id SERIAL PRIMARY KEY,
    feature_code VARCHAR(50) UNIQUE NOT NULL,
    feature_name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    requires_infrastructure BOOLEAN DEFAULT FALSE,
    requires_external_service BOOLEAN DEFAULT FALSE,
    active BOOLEAN DEFAULT TRUE,
    config JSONB DEFAULT '{}',
    icon VARCHAR(50),
    former_lm_id INTEGER,  -- Referenz zu früherer LM-ID (falls ausgelagert)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Kurs-Level Aktivierung
CREATE TABLE support_systems.course_system_features (
    mapping_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses.courses(course_id) ON DELETE CASCADE,
    feature_id INTEGER REFERENCES support_systems.system_features(feature_id),
    enabled BOOLEAN DEFAULT TRUE,
    config_override JSONB DEFAULT '{}',
    enabled_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (course_id, feature_id)
);

-- Kapitel-Level Aktivierung
CREATE TABLE support_systems.chapter_system_features (
    mapping_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chapter_id UUID REFERENCES courses.chapters(chapter_id) ON DELETE CASCADE,
    feature_id INTEGER REFERENCES support_systems.system_features(feature_id),
    enabled BOOLEAN DEFAULT TRUE,
    config_override JSONB DEFAULT '{}',
    enabled_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (chapter_id, feature_id)
);
```

---

## 1. Interactive Tools (aus Content-LMs ausgelagert)

### 1.1 Whiteboard-Engine (former lm05)

**Beschreibung:** Interaktive Whiteboard-Aufgaben mit KI-Erkennung für Formeln, Diagramme, Netzwerk-Skizzen

**Infrastruktur:**
- Whiteboard-Canvas (HTML5 Canvas / WebGL)
- KI-Erkennung (Handwriting Recognition, Shape Detection)
- Bewertungs-Engine

**Einsatzszenarien:**
- Netzwerk-Topologie zeichnen
- OSI-Modell Schichten skizzieren
- Mathematische Formeln schreiben

**Config:**
```json
{
  "recognition_types": ["formula", "diagram", "network", "keywords"],
  "ai_feedback": true,
  "save_history": true
}
```

**Frontend-Komponente:** `WhiteboardEngine.vue`

---

### 1.2 IT-Sandbox (former lm10)

**Beschreibung:** Praktische Übungen in simulierten IT-Umgebungen (Code, Config, Netzwerk, Terminal)

**Infrastruktur:**
- Container-Orchestrierung (Docker/Kubernetes)
- Code-Sandbox (isoliert)
- Config-Testing-Umgebung
- Netzwerk-Simulation
- Terminal-Zugriff

**Einsatzszenarien:**
- Linux-Server-Administration
- Windows Server Setup
- Netzwerk-Konfiguration
- Container/Docker Labs
- Security-Übungen

**Config:**
```json
{
  "sandbox_types": ["code", "config", "network", "terminal"],
  "max_duration": 3600,
  "auto_cleanup": true
}
```

**Frontend-Komponente:** `ITSandbox.vue`

---

### 1.3 Speech-to-Text Engine (former lm17)

**Beschreibung:** Sprachaufnahme mit KI-Transkription & Bewertung (mündliche Prüfungen)

**Infrastruktur:**
- Audio-Recording (WebRTC)
- Speech-to-Text (Whisper / Deepgram)
- KI-Bewertung (GPT/Claude)
- Transkript-Speicherung

**Einsatzszenarien:**
- Mündliche IHK-Prüfung simulieren
- Präsentation üben
- Konzept erklären lassen

**Config:**
```json
{
  "max_duration": 600,
  "language": "de-DE",
  "ai_grading": true,
  "provider": "whisper"
}
```

**Frontend-Komponente:** `SpeechToText.vue`

---

## 2. Exam & Assessment Systems (aus Content-LMs ausgelagert, 2026-01-02)

### 2.1 IHK-Exam System (former lm10 from 15-LM version)

**Beschreibung:** Prüfungsaufgaben im IHK/Kammer-Format mit spezifischen Bewertungskriterien

**Infrastruktur:**
- IHK-Aufgabengenerator (KI-gestützt)
- Prüfungsformat-Templates (IT-Berufe, Kaufmännisch, Handwerk)
- Bewertungs-Engine mit IHK-Richtlinien
- Zertifikats-Generierung

**Einsatzszenarien:**
- IHK Fachinformatiker Systemintegration
- IHK Kaufmann für Büromanagement
- IHK Elektroniker
- Vorbereitung auf schriftliche Abschlussprüfung

**Config:**
```json
{
  "exam_format": "ihk_it|ihk_commercial|ihk_craft",
  "certification_body": "IHK Berlin|IHK München|...",
  "difficulty_level": "intermediate|advanced",
  "time_limit": 180,
  "passing_score": 50
}
```

**Frontend-Komponente:** `IHKExamSystem.vue`

**Agent-Support:** ❌ Nein (standardisierte Prüfungsformate)

---

### 2.2 Practical Exam Engine (former lm11 from 15-LM version)

**Beschreibung:** Mehrstufige praktische Prüfungsaufgaben mit Teilschritt-Bewertung

**Infrastruktur:**
- Multi-Step Workflow Engine
- Teilschritt-Bewertung
- Abhängigkeiten zwischen Schritten
- Progress Tracking
- KI-gestützte Bewertung komplexer Handlungsketten

**Einsatzszenarien:**
- IT-Projekt durchführen (Planung → Implementation → Testing → Doku)
- Troubleshooting-Prozess (Analyse → Diagnose → Lösung → Verifikation)
- Server-Setup (Installation → Konfiguration → Absicherung → Testing)

**Config:**
```json
{
  "max_steps": 10,
  "allow_skip": false,
  "partial_credit": true,
  "time_per_step": 30,
  "dependency_mode": "strict|flexible"
}
```

**Frontend-Komponente:** `PracticalExamEngine.vue`

**Agent-Support:** ✅ Ja (bewertet Handlungsketten, speichert Bewertungsmuster)

---

### 2.3 Comprehension Checker (former lm13 from 15-LM version)

**Beschreibung:** Mikro-Checks nach Lerneinheiten basierend auf Bloom-Taxonomie

**Infrastruktur:**
- Bloom-Taxonomie Engine (recall → create)
- Adaptive Fragegenerierung
- Verständnistiefe-Analyse
- Lernfortschritt-Tracking

**Einsatzszenarien:**
- Nach jedem Theorie-Abschnitt: Verständnis prüfen
- Lernziel-basierte Checks (Verstehen vs. Anwenden vs. Analysieren)
- Wissens-Gaps identifizieren

**Bloom-Level:**
1. **Recall** - Faktenwissen abrufen
2. **Understand** - Zusammenhänge erklären
3. **Apply** - In neuem Kontext nutzen
4. **Analyze** - Strukturen erkennen
5. **Evaluate** - Kritisch beurteilen
6. **Create** - Neues entwickeln

**Config:**
```json
{
  "bloom_levels": ["recall", "understand", "apply", "analyze", "evaluate", "create"],
  "min_questions_per_level": 2,
  "adaptive": true,
  "immediate_feedback": true
}
```

**Frontend-Komponente:** `ComprehensionChecker.vue`

**Agent-Support:** ✅ Ja (analysiert Verständnistiefe, lernt Bewertungsmuster)

---

### 2.4 Chapter Completion System (former lm14 from 15-LM version)

**Beschreibung:** Umfassende Kapitelabschluss-Prüfung mit gemischten Aufgabentypen

**Infrastruktur:**
- Multi-Format Test Engine (MC, True/False, Short Answer, Fill-in-Blank, Matching, Ordering, Free Text, Calculations)
- Zertifikats-Generierung bei Bestehen
- Lernfortschritt-Marker (Kapitel abgeschlossen)
- Statistik & Analytics

**Einsatzszenarien:**
- Kapitelabschluss in strukturierten Kursen
- Kompetenznachweis vor nächstem Kapitel
- IHK-Vorbereitung (simuliert gemischte Prüfungsformate)

**Config:**
```json
{
  "exam_title": "Kapitel 3: Netzwerktechnik",
  "pass_threshold": 70,
  "sections": [
    {
      "section_title": "Teil A: Multiple-Choice",
      "task_type": "multiple_choice",
      "question_count": 10,
      "points_per_question": 2
    },
    {
      "section_title": "Teil B: Freitext",
      "task_type": "free_text",
      "question_count": 2,
      "points_per_question": 10
    }
  ],
  "options": {
    "shuffle_sections": false,
    "shuffle_questions": true,
    "allow_review": true,
    "show_correct_answers": true,
    "certificate_on_pass": true
  }
}
```

**Frontend-Komponente:** `ChapterCompletionSystem.vue`

**Agent-Support:** ✅ Ja (bewertet Freitext-Antworten, speichert Bewertungen)

---

## 3. Meta Features

### 3.1 Timer/Zeitlimit-Feature (former lm14 from old version)

**Beschreibung:** Zeitbegrenzung für beliebige Aufgaben (Meta-Feature, kann auf alle LMs angewendet werden)

**Config:**
```json
{
  "default_time_limit": 60,
  "show_remaining_time": true,
  "auto_submit": true
}
```

**Frontend-Komponente:** `TimerWrapper.vue`

---

## 4. Visualization Features

### 4.1 Mindmap-Generator

**Beschreibung:** Generiert kursweite Mindmaps aus Theorie-Inhalten

**Config:**
```json
{
  "auto_generate": true,
  "max_depth": 3,
  "style": "hierarchical"
}
```

---

## 5. Tutor & Coaching

### 5.1 NPC-/Persona-Tutor

**Beschreibung:** KI-basierter Tutor mit verschiedenen Rollen/Personas

**Personas:**
- Professor (formell, strukturiert)
- Peer (freundlich, gleichgestellt)
- Mentor (unterstützend, erfahren)
- Coach (motivierend, zielorientiert)

**Config:**
```json
{
  "personas": ["professor", "peer", "mentor", "coach"],
  "conversation_style": "adaptive",
  "remember_context": true
}
```

---

### 5.2 Sokratischer Dialog

**Beschreibung:** KI-geführter Dialog zur Wissensvermittlung durch Fragen

**Config:**
```json
{
  "max_questions": 10,
  "difficulty_adaptation": true
}
```

---

## 6. Gamification

### 6.1 Adaptive Schwierigkeit

**Beschreibung:** Passt Aufgabenschwierigkeit automatisch an Leistungsstand an

**Config:**
```json
{
  "adjustment_algorithm": "elo",
  "min_attempts": 3
}
```

---

### 6.2 XP & Quest System

**Beschreibung:** Erfahrungspunkte, Level, Achievements, Daily Quests

**Config:**
```json
{
  "xp_per_task": 100,
  "daily_quests_count": 3
}
```

---

### 6.3 Daily Recall

**Beschreibung:** Tägliche Wiederholungslogik (Spaced Repetition)

**Config:**
```json
{
  "algorithm": "sm2",
  "daily_limit": 20
}
```

---

## 7. Learning Paths

### 7.1 Lernpfad-Generator

**Beschreibung:** KI-gestützte Lernpfad-Erstellung und -Optimierung

**Config:**
```json
{
  "personalized": true,
  "adapt_to_performance": true
}
```

---

## 8. Collaboration Features (aus früheren lm26-32 ausgelagert)

### 8.1 Peer Instruction (former lm26)

**Beschreibung:** Peer Instruction Methode (Think-Pair-Share)

**Frontend-Komponente:** `PeerInstruction.vue`

---

### 8.2 Team-Case (former lm27)

**Beschreibung:** Kollaborative Fallbearbeitung

**Frontend-Komponente:** `TeamCase.vue`

---

### 8.3 Peer Review (former lm28)

**Beschreibung:** Gegenseitige Bewertung von Lösungen

**Config:**
```json
{
  "anonymous": true,
  "min_reviews": 2
}
```

**Frontend-Komponente:** `PeerReview.vue`

---

### 8.4 Lerntagebuch (former lm29)

**Beschreibung:** Persönliche Reflexion und Dokumentation

**Frontend-Komponente:** `LearningJournal.vue`

---

### 8.5 Projekt-Portfolio (former lm30)

**Beschreibung:** Sammlung eigener Projekte

**Frontend-Komponente:** `ProjectPortfolio.vue`

---

### 8.6 Projektbasiertes Lernen (former lm31)

**Beschreibung:** Project-Based Learning Workflows

**Frontend-Komponente:** `ProjectBasedLearning.vue`

---

### 8.7 Inverted Classroom (former lm32)

**Beschreibung:** Flipped Classroom Unterstützung

**Frontend-Komponente:** `InvertedClassroom.vue`

---

## 9. IT Environments (spezifische Typen)

### 9.1 Code-Sandbox

**Beschreibung:** Isolierte Code-Ausführungsumgebung

**Config:**
```json
{
  "languages": ["python", "javascript", "java", "go"],
  "max_execution_time": 30
}
```

---

### 9.2 Netzwerk-Simulation

**Beschreibung:** Virtuelle Netzwerk-Topologien

**Config:**
```json
{
  "max_nodes": 20,
  "protocols": ["tcp", "udp", "icmp"]
}
```

---

### 9.3 Terminal-Zugriff

**Beschreibung:** Web-basierter Terminal-Zugang

**Config:**
```json
{
  "shell": "bash",
  "max_session_time": 1800
}
```

---

## Backend-Integration

### Python Mapping

```python
# backend/app/ki/system_features_mapping.py
SYSTEM_FEATURES = {
    # Interactive Tools
    "whiteboard_engine": SystemFeatureDefinition(
        feature_code="whiteboard_engine",
        former_lm_id=5,
        ...
    ),
    "it_sandbox": SystemFeatureDefinition(
        former_lm_id=10,
        ...
    ),
    "speech_to_text": SystemFeatureDefinition(
        former_lm_id=17,
        ...
    ),

    # Exam & Assessment Systems (NEW 2026-01-02)
    "ihk_exam_system": SystemFeatureDefinition(
        feature_code="ihk_exam_system",
        feature_name="IHK-Prüfungssystem",
        category="exam_systems",
        requires_infrastructure=True,
        requires_external_service=True,
        former_lm_id=10  # from 15-LM version
    ),
    "practical_exam_engine": SystemFeatureDefinition(
        feature_code="practical_exam_engine",
        feature_name="Praxisprüfungs-Engine",
        category="exam_systems",
        former_lm_id=11  # from 15-LM version
    ),
    "comprehension_checker": SystemFeatureDefinition(
        feature_code="comprehension_checker",
        feature_name="Verständnis-Checker",
        category="tutor",
        former_lm_id=13  # from 15-LM version
    ),
    "chapter_completion_system": SystemFeatureDefinition(
        feature_code="chapter_completion_system",
        feature_name="Kapitelabschluss-System",
        category="exam_systems",
        former_lm_id=14  # from 15-LM version
    ),

    # Meta Features
    "timer_wrapper": SystemFeatureDefinition(
        former_lm_id=14,  # from old version
        ...
    ),

    # Collaboration
    "peer_instruction": SystemFeatureDefinition(
        former_lm_id=26,
        ...
    ),
    # ... + 18 weitere
}
```

### Frontend-Komponenten

```
frontend/src/components/system-features/
├── WhiteboardEngine.vue
├── ITSandbox.vue
├── SpeechToText.vue
├── IHKExamSystem.vue              ← NEU (2026-01-02)
├── PracticalExamEngine.vue        ← NEU (2026-01-02)
├── ComprehensionChecker.vue       ← NEU (2026-01-02)
├── ChapterCompletionSystem.vue    ← NEU (2026-01-02)
├── TimerWrapper.vue
├── PeerInstruction.vue
├── TeamCase.vue
├── PeerReview.vue
├── LearningJournal.vue
├── ProjectPortfolio.vue
├── ProjectBasedLearning.vue
└── InvertedClassroom.vue
```

### Aktivierung

System-Features können pro Kurs oder Kapitel aktiviert werden:

```sql
-- Feature für Kurs aktivieren
INSERT INTO support_systems.course_system_features (course_id, feature_id, enabled)
VALUES ('course-uuid', 1, true);

-- Feature für Kapitel aktivieren
INSERT INTO support_systems.chapter_system_features (chapter_id, feature_id, enabled)
VALUES ('chapter-uuid', 1, true);
```

---

## Vorteile der Trennung

| Aspekt | Content-LMs | System-Features |
|--------|-------------|-----------------|
| **Erweiterbarkeit** | Neue LM = Code + Migration | Neue Feature = DB Insert |
| **Aktivierung** | Immer verfügbar | Pro Kurs/Kapitel konfigurierbar |
| **Infrastruktur** | Keine | Explizit dokumentiert |
| **Code-Struktur** | `/learning-methods/` | `/system-features/` |

---

## Changelog

### Version 3.0 (2026-01-02) - Exam & Assessment Systems
- ✅ **4 neue Exam/Assessment Features** von Content-LMs (lm10-11, lm13-14) ausgelagert:
  - `ihk_exam_system` - IHK-Prüfungsformate
  - `practical_exam_engine` - Multi-Step Praxisprüfungen
  - `comprehension_checker` - Bloom-Taxonomie Checks
  - `chapter_completion_system` - Kapitelabschluss-Prüfungen
- ✅ Neue Kategorie "Exam & Assessment" (4 Features)
- ✅ Total: **25 System-Features** (statt 21)
- ✅ Frontend-Komponenten: `IHKExamSystem.vue`, `PracticalExamEngine.vue`, `ComprehensionChecker.vue`, `ChapterCompletionSystem.vue`
- ✅ Agent-Support: 3 von 4 Features nutzen Agent Intelligence

### Version 2.0 (2026-01-02) - Clean Separation
- ✅ 4 Interactive Tools aus Content-LMs ausgelagert (Whiteboard, IT-Sandbox, Timer, Speech-to-Text)
- ✅ 7 Collaboration Features aus lm26-32 ausgelagert
- ✅ 10+ zusätzliche Features dokumentiert (Tutor, Gamification, IT-Environments)
- ✅ DB-Struktur: `system_features`, `course_system_features`, `chapter_system_features`
- ✅ Frontend: Komponenten in `/system-features/`
- ✅ Backend: `system_features_mapping.py`

### Version 1.0 (2025-12-28)
- Initial documentation (vor Clean Separation)

---

*Stand: 2026-01-02 - Clean Separation + Exam/Assessment Complete*
