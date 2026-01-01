-- ============================================================================
-- Migration: 042_learning_method_types
-- Description: Learning method types/templates table (21 method definitions)
-- Author: LernsystemX Migration System
-- Date: 2025-01-19
-- ============================================================================

-- ============================================================================
-- TABLE: learning_method_types
-- Description: Defines the 21 learning method types (templates)
-- ============================================================================
CREATE TABLE IF NOT EXISTS learning_method_types (
    type_id SERIAL PRIMARY KEY,
    method_number INTEGER NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    tier VARCHAR(20) NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    config JSONB,
    icon VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_method_number CHECK (method_number BETWEEN 1 AND 21),
    CONSTRAINT chk_tier CHECK (tier IN ('basic', 'premium', 'pro'))
);

CREATE INDEX IF NOT EXISTS idx_learning_method_types_number ON learning_method_types(method_number);
CREATE INDEX IF NOT EXISTS idx_learning_method_types_tier ON learning_method_types(tier);
CREATE INDEX IF NOT EXISTS idx_learning_method_types_active ON learning_method_types(active) WHERE active = TRUE;
CREATE INDEX IF NOT EXISTS idx_learning_method_types_name ON learning_method_types(name);

COMMENT ON TABLE learning_method_types IS '21 learning method type definitions: Flashcards (1), Quiz (2), etc.';
COMMENT ON COLUMN learning_method_types.method_number IS 'Method number 1-21: 1-11 basic, 12-17 premium, 18-21 pro';
COMMENT ON COLUMN learning_method_types.tier IS 'Subscription tier required: basic (free), premium, or pro';
COMMENT ON COLUMN learning_method_types.config IS 'Method-specific configuration (supports_images, max_questions, etc.)';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_learning_method_types_updated_at BEFORE UPDATE ON learning_method_types
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 042_learning_method_types
-- ============================================================================
