-- Migration: 072_collaboration.sql
-- Purpose: Real-time collaboration and version control (Feature #7)
-- Date: 2026-01-18

BEGIN TRANSACTION;

-- Ensure ai_pipeline schema exists
CREATE SCHEMA IF NOT EXISTS ai_pipeline;

CREATE TABLE IF NOT EXISTS ai_pipeline.content_block_collaborators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_block_id VARCHAR(100) NOT NULL,
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_editor_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,

    -- Permissions
    permission_level VARCHAR(20) DEFAULT 'EDIT' CHECK (permission_level IN ('VIEW', 'EDIT', 'ADMIN')),

    -- Collaboration state
    is_active BOOLEAN DEFAULT TRUE,
    last_activity_at TIMESTAMP NOT NULL DEFAULT NOW(),

    joined_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT fk_session FOREIGN KEY (session_id) REFERENCES ai_pipeline.ai_editor_sessions(id) ON DELETE CASCADE,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES core.users(user_id) ON DELETE CASCADE,
    CONSTRAINT unique_collaborator UNIQUE(session_id, user_id, content_block_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_content_block_collaborators_session_id ON ai_pipeline.content_block_collaborators(session_id);
CREATE INDEX IF NOT EXISTS idx_content_block_collaborators_user_id ON ai_pipeline.content_block_collaborators(user_id);
CREATE INDEX IF NOT EXISTS idx_content_block_collaborators_active ON ai_pipeline.content_block_collaborators(is_active);

-- Change history for version control
CREATE TABLE IF NOT EXISTS ai_pipeline.change_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_editor_sessions(id) ON DELETE CASCADE,
    content_block_id VARCHAR(100),
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,

    -- Operation
    operation VARCHAR(20) NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE', 'MERGE')),
    before_content TEXT,
    after_content TEXT,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT fk_session FOREIGN KEY (session_id) REFERENCES ai_pipeline.ai_editor_sessions(id) ON DELETE CASCADE,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES core.users(user_id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_change_records_session_id ON ai_pipeline.change_records(session_id);
CREATE INDEX IF NOT EXISTS idx_change_records_user_id ON ai_pipeline.change_records(user_id);
CREATE INDEX IF NOT EXISTS idx_change_records_created_at ON ai_pipeline.change_records(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_change_records_operation ON ai_pipeline.change_records(operation);

-- Collaboration comments/threads
CREATE TABLE IF NOT EXISTS ai_pipeline.collaboration_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_pipeline.ai_editor_sessions(id) ON DELETE CASCADE,
    content_block_id VARCHAR(100),
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,

    comment_text TEXT NOT NULL,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    resolved_at TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT fk_session FOREIGN KEY (session_id) REFERENCES ai_pipeline.ai_editor_sessions(id) ON DELETE CASCADE,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES core.users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_resolved_by FOREIGN KEY (resolved_by) REFERENCES core.users(user_id) ON DELETE SET NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_collaboration_comments_session_id ON ai_pipeline.collaboration_comments(session_id);
CREATE INDEX IF NOT EXISTS idx_collaboration_comments_user_id ON ai_pipeline.collaboration_comments(user_id);
CREATE INDEX IF NOT EXISTS idx_collaboration_comments_resolved ON ai_pipeline.collaboration_comments(resolved);
CREATE INDEX IF NOT EXISTS idx_collaboration_comments_created_at ON ai_pipeline.collaboration_comments(created_at DESC);

COMMIT;
