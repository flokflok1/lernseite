-- ============================================================================
-- Migration: 094_agent_global_knowledge_part1.sql
-- Description: Agent Intelligence - Part 1: Core Tables & Knowledge Contribution
--              Tables: domain_taxonomy, global_knowledge_pool, agent_learning_events,
--                     cross_agent_sync_status
--              Function: contribute_to_global_knowledge()
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================
-- Previous number: 069 (03_AI) → Renumbered to 094 to resolve duplicates
-- Phase: Agent Intelligence - Global Knowledge Base
-- Note: Split from original 094_agent_global_knowledge.sql (574 lines)
--       Part 1 of 2: Core tables + knowledge contribution
-- Dependencies: 001_core_users_roles.sql, 055_smart_agent_system.sql
-- ============================================================================

BEGIN;

-- NOTE: agent_intelligence schema is created in 01_Core/000_schemas.sql
-- No schema creation needed here

-- ============================================================================
-- TABLE: domain_taxonomy
-- Description: Knowledge domains for classification
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_intelligence.domain_taxonomy (
    domain_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_domain_id UUID REFERENCES agent_intelligence.domain_taxonomy(domain_id),

    -- Domain Info
    domain_code VARCHAR(50) UNIQUE NOT NULL,
    domain_name VARCHAR(100) NOT NULL,
    domain_level INTEGER DEFAULT 1,

    -- Examples: 'networking', 'programming', 'math', 'business'
    description TEXT,

    -- Topics within domain
    topics JSONB DEFAULT '[]',

    -- Metadata
    knowledge_count INTEGER DEFAULT 0,
    last_contribution TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_domain_level CHECK (domain_level BETWEEN 1 AND 5)
);

CREATE INDEX idx_domain_parent ON agent_intelligence.domain_taxonomy(parent_domain_id);
CREATE INDEX idx_domain_code ON agent_intelligence.domain_taxonomy(domain_code);
CREATE INDEX idx_domain_level ON agent_intelligence.domain_taxonomy(domain_level);

-- ============================================================================
-- TABLE: global_knowledge_pool
-- Description: Cross-course shared knowledge base
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_intelligence.global_knowledge_pool (
    global_knowledge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Domain Classification
    domain_id UUID REFERENCES agent_intelligence.domain_taxonomy(domain_id),
    topic VARCHAR(255) NOT NULL,

    -- Content (aggregated from multiple courses)
    question_text TEXT NOT NULL,
    question_hash VARCHAR(64) UNIQUE NOT NULL,
    canonical_answer TEXT NOT NULL,
    answer_variants JSONB DEFAULT '[]',

    -- Knowledge Type
    knowledge_type VARCHAR(30) NOT NULL,
    complexity_level INTEGER DEFAULT 1,

    -- Sources (which courses contributed this?)
    source_courses UUID[] DEFAULT '{}',
    contributor_agents UUID[] DEFAULT '{}',
    total_contributions INTEGER DEFAULT 1,

    -- Quality Metrics (across all courses)
    avg_quality_score DECIMAL(5,2) DEFAULT 0.00,
    total_usage_count INTEGER DEFAULT 0,
    positive_feedback INTEGER DEFAULT 0,
    negative_feedback INTEGER DEFAULT 0,

    -- Confidence (when multiple agents agree, confidence is higher)
    confidence_score DECIMAL(3,2) DEFAULT 0.50,
    consensus_level VARCHAR(20) DEFAULT 'low',

    -- Version Control
    version INTEGER DEFAULT 1,
    last_updated_by UUID REFERENCES smart_agents.course_agents(agent_id),
    superseded_by UUID REFERENCES agent_intelligence.global_knowledge_pool(global_knowledge_id),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_global_knowledge_type CHECK (
        knowledge_type IN ('definition', 'concept', 'process', 'formula', 'best_practice', 'troubleshooting')
    ),
    CONSTRAINT chk_global_complexity CHECK (complexity_level BETWEEN 1 AND 5),
    CONSTRAINT chk_global_consensus CHECK (
        consensus_level IN ('low', 'medium', 'high', 'verified')
    ),
    CONSTRAINT chk_global_confidence CHECK (confidence_score BETWEEN 0 AND 1)
);

CREATE INDEX idx_global_knowledge_domain ON agent_intelligence.global_knowledge_pool(domain_id);
CREATE INDEX idx_global_knowledge_topic ON agent_intelligence.global_knowledge_pool(topic);
CREATE INDEX idx_global_knowledge_hash ON agent_intelligence.global_knowledge_pool(question_hash);
CREATE INDEX idx_global_knowledge_type ON agent_intelligence.global_knowledge_pool(knowledge_type);
CREATE INDEX idx_global_knowledge_confidence ON agent_intelligence.global_knowledge_pool(confidence_score DESC);
CREATE INDEX idx_global_knowledge_quality ON agent_intelligence.global_knowledge_pool(avg_quality_score DESC);

-- Full-text search index for global knowledge
CREATE INDEX idx_global_knowledge_question_fts ON agent_intelligence.global_knowledge_pool
    USING GIN (to_tsvector('german', question_text));

-- ============================================================================
-- TABLE: agent_learning_events
-- Description: Track when agents learn and share knowledge
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_intelligence.agent_learning_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES smart_agents.course_agents(agent_id) ON DELETE CASCADE,

    -- What happened?
    event_type VARCHAR(30) NOT NULL,
    event_description TEXT,

    -- Knowledge Involved
    local_knowledge_id UUID REFERENCES smart_agents.agent_knowledge_base(knowledge_id),
    global_knowledge_id UUID REFERENCES agent_intelligence.global_knowledge_pool(global_knowledge_id),

    -- Impact
    tokens_saved INTEGER DEFAULT 0,
    quality_improvement DECIMAL(5,2),

    -- Context
    triggered_by VARCHAR(50),
    user_id UUID REFERENCES core.users(user_id),

    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_learning_event_type CHECK (
        event_type IN (
            'knowledge_contributed',
            'knowledge_imported',
            'knowledge_refined',
            'consensus_reached',
            'conflict_detected',
            'quality_degraded'
        )
    )
);

CREATE INDEX idx_learning_events_agent ON agent_intelligence.agent_learning_events(agent_id);
CREATE INDEX idx_learning_events_type ON agent_intelligence.agent_learning_events(event_type);
CREATE INDEX idx_learning_events_created ON agent_intelligence.agent_learning_events(created_at DESC);

-- ============================================================================
-- TABLE: cross_agent_sync_status
-- Description: Track synchronization between local and global knowledge
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_intelligence.cross_agent_sync_status (
    sync_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES smart_agents.course_agents(agent_id) ON DELETE CASCADE,

    -- Sync Info
    last_sync_at TIMESTAMPTZ,
    last_sync_version INTEGER DEFAULT 0,
    sync_status VARCHAR(20) DEFAULT 'pending',

    -- Statistics
    knowledge_imported INTEGER DEFAULT 0,
    knowledge_exported INTEGER DEFAULT 0,
    conflicts_detected INTEGER DEFAULT 0,
    conflicts_resolved INTEGER DEFAULT 0,

    -- Next Sync
    next_sync_at TIMESTAMPTZ,
    sync_frequency_hours INTEGER DEFAULT 24,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(agent_id),
    CONSTRAINT chk_sync_status CHECK (
        sync_status IN ('pending', 'syncing', 'completed', 'failed', 'conflict')
    )
);

CREATE INDEX idx_cross_agent_sync_agent ON agent_intelligence.cross_agent_sync_status(agent_id);
CREATE INDEX idx_cross_agent_sync_status ON agent_intelligence.cross_agent_sync_status(sync_status);
CREATE INDEX idx_cross_agent_sync_next ON agent_intelligence.cross_agent_sync_status(next_sync_at);

-- ============================================================================
-- FUNCTION: contribute_to_global_knowledge
-- Description: Agent contributes local knowledge to global pool
-- ============================================================================
CREATE OR REPLACE FUNCTION contribute_to_global_knowledge(
    p_agent_id UUID,
    p_local_knowledge_id UUID,
    p_domain_id UUID,
    p_topic VARCHAR(255)
) RETURNS UUID AS $$
DECLARE
    v_global_knowledge_id UUID;
    v_question_text TEXT;
    v_question_hash VARCHAR(64);
    v_answer_text TEXT;
    v_knowledge_type VARCHAR(30);
    v_quality_score DECIMAL(5,2);
    v_course_id UUID;
    v_existing_global_id UUID;
BEGIN
    -- Get local knowledge details
    SELECT question_text, question_hash, answer_text, knowledge_type, quality_score
    INTO v_question_text, v_question_hash, v_answer_text, v_knowledge_type, v_quality_score
    FROM smart_agents.agent_knowledge_base
    WHERE knowledge_id = p_local_knowledge_id;

    -- Get course_id for this agent
    SELECT course_id INTO v_course_id
    FROM smart_agents.course_agents
    WHERE agent_id = p_agent_id;

    -- Check if similar global knowledge exists
    SELECT global_knowledge_id INTO v_existing_global_id
    FROM agent_intelligence.global_knowledge_pool
    WHERE question_hash = v_question_hash;

    IF v_existing_global_id IS NOT NULL THEN
        -- Update existing global knowledge
        UPDATE agent_intelligence.global_knowledge_pool
        SET
            source_courses = array_append(source_courses, v_course_id),
            contributor_agents = array_append(contributor_agents, p_agent_id),
            total_contributions = total_contributions + 1,
            avg_quality_score = (avg_quality_score * total_contributions + v_quality_score) / (total_contributions + 1),
            total_usage_count = total_usage_count + 1,
            confidence_score = LEAST(1.0, confidence_score + 0.1),
            consensus_level = CASE
                WHEN total_contributions >= 10 THEN 'verified'
                WHEN total_contributions >= 5 THEN 'high'
                WHEN total_contributions >= 2 THEN 'medium'
                ELSE 'low'
            END,
            last_updated_by = p_agent_id,
            updated_at = NOW()
        WHERE global_knowledge_id = v_existing_global_id
        RETURNING global_knowledge_id INTO v_global_knowledge_id;
    ELSE
        -- Create new global knowledge
        INSERT INTO agent_intelligence.global_knowledge_pool (
            domain_id,
            topic,
            question_text,
            question_hash,
            canonical_answer,
            knowledge_type,
            source_courses,
            contributor_agents,
            avg_quality_score,
            last_updated_by
        ) VALUES (
            p_domain_id,
            p_topic,
            v_question_text,
            v_question_hash,
            v_answer_text,
            v_knowledge_type,
            ARRAY[v_course_id],
            ARRAY[p_agent_id],
            v_quality_score,
            p_agent_id
        )
        RETURNING global_knowledge_id INTO v_global_knowledge_id;

        -- Update domain knowledge count
        UPDATE agent_intelligence.domain_taxonomy
        SET knowledge_count = knowledge_count + 1,
            last_contribution = NOW()
        WHERE domain_id = p_domain_id;
    END IF;

    -- Log learning event
    INSERT INTO agent_intelligence.agent_learning_events (
        agent_id,
        event_type,
        local_knowledge_id,
        global_knowledge_id,
        event_description
    ) VALUES (
        p_agent_id,
        'knowledge_contributed',
        p_local_knowledge_id,
        v_global_knowledge_id,
        'Contributed knowledge to global pool'
    );

    RETURN v_global_knowledge_id;
END;
$$ LANGUAGE plpgsql;



-- ============================================================================
-- Migration: 094_agent_global_knowledge_part2.sql
-- Description: Agent Intelligence - Part 2: Knowledge Import & Sync
--              Function: import_global_knowledge()
--              Features: Cross-agent knowledge synchronization, conflict resolution
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================
-- Previous number: 069 (03_AI) → Renumbered to 094 to resolve duplicates
-- Phase: Agent Intelligence - Global Knowledge Base
-- Note: Split from original 094_agent_global_knowledge.sql (574 lines)
--       Part 2 of 2: Knowledge import and synchronization
-- Dependencies: 094_agent_global_knowledge_part1.sql
-- ============================================================================

-- ============================================================================
-- FUNCTION: import_global_knowledge
-- Description: Agent imports global knowledge to local base
-- ============================================================================
CREATE OR REPLACE FUNCTION import_global_knowledge(
    p_agent_id UUID,
    p_global_knowledge_id UUID,
    p_scope_type VARCHAR(20),
    p_scope_id UUID
) RETURNS UUID AS $$
DECLARE
    v_local_knowledge_id UUID;
    v_question_text TEXT;
    v_canonical_answer TEXT;
    v_knowledge_type VARCHAR(30);
    v_quality_score DECIMAL(5,2);
BEGIN
    -- Get global knowledge details
    SELECT question_text, canonical_answer, knowledge_type, avg_quality_score
    INTO v_question_text, v_canonical_answer, v_knowledge_type, v_quality_score
    FROM agent_intelligence.global_knowledge_pool
    WHERE global_knowledge_id = p_global_knowledge_id;

    -- Check if agent already has this knowledge locally
    SELECT knowledge_id INTO v_local_knowledge_id
    FROM smart_agents.agent_knowledge_base
    WHERE agent_id = p_agent_id
      AND question_text = v_question_text;

    IF v_local_knowledge_id IS NULL THEN
        -- Import to local knowledge base
        INSERT INTO smart_agents.agent_knowledge_base (
            agent_id,
            scope_type,
            scope_id,
            knowledge_type,
            question_text,
            answer_text,
            source,
            quality_score
        ) VALUES (
            p_agent_id,
            p_scope_type,
            p_scope_id,
            v_knowledge_type,
            v_question_text,
            v_canonical_answer,
            'imported',
            v_quality_score
        )
        RETURNING knowledge_id INTO v_local_knowledge_id;

        -- Log learning event
        INSERT INTO agent_intelligence.agent_learning_events (
            agent_id,
            event_type,
            local_knowledge_id,
            global_knowledge_id,
            event_description
        ) VALUES (
            p_agent_id,
            'knowledge_imported',
            v_local_knowledge_id,
            p_global_knowledge_id,
            'Imported knowledge from global pool'
        );
    END IF;

    RETURN v_local_knowledge_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- FUNCTION: find_global_knowledge
-- Description: Search global knowledge pool (cross-course)
-- ============================================================================
CREATE OR REPLACE FUNCTION find_global_knowledge(
    p_query_text TEXT,
    p_domain_id UUID DEFAULT NULL,
    p_min_confidence DECIMAL(3,2) DEFAULT 0.5,
    p_limit INTEGER DEFAULT 5
) RETURNS TABLE (
    global_knowledge_id UUID,
    question_text TEXT,
    canonical_answer TEXT,
    confidence_score DECIMAL(3,2),
    total_contributions INTEGER,
    similarity_rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        gkp.global_knowledge_id,
        gkp.question_text,
        gkp.canonical_answer,
        gkp.confidence_score,
        gkp.total_contributions,
        ts_rank(
            to_tsvector('german', gkp.question_text),
            plainto_tsquery('german', p_query_text)
        ) as similarity_rank
    FROM agent_intelligence.global_knowledge_pool gkp
    WHERE
        (p_domain_id IS NULL OR gkp.domain_id = p_domain_id)
        AND gkp.confidence_score >= p_min_confidence
        AND to_tsvector('german', gkp.question_text) @@ plainto_tsquery('german', p_query_text)
    ORDER BY similarity_rank DESC, gkp.confidence_score DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- FUNCTION: sync_agent_knowledge
-- Description: Sync local agent knowledge with global pool
-- ============================================================================
CREATE OR REPLACE FUNCTION sync_agent_knowledge(
    p_agent_id UUID
) RETURNS TABLE (
    imported INTEGER,
    exported INTEGER,
    conflicts INTEGER
) AS $$
DECLARE
    v_imported INTEGER := 0;
    v_exported INTEGER := 0;
    v_conflicts INTEGER := 0;
    v_course_id UUID;
    v_domain_id UUID;
    v_local_knowledge RECORD;
    v_global_knowledge RECORD;
BEGIN
    -- Get course and domain for this agent
    SELECT course_id INTO v_course_id
    FROM smart_agents.course_agents
    WHERE agent_id = p_agent_id;

    -- Export high-quality local knowledge to global pool
    FOR v_local_knowledge IN
        SELECT * FROM smart_agents.agent_knowledge_base
        WHERE agent_id = p_agent_id
          AND quality_score >= 4.0
          AND source != 'imported'
    LOOP
        -- Try to contribute to global pool
        BEGIN
            PERFORM contribute_to_global_knowledge(
                p_agent_id,
                v_local_knowledge.knowledge_id,
                v_domain_id,
                'general'
            );
            v_exported := v_exported + 1;
        EXCEPTION WHEN OTHERS THEN
            v_conflicts := v_conflicts + 1;
        END;
    END LOOP;

    -- Import relevant global knowledge
    FOR v_global_knowledge IN
        SELECT * FROM agent_intelligence.global_knowledge_pool
        WHERE confidence_score >= 0.8
          AND NOT (v_course_id = ANY(source_courses))
    LOOP
        -- Try to import to local base
        BEGIN
            PERFORM import_global_knowledge(
                p_agent_id,
                v_global_knowledge.global_knowledge_id,
                'course',
                v_course_id
            );
            v_imported := v_imported + 1;
        EXCEPTION WHEN OTHERS THEN
            -- Already exists or conflict
            CONTINUE;
        END;
    END LOOP;

    -- Update sync status
    INSERT INTO agent_intelligence.cross_agent_sync_status (agent_id, last_sync_at, sync_status)
    VALUES (p_agent_id, NOW(), 'completed')
    ON CONFLICT (agent_id) DO UPDATE
    SET
        last_sync_at = NOW(),
        sync_status = 'completed',
        knowledge_imported = cross_agent_sync_status.knowledge_imported + v_imported,
        knowledge_exported = cross_agent_sync_status.knowledge_exported + v_exported,
        conflicts_detected = cross_agent_sync_status.conflicts_detected + v_conflicts,
        next_sync_at = NOW() + INTERVAL '24 hours',
        updated_at = NOW();

    RETURN QUERY SELECT v_imported, v_exported, v_conflicts;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VIEW: v_global_knowledge_stats
-- Description: Statistics about global knowledge pool
-- ============================================================================
CREATE OR REPLACE VIEW v_global_knowledge_stats AS
SELECT
    dt.domain_name,
    dt.domain_code,
    COUNT(gkp.global_knowledge_id) as total_knowledge,
    COALESCE((
        SELECT COUNT(DISTINCT course_id)
        FROM unnest(array_agg(gkp.source_courses)) as course_id
    ), 0) as contributing_courses,
    AVG(gkp.confidence_score) as avg_confidence,
    AVG(gkp.avg_quality_score) as avg_quality,
    SUM(gkp.total_usage_count) as total_usage
FROM agent_intelligence.domain_taxonomy dt
LEFT JOIN agent_intelligence.global_knowledge_pool gkp ON dt.domain_id = gkp.domain_id
GROUP BY dt.domain_id, dt.domain_name, dt.domain_code;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update timestamp triggers
DROP TRIGGER IF EXISTS update_domain_taxonomy_updated_at ON agent_intelligence.domain_taxonomy;
CREATE TRIGGER update_domain_taxonomy_updated_at
    BEFORE UPDATE ON agent_intelligence.domain_taxonomy
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_global_knowledge_updated_at ON agent_intelligence.global_knowledge_pool;
CREATE TRIGGER update_global_knowledge_updated_at
    BEFORE UPDATE ON agent_intelligence.global_knowledge_pool
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_cross_agent_sync_updated_at ON agent_intelligence.cross_agent_sync_status;
CREATE TRIGGER update_cross_agent_sync_updated_at
    BEFORE UPDATE ON agent_intelligence.cross_agent_sync_status
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SEED: Initial domain taxonomy
-- ============================================================================
INSERT INTO agent_intelligence.domain_taxonomy (domain_code, domain_name, domain_level, description, topics) VALUES
('networking', 'Netzwerktechnik', 1, 'Computernetzwerke, Protokolle, Topologien', '["TCP/IP", "OSI-Modell", "Routing", "Switching", "Firewall"]'),
('programming', 'Programmierung', 1, 'Programmiersprachen, Algorithmen, Design Patterns', '["Python", "JavaScript", "OOP", "Funktional", "Datenstrukturen"]'),
('databases', 'Datenbanken', 1, 'SQL, NoSQL, Datenmodellierung', '["PostgreSQL", "MongoDB", "Normalisierung", "Indexierung", "Transaktionen"]'),
('web_dev', 'Webentwicklung', 1, 'Frontend, Backend, APIs', '["Vue.js", "React", "REST", "GraphQL", "Authentication"]'),
('devops', 'DevOps', 1, 'CI/CD, Container, Cloud', '["Docker", "Kubernetes", "Git", "Jenkins", "AWS"]'),
('security', 'IT-Sicherheit', 1, 'Verschlüsselung, Authentifizierung, Bedrohungen', '["OWASP", "JWT", "SSL/TLS", "Penetration Testing", "Firewalls"]'),
('math', 'Mathematik', 1, 'Algebra, Analysis, Statistik', '["Lineare Algebra", "Calculus", "Wahrscheinlichkeit", "Statistik"]'),
('business', 'Betriebswirtschaft', 1, 'BWL, Controlling, Marketing', '["Buchhaltung", "Kostenrechnung", "Marketing", "Projektmanagement"]')
ON CONFLICT (domain_code) DO NOTHING;

COMMIT;

-- ============================================================================
-- Post-migration verification
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE 'Migration 066_agent_global_knowledge.sql completed successfully';
    RAISE NOTICE 'Created schema: agent_intelligence';
    RAISE NOTICE 'Created tables: domain_taxonomy, global_knowledge_pool, agent_learning_events, cross_agent_sync_status';
    RAISE NOTICE 'Created functions: contribute_to_global_knowledge, import_global_knowledge, find_global_knowledge, sync_agent_knowledge';
    RAISE NOTICE 'Created view: v_global_knowledge_stats';
    RAISE NOTICE 'Seeded 8 initial knowledge domains';
    RAISE NOTICE '';
    RAISE NOTICE '=== AGENT INTELLIGENCE SYSTEM ===';
    RAISE NOTICE 'Agents can now:';
    RAISE NOTICE '1. Contribute local knowledge to global pool';
    RAISE NOTICE '2. Import high-quality knowledge from other courses';
    RAISE NOTICE '3. Benefit from cross-course consensus';
    RAISE NOTICE '4. Save tokens through shared learning';
END $$;
