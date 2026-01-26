# Migration Struktur - Logische Erklärung

**Stand:** 2026-01-26
**Ziel:** Saubere, nachvollziehbare Migrations-Architektur für Production

---

## 1. Zentrale Struktur

```
backend/migrations/
├── 00_Schemas/
│   └── 000_schemas.sql               ← ZENTRAL: 12 Schemas erstellen
│                                       (core, organisations, courses, learning_methods,
│                                        ai_pipeline, agent_intelligence, billing_storage,
│                                        system_features, support_systems, dashboards,
│                                        analytics, translations)
│
├── 01_Core/                           ← Kern: Auth, Benutzer, Organisationen
│   ├── 001_users_auth.sql
│   ├── 002_organisations.sql
│   ├── 003_permissions.sql
│   └── ... (4-5 Dateien)
│
├── 02_Content/                        ← Inhalte: Kurse, Kapitel, Lektionen
│   ├── 010_courses.sql
│   ├── 011_chapters.sql
│   ├── 012_lessons.sql
│   └── ... (3-4 Dateien)
│
├── 03_AI/                             ← KI-System: Modelle, Prompts, Jobs
│   ├── 020_ai_models.sql
│   ├── 021_ai_prompts.sql             ← PROMPTS sind AI-Feature
│   └── ... (2-3 Dateien)
│
├── 04_LearningMethods/                ← ZENTRAL: 12 Content-Lernmethoden
│   ├── 030_learning_methods_core.sql  ← Einzige Datei für ALL LM-Tabellen
│   └── 031_learning_progress.sql
│
├── 05_SystemFeatures/                 ← ZENTRAL: 25 System-Features (Infrastruktur-Tools)
│   ├── 040_system_features_core.sql   ← Einzige Datei für ALL System-Feature-Tabellen
│   └── 041_system_features_advanced.sql (optional, falls nötig)
│
├── 06_Tutor/                          ← Tutor-System: Erklärungen, Evaluation, TTS
│   ├── 050_tutor_system.sql
│   ├── 051_theory_explanations.sql
│   ├── 052_task_evaluation.sql
│   └── 053_tts_configuration.sql
│
├── 07_Social/                         ← Soziales Netzwerk
├── 08_Assessment/                     ← Prüfungen
├── 09_Gamification/                   ← Gamification
├── 10_Notifications/                  ← Benachrichtigungen
├── 11_Storage/                        ← Dateispeicher
├── 12_Billing/                        ← Abrechnung
├── 13_Compliance/                     ← Datenschutz, Moderation, Child Safety
│
└── 00_Seeds/                          ← SEED-DATEN (Konfiguration, nicht Struktur!)
    ├── 01_learning_methods_seed.sql   ← Seeded: 12 Content-LMs
    ├── 02_system_features_seed.sql    ← Seeded: 25 System-Features
    ├── 03_permissions_seed.sql        ← Seeded: Default-Gruppen, Rollen
    ├── 04_ai_prompts_seed.sql         ← Seeded: Template-Prompts
    └── ... (weitere Seeds)
```

---

## 2. KRITISCHE UNTERSCHEIDUNG

### Content-Lernmethoden - Ordner: 04_LearningMethods

**Was:** 12 Aufgabenformate (Task-Vorlagen)
- Flashcards, Lückentext, Freitext, Multiple Choice, True/False, Code Challenge, Case Study, Simulation, Peer Review Exercise, Objective Assessment, Practical Exam, Portfolio Assessment
- Jeder Kurs füllt diese mit **eigenem Content** (JSONB)

**Schema:** `learning_methods`

**Tabellen (in 030_learning_methods_core.sql):**
- `learning_methods.learning_method_types` - Die 12 LM-Typen
- `learning_methods.learning_method_instances` - Konkrete Aufgaben pro Kapitel
- `learning_methods.learning_method_progress` - Fortschritt der Studenten

**Seed (01_learning_methods_seed.sql):**
```sql
INSERT INTO learning_methods.learning_method_types VALUES
  (0, 'Flashcards', 'A', 'basic'),
  (1, 'Lückentext', 'A', 'basic'),
  (2, 'Freitext', 'A', 'basic'),
  (3, 'Multiple Choice', 'A', 'basic'),
  (4, 'True/False', 'A', 'basic'),
  (5, 'Code Challenge', 'B', 'premium'),
  (6, 'Case Study', 'B', 'premium'),
  (7, 'Simulation', 'B', 'premium'),
  (8, 'Peer Review Exercise', 'B', 'premium'),
  (9, 'Objective Assessment', 'C', 'premium'),
  (10, 'Practical Exam', 'C', 'premium'),
  (11, 'Portfolio Assessment', 'C', 'premium')
```

---

### System-Features (25) - Ordner: 05_SystemFeatures

**Was:** Infrastructure-Tools mit eigenen Servern/APIs
- math_patterns, whiteboard_engine, code_sandbox, TTS, AI Tutor, etc.
- Kurs-übergreifend konfigurierbar

**Schema:** `system_features`

**Tabellen (in 040_system_features_core.sql):**
- `system_features.system_features` - Die 25 Features
- `system_features.course_system_features` - Aktivierung pro Kurs
- `system_features.chapter_system_features` - Aktivierung pro Kapitel

**Seed (02_system_features_seed.sql):**
```sql
INSERT INTO system_features.system_features VALUES
  ('math_patterns', 'Math Pattern Recognition', 'interactive_tools', true),
  ('whiteboard_engine', 'Interactive Whiteboard', 'interactive_tools', true),
  ... (alle 25)
```

---

## 3. SCHEMAS (Zentral in 000_schemas.sql)

```sql
-- Struktur-Schemas
CREATE SCHEMA core;              -- Users, Auth, Orgs
CREATE SCHEMA organisations;     -- Multi-Tenancy
CREATE SCHEMA courses;           -- Kurse, Kapitel, Lektionen
CREATE SCHEMA learning_methods;  -- 12 Content-LMs (eigenes Schema!)
CREATE SCHEMA ai_pipeline;       -- KI-Modelle, Prompts
CREATE SCHEMA system_features;   -- 25 Infrastructure-Features (eigenes Schema!)
CREATE SCHEMA support_systems;   -- Tutor-System (Erklärungen, Evaluation)
CREATE SCHEMA billing_storage;   -- Abrechnung, Dateien
CREATE SCHEMA agent_intelligence;-- KI-Agents
CREATE SCHEMA dashboards;        -- Dashboards, Widgets
CREATE SCHEMA analytics;         -- Analysen
CREATE SCHEMA translations;      -- i18n
```

**Wichtig:**
- Jedes Schema hat **EINEN Ordner** in migrations/
- 04_LearningMethods/ ← `learning_methods` schema
- 05_SystemFeatures/ ← `system_features` schema

---

## 4. MIGRATIONS-DATEISTRUKTUR

### 04_LearningMethods/030_learning_methods_core.sql

**EINE Datei für ALLE LM-Tabellen:**
```sql
-- Create learning_methods.learning_method_types (12 Methods)
CREATE TABLE learning_methods.learning_method_types (
  method_type INTEGER PRIMARY KEY CHECK (method_type BETWEEN 0 AND 11),
  name VARCHAR(100),
  group_code CHAR(1) CHECK (group_code IN ('A', 'B', 'C')),
  ...
);

-- Create learning_methods.learning_method_instances
CREATE TABLE learning_methods.learning_method_instances (
  method_id UUID,
  chapter_id UUID,
  method_type INTEGER REFERENCES learning_methods.learning_method_types,
  ...
);

-- Create learning_methods.learning_method_progress
CREATE TABLE learning_methods.learning_method_progress (
  progress_id UUID,
  method_id UUID,
  user_id UUID,
  ...
);
```

**Warum eine Datei?**
- Diese gehören zusammen (Lernmethoden)
- Übersichtlich
- Nicht zu viele Dateien

---

### 05_SystemFeatures/040_system_features_core.sql

**EINE Datei für ALLE System-Feature-Tabellen:**
```sql
-- Create system_features.system_features (25 Features)
CREATE TABLE system_features.system_features (
  feature_id SERIAL PRIMARY KEY,
  feature_code VARCHAR(50) UNIQUE,
  feature_name VARCHAR(100),
  category VARCHAR(50),
  requires_infrastructure BOOLEAN,
  ...
);

-- Create system_features.course_system_features
CREATE TABLE system_features.course_system_features (
  mapping_id UUID,
  course_id UUID REFERENCES courses.courses,
  feature_id INTEGER REFERENCES system_features.system_features,
  enabled BOOLEAN,
  ...
);

-- Create system_features.chapter_system_features
CREATE TABLE system_features.chapter_system_features (
  mapping_id UUID,
  chapter_id UUID REFERENCES courses.chapters,
  feature_id INTEGER REFERENCES system_features.system_features,
  enabled BOOLEAN,
  ...
);
```

**Warum eine Datei?**
- Diese gehören zusammen (System-Features)
- Klare Strukturierung
- Nicht zu viele Dateien

---

## 5. SEED-DATEN (00_Seeds/)

### 01_learning_methods_seed.sql
```sql
-- Seed 12 Content-Lernmethoden
INSERT INTO learning_methods.learning_method_types VALUES
  (0, 'Flashcards', 'A', ...),
  (1, 'Lückentext', 'A', ...),
  (2, 'Freitext', 'A', ...),
  ...
  (11, 'Praktische Prüfung', 'C', ...);
```

### 02_system_features_seed.sql
```sql
-- Seed 25 System-Features
INSERT INTO system_features.system_features VALUES
  ('math_patterns', 'Math Pattern Recognition', 'interactive_tools', true),
  ('whiteboard_engine', 'Interactive Whiteboard', 'interactive_tools', true),
  ('code_sandbox', 'Code Execution Sandbox', 'it_environments', true),
  ('ihk_exam_system', 'IHK Exam Format', 'exam_systems', false),
  ('npc_tutor', 'NPC Tutor Companion', 'tutor_coaching', false),
  ...
  (25 total);
```

---

## 6. WARUM IST DAS LOGISCH?

✅ **Für einen Senior Dev:**

1. **Schema-Ordnung** - Jedes Schema hat einen Ordner
2. **LMs vs Features** - Klar getrennt (04/ vs 05/)
3. **Eine Datei pro Schema** - Nicht 20 Dateien durchsuchen
4. **Seed-Daten getrennt** - Struktur (Tabellen) vs Konfiguration (Seeds)
5. **Nummerierung klar** - 00_Schemas → 01_Core → 02_Content → ...
6. **Keine Redundanz** - Keine doppelten CREATE SCHEMA
7. **Nachvollziehbar** - Ein Senior Dev versteht sofort: "Ah, 04/ sind die Lernmethoden, 05/ die System-Features"

---

## 7. IMPLEMENTATION-SCHRITTE

### Phase 1: Ordner-Struktur erstellen
```bash
mkdir -p backend/migrations/04_LearningMethods/
mkdir -p backend/migrations/05_SystemFeatures/
```

### Phase 2: Tabellen-Migrations erstellen
- `04_LearningMethods/030_learning_methods_core.sql` ← Alle LM-Tabellen
- `05_SystemFeatures/040_system_features_core.sql` ← Alle System-Feature-Tabellen

### Phase 3: Seed-Daten erstellen
- `00_Seeds/01_learning_methods_seed.sql` ← 12 LMs seeden
- `00_Seeds/02_system_features_seed.sql` ← 25 Features seeden

### Phase 4: Aufräumen
- Alte Dateien löschen (nicht mehr nötig)
- `070_system_features.sql` → **LÖSCHEN** (in 040 integriert)
- `021_ai_prompts.sql` → Bleibt in 03_AI (gehört zur AI)
- Tutor-Migrations in neuen Ordner 06_Tutor/ verschieben

---

## 8. FINAL STRUCTURE

```
04_LearningMethods/
  ├── 030_learning_methods_core.sql    ← learning_method_types, instances, progress
  └── 031_learning_progress.sql        ← Weitere Progress-Tabellen (optional)

05_SystemFeatures/
  ├── 040_system_features_core.sql     ← system_features, course/chapter activation
  └── 041_system_features_advanced.sql ← Weitere Advanced-Features (optional)

00_Seeds/
  ├── 01_learning_methods_seed.sql     ← 12 Content-LMs
  └── 02_system_features_seed.sql      ← 25 System-Features
```

**Ein Senior Dev sieht das und denkt:**
> "Ah, Lernmethoden haben ihren Ordner (04), System-Features haben ihren Ordner (05),
> Schemas sind zentral (00), Seeds sind separat (00_Seeds). Clean. Verständlich. Gut."

---

## FEHLER VERMEIDEN

❌ **FALSCH:**
- 30 verschiedene Migrations-Dateien
- Schemas verstreut in mehreren Dateien
- LMs und Features gemischt
- Seeds mit Struktur vermischt

✅ **RICHTIG:**
- ~30 Migrations-Dateien insgesamt
- Schemas zentral (000_schemas.sql)
- LMs in 04_LearningMethods/
- Features in 05_SystemFeatures/
- Seeds separat in 00_Seeds/

---

**Ziel:** Ein Senior Dev öffnet migrations/ und versteht sofort die Architektur. ✓
