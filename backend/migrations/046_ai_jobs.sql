-- ============================================================================
-- Migration: 046_ai_jobs.sql
-- Description: AI Job Management System for course generation
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-11-20
-- Phase: B24-05 - AI Course Generator
-- ============================================================================

-- ============================================================================
-- TABLE: ai_jobs
-- Description: Track AI-powered content generation jobs
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    course_id UUID NULL REFERENCES courses(course_id) ON DELETE SET NULL,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    progress INT DEFAULT 0,
    input_file VARCHAR(255),
    input_prompt TEXT,
    output_data JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_ai_job_type CHECK (type IN (
        'course_from_pdf',
        'chapter_autogen',
        'lesson_autogen'
    )),

    CONSTRAINT chk_ai_job_status CHECK (status IN (
        'pending',
        'processing',
        'completed',
        'failed',
        'cancelled'
    )),

    CONSTRAINT chk_progress_range CHECK (progress >= 0 AND progress <= 100)
);

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_ai_jobs_user ON ai_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_jobs_course ON ai_jobs(course_id) WHERE course_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ai_jobs_type ON ai_jobs(type);
CREATE INDEX IF NOT EXISTS idx_ai_jobs_status ON ai_jobs(status);
CREATE INDEX IF NOT EXISTS idx_ai_jobs_created ON ai_jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_jobs_user_status ON ai_jobs(user_id, status);

-- ============================================================================
-- TRIGGER: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_ai_jobs_updated_at BEFORE UPDATE ON ai_jobs
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMMENTS
-- ============================================================================
COMMENT ON TABLE ai_jobs IS 'AI-powered content generation jobs for courses, chapters, and lessons';
COMMENT ON COLUMN ai_jobs.type IS 'Job type: course_from_pdf (PDF → Course), chapter_autogen (Auto-gen chapters), lesson_autogen (Auto-gen lessons)';
COMMENT ON COLUMN ai_jobs.status IS 'Job status: pending (queued), processing (running), completed (success), failed (error), cancelled (stopped)';
COMMENT ON COLUMN ai_jobs.progress IS 'Progress percentage (0-100)';
COMMENT ON COLUMN ai_jobs.input_file IS 'Path or name of input file (e.g., PDF filename)';
COMMENT ON COLUMN ai_jobs.input_prompt IS 'Optional user prompt for AI guidance';
COMMENT ON COLUMN ai_jobs.output_data IS 'JSONB containing generated course structure, chapters, lessons';
COMMENT ON COLUMN ai_jobs.error_message IS 'Error message if job failed';

-- ============================================================================
-- End of Migration: 046_ai_jobs.sql
-- ============================================================================
