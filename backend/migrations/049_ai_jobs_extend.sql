-- ============================================================================
-- Migration: 049_ai_jobs_extend.sql
-- Description: Extend AI Jobs table with prompt_id and storage_path
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-11-25
-- Phase: B24-05 - AI Course Generator Enhancement
-- ============================================================================

-- ============================================================================
-- ADD COLUMNS: prompt_id and storage_path
-- ============================================================================

-- Add prompt_id column (without FK for now - prompt system is optional)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_jobs' AND column_name = 'prompt_id') THEN
        ALTER TABLE ai_jobs ADD COLUMN prompt_id UUID;
    END IF;
END $$;

-- Add storage_path column for full file path of uploaded files
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_jobs' AND column_name = 'storage_path') THEN
        ALTER TABLE ai_jobs ADD COLUMN storage_path TEXT;
    END IF;
END $$;

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_ai_jobs_prompt ON ai_jobs(prompt_id) WHERE prompt_id IS NOT NULL;

-- ============================================================================
-- COMMENTS
-- ============================================================================
COMMENT ON COLUMN ai_jobs.prompt_id IS 'Reference to course_prompts template used for generation';
COMMENT ON COLUMN ai_jobs.storage_path IS 'Full filesystem path to uploaded input file';

-- ============================================================================
-- End of Migration: 049_ai_jobs_extend.sql
-- ============================================================================
