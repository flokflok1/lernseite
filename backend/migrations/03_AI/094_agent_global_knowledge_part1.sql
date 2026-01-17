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

-- ============================================================================
-- SCHEMA: agent_intelligence
-- Description: Cross-course agent knowledge and learning
-- ============================================================================
CREATE SCHEMA IF NOT EXISTS agent_intelligence;

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

