-- ============================================================================
-- Migration: 055_smart_agent_system.sql
-- Description: Smart Agent System with Knowledge Caching
-- Author: Claude Code
-- Date: 2025-12-10
-- ============================================================================

BEGIN;

-- ============================================================================
-- TABLE: course_agents
-- Description: Configuration for each course's smart agent
-- ============================================================================
CREATE TABLE IF NOT EXISTS smart_agents.course_agents (
    agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses.courses(course_id) ON DELETE CASCADE,

    -- Agent Settings
    name VARCHAR(100) DEFAULT 'KI-Tutor',
    persona VARCHAR(50) DEFAULT 'friendly',
    language VARCHAR(5) DEFAULT 'de',

    -- Knowledge Status
    knowledge_status VARCHAR(20) DEFAULT 'pending',
    last_warmed_at TIMESTAMPTZ,
    knowledge_version INTEGER DEFAULT 1,

    -- AI Configuration
    primary_provider VARCHAR(50) DEFAULT 'openai',
    primary_model VARCHAR(100) DEFAULT 'gpt-4o-mini',
    fallback_provider VARCHAR(50),
    fallback_model VARCHAR(100),
    temperature DECIMAL(3,2) DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 2000,

    -- Organization Override
    org_config_override JSONB DEFAULT '{}',

    -- Statistics
    total_queries INTEGER DEFAULT 0,
    cache_hits INTEGER DEFAULT 0,
    tokens_saved INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(course_id),
    CONSTRAINT chk_agent_knowledge_status CHECK (
        knowledge_status IN ('pending', 'warming', 'ready', 'stale')
    ),
    CONSTRAINT chk_agent_persona CHECK (
        persona IN ('strict', 'friendly', 'motivating', 'expert')
    )
);

CREATE INDEX idx_course_agents_course ON smart_agents.course_agents (course_id);
CREATE INDEX idx_course_agents_status ON smart_agents.course_agents (knowledge_status);

-- ============================================================================
-- TABLE: agent_knowledge_base
-- Description: Pre-generated and learned knowledge entries
-- ============================================================================
CREATE TABLE IF NOT EXISTS smart_agents.agent_knowledge_base (
    knowledge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES smart_agents.course_agents(agent_id) ON DELETE CASCADE,

    -- Scope (where this knowledge applies)
    scope_type VARCHAR(20) NOT NULL,
    scope_id UUID,

    -- Content Classification
    knowledge_type VARCHAR(30) NOT NULL,
    method_type INTEGER,

    -- Content
    question_hash VARCHAR(64),
    question_text TEXT,
    answer_text TEXT NOT NULL,
    answer_html TEXT,

    -- Source
    source VARCHAR(20) NOT NULL,
    generated_by VARCHAR(50),

    -- Quality Metrics
    quality_score DECIMAL(5,2) DEFAULT 0.00,
    usage_count INTEGER DEFAULT 0,
    positive_feedback INTEGER DEFAULT 0,
    negative_feedback INTEGER DEFAULT 0,

    -- Versioning
    version INTEGER DEFAULT 1,
    superseded_by UUID REFERENCES smart_agents.agent_knowledge_base(knowledge_id),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_knowledge_scope_type CHECK (
        scope_type IN ('course', 'chapter', 'lesson', 'method')
    ),
    CONSTRAINT chk_knowledge_type CHECK (
        knowledge_type IN ('qa_pair', 'explanation', 'example', 'definition', 'summary', 'flashcard', 'quiz_item')
    ),
    CONSTRAINT chk_knowledge_source CHECK (
        source IN ('auto_generated', 'user_interaction', 'manual', 'imported')
    )
);

CREATE INDEX idx_agent_knowledge_agent ON smart_agents.agent_knowledge_base (agent_id);
CREATE INDEX idx_agent_knowledge_scope ON smart_agents.agent_knowledge_base (scope_type, scope_id);
CREATE INDEX idx_agent_knowledge_hash ON smart_agents.agent_knowledge_base (question_hash);
CREATE INDEX idx_agent_knowledge_type ON smart_agents.agent_knowledge_base (knowledge_type);
CREATE INDEX idx_agent_knowledge_method ON smart_agents.agent_knowledge_base (method_type) WHERE method_type IS NOT NULL;
CREATE INDEX idx_agent_knowledge_quality ON smart_agents.agent_knowledge_base (quality_score DESC);

-- Full-text search index for question matching
CREATE INDEX idx_agent_knowledge_question_fts ON smart_agents.agent_knowledge_base USING GIN (to_tsvector('german', COALESCE(question_text, '')));

-- ============================================================================
-- TABLE: agent_cache_entries
-- Description: Redis cache metadata and warm-up tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS smart_agents.agent_cache_entries (
    cache_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES smart_agents.course_agents(agent_id) ON DELETE CASCADE,

    -- Cache Key Info
    cache_key VARCHAR(200) NOT NULL,
    cache_tier INTEGER NOT NULL,

    -- TTL Management
    ttl_seconds INTEGER NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,

    -- Statistics
    hit_count INTEGER DEFAULT 0,
    last_hit_at TIMESTAMPTZ,

    -- Source Knowledge
    knowledge_id UUID REFERENCES smart_agents.agent_knowledge_base(knowledge_id) ON DELETE SET NULL,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(cache_key),
    CONSTRAINT chk_cache_tier CHECK (cache_tier BETWEEN 1 AND 3)
);

CREATE INDEX idx_agent_cache_agent ON smart_agents.agent_cache_entries (agent_id);
CREATE INDEX idx_agent_cache_expires ON smart_agents.agent_cache_entries (expires_at);
CREATE INDEX idx_agent_cache_tier ON smart_agents.agent_cache_entries (cache_tier);

-- ============================================================================
-- TABLE: agent_query_log
-- Description: Track all agent queries for learning and analytics
-- ============================================================================
CREATE TABLE IF NOT EXISTS smart_agents.agent_query_log (
    query_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES smart_agents.course_agents(agent_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,

    -- Query Details
    query_text TEXT NOT NULL,
    query_hash VARCHAR(64) NOT NULL,
    context_scope VARCHAR(20),
    context_id UUID,
    method_type INTEGER,

    -- Response
    response_text TEXT,
    response_source VARCHAR(20) NOT NULL,
    cache_key VARCHAR(200),

    -- Token Economics
    tokens_used INTEGER DEFAULT 0,
    tokens_saved INTEGER DEFAULT 0,
    cost_eur DECIMAL(10,6) DEFAULT 0,

    -- Performance
    latency_ms INTEGER,
    ai_provider VARCHAR(50),
    ai_model VARCHAR(100),

    -- Quality
    user_rating INTEGER,
    user_feedback TEXT,
    was_helpful BOOLEAN,

    -- Offline Mode
    was_offline_mode BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_query_response_source CHECK (
        response_source IN ('cache_hit', 'partial_cache', 'ai_generated', 'offline_fallback', 'error')
    ),
    CONSTRAINT chk_query_rating CHECK (user_rating IS NULL OR user_rating BETWEEN 1 AND 5)
);

CREATE INDEX idx_agent_query_agent ON smart_agents.agent_query_log (agent_id);
CREATE INDEX idx_agent_query_user ON smart_agents.agent_query_log (user_id);
CREATE INDEX idx_agent_query_hash ON smart_agents.agent_query_log (query_hash);
CREATE INDEX idx_agent_query_created ON smart_agents.agent_query_log (created_at DESC);
CREATE INDEX idx_agent_query_source ON smart_agents.agent_query_log (response_source);

-- ============================================================================
-- TABLE: agent_org_extensions
-- Description: Organization-specific agent customizations
-- ============================================================================
CREATE TABLE IF NOT EXISTS smart_agents.agent_org_extensions (
    extension_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES smart_agents.course_agents(agent_id) ON DELETE CASCADE,
    organisation_id UUID NOT NULL REFERENCES organisations.organisations(organisation_id) ON DELETE CASCADE,

    -- Custom Settings
    custom_persona VARCHAR(50),
    custom_language VARCHAR(5),
    custom_terminology JSONB DEFAULT '{}',
    custom_examples JSONB DEFAULT '[]',

    -- Knowledge Extensions
    additional_context TEXT,

    -- Restrictions
    blocked_topics JSONB DEFAULT '[]',

    enabled BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(agent_id, organisation_id)
);

CREATE INDEX idx_agent_org_ext_agent ON smart_agents.agent_org_extensions (agent_id);
CREATE INDEX idx_agent_org_ext_org ON smart_agents.agent_org_extensions (organisation_id);

-- ============================================================================
-- TABLE: agent_warm_jobs
-- Description: Background jobs for knowledge warm-up
-- ============================================================================
CREATE TABLE IF NOT EXISTS smart_agents.agent_warm_jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES smart_agents.course_agents(agent_id) ON DELETE CASCADE,

    -- Job Config
    job_type VARCHAR(30) NOT NULL,
    target_tier INTEGER,

    -- Progress
    status VARCHAR(20) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    total_items INTEGER DEFAULT 0,
    completed_items INTEGER DEFAULT 0,

    -- Results
    tokens_used INTEGER DEFAULT 0,
    cost_eur DECIMAL(10,6) DEFAULT 0,
    items_cached INTEGER DEFAULT 0,
    errors JSONB DEFAULT '[]',

    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_warm_job_type CHECK (
        job_type IN ('full_warm', 'incremental', 'tier_specific', 'chapter_warm', 'lesson_warm')
    ),
    CONSTRAINT chk_warm_job_status CHECK (
        status IN ('pending', 'running', 'completed', 'failed', 'cancelled')
    )
);

CREATE INDEX idx_agent_warm_jobs_agent ON smart_agents.agent_warm_jobs (agent_id);
CREATE INDEX idx_agent_warm_jobs_status ON smart_agents.agent_warm_jobs (status);

-- ============================================================================
-- VIEW: v_agent_stats
-- Description: Aggregated agent statistics
-- ============================================================================
CREATE OR REPLACE VIEW v_agent_stats AS
SELECT
    ca.agent_id,
    ca.course_id,
    c.title as course_title,
    ca.name as agent_name,
    ca.knowledge_status,
    ca.total_queries,
    ca.cache_hits,
    ca.tokens_saved,
    CASE
        WHEN ca.total_queries > 0
        THEN ROUND((ca.cache_hits::DECIMAL / ca.total_queries) * 100, 2)
        ELSE 0
    END as cache_hit_rate,
    COUNT(DISTINCT akb.knowledge_id) as knowledge_count,
    COUNT(DISTINCT aql.query_id) FILTER (WHERE aql.created_at > NOW() - INTERVAL '24 hours') as queries_24h,
    ca.last_warmed_at,
    ca.created_at
FROM smart_agents.course_agents ca
JOIN courses.courses c ON ca.course_id = c.course_id
LEFT JOIN smart_agents.agent_knowledge_base akb ON ca.agent_id = akb.agent_id
LEFT JOIN smart_agents.agent_query_log aql ON ca.agent_id = aql.agent_id
GROUP BY ca.agent_id, ca.course_id, c.title, ca.name, ca.knowledge_status,
         ca.total_queries, ca.cache_hits, ca.tokens_saved, ca.last_warmed_at, ca.created_at;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update timestamp triggers
DROP TRIGGER IF EXISTS update_course_agents_updated_at ON smart_agents.course_agents ;
CREATE TRIGGER update_course_agents_updated_at
    BEFORE UPDATE ON smart_agents.course_agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_agent_knowledge_updated_at ON smart_agents.agent_knowledge_base ;
CREATE TRIGGER update_agent_knowledge_updated_at
    BEFORE UPDATE ON smart_agents.agent_knowledge_base
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_agent_org_ext_updated_at ON smart_agents.agent_org_extensions ;
CREATE TRIGGER update_agent_org_ext_updated_at
    BEFORE UPDATE ON smart_agents.agent_org_extensions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- FUNCTION: increment_agent_stats
-- Description: Atomically update agent statistics after query
-- ============================================================================
CREATE OR REPLACE FUNCTION increment_agent_stats(
    p_agent_id UUID,
    p_cache_hit BOOLEAN,
    p_tokens_saved INTEGER DEFAULT 0
) RETURNS VOID AS $$
BEGIN
    UPDATE smart_agents.course_agents
    SET
        total_queries = total_queries + 1,
        cache_hits = cache_hits + CASE WHEN p_cache_hit THEN 1 ELSE 0 END,
        tokens_saved = tokens_saved + COALESCE(p_tokens_saved, 0),
        updated_at = NOW()
    WHERE agent_id = p_agent_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- FUNCTION: find_similar_knowledge
-- Description: Full-text search for similar questions
-- ============================================================================
CREATE OR REPLACE FUNCTION find_similar_knowledge(
    p_agent_id UUID,
    p_query_text TEXT,
    p_limit INTEGER DEFAULT 5
) RETURNS TABLE (
    knowledge_id UUID,
    question_text TEXT,
    answer_text TEXT,
    similarity_rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        akb.knowledge_id,
        akb.question_text,
        akb.answer_text,
        ts_rank(
            to_tsvector('german', COALESCE(akb.question_text, '')),
            plainto_tsquery('german', p_query_text)
        ) as similarity_rank
    FROM smart_agents.agent_knowledge_base akb
    WHERE akb.agent_id = p_agent_id
      AND akb.question_text IS NOT NULL
      AND to_tsvector('german', akb.question_text) @@ plainto_tsquery('german', p_query_text)
    ORDER BY similarity_rank DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Extend ki_requests table for cache tracking
-- ============================================================================
ALTER TABLE ai_pipeline.ki_requests ADD COLUMN IF NOT EXISTS cache_hit BOOLEAN DEFAULT FALSE;
ALTER TABLE ai_pipeline.ki_requests ADD COLUMN IF NOT EXISTS cache_key VARCHAR(200);
ALTER TABLE ai_pipeline.ki_requests ADD COLUMN IF NOT EXISTS tokens_saved INTEGER DEFAULT 0;

COMMIT;

-- ============================================================================
-- Post-migration verification
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE 'Migration 065_smart_agent_system.sql completed successfully';
    RAISE NOTICE 'Created tables: course_agents, agent_knowledge_base, agent_cache_entries, agent_query_log, agent_org_extensions, agent_warm_jobs';
    RAISE NOTICE 'Created view: v_agent_stats';
    RAISE NOTICE 'Created functions: increment_agent_stats, find_similar_knowledge';
END $$;
