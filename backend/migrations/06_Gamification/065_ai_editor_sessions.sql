-- Migration: 067_ai_editor_sessions.sql
-- Purpose: Create core AI Editor session tracking tables
-- Date: 2026-01-18

BEGIN TRANSACTION;

-- Main AI Editor sessions table
-- Note: ai_pipeline schema created in migration 021_ai_providers.sql
CREATE TABLE IF NOT EXISTS ai_pipeline.ai_editor_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses.courses(course_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    organisation_id UUID NOT NULL REFERENCES organisations.organisations(organization_id) ON DELETE CASCADE,

    -- Session state
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'PAUSED', 'COMPLETED', 'ARCHIVED')),
    ai_model VARCHAR(50) DEFAULT 'claude-3-opus',

    -- Tracking
    total_tokens_used INT DEFAULT 0,
    total_cost_cents DECIMAL(10, 2) DEFAULT 0.00,
    generation_count INT DEFAULT 0,
    refinement_count INT DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_activity_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT fk_course FOREIGN KEY (course_id) REFERENCES courses.courses(course_id) ON DELETE CASCADE,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES core.users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_organisation FOREIGN KEY (organisation_id) REFERENCES organisations.organisations(organization_id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ai_editor_sessions_user_course ON ai_pipeline.ai_editor_sessions(user_id, course_id);
CREATE INDEX IF NOT EXISTS idx_ai_editor_sessions_status ON ai_pipeline.ai_editor_sessions(status);
CREATE INDEX IF NOT EXISTS idx_ai_editor_sessions_created_at ON ai_pipeline.ai_editor_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_editor_sessions_organisation ON ai_pipeline.ai_editor_sessions(organisation_id);

-- Audit table for session changes
CREATE TABLE IF NOT EXISTS ai_pipeline.ai_editor_session_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_editor_sessions(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    details JSONB,
    created_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CHECK (action IN ('CREATED', 'GENERATION_STARTED', 'REFINEMENT', 'COMPLETED', 'ARCHIVED', 'RESUMED', 'PAUSED'))
);

-- Create indexes for session history
CREATE INDEX IF NOT EXISTS idx_ai_editor_session_history_session_id ON ai_pipeline.ai_editor_session_history(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_editor_session_history_action ON ai_pipeline.ai_editor_session_history(action);
CREATE INDEX IF NOT EXISTS idx_ai_editor_session_history_created_at ON ai_pipeline.ai_editor_session_history(created_at DESC);

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION ai_pipeline.update_ai_editor_sessions_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ai_editor_sessions_update_timestamp
BEFORE UPDATE ON ai_pipeline.ai_editor_sessions
FOR EACH ROW
EXECUTE FUNCTION ai_pipeline.update_ai_editor_sessions_timestamp();

COMMIT;

-- Verification queries (can be removed after testing)
-- SELECT COUNT(*) FROM ai_editor_sessions;
-- SELECT COUNT(*) FROM ai_editor_session_history;
-- \d ai_editor_sessions
-- \d ai_editor_session_history
