-- ============================================================================
-- Migration: 030_learning_methods_core.sql
-- Version: 1.0.0
-- Description: Learning Methods Core (12 Content-Lernmethoden + Progress Tracking)
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 2 (Content Layer)
-- Dependencies: 000_schemas.sql (learning_methods schema)
--
-- ZENTRAL: Dies ist die EINZIGE Datei für Lernmethoden-Strukturen
-- - Content-LMs (ERWEITERBAR): learning_method_types
-- - Instanzen pro Kapitel: learning_method_instances
-- - Fortschritt-Tracking: learning_method_progress
--
-- DESIGN-PHILOSOPHIE: ERWEITERBAR, NICHT HARDCODED
-- - Keine CHECK Constraints für max method_type (erlaubt Wachstum)
-- - Verwendung von active/deprecated Flags statt Löschung
-- - Application-Logic prüft Limits, nicht Datenbank
--
-- AKTUELL: 12 Content-Lernmethoden in 3 Gruppen
-- Gruppe A (Erklärend): Flashcards, Lückentext, Freitext, Multiple Choice, True/False
-- Gruppe B (Praxis): Code Challenge, Case Study, Simulation, Peer Review Exercise
-- Gruppe C (Prüfung): Objective Assessment, Practical Exam, Portfolio Assessment
-- ZUKÜNFTIG: Kann auf 13+ erweitert werden, wenn Geschäftsanforderung es verlangt
--
-- NICHT verwechseln mit System-Features (25+ Infrastructure-Tools)!
-- System-Features sind in 05_SystemFeatures/040_system_features_core.sql
-- ============================================================================

-- ============================================================================
-- TABLE: learning_methods.learning_method_types
-- Description: Content-Lernmethoden - Aufgabenformate (ERWEITERBAR)
--
-- CURRENT SETUP (12 Methods):
-- Gruppe A (Erklärend): Flashcards, Lückentext, Freitext, Multiple Choice, True/False (5 Methoden)
-- Gruppe B (Praxis): Code Challenge, Case Study, Simulation, Peer Review Exercise (4 Methoden)
-- Gruppe C (Prüfung): Objective Assessment, Practical Exam, Portfolio Assessment (3 Methoden)
--
-- FUTURE EXTENSIBILITY:
-- - Kann auf Gruppe D, E, F erweitert werden
-- - Neue method_types können hinzugefügt werden
-- - Alte Methoden werden deprecated markiert, nicht gelöscht
-- - active Flag erlaubt Disabling ohne Datenverlust
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_methods.learning_method_types (
    type_id SERIAL PRIMARY KEY,
    method_type INTEGER NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,

    -- Gruppierung
    group_code CHAR(1) NOT NULL,  -- 'A' (erklärend), 'B' (praxis), 'C' (prüfung)

    -- Tier
    tier VARCHAR(20) NOT NULL,  -- 'basic' oder 'premium'

    -- KI-Nutzung
    ki_usage VARCHAR(20) NOT NULL,  -- 'intensive', 'medium', 'optional'

    -- Backend Configuration (from learning_method_mapping.py)
    prompt_template VARCHAR(255),  -- KI Prompt Template key (e.g., 'deep_explanation', 'flashcards')
    default_config JSONB DEFAULT '{}',  -- Default LM-specific config
    agent_support JSONB,  -- Agent support configuration: {agent_can_handle, requires_fresh_ai, knowledge_domains, knowledge_cacheable, complexity_threshold}

    -- Frontend Configuration
    ui_schema JSONB DEFAULT '{}',  -- Dynamic form schema for frontend rendering

    -- Weitere Konfiguration
    active BOOLEAN DEFAULT TRUE,  -- Allows disabling without deleting
    deprecated BOOLEAN DEFAULT FALSE,  -- For future methods, mark old ones as deprecated
    config JSONB DEFAULT '{}',  -- Legacy config (kept for backward compatibility)
    icon VARCHAR(50),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- CONSTRAINTS - FLEXIBLE FOR EXTENSIBILITY
    -- Application logic enforces max reasonable limit, not database constraint
    CONSTRAINT chk_method_type CHECK (method_type >= 0),  -- Allow future growth
    CONSTRAINT chk_group_code CHECK (group_code IN ('A', 'B', 'C', 'D', 'E', 'F')),  -- Allow future groups
    CONSTRAINT chk_ki_usage CHECK (ki_usage IN ('intensive', 'medium', 'optional')),
    CONSTRAINT chk_active_not_deprecated CHECK (NOT (active = FALSE AND deprecated = TRUE))
);

CREATE INDEX IF NOT EXISTS idx_lm_types_method_type ON learning_methods.learning_method_types(method_type);
CREATE INDEX IF NOT EXISTS idx_lm_types_group ON learning_methods.learning_method_types(group_code);
CREATE INDEX IF NOT EXISTS idx_lm_types_tier ON learning_methods.learning_method_types(tier);
CREATE INDEX IF NOT EXISTS idx_lm_types_active ON learning_methods.learning_method_types(active) WHERE active = TRUE;

COMMENT ON TABLE learning_methods.learning_method_types IS '12 Content-Lernmethoden in 3 Gruppen A-C';

-- ============================================================================
-- TABLE: learning_methods.learning_method_instances
-- Description: Konkrete Aufgaben-Instanzen pro Kapitel (Aufgaben im Kurs)
--
-- Jedes Chapter kann mehrere Instances verschiedener Lernmethoden haben.
-- Beispiel: Kapitel "Algebra Basics" hat:
--  - Flashcards Instance: Für Vokabeln lernen
--  - Multiple Choice Instance: Quiz zum Verständnis prüfen
--  - Objective Assessment Instance: Kompetenz nachweisen
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_methods.learning_method_instances (
    method_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chapter_id UUID REFERENCES courses.chapters(chapter_id) ON DELETE CASCADE,
    method_type INTEGER NOT NULL REFERENCES learning_methods.learning_method_types(method_type) ON DELETE RESTRICT,

    -- Instance Metadata
    title VARCHAR(255) NOT NULL,
    instructions TEXT,

    -- Content & Solution (JSONB for flexibility)
    data JSONB NOT NULL,  -- Aufgaben-Inhalt (format varies by method_type)
    solution JSONB,  -- Lösungsschlüssel (optional)

    -- Difficulty & Tier
    tier VARCHAR(20) NOT NULL,  -- 'basic' oder 'premium'
    duration_minutes INTEGER,
    difficulty VARCHAR(20),

    -- Sequencing
    order_index INTEGER DEFAULT 0,

    -- Publishing
    published BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lm_instances_chapter ON learning_methods.learning_method_instances(chapter_id);
CREATE INDEX IF NOT EXISTS idx_lm_instances_type ON learning_methods.learning_method_instances(method_type);
CREATE INDEX IF NOT EXISTS idx_lm_instances_tier ON learning_methods.learning_method_instances(tier);
CREATE INDEX IF NOT EXISTS idx_lm_instances_data ON learning_methods.learning_method_instances USING GIN(data);
CREATE INDEX IF NOT EXISTS idx_lm_instances_published ON learning_methods.learning_method_instances(published) WHERE published = TRUE;
CREATE INDEX IF NOT EXISTS idx_lm_instances_order ON learning_methods.learning_method_instances(chapter_id, order_index);

COMMENT ON TABLE learning_methods.learning_method_instances IS '12 Content-Lernmethoden: Gruppe A (Flashcards, Lückentext, Freitext, Multiple Choice, True/False), B (Code Challenge, Case Study, Simulation, Peer Review), C (Assessment, Practical Exam, Portfolio)';
COMMENT ON COLUMN learning_methods.learning_method_instances.method_type IS 'Content-LM IDs: 0-11 (12 Methoden). Foreign Key to learning_method_types.';
COMMENT ON COLUMN learning_methods.learning_method_instances.data IS 'JSONB structure varies by method_type (questions, flashcards, code, etc.)';

-- ============================================================================
-- TABLE: learning_methods.learning_method_progress
-- Description: Student completion & performance tracking for learning methods
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_methods.learning_method_progress (
    progress_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    method_id UUID REFERENCES learning_methods.learning_method_instances(method_id) ON DELETE CASCADE,
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,

    -- Completion tracking
    completed_at TIMESTAMPTZ DEFAULT NOW(),
    time_spent_seconds INTEGER,

    -- Performance
    score DECIMAL(5,2),  -- 0-100
    attempts INTEGER DEFAULT 1,

    -- Student answer (for review/evaluation)
    user_answer JSONB,

    -- Constraints
    UNIQUE (method_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_lm_progress_method ON learning_methods.learning_method_progress(method_id);
CREATE INDEX IF NOT EXISTS idx_lm_progress_user ON learning_methods.learning_method_progress(user_id, completed_at DESC);
CREATE INDEX IF NOT EXISTS idx_lm_progress_score ON learning_methods.learning_method_progress(score);

COMMENT ON TABLE learning_methods.learning_method_progress IS 'User completion and performance tracking for learning methods';

-- ============================================================================
-- End of Migration: 030_learning_methods_core.sql
-- ============================================================================
