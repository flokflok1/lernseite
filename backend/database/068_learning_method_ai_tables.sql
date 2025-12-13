-- ============================================================================
-- LernsystemX Migration 068: Learning Method AI Execution Tables
-- Creates missing tables for AI-powered learning method execution
-- Structure: courses -> chapters -> lessons
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. LEARNING METHOD EXECUTIONS - Tracks AI method executions
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_method_executions (
    execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    method_id UUID NOT NULL REFERENCES learning_methods(method_id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(course_id) ON DELETE SET NULL,
    chapter_id UUID REFERENCES chapters(chapter_id) ON DELETE SET NULL,
    lesson_id UUID REFERENCES lessons(lesson_id) ON DELETE SET NULL,

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
CREATE INDEX IF NOT EXISTS idx_lm_executions_user ON learning_method_executions(user_id);
CREATE INDEX IF NOT EXISTS idx_lm_executions_method ON learning_method_executions(method_id);
CREATE INDEX IF NOT EXISTS idx_lm_executions_course ON learning_method_executions(course_id);
CREATE INDEX IF NOT EXISTS idx_lm_executions_chapter ON learning_method_executions(chapter_id);
CREATE INDEX IF NOT EXISTS idx_lm_executions_executed_at ON learning_method_executions(executed_at DESC);

-- ============================================================================
-- 2. AI TOKEN USAGE - Tracks token consumption per user/method
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_token_usage (
    usage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(organization_id) ON DELETE SET NULL,
    method_id UUID REFERENCES learning_methods(method_id) ON DELETE SET NULL,
    method_name VARCHAR(100),

    course_id UUID REFERENCES courses(course_id) ON DELETE SET NULL,
    chapter_id UUID REFERENCES chapters(chapter_id) ON DELETE SET NULL,
    lesson_id UUID REFERENCES lessons(lesson_id) ON DELETE SET NULL,

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
CREATE INDEX IF NOT EXISTS idx_token_usage_user ON ai_token_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_token_usage_org ON ai_token_usage(organization_id);
CREATE INDEX IF NOT EXISTS idx_token_usage_method ON ai_token_usage(method_id);
CREATE INDEX IF NOT EXISTS idx_token_usage_chapter ON ai_token_usage(chapter_id);
CREATE INDEX IF NOT EXISTS idx_token_usage_used_at ON ai_token_usage(used_at DESC);
CREATE INDEX IF NOT EXISTS idx_token_usage_provider ON ai_token_usage(provider);

-- ============================================================================
-- 3. AI FEEDBACK - User feedback on AI responses
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_feedback (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    execution_id UUID REFERENCES learning_method_executions(execution_id) ON DELETE CASCADE,
    method_id UUID REFERENCES learning_methods(method_id) ON DELETE SET NULL,

    course_id UUID REFERENCES courses(course_id) ON DELETE SET NULL,
    chapter_id UUID REFERENCES chapters(chapter_id) ON DELETE SET NULL,
    lesson_id UUID REFERENCES lessons(lesson_id) ON DELETE SET NULL,

    -- Feedback data
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    feedback_text TEXT,
    is_helpful BOOLEAN DEFAULT TRUE,
    ai_generated BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for ai_feedback
CREATE INDEX IF NOT EXISTS idx_ai_feedback_user ON ai_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_feedback_execution ON ai_feedback(execution_id);
CREATE INDEX IF NOT EXISTS idx_ai_feedback_method ON ai_feedback(method_id);
CREATE INDEX IF NOT EXISTS idx_ai_feedback_chapter ON ai_feedback(chapter_id);
CREATE INDEX IF NOT EXISTS idx_ai_feedback_rating ON ai_feedback(rating);
CREATE INDEX IF NOT EXISTS idx_ai_feedback_created ON ai_feedback(created_at DESC);

COMMIT;
