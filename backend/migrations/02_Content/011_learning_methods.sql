-- ============================================================================
-- Migration: 011_learning_methods.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

-- NOTE: learning_methods schema is created in 01_Core/000_schemas.sql
-- No schema creation needed here

-- ============================================================================
-- TABLE: learning_method_types (moved from 041 - needed as FK dependency)
-- ============================================================================
CREATE TABLE IF NOT EXISTS learning_methods.learning_method_types (
    type_id SERIAL PRIMARY KEY,
    method_type INTEGER NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    group_code CHAR(1) NOT NULL,
    tier VARCHAR(20) NOT NULL,
    ki_usage VARCHAR(20) NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    config JSONB DEFAULT '{}',
    icon VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_method_type CHECK (method_type >= 0 AND method_type <= 11),
    CONSTRAINT chk_group_code CHECK (group_code IN ('A', 'B', 'C'))
);

CREATE INDEX IF NOT EXISTS idx_lm_types_method_type ON learning_methods.learning_method_types(method_type);
CREATE INDEX IF NOT EXISTS idx_lm_types_group ON learning_methods.learning_method_types(group_code);
CREATE INDEX IF NOT EXISTS idx_lm_types_tier ON learning_methods.learning_method_types(tier);
CREATE INDEX IF NOT EXISTS idx_lm_types_active ON learning_methods.learning_method_types(active) WHERE active = TRUE;

COMMENT ON TABLE learning_methods.learning_method_types IS '12 Content-Lernmethoden in 3 Gruppen A-C';

-- ============================================================================
-- TABLE: learning_method_instances
-- ============================================================================
CREATE TABLE IF NOT EXISTS learning_methods.learning_method_instances (
    method_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chapter_id UUID REFERENCES courses.chapters(chapter_id) ON DELETE CASCADE,
    method_type INTEGER NOT NULL REFERENCES learning_methods.learning_method_types(method_type) ON DELETE RESTRICT,
    title VARCHAR(255) NOT NULL,
    instructions TEXT,
    data JSONB NOT NULL,
    solution JSONB,
    tier VARCHAR(20) NOT NULL,
    duration_minutes INTEGER,
    difficulty VARCHAR(20),
    order_index INTEGER DEFAULT 0,
    published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
    -- Note: tier and difficulty validation removed for flexibility
    -- Valid values should be managed through application config
);

CREATE INDEX IF NOT EXISTS idx_lm_instances_chapter ON learning_methods.learning_method_instances(chapter_id);
CREATE INDEX IF NOT EXISTS idx_lm_instances_type ON learning_methods.learning_method_instances(method_type);
CREATE INDEX IF NOT EXISTS idx_lm_instances_tier ON learning_methods.learning_method_instances(tier);
CREATE INDEX IF NOT EXISTS idx_lm_instances_data ON learning_methods.learning_method_instances USING GIN(data);
CREATE INDEX IF NOT EXISTS idx_lm_instances_published ON learning_methods.learning_method_instances(published) WHERE published = TRUE;
CREATE INDEX IF NOT EXISTS idx_lm_instances_order ON learning_methods.learning_method_instances(chapter_id, order_index);

COMMENT ON TABLE learning_methods.learning_method_instances IS '12 Content-Lernmethoden: Gruppe A (lm00-lm04), B (lm05-lm08), C (lm09-lm11). System-Features in support_systems.system_features.';
COMMENT ON COLUMN learning_methods.learning_method_instances.method_type IS 'Content-LM IDs: 0-11 (12 Methoden). Foreign Key to learning_method_types.';
COMMENT ON COLUMN learning_methods.learning_method_instances.data IS 'JSONB structure varies by method_type';
COMMENT ON COLUMN learning_methods.learning_method_instances.tier IS 'basic (Gruppe A+B), premium (Gruppe C)';

-- ============================================================================
-- TABLE: learning_method_progress (user completions)
-- Description: Track user completion of learning methods
-- ============================================================================
CREATE TABLE IF NOT EXISTS learning_methods.learning_method_progress (
    progress_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    method_id UUID REFERENCES learning_methods.learning_method_instances(method_id) ON DELETE CASCADE,
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    completed_at TIMESTAMPTZ DEFAULT NOW(),
    time_spent_seconds INTEGER,
    score DECIMAL(5,2),
    attempts INTEGER DEFAULT 1,
    user_answer JSONB,
    UNIQUE (method_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_lm_progress_method ON learning_methods.learning_method_progress(method_id);
CREATE INDEX IF NOT EXISTS idx_lm_progress_user ON learning_methods.learning_method_progress(user_id, completed_at DESC);
CREATE INDEX IF NOT EXISTS idx_lm_progress_score ON learning_methods.learning_method_progress(score);

COMMENT ON TABLE learning_methods.learning_method_progress IS 'User completion and performance tracking for learning methods';

-- ============================================================================
-- SEED DATA: 12 Content-Lernmethoden (moved from 041)
-- ============================================================================
INSERT INTO learning_methods.learning_method_types (method_type, name, description, group_code, tier, ki_usage, icon) VALUES
    -- Gruppe A: Erklärend (lm00-lm04) - 5 Methoden
    (0, 'Tiefgehende Erklärung', 'KI-generierte Erklärung mit Beispielen & Analogien', 'A', 'basic', 'intensive', 'book-open'),
    (1, 'Schritt-für-Schritt', 'Sequenzielle Anleitung in nummerierten Schritten', 'A', 'basic', 'medium', 'list-ordered'),
    (2, 'Interaktive Theorie', 'Theorie mit interaktiven Frage-Antwort-Elementen', 'A', 'basic', 'medium', 'lightbulb'),
    (3, 'Diagramm/Visualisierung', 'Grafische Darstellung komplexer Konzepte', 'A', 'basic', 'medium', 'chart-network'),
    (4, 'Beispiel-Szenario', 'Praxisnahes Anwendungsbeispiel mit Kontext', 'A', 'basic', 'medium', 'clipboard-list'),
    -- Gruppe B: Praxis (lm05-lm08) - 4 Methoden
    (5, 'Mathe-Interaktiv', 'Mathematische Aufgaben mit Schritt-Erkennung', 'B', 'basic', 'medium', 'calculator'),
    (6, 'Flashcards', 'Digitale Lernkarten für Wiederholung', 'B', 'basic', 'optional', 'cards'),
    (7, 'Drag & Drop', 'Zuordnungsaufgaben per Drag & Drop', 'B', 'basic', 'optional', 'hand-pointer'),
    (8, 'Lückentext', 'Lückentexte mit Auto-Korrektur', 'B', 'basic', 'optional', 'align-left'),
    -- Gruppe C: Prüfung (lm09-lm11) - 3 Methoden
    (9, 'Freitext-Langantwort', 'Offene Fragen mit KI-Bewertung', 'C', 'premium', 'medium', 'pen-fancy'),
    (10, 'IHK-Stil Aufgaben', 'Prüfungsaufgaben nach IHK-Standard', 'C', 'premium', 'intensive', 'file-certificate'),
    (11, 'Multi-Step Praxisprüfung', 'Mehrstufige praktische Prüfung', 'C', 'premium', 'intensive', 'tasks')
ON CONFLICT (method_type) DO NOTHING;

-- NOTE: LM12-LM32 are deprecated and moved to support_systems.system_features
-- See migrations/11_System/074_system_features.sql for System-Features

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- Note: Function update_updated_at_column() defined in 000_functions.sql
-- ============================================================================
DROP TRIGGER IF EXISTS update_lm_types_updated_at ON learning_methods.learning_method_types;
CREATE TRIGGER update_lm_types_updated_at
    BEFORE UPDATE ON learning_methods.learning_method_types
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_lm_instances_updated_at ON learning_methods.learning_method_instances;
CREATE TRIGGER update_lm_instances_updated_at
    BEFORE UPDATE ON learning_methods.learning_method_instances
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 011_learning_methods.sql
-- ============================================================================
