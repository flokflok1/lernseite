-- Migration: 069_ai_prompt_templates.sql
-- Purpose: Reusable prompt templates with parameterization (Feature #4)
-- Date: 2026-01-18

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS ai_prompt_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,

    template_name VARCHAR(255) NOT NULL,
    template_category VARCHAR(50) NOT NULL CHECK (template_category IN ('COURSE_OVERVIEW', 'MODULE_INTRO', 'LESSON', 'ASSESSMENT', 'SCENARIO')),
    template_type VARCHAR(50) DEFAULT 'CUSTOM' CHECK (template_type IN ('BUILTIN', 'CUSTOM')),
    base_prompt TEXT NOT NULL,
    parameters JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Performance tracking
    usage_count INT DEFAULT 0,
    success_rate FLOAT CHECK (success_rate >= 0.0 AND success_rate <= 1.0),
    avg_generation_time_seconds INT DEFAULT 0,

    -- Metadata
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_used_at TIMESTAMP,
    is_public BOOLEAN DEFAULT FALSE,
    version INT DEFAULT 1 CHECK (version >= 1),

    -- Constraints
    CONSTRAINT fk_organisation FOREIGN KEY (organisation_id) REFERENCES organisations(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ai_prompt_templates_org_category ON ai_prompt_templates(organisation_id, template_category);
CREATE INDEX IF NOT EXISTS idx_ai_prompt_templates_type ON ai_prompt_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_ai_prompt_templates_public ON ai_prompt_templates(is_public);
CREATE INDEX IF NOT EXISTS idx_ai_prompt_templates_created_by ON ai_prompt_templates(created_by);

-- Template usage tracking
CREATE TABLE IF NOT EXISTS ai_template_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES ai_prompt_templates(id) ON DELETE CASCADE,
    session_id UUID REFERENCES ai_editor_sessions(id) ON DELETE SET NULL,
    course_id UUID REFERENCES courses(id) ON DELETE SET NULL,

    parameter_values JSONB,
    generated_content TEXT,
    generation_time_seconds INT,
    tokens_used INT DEFAULT 0,
    user_action VARCHAR(20) CHECK (user_action IN ('ACCEPTED', 'REJECTED', 'MODIFIED', NULL)),

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT fk_template FOREIGN KEY (template_id) REFERENCES ai_prompt_templates(id) ON DELETE CASCADE,
    CONSTRAINT fk_session FOREIGN KEY (session_id) REFERENCES ai_editor_sessions(id) ON DELETE SET NULL,
    CONSTRAINT fk_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE SET NULL
);

-- Create indexes for template usage
CREATE INDEX IF NOT EXISTS idx_ai_template_usage_template_id ON ai_template_usage(template_id);
CREATE INDEX IF NOT EXISTS idx_ai_template_usage_session_id ON ai_template_usage(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_template_usage_created_at ON ai_template_usage(created_at DESC);

COMMIT;
