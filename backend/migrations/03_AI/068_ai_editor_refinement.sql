-- ============================================================================
-- Migration: 068_ai_editor_refinement.sql
-- Purpose: AI Editor Refinement History
-- Date: 2026-01-18
-- ============================================================================

BEGIN TRANSACTION;

-- NOTE: ai_pipeline schema is created in 01_Core/000_schemas.sql
-- No schema creation needed here

-- ============================================================================
-- Table: AI Editor Refinement History (Feature #1)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_pipeline.ai_editor_refinement_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_editor_sessions(id) ON DELETE CASCADE,
    refinement_number INT NOT NULL,
    request_text TEXT NOT NULL,

    -- Targeting
    target_section VARCHAR(50) NOT NULL CHECK (target_section IN ('COURSE', 'CHAPTER', 'LESSON', 'METHOD', 'ASSESSMENT')),
    target_id VARCHAR(100),

    -- AI execution
    ai_model VARCHAR(50) DEFAULT 'claude-3-opus',
    prompt_template_id UUID REFERENCES ai_pipeline.prompt_templates(template_id) ON DELETE SET NULL,
    tokens_used INT DEFAULT 0,
    cost_cents DECIMAL(10, 2) DEFAULT 0.00,

    -- Results
    status VARCHAR(20) DEFAULT 'PROCESSING' CHECK (status IN ('PROCESSING', 'COMPLETED', 'FAILED', 'ROLLED_BACK')),
    generated_content JSONB,
    quality_score FLOAT CHECK (quality_score >= 0.0 AND quality_score <= 1.0),
    user_action VARCHAR(20) CHECK (user_action IN ('ACCEPTED', 'REJECTED', 'REROLLED', NULL)),

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,

    -- Constraints
    CONSTRAINT fk_session FOREIGN KEY (session_id) REFERENCES ai_pipeline.ai_editor_sessions(id) ON DELETE CASCADE
);

-- Refinement history indexes
CREATE INDEX IF NOT EXISTS idx_ai_editor_refinement_session_id ON ai_pipeline.ai_editor_refinement_history(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_editor_refinement_status ON ai_pipeline.ai_editor_refinement_history(status);
CREATE INDEX IF NOT EXISTS idx_ai_editor_refinement_created_at ON ai_pipeline.ai_editor_refinement_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_editor_refinement_target ON ai_pipeline.ai_editor_refinement_history(target_section, target_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_ai_editor_refinement_unique ON ai_pipeline.ai_editor_refinement_history(session_id, refinement_number);

COMMIT;
