-- ============================================================================
-- Migration: 095_ai_content_plans.sql
-- Description: AI Content Plans + Generation Log for Unified AI Editor
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-02-23
-- ============================================================================

BEGIN;

-- ai_content_plans: Stores content plans (AI-suggested or manual)
CREATE TABLE IF NOT EXISTS ai_pipeline.ai_content_plans (
    plan_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL,
    scope VARCHAR(20) NOT NULL,
    scope_id UUID,
    user_id UUID NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    plan_data JSONB NOT NULL,
    estimated_tokens INTEGER,
    actual_tokens INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ai_generation_log: Tracks individual generations for history/rollback
CREATE TABLE IF NOT EXISTS ai_pipeline.ai_generation_log (
    generation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID REFERENCES ai_pipeline.ai_content_plans(plan_id),
    skill_code VARCHAR(50) NOT NULL,
    course_id UUID NOT NULL,
    target_type VARCHAR(20),
    target_id UUID,
    input_prompt TEXT,
    output_content JSONB,
    tokens_input INTEGER,
    tokens_output INTEGER,
    model_name VARCHAR(100),
    provider_name VARCHAR(50),
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for frequent queries
CREATE INDEX IF NOT EXISTS idx_content_plans_course ON ai_pipeline.ai_content_plans(course_id);
CREATE INDEX IF NOT EXISTS idx_content_plans_user ON ai_pipeline.ai_content_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_content_plans_status ON ai_pipeline.ai_content_plans(status);
CREATE INDEX IF NOT EXISTS idx_generation_log_plan ON ai_pipeline.ai_generation_log(plan_id);
CREATE INDEX IF NOT EXISTS idx_generation_log_course ON ai_pipeline.ai_generation_log(course_id);
CREATE INDEX IF NOT EXISTS idx_generation_log_skill ON ai_pipeline.ai_generation_log(skill_code);

COMMIT;
