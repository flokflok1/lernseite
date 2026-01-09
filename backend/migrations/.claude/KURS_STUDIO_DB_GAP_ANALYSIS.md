# Kurs Studio - DB Gap Analysis

**Datum:** 2025-01-07
**Status:** Vergleich: Konzept vs. Bestehende Migrationen

---

## Bestehende Tabellen (3 Migrationen)

### Migration 048: ai_authoring_studio.sql
```sql
✅ ai_pipeline.ai_authoring_sessions
   - session_id, user_id, course_id, chapter_id
   - session_name, status
   - source_type, source_data
   - ai_config
   - generated_theory, generated_lessons, generated_methods
   - current_step, steps_completed

✅ ai_pipeline.ai_session_snapshots
   - snapshot_id, session_id
   - snapshot_data, description
   - sequence_number, is_current

✅ ai_pipeline.ai_generation_variants
   - variant_id, session_id
   - variant_type, variant_index
   - content, ai_provider, ai_model
```

### Migration 061: authoring_actions.sql
```sql
✅ learning_methods.authoring_actions
   - action_id, action_key, category
   - label, description, icon
   - prompt_template
   - requires_context, variables
   - action_type, output_format

✅ learning_methods.authoring_action_usage
   - usage_id, action_id, user_id
   - context_data
   - was_successful, tokens_used
```

### Migration 066: course_authoring_sessions.sql
```sql
✅ courses.course_authoring_sessions
   - session_id, course_id, created_by
   - model_profile
   - draft_structure (Kurs-Entwurf)
   - chat_history
   - file_context
   - status, total_tokens_used
```

---

## Fehlende Komponenten (Konzept vs. Realität)

### ❌ FEHLT: Datei-Upload System
**Geplant:**
```sql
authoring_files
  - file_id, session_id
  - filename, file_type, file_size
  - storage_path
  - extracted_text, extracted_metadata
  - analysis_status
```

**Bestehend:** Nur `file_context JSONB` in `course_authoring_sessions`

**Gap:** Keine dedizierte Datei-Verwaltung!

---

### ❌ FEHLT: Multi-File KI-Analyse
**Geplant:**
```sql
authoring_analysis
  - analysis_id, session_id
  - file_ids[] (Multi-File!)
  - analysis_type ('exam_pattern', 'multi_file')
  - topics_found, difficulty_analysis
  - exam_patterns (7 Jahre Prüfungen!)
  - content_structure
```

**Bestehend:** `source_data JSONB` in `ai_authoring_sessions` (nur Single-Source!)

**Gap:** Keine Multi-File Analyse! Keine Prüfungs-Muster-Erkennung!

---

### ⚠️ TEILWEISE: Dialog-System
**Geplant:**
```sql
authoring_dialogs
  - dialog_id, session_id
  - message_index, role, content
  - structured_data
  - tokens_used
```

**Bestehend:** `chat_history JSONB` in `course_authoring_sessions`

**Gap:** Nur flaches Array, keine strukturierte Dialog-Historie!

---

### ⚠️ TEILWEISE: Lehrplan-System
**Geplant:**
```sql
authoring_plans
  - plan_id, session_id
  - plan_name, plan_version
  - course_metadata, chapters
  - learning_objectives
  - exam_integration
  - approval_status
```

**Bestehend:** `draft_structure JSONB` in `course_authoring_sessions`

**Gap:** Keine Versionierung! Kein Approval-Workflow!

---

### ❌ FEHLT: Generierungs-Jobs
**Geplant:**
```sql
authoring_generations
  - generation_id, session_id, plan_id
  - generation_scope ('full_course', 'single_chapter')
  - status, progress_percentage
  - generated_course_id, generated_chapters
  - total_tokens_used, estimated_cost
```

**Bestehend:** Nichts!

**Gap:** Keine Job-Verwaltung für lange Generierungen!

---

### ❌ FEHLT: Refinements
**Geplant:**
```sql
authoring_refinements
  - refinement_id, session_id
  - target_type, target_id
  - refinement_type ('simplify', 'expand', 'split')
  - user_request, ai_suggestion
  - user_approved, applied
```

**Bestehend:** Nichts!

**Gap:** Keine iterative Verbesserung dokumentiert!

---

## Mapping: Konzept → Bestehende Tabellen

| Konzept | Bestehende Tabelle | Status | Gap |
|---------|-------------------|--------|-----|
| authoring_sessions | ai_authoring_sessions | ✅ Vorhanden | Erweitern für Multi-File |
| authoring_files | - | ❌ FEHLT | Neu erstellen |
| authoring_analysis | - | ❌ FEHLT | Neu erstellen |
| authoring_dialogs | course_authoring_sessions.chat_history | ⚠️ JSONB | Dedizierte Tabelle besser |
| authoring_plans | course_authoring_sessions.draft_structure | ⚠️ JSONB | Erweitern für Versionierung |
| authoring_generations | - | ❌ FEHLT | Neu erstellen |
| authoring_refinements | - | ❌ FEHLT | Neu erstellen |
| authoring_snapshots | ai_session_snapshots | ✅ Vorhanden | OK |

---

## Empfohlene Migrations-Strategie

### Option A: Erweitern statt neu (Migrations-Regel konform!)

**Erweitere Migration 048 (ai_authoring_studio.sql):**
```sql
-- HINZUFÜGEN zu bestehender Datei:

-- 1. Datei-Upload System
CREATE TABLE IF NOT EXISTS ai_pipeline.authoring_files (...);

-- 2. Multi-File Analyse
CREATE TABLE IF NOT EXISTS ai_pipeline.authoring_analysis (...);

-- 3. Generierungs-Jobs
CREATE TABLE IF NOT EXISTS ai_pipeline.authoring_generations (...);

-- 4. Refinements
CREATE TABLE IF NOT EXISTS ai_pipeline.authoring_refinements (...);

-- 5. Erweitere bestehende Tabelle
ALTER TABLE ai_pipeline.ai_authoring_sessions
  ADD COLUMN IF NOT EXISTS target_audience JSONB,
  ADD COLUMN IF NOT EXISTS exam_integration JSONB,
  ADD COLUMN IF NOT EXISTS multi_file_support BOOLEAN DEFAULT false;
```

**Erweitere Migration 066 (course_authoring_sessions.sql):**
```sql
-- HINZUFÜGEN zu bestehender Datei:

-- 1. Dedizierte Dialog-Tabelle (besser als JSONB)
CREATE TABLE IF NOT EXISTS courses.authoring_dialog_messages (...);

-- 2. Plan-Versionierung
CREATE TABLE IF NOT EXISTS courses.authoring_plan_versions (...);

-- 3. Erweitere bestehende Tabelle
ALTER TABLE courses.course_authoring_sessions
  ADD COLUMN IF NOT EXISTS plan_version INTEGER DEFAULT 1,
  ADD COLUMN IF NOT EXISTS approval_status VARCHAR(50) DEFAULT 'draft',
  ADD COLUMN IF NOT EXISTS approved_by UUID REFERENCES core.users(user_id),
  ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ;
```

---

### Option B: Neue Migration (nur wenn wirklich nötig)

**Neue Migration: 070_authoring_studio_v2.sql**
- Nur für wirklich neue Features
- Wenn bestehende Migrationen zu groß werden
- Bei Breaking Changes

**ABER:** Laut Migrations-Regel bevorzugen wir Option A!

---

## Konkrete TODOs

### 1. Migration 048 erweitern ✏️
```sql
-- am Ende von 048_ai_authoring_studio.sql hinzufügen:

-- ============================================================================
-- FILE UPLOAD SYSTEM (2025-01-07)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.authoring_files (
    file_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_authoring_sessions(session_id) ON DELETE CASCADE,

    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    storage_path TEXT NOT NULL,

    extracted_text TEXT,
    extracted_metadata JSONB,

    analysis_status VARCHAR(50) DEFAULT 'pending',
    ai_analysis_id UUID,

    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_authoring_files_session ON ai_pipeline.authoring_files(session_id);

-- ============================================================================
-- MULTI-FILE AI ANALYSIS (2025-01-07)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.authoring_analysis (
    analysis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_authoring_sessions(session_id) ON DELETE CASCADE,

    file_ids UUID[] NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,

    topics_found JSONB,
    difficulty_analysis JSONB,
    exam_patterns JSONB,
    content_structure JSONB,
    quality_metrics JSONB,

    ai_provider VARCHAR(50) NOT NULL,
    ai_model VARCHAR(100) NOT NULL,
    tokens_used INT NOT NULL,

    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_authoring_analysis_session ON ai_pipeline.authoring_analysis(session_id);

-- ============================================================================
-- GENERATION JOBS (2025-01-07)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.authoring_generations (
    generation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_authoring_sessions(session_id) ON DELETE CASCADE,

    generation_scope VARCHAR(50) NOT NULL,
    scope_details JSONB,

    status VARCHAR(50) DEFAULT 'queued',
    progress_percentage INT DEFAULT 0,
    current_step VARCHAR(100),

    generated_course_id UUID REFERENCES courses.courses(course_id),
    generated_chapters INT DEFAULT 0,
    generated_lessons INT DEFAULT 0,

    ai_provider VARCHAR(50) NOT NULL,
    ai_model VARCHAR(100) NOT NULL,
    total_tokens_used INT DEFAULT 0,

    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    error_message TEXT
);

CREATE INDEX idx_authoring_generations_session ON ai_pipeline.authoring_generations(session_id);

-- ============================================================================
-- REFINEMENTS (2025-01-07)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.authoring_refinements (
    refinement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_authoring_sessions(session_id) ON DELETE CASCADE,
    generation_id UUID REFERENCES ai_pipeline.authoring_generations(generation_id),

    target_type VARCHAR(50) NOT NULL,
    target_id UUID NOT NULL,

    refinement_type VARCHAR(50) NOT NULL,
    user_request TEXT NOT NULL,
    ai_suggestion TEXT,
    ai_actions JSONB,

    user_approved BOOLEAN,
    applied BOOLEAN DEFAULT false,
    applied_at TIMESTAMPTZ,

    ai_provider VARCHAR(50),
    ai_model VARCHAR(100),
    tokens_used INT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_authoring_refinements_session ON ai_pipeline.authoring_refinements(session_id);

-- ============================================================================
-- EXTEND EXISTING TABLE (2025-01-07)
-- ============================================================================
ALTER TABLE ai_pipeline.ai_authoring_sessions
  ADD COLUMN IF NOT EXISTS target_audience JSONB,
  ADD COLUMN IF NOT EXISTS exam_integration JSONB,
  ADD COLUMN IF NOT EXISTS multi_file_support BOOLEAN DEFAULT false;
```

### 2. Migration 066 erweitern ✏️
```sql
-- am Ende von 066_course_authoring_sessions.sql hinzufügen:

-- ============================================================================
-- DIALOG MESSAGES (2025-01-07)
-- ============================================================================
CREATE TABLE IF NOT EXISTS courses.authoring_dialog_messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES courses.course_authoring_sessions(session_id) ON DELETE CASCADE,

    message_index INT NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,

    structured_data JSONB,

    ai_provider VARCHAR(50),
    ai_model VARCHAR(100),
    tokens_used INT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_authoring_dialog_messages_session ON courses.authoring_dialog_messages(session_id, message_index);

-- ============================================================================
-- EXTEND EXISTING TABLE (2025-01-07)
-- ============================================================================
ALTER TABLE courses.course_authoring_sessions
  ADD COLUMN IF NOT EXISTS plan_version INTEGER DEFAULT 1,
  ADD COLUMN IF NOT EXISTS approval_status VARCHAR(50) DEFAULT 'draft'
      CHECK (approval_status IN ('draft', 'approved', 'rejected', 'in_revision')),
  ADD COLUMN IF NOT EXISTS approved_by UUID REFERENCES core.users(user_id),
  ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ;
```

---

## Zusammenfassung

**Was wir haben:**
- ✅ Basis-Sessions (3 Tabellen)
- ✅ Snapshots (Undo/Redo)
- ✅ Actions (Quick-Actions)
- ✅ Draft-System (course_authoring_sessions)

**Was fehlt:**
- ❌ Datei-Upload & Management
- ❌ Multi-File Analyse (7 Jahre Prüfungen!)
- ❌ Generierungs-Jobs mit Progress
- ❌ Refinement-Tracking
- ⚠️ Dialog-Historie (nur JSONB)
- ⚠️ Plan-Versionierung (nur JSONB)

**Strategie:**
1. **Erweitere Migration 048** - 4 neue Tabellen + ALTER
2. **Erweitere Migration 066** - 1 neue Tabelle + ALTER
3. **Kein neue Migration** (Migrations-Regel!)

**Aufwand:** 2 Datei-Edits statt neue Migration

---

**Next Steps:**
1. Migration 048 erweitern
2. Migration 066 erweitern
3. Backend-Repositories erstellen
4. Frontend-Integration

**Status:** ✅ GAP ANALYSIS KOMPLETT
