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
