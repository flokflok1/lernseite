-- ============================================================================
-- Migration: 096_plan_wizard_columns.sql
-- Description: Add phased plan wizard columns to ai_content_plans
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-02-26
-- ============================================================================

BEGIN;

-- Phase tracking for the 4-phase plan wizard
ALTER TABLE ai_pipeline.ai_content_plans
    ADD COLUMN IF NOT EXISTS current_phase INTEGER DEFAULT 1;

-- Course metadata (title, description, difficulty, audience, language)
ALTER TABLE ai_pipeline.ai_content_plans
    ADD COLUMN IF NOT EXISTS course_meta JSONB DEFAULT '{}';

-- Chapter drafts array (structured chapter/lesson outlines)
ALTER TABLE ai_pipeline.ai_content_plans
    ADD COLUMN IF NOT EXISTS chapters JSONB DEFAULT '[]';

-- Chat history for the AI conversation during plan creation
ALTER TABLE ai_pipeline.ai_content_plans
    ADD COLUMN IF NOT EXISTS chat_history JSONB DEFAULT '[]';

-- Ensure phase stays within valid range (1-4)
ALTER TABLE ai_pipeline.ai_content_plans
    ADD CONSTRAINT chk_plan_phase
    CHECK (current_phase >= 1 AND current_phase <= 4);

COMMIT;
