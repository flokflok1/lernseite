# Kurs Studio - Database Schema

**Datum:** 2025-01-07
**Status:** Schema-Design
**Scope:** Komplette Persistierung aller Studio-Aktivitäten

---

## Übersicht: Neue Tabellen

```
🗄️ Kurs Studio Datenmodell

├── authoring_sessions          ← Studio-Sessions
├── authoring_files             ← Hochgeladene Dateien
├── authoring_analysis          ← KI-Analysen
├── authoring_dialogs           ← KI-Dialog-Historie
├── authoring_plans             ← Lehrpläne/Entwürfe
├── authoring_generations       ← Generierungs-Jobs
├── authoring_refinements       ← Iterative Verbesserungen
└── authoring_snapshots         ← Versions-Historie
```

---

## 1. Authoring Sessions (Studio-Sitzungen)

```sql
CREATE TABLE authoring_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Benutzer & Organisation
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    organisation_id UUID REFERENCES organisations(organisation_id),

    -- Session-Info
    session_name VARCHAR(255),
    session_type VARCHAR(50) NOT NULL DEFAULT 'full_course',
        -- 'full_course', 'chapter_only', 'lesson_only', 'refinement'

    -- Zielgruppe
    target_audience JSONB,
        -- {
        --   "type": "apprentice|student|professional|retraining",
        --   "age_range": "16-18",
        --   "prior_knowledge": "basic|intermediate|advanced",
        --   "exam_prep": true,
        --   "exam_type": "IHK|University|Certification",
        --   "custom_notes": "..."
        -- }

    -- Workflow-State
    current_phase VARCHAR(50) NOT NULL DEFAULT 'upload',
        -- 'upload', 'analysis', 'dialog', 'generation', 'refinement', 'preview', 'completed'
    phase_data JSONB,
        -- Phase-spezifische Daten

    -- Kurs-Referenz (nach Generierung)
    course_id UUID REFERENCES courses(course_id) ON DELETE SET NULL,

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'active',
        -- 'active', 'paused', 'completed', 'archived'

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_activity_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,

    -- Metadata
    total_files INT DEFAULT 0,
    total_ai_cost DECIMAL(10,2) DEFAULT 0.00,
    estimated_duration_hours INT,

    CONSTRAINT chk_session_type CHECK (session_type IN (
        'full_course', 'chapter_only', 'lesson_only', 'refinement'
    )),
    CONSTRAINT chk_phase CHECK (current_phase IN (
        'upload', 'analysis', 'dialog', 'generation', 'refinement', 'preview', 'completed'
    )),
    CONSTRAINT chk_status CHECK (status IN (
        'active', 'paused', 'completed', 'archived'
    ))
);

CREATE INDEX idx_authoring_sessions_user ON authoring_sessions(user_id);
CREATE INDEX idx_authoring_sessions_org ON authoring_sessions(organisation_id);
CREATE INDEX idx_authoring_sessions_course ON authoring_sessions(course_id);
CREATE INDEX idx_authoring_sessions_status ON authoring_sessions(status, current_phase);
CREATE INDEX idx_authoring_sessions_activity ON authoring_sessions(last_activity_at DESC);
```

---

## 2. Authoring Files (Hochgeladene Dateien)

```sql
CREATE TABLE authoring_files (
    file_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES authoring_sessions(session_id) ON DELETE CASCADE,

    -- Datei-Info
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
        -- 'pdf', 'docx', 'pptx', 'xlsx', 'txt', 'md', 'video', 'audio', 'image'
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100),

    -- Storage
    storage_path TEXT NOT NULL,
        -- S3/Local path
    storage_provider VARCHAR(50) DEFAULT 'local',
        -- 'local', 's3', 'azure', 'gcp'

    -- Content-Extraktion
    extracted_text TEXT,
        -- Volltext aus PDF/DOCX
    extracted_metadata JSONB,
        -- {
        --   "page_count": 120,
        --   "author": "...",
        --   "creation_date": "...",
        --   "language": "de",
        --   "has_images": true,
        --   "has_tables": true,
        --   "keywords": [...]
        -- }

    -- Analyse-Status
    analysis_status VARCHAR(50) DEFAULT 'pending',
        -- 'pending', 'processing', 'completed', 'failed'
    analysis_progress INT DEFAULT 0,
        -- 0-100

    -- AI-Processing
    ai_analysis_id UUID REFERENCES authoring_analysis(analysis_id),

    -- Timestamps
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMP,

    CONSTRAINT chk_file_type CHECK (file_type IN (
        'pdf', 'docx', 'pptx', 'xlsx', 'txt', 'md', 'video', 'audio', 'image', 'other'
    )),
    CONSTRAINT chk_analysis_status CHECK (analysis_status IN (
        'pending', 'processing', 'completed', 'failed'
    ))
);

CREATE INDEX idx_authoring_files_session ON authoring_files(session_id);
CREATE INDEX idx_authoring_files_type ON authoring_files(file_type);
CREATE INDEX idx_authoring_files_status ON authoring_files(analysis_status);
```

---

## 3. Authoring Analysis (KI-Analysen)

```sql
CREATE TABLE authoring_analysis (
    analysis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES authoring_sessions(session_id) ON DELETE CASCADE,

    -- Analysierte Dateien
    file_ids UUID[] NOT NULL,
        -- Array of file_ids

    -- Analyse-Typ
    analysis_type VARCHAR(50) NOT NULL,
        -- 'initial', 'multi_file', 'exam_pattern', 'content_structure', 'quality_check'

    -- Ergebnisse
    topics_found JSONB,
        -- [
        --   {"topic": "Netzwerke", "percentage": 34, "subtopics": [...]},
        --   {"topic": "Datenbanken", "percentage": 28, ...}
        -- ]

    difficulty_analysis JSONB,
        -- {
        --   "overall": "intermediate",
        --   "trend": "+15% since 2020",
        --   "distribution": {"basic": 20, "intermediate": 50, "advanced": 30}
        -- }

    exam_patterns JSONB,
        -- Nur bei Prüfungs-PDFs
        -- {
        --   "years_analyzed": [2018, 2019, ..., 2024],
        --   "question_types": {"multiple_choice": 45, "practical": 30, "essay": 25},
        --   "frequent_topics": [...],
        --   "new_topics": {"year": 2023, "topics": ["Cloud", "DevOps"]}
        -- }

    content_structure JSONB,
        -- Vorgeschlagene Struktur
        -- {
        --   "suggested_chapters": 12,
        --   "suggested_lessons_per_chapter": 8,
        --   "total_hours": 72,
        --   "structure": [
        --     {"chapter": 1, "title": "...", "topics": [...], "duration_hours": 6}
        --   ]
        -- }

    quality_metrics JSONB,
        -- {
        --   "completeness": 85,
        --   "clarity": 90,
        --   "exam_relevance": 96,
        --   "practical_examples": 60
        -- }

    -- AI-Info
    ai_provider VARCHAR(50) NOT NULL,
        -- 'anthropic', 'openai', 'local'
    ai_model VARCHAR(100) NOT NULL,
    tokens_used INT NOT NULL,
    processing_time_seconds INT,

    -- Timestamps
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,

    CONSTRAINT chk_analysis_type CHECK (analysis_type IN (
        'initial', 'multi_file', 'exam_pattern', 'content_structure', 'quality_check'
    ))
);

CREATE INDEX idx_authoring_analysis_session ON authoring_analysis(session_id);
CREATE INDEX idx_authoring_analysis_type ON authoring_analysis(analysis_type);
```

---

## 4. Authoring Dialogs (KI-Dialog-Historie)

```sql
CREATE TABLE authoring_dialogs (
    dialog_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES authoring_sessions(session_id) ON DELETE CASCADE,
    analysis_id UUID REFERENCES authoring_analysis(analysis_id),

    -- Dialog-Verlauf
    message_index INT NOT NULL,
        -- Reihenfolge im Dialog
    role VARCHAR(20) NOT NULL,
        -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,

    -- Kontext
    dialog_phase VARCHAR(50),
        -- 'planning', 'refinement', 'question', 'suggestion'

    -- Structured Data (bei AI-Antworten)
    structured_data JSONB,
        -- {
        --   "action": "suggest_structure",
        --   "suggestions": [...],
        --   "reasoning": "..."
        -- }

    -- AI-Info (nur bei assistant-messages)
    ai_provider VARCHAR(50),
    ai_model VARCHAR(100),
    tokens_used INT,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_role CHECK (role IN ('user', 'assistant', 'system')),
    CONSTRAINT chk_dialog_phase CHECK (dialog_phase IN (
        'planning', 'refinement', 'question', 'suggestion', 'approval'
    ))
);

CREATE INDEX idx_authoring_dialogs_session ON authoring_dialogs(session_id);
CREATE INDEX idx_authoring_dialogs_order ON authoring_dialogs(session_id, message_index);
```

---

## 5. Authoring Plans (Lehrpläne/Entwürfe)

```sql
CREATE TABLE authoring_plans (
    plan_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES authoring_sessions(session_id) ON DELETE CASCADE,

    -- Plan-Info
    plan_name VARCHAR(255) NOT NULL,
    plan_version INT NOT NULL DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
        -- Nur eine aktive Version pro Session

    -- Lehrplan-Struktur
    course_metadata JSONB NOT NULL,
        -- {
        --   "title": "IHK Fachinformatiker 2025",
        --   "description": "...",
        --   "target_audience": {...},
        --   "estimated_hours": 72,
        --   "difficulty": "intermediate"
        -- }

    chapters JSONB NOT NULL,
        -- [
        --   {
        --     "chapter_number": 1,
        --     "title": "Netzwerk-Grundlagen",
        --     "description": "...",
        --     "duration_hours": 6,
        --     "lessons": [
        --       {
        --         "lesson_number": 1,
        --         "title": "OSI-Modell",
        --         "learning_methods": [
        --           {"type": "LM00", "title": "Tiefgehende Erklärung"},
        --           {"type": "LM03", "title": "Schichten-Diagramm"}
        --         ]
        --       }
        --     ]
        --   }
        -- ]

    learning_objectives JSONB,
        -- [
        --   {"chapter": 1, "objectives": ["...", "..."]},
        --   ...
        -- ]

    exam_integration JSONB,
        -- {
        --   "exam_questions_included": 80,
        --   "exam_years": [2018, ..., 2024],
        --   "mock_exams": 3
        -- }

    -- Status
    approval_status VARCHAR(50) DEFAULT 'draft',
        -- 'draft', 'approved', 'rejected', 'in_revision'
    approved_by UUID REFERENCES users(user_id),
    approved_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_approval_status CHECK (approval_status IN (
        'draft', 'approved', 'rejected', 'in_revision'
    ))
);

CREATE INDEX idx_authoring_plans_session ON authoring_plans(session_id);
CREATE INDEX idx_authoring_plans_active ON authoring_plans(session_id, is_active) WHERE is_active = true;
CREATE INDEX idx_authoring_plans_version ON authoring_plans(session_id, plan_version DESC);
```

---

## 6. Authoring Generations (Generierungs-Jobs)

```sql
CREATE TABLE authoring_generations (
    generation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES authoring_sessions(session_id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES authoring_plans(plan_id),

    -- Generation-Scope
    generation_scope VARCHAR(50) NOT NULL,
        -- 'full_course', 'single_chapter', 'single_lesson', 'learning_methods'
    scope_details JSONB,
        -- {"chapter_id": "...", "lesson_id": "..."} etc.

    -- Progress
    status VARCHAR(50) NOT NULL DEFAULT 'queued',
        -- 'queued', 'running', 'completed', 'failed', 'cancelled'
    progress_percentage INT DEFAULT 0,
    current_step VARCHAR(100),
        -- "Generiere Kapitel 3 von 12..."

    -- Ergebnisse
    generated_course_id UUID REFERENCES courses(course_id),
    generated_chapters INT DEFAULT 0,
    generated_lessons INT DEFAULT 0,
    generated_learning_methods INT DEFAULT 0,

    -- AI-Info
    ai_provider VARCHAR(50) NOT NULL,
    ai_model VARCHAR(100) NOT NULL,
    total_tokens_used INT DEFAULT 0,
    estimated_cost DECIMAL(10,4),

    -- Performance
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    processing_time_seconds INT,

    -- Fehler
    error_message TEXT,
    error_details JSONB,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_generation_scope CHECK (generation_scope IN (
        'full_course', 'single_chapter', 'single_lesson', 'learning_methods'
    )),
    CONSTRAINT chk_generation_status CHECK (status IN (
        'queued', 'running', 'completed', 'failed', 'cancelled'
    ))
);

CREATE INDEX idx_authoring_generations_session ON authoring_generations(session_id);
CREATE INDEX idx_authoring_generations_plan ON authoring_generations(plan_id);
CREATE INDEX idx_authoring_generations_status ON authoring_generations(status);
CREATE INDEX idx_authoring_generations_course ON authoring_generations(generated_course_id);
```

---

## 7. Authoring Refinements (Iterative Verbesserungen)

```sql
CREATE TABLE authoring_refinements (
    refinement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES authoring_sessions(session_id) ON DELETE CASCADE,
    generation_id UUID REFERENCES authoring_generations(generation_id),

    -- Target
    target_type VARCHAR(50) NOT NULL,
        -- 'course', 'chapter', 'lesson', 'learning_method'
    target_id UUID NOT NULL,
        -- course_id, chapter_id, lesson_id, learning_method_instance_id

    -- Refinement-Request
    refinement_type VARCHAR(50) NOT NULL,
        -- 'simplify', 'expand', 'split', 'merge', 'improve_quality', 'add_examples', 'adjust_difficulty'
    user_request TEXT NOT NULL,
        -- "Kapitel 5 zu schwer, bitte aufteilen"

    -- AI-Response
    ai_suggestion TEXT,
        -- "Ich schlage vor, Kapitel 5 in 5.1 Basics und 5.2 Advanced aufzuteilen"

    ai_actions JSONB,
        -- [
        --   {"action": "split_chapter", "chapter_id": "...", "new_chapters": 2},
        --   {"action": "add_examples", "lesson_id": "...", "example_count": 10}
        -- ]

    -- Approval
    user_approved BOOLEAN,
    applied BOOLEAN DEFAULT false,
    applied_at TIMESTAMP,

    -- AI-Info
    ai_provider VARCHAR(50),
    ai_model VARCHAR(100),
    tokens_used INT,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_target_type CHECK (target_type IN (
        'course', 'chapter', 'lesson', 'learning_method'
    )),
    CONSTRAINT chk_refinement_type CHECK (refinement_type IN (
        'simplify', 'expand', 'split', 'merge', 'improve_quality',
        'add_examples', 'adjust_difficulty', 'custom'
    ))
);

CREATE INDEX idx_authoring_refinements_session ON authoring_refinements(session_id);
CREATE INDEX idx_authoring_refinements_generation ON authoring_refinements(generation_id);
CREATE INDEX idx_authoring_refinements_target ON authoring_refinements(target_type, target_id);
CREATE INDEX idx_authoring_refinements_applied ON authoring_refinements(applied);
```

---

## 8. Authoring Snapshots (Versions-Historie)

```sql
CREATE TABLE authoring_snapshots (
    snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES authoring_sessions(session_id) ON DELETE CASCADE,

    -- Snapshot-Info
    snapshot_name VARCHAR(255),
    snapshot_type VARCHAR(50) NOT NULL,
        -- 'manual', 'auto_save', 'before_generation', 'after_refinement'
    description TEXT,

    -- Snapshot-Data
    plan_snapshot JSONB,
        -- Kopie des authoring_plans
    course_snapshot JSONB,
        -- Kopie des generierten Kurses

    -- Version
    version_number INT NOT NULL,
    parent_snapshot_id UUID REFERENCES authoring_snapshots(snapshot_id),

    -- Metadata
    created_by UUID NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_snapshot_type CHECK (snapshot_type IN (
        'manual', 'auto_save', 'before_generation', 'after_refinement', 'milestone'
    ))
);

CREATE INDEX idx_authoring_snapshots_session ON authoring_snapshots(session_id);
CREATE INDEX idx_authoring_snapshots_version ON authoring_snapshots(session_id, version_number DESC);
CREATE INDEX idx_authoring_snapshots_type ON authoring_snapshots(snapshot_type);
```

---

## Integration mit bestehenden Tabellen

### Verknüpfungen:

```sql
-- Nach erfolgreicher Generierung:
authoring_sessions.course_id → courses.course_id
authoring_generations.generated_course_id → courses.course_id

-- Kurs-Metadaten erweitern:
ALTER TABLE courses ADD COLUMN authoring_session_id UUID REFERENCES authoring_sessions(session_id);
ALTER TABLE courses ADD COLUMN generation_id UUID REFERENCES authoring_generations(generation_id);
ALTER TABLE courses ADD COLUMN ai_generated BOOLEAN DEFAULT false;
ALTER TABLE courses ADD COLUMN ai_generation_date TIMESTAMP;

-- Chapter-Level:
ALTER TABLE chapters ADD COLUMN ai_generated BOOLEAN DEFAULT false;
ALTER TABLE chapters ADD COLUMN ai_source_files UUID[];
    -- Array of authoring_files.file_id

-- Lesson-Level:
ALTER TABLE lessons ADD COLUMN ai_generated BOOLEAN DEFAULT false;
ALTER TABLE lessons ADD COLUMN ai_prompt_used TEXT;

-- Learning Method Instances:
ALTER TABLE learning_method_instances ADD COLUMN ai_generated BOOLEAN DEFAULT false;
ALTER TABLE learning_method_instances ADD COLUMN ai_generation_context JSONB;
```

---

## Beispiel-Workflow in der DB

### 1. User startet Session
```sql
INSERT INTO authoring_sessions (user_id, session_name, target_audience)
VALUES ('user-123', 'IHK Fachinformatiker 2025', '{
    "type": "apprentice",
    "age_range": "16-18",
    "exam_prep": true,
    "exam_type": "IHK"
}');
-- → session_id: abc-def
```

### 2. User lädt 7 PDFs hoch
```sql
INSERT INTO authoring_files (session_id, filename, file_type, ...)
VALUES
    ('abc-def', 'IHK_2018.pdf', 'pdf', ...),
    ('abc-def', 'IHK_2019.pdf', 'pdf', ...),
    ... -- 5 weitere
```

### 3. KI analysiert Dateien
```sql
INSERT INTO authoring_analysis (session_id, file_ids, analysis_type, topics_found, exam_patterns, ...)
VALUES ('abc-def', ARRAY['file-1', 'file-2', ...], 'exam_pattern', '{
    "topics": [
        {"topic": "Netzwerke", "percentage": 34},
        {"topic": "Datenbanken", "percentage": 28}
    ]
}', '{
    "years_analyzed": [2018, 2019, ..., 2024],
    "frequent_topics": ["TCP/IP", "SQL", "OOP"]
}', ...);
-- → analysis_id: xyz-123
```

### 4. Dialog mit KI
```sql
-- User
INSERT INTO authoring_dialogs (session_id, analysis_id, message_index, role, content)
VALUES ('abc-def', 'xyz-123', 1, 'user', 'Für welche Zielgruppe ist der Kurs?');

-- AI
INSERT INTO authoring_dialogs (session_id, analysis_id, message_index, role, content, structured_data)
VALUES ('abc-def', 'xyz-123', 2, 'assistant', 'Azubis, 2. Lehrjahr...', '{
    "action": "suggest_structure",
    "suggestions": {"chapters": 12, "duration": 72}
}');
```

### 5. Lehrplan erstellen
```sql
INSERT INTO authoring_plans (session_id, plan_name, course_metadata, chapters, ...)
VALUES ('abc-def', 'IHK Lehrplan v1', '{
    "title": "IHK Fachinformatiker 2025",
    "estimated_hours": 72
}', '[
    {"chapter_number": 1, "title": "Netzwerk-Grundlagen", "lessons": [...]}
]', ...);
-- → plan_id: plan-456
```

### 6. Generierung starten
```sql
INSERT INTO authoring_generations (session_id, plan_id, generation_scope, ...)
VALUES ('abc-def', 'plan-456', 'full_course', ...);
-- → generation_id: gen-789

-- Progress-Updates während Generierung:
UPDATE authoring_generations
SET status = 'running', progress_percentage = 25, current_step = 'Generiere Kapitel 3 von 12'
WHERE generation_id = 'gen-789';

-- Nach Abschluss:
UPDATE authoring_generations
SET status = 'completed', progress_percentage = 100, generated_course_id = 'course-new'
WHERE generation_id = 'gen-789';
```

### 7. User verfeinert
```sql
INSERT INTO authoring_refinements (session_id, generation_id, target_type, target_id, refinement_type, user_request, ...)
VALUES ('abc-def', 'gen-789', 'chapter', 'chapter-5', 'split', 'Kapitel 5 zu schwer, bitte aufteilen', ...);
```

### 8. Snapshot erstellen
```sql
INSERT INTO authoring_snapshots (session_id, snapshot_type, plan_snapshot, course_snapshot, version_number)
VALUES ('abc-def', 'milestone', '{...}', '{...}', 1);
```

---

## Queries für UI

### Studio-Dashboard
```sql
-- Alle aktiven Sessions des Users
SELECT
    s.*,
    COUNT(DISTINCT f.file_id) as file_count,
    COUNT(DISTINCT d.dialog_id) as dialog_count,
    g.status as generation_status,
    g.progress_percentage
FROM authoring_sessions s
LEFT JOIN authoring_files f ON s.session_id = f.session_id
LEFT JOIN authoring_dialogs d ON s.session_id = d.session_id
LEFT JOIN authoring_generations g ON s.session_id = g.session_id AND g.status IN ('queued', 'running')
WHERE s.user_id = $1 AND s.status = 'active'
GROUP BY s.session_id, g.status, g.progress_percentage
ORDER BY s.last_activity_at DESC;
```

### Datei-Analyse-Status
```sql
SELECT
    f.*,
    a.topics_found,
    a.difficulty_analysis,
    a.exam_patterns
FROM authoring_files f
LEFT JOIN authoring_analysis a ON f.ai_analysis_id = a.analysis_id
WHERE f.session_id = $1
ORDER BY f.uploaded_at;
```

### Dialog-Historie
```sql
SELECT *
FROM authoring_dialogs
WHERE session_id = $1
ORDER BY message_index ASC;
```

### Generierungs-Progress
```sql
SELECT
    generation_id,
    status,
    progress_percentage,
    current_step,
    generated_chapters,
    generated_lessons,
    generated_learning_methods,
    total_tokens_used,
    estimated_cost
FROM authoring_generations
WHERE session_id = $1
ORDER BY created_at DESC
LIMIT 1;
```

---

## Speicher-Schätzung

**Pro Session (durchschnittlich):**
- authoring_sessions: 2 KB
- authoring_files (5 Dateien): 50 MB (Dateien) + 50 KB (Metadaten)
- authoring_analysis: 100 KB
- authoring_dialogs (20 Messages): 20 KB
- authoring_plans: 500 KB
- authoring_generations: 10 KB
- authoring_refinements (10): 50 KB
- authoring_snapshots (3): 1.5 MB

**Total pro Session:** ~52 MB

**Bei 1000 aktiven Sessions:** ~52 GB

---

## Migration SQL

```sql
-- Migration erstellen
-- backend/migrations/03_AI/070_authoring_studio_system.sql

BEGIN;

-- 1. Sessions
CREATE TABLE authoring_sessions (...);

-- 2. Files
CREATE TABLE authoring_files (...);

-- 3. Analysis
CREATE TABLE authoring_analysis (...);

-- 4. Dialogs
CREATE TABLE authoring_dialogs (...);

-- 5. Plans
CREATE TABLE authoring_plans (...);

-- 6. Generations
CREATE TABLE authoring_generations (...);

-- 7. Refinements
CREATE TABLE authoring_refinements (...);

-- 8. Snapshots
CREATE TABLE authoring_snapshots (...);

-- 9. Extend existing tables
ALTER TABLE courses ADD COLUMN authoring_session_id UUID;
ALTER TABLE courses ADD COLUMN ai_generated BOOLEAN DEFAULT false;
-- ... weitere ALTER statements

COMMIT;
```

---

**Status:** ✅ SCHEMA KOMPLETT
**Nächster Schritt:** Migration erstellen + Backend-Repositories bauen
