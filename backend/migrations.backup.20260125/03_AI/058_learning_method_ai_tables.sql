-- ============================================================================
-- Migration: 058_learning_method_ai_tables.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. LEARNING METHOD EXECUTIONS - Tracks AI method executions
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_methods.learning_method_executions (
    execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    method_id UUID NOT NULL REFERENCES learning_methods.learning_method_instances(method_id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses.courses(course_id) ON DELETE SET NULL,
    chapter_id UUID REFERENCES courses.chapters(chapter_id) ON DELETE SET NULL,
    lesson_id UUID REFERENCES courses.lessons(lesson_id) ON DELETE SET NULL,

    -- Input/Output
    user_input TEXT NOT NULL,
    output_text TEXT NOT NULL,
    context TEXT,
    language VARCHAR(10) DEFAULT 'de',
    difficulty VARCHAR(20),

    -- Token usage
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0,

    -- AI details
    model VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    latency_ms INTEGER,
    cost_eur DECIMAL(10, 6) DEFAULT 0,

    -- Timestamps
    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for learning_method_executions
CREATE INDEX IF NOT EXISTS idx_lm_executions_user ON learning_methods.learning_method_executions(user_id);
CREATE INDEX IF NOT EXISTS idx_lm_executions_method ON learning_methods.learning_method_executions(method_id);
CREATE INDEX IF NOT EXISTS idx_lm_executions_course ON learning_methods.learning_method_executions(course_id);
CREATE INDEX IF NOT EXISTS idx_lm_executions_chapter ON learning_methods.learning_method_executions(chapter_id);
CREATE INDEX IF NOT EXISTS idx_lm_executions_executed_at ON learning_methods.learning_method_executions(executed_at DESC);

-- ============================================================================
-- 2. AI TOKEN USAGE - Tracks token consumption per user/method
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_pipeline.ai_token_usage (
    usage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organisations.organisations(organization_id) ON DELETE SET NULL,
    method_id UUID REFERENCES learning_methods.learning_method_instances(method_id) ON DELETE SET NULL,
    method_name VARCHAR(100),

    course_id UUID REFERENCES courses.courses(course_id) ON DELETE SET NULL,
    chapter_id UUID REFERENCES courses.chapters(chapter_id) ON DELETE SET NULL,
    lesson_id UUID REFERENCES courses.lessons(lesson_id) ON DELETE SET NULL,

    -- Token counts
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0,

    -- AI details
    model VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    cost_eur DECIMAL(10, 6) DEFAULT 0,

    -- Timestamp
    used_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for ai_token_usage
CREATE INDEX IF NOT EXISTS idx_token_usage_user ON ai_pipeline.ai_token_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_token_usage_org ON ai_pipeline.ai_token_usage(organization_id);
CREATE INDEX IF NOT EXISTS idx_token_usage_method ON ai_pipeline.ai_token_usage(method_id);
CREATE INDEX IF NOT EXISTS idx_token_usage_chapter ON ai_pipeline.ai_token_usage(chapter_id);
CREATE INDEX IF NOT EXISTS idx_token_usage_used_at ON ai_pipeline.ai_token_usage(used_at DESC);
CREATE INDEX IF NOT EXISTS idx_token_usage_provider ON ai_pipeline.ai_token_usage(provider);

-- ============================================================================
-- 3. AI FEEDBACK - User feedback on AI responses
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_pipeline.ai_feedback (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    execution_id UUID REFERENCES learning_methods.learning_method_executions(execution_id) ON DELETE CASCADE,
    method_id UUID REFERENCES learning_methods.learning_method_instances(method_id) ON DELETE SET NULL,

    course_id UUID REFERENCES courses.courses(course_id) ON DELETE SET NULL,
    chapter_id UUID REFERENCES courses.chapters(chapter_id) ON DELETE SET NULL,
    lesson_id UUID REFERENCES courses.lessons(lesson_id) ON DELETE SET NULL,

    -- Feedback data
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    feedback_text TEXT,
    is_helpful BOOLEAN DEFAULT TRUE,
    ai_generated BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for ai_feedback
CREATE INDEX IF NOT EXISTS idx_ai_feedback_user ON ai_pipeline.ai_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_feedback_execution ON ai_pipeline.ai_feedback(execution_id);
CREATE INDEX IF NOT EXISTS idx_ai_feedback_method ON ai_pipeline.ai_feedback(method_id);
CREATE INDEX IF NOT EXISTS idx_ai_feedback_chapter ON ai_pipeline.ai_feedback(chapter_id);
CREATE INDEX IF NOT EXISTS idx_ai_feedback_rating ON ai_pipeline.ai_feedback(rating);
CREATE INDEX IF NOT EXISTS idx_ai_feedback_created ON ai_pipeline.ai_feedback(created_at DESC);

COMMIT;
