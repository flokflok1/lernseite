-- ============================================================================
-- Migration: 111_crawl_system.sql
-- Description: Tables for the web research crawl system (domain config,
--              job execution history, and discovered URL tracking)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-03-12
-- ============================================================================

BEGIN;

-- 1. crawl_domains: Domain configuration
CREATE TABLE IF NOT EXISTS ai_pipeline.crawl_domains (
    domain_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_name VARCHAR(255) NOT NULL UNIQUE,
    base_url VARCHAR(1024) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    url_patterns JSONB DEFAULT '[]'::jsonb,
    crawl_schedule VARCHAR(50) DEFAULT 'monthly',
    rate_limit_seconds NUMERIC(4,1) DEFAULT 1.5,
    max_pages_per_crawl INTEGER DEFAULT 500,
    max_depth INTEGER DEFAULT 3,
    is_active BOOLEAN DEFAULT true,
    last_crawled_at TIMESTAMPTZ,
    total_pdfs_found INTEGER DEFAULT 0,
    config JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. crawl_jobs: Job execution history
CREATE TABLE IF NOT EXISTS ai_pipeline.crawl_jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id UUID REFERENCES ai_pipeline.crawl_domains(domain_id) ON DELETE SET NULL,
    status VARCHAR(30) DEFAULT 'pending'
        CHECK (status IN ('pending','running','completed','failed','cancelled')),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    pages_crawled INTEGER DEFAULT 0,
    pdfs_discovered INTEGER DEFAULT 0,
    pdfs_downloaded INTEGER DEFAULT 0,
    pdfs_new INTEGER DEFAULT 0,
    pdfs_updated INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    error_log JSONB DEFAULT '[]'::jsonb,
    celery_task_id VARCHAR(255),
    progress_pct SMALLINT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_crawl_jobs_domain ON ai_pipeline.crawl_jobs(domain_id);
CREATE INDEX IF NOT EXISTS idx_crawl_jobs_status ON ai_pipeline.crawl_jobs(status);
CREATE INDEX IF NOT EXISTS idx_crawl_jobs_created ON ai_pipeline.crawl_jobs(created_at DESC);

-- 3. crawl_discovered_urls: Discovered URLs with status tracking
CREATE TABLE IF NOT EXISTS ai_pipeline.crawl_discovered_urls (
    url_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id UUID NOT NULL REFERENCES ai_pipeline.crawl_domains(domain_id) ON DELETE CASCADE,
    job_id UUID REFERENCES ai_pipeline.crawl_jobs(job_id) ON DELETE SET NULL,
    url VARCHAR(2048) NOT NULL,
    url_type VARCHAR(20) DEFAULT 'page'
        CHECK (url_type IN ('page','pdf','sitemap')),
    status VARCHAR(20) DEFAULT 'discovered'
        CHECK (status IN ('discovered','queued','crawled','downloaded','skipped','failed')),
    content_hash VARCHAR(64),
    pdf_cache_id UUID,
    relevance_score NUMERIC(3,2) DEFAULT 0.0,
    relevance_reason VARCHAR(500),
    has_extractable_text BOOLEAN,
    page_count INTEGER,
    file_size_bytes BIGINT,
    last_checked_at TIMESTAMPTZ,
    last_changed_at TIMESTAMPTZ,
    error_message VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_crawl_urls_unique ON ai_pipeline.crawl_discovered_urls(domain_id, url);
CREATE INDEX IF NOT EXISTS idx_crawl_urls_status ON ai_pipeline.crawl_discovered_urls(status);
CREATE INDEX IF NOT EXISTS idx_crawl_urls_type ON ai_pipeline.crawl_discovered_urls(url_type);
CREATE INDEX IF NOT EXISTS idx_crawl_urls_relevance ON ai_pipeline.crawl_discovered_urls(relevance_score DESC);

-- Seed default domains
INSERT INTO ai_pipeline.crawl_domains (domain_name, base_url, display_name, url_patterns, crawl_schedule)
VALUES
    ('ihk.de', 'https://www.ihk.de', 'IHK', '["*/fachinformatiker/*","*/pruefungen/*","*/ausbildung/*"]'::jsonb, 'monthly'),
    ('bibb.de', 'https://www.bibb.de', 'BIBB', '["*/berufe/*","*/dokumente/*"]'::jsonb, 'monthly'),
    ('fachinformatiker.de', 'https://www.fachinformatiker.de', 'Fachinformatiker Forum', '["*/topic/*","*/forum/*"]'::jsonb, 'weekly'),
    ('it-handbuch.de', 'https://www.it-handbuch.de', 'IT-Handbuch', '["*"]'::jsonb, 'monthly')
ON CONFLICT (domain_name) DO NOTHING;

COMMIT;
