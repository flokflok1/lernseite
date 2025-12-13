-- ============================================================================
-- Migration: 011_learning_methods.sql
-- Description: 32 learning methods system (LM00-LM31)
-- Version: 2.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- Updated: 2025-11-27 (Refactoring: modules → chapters, 21 → 32 methods)
-- ============================================================================

-- ============================================================================
-- TABLE: learning_methods
-- Description: Learning method instances (32 types: LM00-LM31)
-- ============================================================================
CREATE TABLE IF NOT EXISTS learning_methods (
    method_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chapter_id UUID REFERENCES chapters(chapter_id) ON DELETE CASCADE,
    method_type INTEGER NOT NULL,
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
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_method_type CHECK (method_type BETWEEN 0 AND 31),
    CONSTRAINT chk_method_tier CHECK (tier IN ('basic', 'premium', 'pro')),
    CONSTRAINT chk_method_difficulty CHECK (difficulty IN ('easy', 'medium', 'hard'))
);

CREATE INDEX IF NOT EXISTS idx_learning_methods_chapter ON learning_methods(chapter_id);
CREATE INDEX IF NOT EXISTS idx_learning_methods_type ON learning_methods(method_type);
CREATE INDEX IF NOT EXISTS idx_learning_methods_tier ON learning_methods(tier);
CREATE INDEX IF NOT EXISTS idx_learning_methods_data ON learning_methods USING GIN(data);
CREATE INDEX IF NOT EXISTS idx_learning_methods_published ON learning_methods(published) WHERE published = TRUE;
CREATE INDEX IF NOT EXISTS idx_learning_methods_order ON learning_methods(chapter_id, order_index);

COMMENT ON TABLE learning_methods IS '32 learning method instances (LM00-LM31): Group A (0-7), B (8-17), C (18-25), D (26-31)';
COMMENT ON COLUMN learning_methods.method_type IS '0-31: maps to specific learning method type (LM00-LM31)';
COMMENT ON COLUMN learning_methods.data IS 'JSONB structure varies by method_type';
COMMENT ON COLUMN learning_methods.tier IS 'basic (Group A+B), premium (Group C), pro (Group D)';

-- ============================================================================
-- TABLE: method_completions
-- Description: Track user completion of learning methods
-- ============================================================================
CREATE TABLE IF NOT EXISTS method_completions (
    completion_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    method_id UUID REFERENCES learning_methods(method_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    completed_at TIMESTAMPTZ DEFAULT NOW(),
    time_spent_seconds INTEGER,
    score DECIMAL(5,2),
    attempts INTEGER DEFAULT 1,
    user_answer JSONB,
    UNIQUE (method_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_method_completions_method ON method_completions(method_id);
CREATE INDEX IF NOT EXISTS idx_method_completions_user ON method_completions(user_id, completed_at DESC);
CREATE INDEX IF NOT EXISTS idx_method_completions_score ON method_completions(score);

COMMENT ON TABLE method_completions IS 'User completion and performance tracking for learning methods';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_learning_methods_updated_at BEFORE UPDATE ON learning_methods
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 011_learning_methods.sql
-- ============================================================================
