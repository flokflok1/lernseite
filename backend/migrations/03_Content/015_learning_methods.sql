-- ============================================================================
-- Migration: 015_learning_methods.sql
-- Version: 1.0.0
-- Description: Learning methods tables (CREATE only)
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- Phase: 2 (Content Layer)
-- ============================================================================

-- Create learning_methods schema if it doesn't exist

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
-- End of Migration: 015_learning_methods.sql
-- ============================================================================
