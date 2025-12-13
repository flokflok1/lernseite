-- ============================================================================
-- Migration: 021_ai_jobs.sql
-- Description: Asynchronous AI job queue and processing
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: ai_jobs
-- Description: Asynchronous AI processing jobs
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_jobs (
    job_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    organization_id UUID REFERENCES organizations(organization_id) ON DELETE SET NULL,
    job_type VARCHAR(100) NOT NULL,
    input_data JSONB NOT NULL,
    output_data JSONB,
    priority INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'queued',
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    scheduled_for TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_ai_job_status CHECK (status IN ('queued', 'processing', 'completed', 'failed', 'cancelled')),
    CONSTRAINT chk_ai_job_priority CHECK (priority >= 0 AND priority <= 10)
);

CREATE INDEX IF NOT EXISTS idx_ai_jobs_user ON ai_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_jobs_org ON ai_jobs(organization_id);
CREATE INDEX IF NOT EXISTS idx_ai_jobs_type ON ai_jobs(job_type);
CREATE INDEX IF NOT EXISTS idx_ai_jobs_status ON ai_jobs(status, priority DESC, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_ai_jobs_scheduled ON ai_jobs(scheduled_for) WHERE status = 'queued' AND scheduled_for IS NOT NULL;

COMMENT ON TABLE ai_jobs IS 'Async AI job queue (Celery tasks)';

-- ============================================================================
-- TABLE: ai_job_steps
-- Description: Individual steps within multi-step AI jobs
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_job_steps (
    step_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES ai_jobs(job_id) ON DELETE CASCADE,
    step_name VARCHAR(100) NOT NULL,
    step_order INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    output_data JSONB,
    error_message TEXT,
    CONSTRAINT chk_job_step_status CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'skipped'))
);

CREATE INDEX IF NOT EXISTS idx_ai_job_steps_job ON ai_job_steps(job_id, step_order);
CREATE INDEX IF NOT EXISTS idx_ai_job_steps_status ON ai_job_steps(status);

COMMENT ON TABLE ai_job_steps IS 'Individual steps within complex AI processing jobs';

-- ============================================================================
-- End of Migration: 021_ai_jobs.sql
-- ============================================================================
