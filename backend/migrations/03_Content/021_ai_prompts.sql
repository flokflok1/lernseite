-- ============================================================================
-- Migration: 021_ai_prompts.sql
-- Version: 1.0.0
-- Description: AI Prompts System (Centralized Prompt Management for AI Features)
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 3 (Extended Systems - AI Pipeline)
-- Dependencies: 000_schemas.sql (ai_pipeline schema)
-- ============================================================================

-- ============================================================================
-- TABLE: ai_pipeline.prompts
-- Description: Centralized prompt storage for AI Editor, Tutor, Task Evaluation
--
-- A Prompt is a template for AI operations with:
-- - Use case (ai_editor, tutor_explanation, task_evaluation, content_generation)
-- - System prompt (base instructions for AI)
-- - Template variables (e.g., {course_title}, {task_type})
-- - Version history (tracks all changes)
--
-- Used by:
-- 1. AI Editor: Course creation prompts
-- 2. Tutor: Explanation generation, Q&A
-- 3. Task Evaluation: Auto-grading rubrics
-- 4. Content Generation: Theory sheets, examples
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_pipeline.prompts (
    prompt_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Identification
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,

    -- Use case classification
    use_case VARCHAR(50) NOT NULL,  -- ai_editor, tutor_explanation, task_evaluation, content_generation, etc.
    prompt_type VARCHAR(50) NOT NULL,  -- system, user, assistant, template

    -- The actual prompt content
    system_prompt TEXT NOT NULL,  -- System instructions for AI
    template_variables TEXT[] DEFAULT ARRAY[]::TEXT[],  -- e.g., ARRAY['{course_title}', '{student_level}']
    example_variables JSONB DEFAULT '{}',  -- Example values for template

    -- Metadata
    language VARCHAR(10) DEFAULT 'de',  -- de, en, pl, etc.
    model VARCHAR(100),  -- Suggested model (gpt-4, claude-3-opus, etc.)
    temperature DECIMAL(3,2) DEFAULT 0.7,  -- Creativity level (0.0-1.0)
    max_tokens INTEGER DEFAULT 2000,

    -- Quality tracking
    is_approved BOOLEAN DEFAULT FALSE,
    approval_notes TEXT,
    approved_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    approved_at TIMESTAMPTZ,

    -- Usage statistics
    total_uses INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    success_rate DECIMAL(5,2),  -- % of successful uses

    -- Versioning
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES core.users(user_id),

    -- Constraints
    CONSTRAINT chk_use_case CHECK (use_case IN (
        'ai_editor',
        'tutor_explanation',
        'task_evaluation',
        'content_generation',
        'example_generation',
        'hint_generation',
        'feedback_generation'
    )),
    CONSTRAINT chk_prompt_type CHECK (prompt_type IN ('system', 'user', 'assistant', 'template')),
    CONSTRAINT chk_temperature CHECK (temperature >= 0.0 AND temperature <= 1.0)
);

CREATE INDEX IF NOT EXISTS idx_prompts_slug ON ai_pipeline.prompts(slug);
CREATE INDEX IF NOT EXISTS idx_prompts_use_case ON ai_pipeline.prompts(use_case);
CREATE INDEX IF NOT EXISTS idx_prompts_active ON ai_pipeline.prompts(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE ai_pipeline.prompts IS 'Centralized AI prompt storage for Editor, Tutor, Task Evaluation';
COMMENT ON COLUMN ai_pipeline.prompts.use_case IS 'Purpose: ai_editor, tutor_explanation, task_evaluation, content_generation, etc.';
COMMENT ON COLUMN ai_pipeline.prompts.template_variables IS 'Variables to substitute: {course_title}, {student_level}, {task_type}';

-- ============================================================================
-- TABLE: ai_pipeline.prompt_versions
-- Description: Version history of prompts (for A/B testing and rollback)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_pipeline.prompt_versions (
    version_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prompt_id UUID NOT NULL REFERENCES ai_pipeline.prompts(prompt_id) ON DELETE CASCADE,

    -- Version number
    version_number INTEGER NOT NULL,

    -- Content snapshot
    system_prompt TEXT NOT NULL,
    template_variables TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Change tracking
    change_description TEXT,
    changed_by UUID REFERENCES core.users(user_id),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE(prompt_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_prompt_versions_prompt ON ai_pipeline.prompt_versions(prompt_id);
CREATE INDEX IF NOT EXISTS idx_prompt_versions_created ON ai_pipeline.prompt_versions(created_at DESC);

COMMENT ON TABLE ai_pipeline.prompt_versions IS 'Version history for prompts (for rollback, A/B testing, audit trail)';

-- ============================================================================
-- TABLE: ai_pipeline.prompt_usage_stats
-- Description: Analytics for prompt effectiveness
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_pipeline.prompt_usage_stats (
    stat_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prompt_id UUID NOT NULL REFERENCES ai_pipeline.prompts(prompt_id) ON DELETE CASCADE,

    -- What happened
    use_case VARCHAR(50),
    model_used VARCHAR(100),
    tokens_used INTEGER,
    response_time_ms INTEGER,

    -- Quality metrics
    was_successful BOOLEAN DEFAULT TRUE,
    user_satisfaction INTEGER,  -- 1-5 rating
    quality_score DECIMAL(5,2),  -- 0-100

    -- Context
    user_id UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    course_id UUID REFERENCES courses.courses(course_id) ON DELETE SET NULL,
    context_data JSONB,  -- {user_level, difficulty, language, etc.}

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_prompt_usage_stats_prompt ON ai_pipeline.prompt_usage_stats(prompt_id);
CREATE INDEX IF NOT EXISTS idx_prompt_usage_stats_created ON ai_pipeline.prompt_usage_stats(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_prompt_usage_stats_success ON ai_pipeline.prompt_usage_stats(was_successful);

COMMENT ON TABLE ai_pipeline.prompt_usage_stats IS 'Usage analytics and effectiveness tracking for prompts';

-- ============================================================================
-- Function: get_prompt_by_use_case()
-- Description: Retrieve active prompt for given use case
-- ============================================================================

CREATE OR REPLACE FUNCTION get_prompt_by_use_case(p_use_case VARCHAR, p_language VARCHAR DEFAULT 'de')
RETURNS TABLE (
    prompt_id UUID,
    name VARCHAR,
    system_prompt TEXT,
    template_variables TEXT[],
    model VARCHAR,
    temperature DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.prompt_id,
        p.name,
        p.system_prompt,
        p.template_variables,
        p.model,
        p.temperature
    FROM ai_pipeline.prompts p
    WHERE p.use_case = p_use_case
      AND p.language = p_language
      AND p.is_active = TRUE
      AND p.is_approved = TRUE
    ORDER BY p.last_used_at DESC NULLS LAST
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Trigger: Update prompt statistics on usage
-- ============================================================================

DROP TRIGGER IF EXISTS update_prompt_stats ON ai_pipeline.prompt_usage_stats;

CREATE TRIGGER update_prompt_stats
AFTER INSERT ON ai_pipeline.prompt_usage_stats
FOR EACH ROW
EXECUTE FUNCTION (
    UPDATE ai_pipeline.prompts
    SET total_uses = total_uses + 1,
        last_used_at = CURRENT_TIMESTAMP
    WHERE prompt_id = NEW.prompt_id
);

-- ============================================================================
-- End of Migration: 021_ai_prompts.sql
-- ============================================================================
