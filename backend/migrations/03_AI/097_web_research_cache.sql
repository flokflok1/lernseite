-- ============================================================================
-- Migration: 097_web_research_cache.sql
-- Description: Cache table for Gemini Grounding web research results
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-03-12
-- ============================================================================

BEGIN;

-- Web research cache: Stores Gemini Grounding results with real source URLs
CREATE TABLE IF NOT EXISTS ai_pipeline.web_research_cache (
    cache_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identification
    position_id INTEGER NOT NULL,
    language VARCHAR(5) NOT NULL DEFAULT 'de',
    cache_key VARCHAR(255) NOT NULL UNIQUE,

    -- Research result
    summary TEXT NOT NULL,
    key_points JSONB DEFAULT '[]',
    difficulty_level VARCHAR(20),
    recommended_study_time_minutes INTEGER,

    -- Sources (real URLs from Gemini Grounding)
    sources JSONB DEFAULT '[]',
    grounding_status VARCHAR(20) NOT NULL DEFAULT 'success',

    -- Queries used
    queries_used JSONB DEFAULT '[]',
    search_language VARCHAR(5),

    -- Cache management
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_grounding_status CHECK (
        grounding_status IN ('success', 'partial', 'failed')
    )
);

CREATE INDEX IF NOT EXISTS idx_research_cache_position
    ON ai_pipeline.web_research_cache(position_id, language);
CREATE INDEX IF NOT EXISTS idx_research_cache_expires
    ON ai_pipeline.web_research_cache(expires_at)
    WHERE expires_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_research_cache_key
    ON ai_pipeline.web_research_cache(cache_key);

COMMENT ON TABLE ai_pipeline.web_research_cache IS 'Cached Gemini Grounding results for curriculum gap positions';
COMMENT ON COLUMN ai_pipeline.web_research_cache.sources IS 'Real source URLs from Google Search via Gemini Grounding';
COMMENT ON COLUMN ai_pipeline.web_research_cache.grounding_status IS 'success=real sources, partial=some queries ok, failed=grounding failed';

COMMIT;
