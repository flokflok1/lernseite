-- ============================================================================
-- Migration: 053_capability_slots_part2.sql
-- Description: Capability Slots - Part 2: Extended Features
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================
-- Note: Split from original 053_capability_slots.sql (505 lines)
--       Part 2 of 2
-- ============================================================================


    -- Priority (lower = higher priority)
    priority INTEGER NOT NULL DEFAULT 100,

    -- Is this assignment active?
    active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NULL REFERENCES core.users(user_id),

    -- Constraints (0-31 für Abwärtskompatibilität)
    CONSTRAINT chk_lm_slot_assign_lm_id CHECK (learning_method_id >= 0 AND learning_method_id <= 31),
    CONSTRAINT chk_lm_slot_assign_scope CHECK (scope IN ('system', 'course', 'chapter')),
    CONSTRAINT chk_lm_slot_assign_scope_ref CHECK (
        (scope = 'system' AND scope_reference_id IS NULL) OR
        (scope IN ('course', 'chapter') AND scope_reference_id IS NOT NULL)
    )
);

-- Unique indexes per scope level
CREATE UNIQUE INDEX IF NOT EXISTS idx_lm_slot_assign_system_unique
ON learning_methods.lm_slot_assignments (learning_method_id, slot_id)
WHERE scope = 'system' AND active = TRUE;

CREATE UNIQUE INDEX IF NOT EXISTS idx_lm_slot_assign_course_unique
ON learning_methods.lm_slot_assignments (learning_method_id, slot_id, scope_reference_id)
WHERE scope = 'course' AND active = TRUE;

CREATE UNIQUE INDEX IF NOT EXISTS idx_lm_slot_assign_chapter_unique
ON learning_methods.lm_slot_assignments (learning_method_id, slot_id, scope_reference_id)
WHERE scope = 'chapter' AND active = TRUE;

-- General indexes
CREATE INDEX IF NOT EXISTS idx_lm_slot_assign_lm ON learning_methods.lm_slot_assignments (learning_method_id);
CREATE INDEX IF NOT EXISTS idx_lm_slot_assign_slot ON learning_methods.lm_slot_assignments (slot_id);
CREATE INDEX IF NOT EXISTS idx_lm_slot_assign_model ON learning_methods.lm_slot_assignments (model_id);
CREATE INDEX IF NOT EXISTS idx_lm_slot_assign_active ON learning_methods.lm_slot_assignments (active) WHERE active = TRUE;

-- Comments
COMMENT ON TABLE learning_methods.lm_slot_assignments IS 'Admin assignments of AI models to capability slots per Learning Method';
COMMENT ON COLUMN learning_methods.lm_slot_assignments.scope IS 'system = global default, course/chapter = override';

-- ============================================================================
-- DATA MIGRATION: Migrate existing assignments to chat slot
-- ============================================================================

-- Get chat slot ID for migration
DO $$
DECLARE
    v_chat_slot_id INTEGER;
BEGIN
    SELECT slot_id INTO v_chat_slot_id FROM learning_methods.capability_slots WHERE slot_code = 'chat';

    -- Migrate existing learning_method_model_assignments to lm_slot_assignments
    INSERT INTO learning_methods.lm_slot_assignments (
        learning_method_id,
        slot_id,
        model_id,
        scope,
        scope_reference_id,
        priority,
        active,
        created_at,
        updated_at,
        created_by
    )
    SELECT
        learning_method_id,
        v_chat_slot_id,
        model_id,
        scope,
        scope_reference_id,
        priority,
        active,
        created_at,
        updated_at,
        created_by
    FROM learning_methods.learning_method_model_assignments
    WHERE active = TRUE
    ON CONFLICT DO NOTHING;

    RAISE NOTICE 'Migrated % existing assignments to chat slot', (SELECT COUNT(*) FROM learning_methods.learning_method_model_assignments WHERE active = TRUE);
END $$;

-- ============================================================================
-- FUNCTION: resolve_lm_slot_models
-- Returns all assigned models for all slots of a learning method
-- ============================================================================

CREATE OR REPLACE FUNCTION resolve_lm_slot_models(
    p_learning_method_id INTEGER,
    p_chapter_id UUID DEFAULT NULL,
    p_course_id UUID DEFAULT NULL
) RETURNS TABLE (
    slot_code VARCHAR(30),
    slot_display_name VARCHAR(100),
    is_required BOOLEAN,
    is_primary BOOLEAN,
    model_id INTEGER,
    model_name TEXT,
    model_display_name TEXT,
    provider_name TEXT,
    resolved_scope TEXT,
    is_configured BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    WITH slot_requirements AS (
        -- Get all slot requirements for this LM
        SELECT
            cs.slot_id,
            cs.slot_code,
            cs.display_name AS slot_display_name,
            COALESCE(lsr.is_required, FALSE) AS is_required,
            COALESCE(lsr.is_primary, FALSE) AS is_primary
        FROM capability_slots cs
        LEFT JOIN learning_methods.lm_slot_requirements lsr ON cs.slot_id = lsr.slot_id
            AND lsr.learning_method_id = p_learning_method_id
        WHERE lsr.requirement_id IS NOT NULL  -- Only slots that this LM uses
    ),
    all_assignments AS (
        -- Get all possible assignments for all scopes
        SELECT
            lsa.slot_id,
            lsa.model_id AS assigned_model_id,
            lsa.scope AS assigned_scope,
            lsa.priority,
            -- Priority order: chapter=1, course=2, system=3
            CASE lsa.scope WHEN 'chapter' THEN 1 WHEN 'course' THEN 2 ELSE 3 END AS scope_priority
        FROM learning_methods.lm_slot_assignments lsa
        WHERE lsa.learning_method_id = p_learning_method_id
        AND lsa.active = TRUE
        AND (
            (lsa.scope = 'chapter' AND lsa.scope_reference_id = p_chapter_id AND p_chapter_id IS NOT NULL)
            OR (lsa.scope = 'course' AND lsa.scope_reference_id = p_course_id AND p_course_id IS NOT NULL)
            OR (lsa.scope = 'system')
        )
    ),
    best_assignments AS (
        -- Select best assignment per slot (lowest scope_priority, then lowest priority)
        SELECT DISTINCT ON (aa.slot_id)
            aa.slot_id,
            aa.assigned_model_id,
            aa.assigned_scope,
            aa.priority
        FROM all_assignments aa
        ORDER BY aa.slot_id, aa.scope_priority, aa.priority
    ),
    resolved_assignments AS (
        -- Join slot requirements with their best assignments
        SELECT
            sr.slot_id,
            sr.slot_code,
            sr.slot_display_name,
            sr.is_required,
            sr.is_primary,
            ba.assigned_model_id AS model_id,
            m.model_name,
            m.display_name AS model_display_name,
            p.display_name AS provider_name,
            ba.assigned_scope AS resolved_scope
        FROM slot_requirements sr
        LEFT JOIN best_assignments ba ON sr.slot_id = ba.slot_id
        LEFT JOIN ai_pipeline.ai_models m ON ba.assigned_model_id = m.model_id
        LEFT JOIN ai_pipeline.ai_providers p ON m.provider_id = p.provider_id
    )
    SELECT
        ra.slot_code::VARCHAR(30),
        ra.slot_display_name::VARCHAR(100),
        ra.is_required,
        ra.is_primary,
        ra.model_id,
        ra.model_name::TEXT,
        ra.model_display_name::TEXT,
        ra.provider_name::TEXT,
        COALESCE(ra.resolved_scope, 'none')::TEXT,
        (ra.model_id IS NOT NULL)::BOOLEAN AS is_configured
    FROM resolved_assignments ra
    ORDER BY
        ra.is_primary DESC,
        ra.is_required DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION resolve_lm_slot_models IS 'Resolves all AI models for all capability slots of a learning method (uses CTEs for PostgreSQL compatibility)';

-- ============================================================================
-- VIEW: v_lm_slot_overview
-- Admin overview of all LM slot configurations
-- ============================================================================

CREATE OR REPLACE VIEW v_lm_slot_overview AS
WITH lm_slots AS (
    SELECT
        lm.learning_method_id,
        cs.slot_id,
        cs.slot_code,
        cs.display_name AS slot_name,
        lsr.is_required,
        lsr.is_primary
    -- Nur Content-LMs (0-25), System-Features werden separat behandelt
    FROM (SELECT generate_series(0, 25) AS learning_method_id) lm
    CROSS JOIN learning_methods.capability_slots cs
    LEFT JOIN learning_methods.lm_slot_requirements lsr ON lm.learning_method_id = lsr.learning_method_id
        AND cs.slot_id = lsr.slot_id
    WHERE lsr.requirement_id IS NOT NULL
)
SELECT
    ls.learning_method_id,
    ls.slot_code,
    ls.slot_name,
    ls.is_required,
    ls.is_primary,
    a.assignment_id,
    a.scope,
    m.model_id,
    m.model_name,
    m.display_name AS model_display_name,
    p.name AS provider_name,
    p.display_name AS provider_display_name
FROM lm_slots ls
LEFT JOIN learning_methods.lm_slot_assignments a ON ls.learning_method_id = a.learning_method_id
    AND ls.slot_id = a.slot_id
    AND a.scope = 'system'
    AND a.active = TRUE
LEFT JOIN ai_pipeline.ai_models m ON a.model_id = m.model_id
LEFT JOIN ai_pipeline.ai_providers p ON m.provider_id = p.provider_id
ORDER BY ls.learning_method_id, ls.is_primary DESC, ls.is_required DESC, ls.slot_code;

COMMENT ON VIEW v_lm_slot_overview IS 'Admin overview of LM capability slot configurations';

-- ============================================================================
-- Trigger: Update timestamps
-- ============================================================================

CREATE TRIGGER update_capability_slots_updated_at BEFORE UPDATE ON learning_methods.capability_slots
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_lm_slot_requirements_updated_at BEFORE UPDATE ON learning_methods.lm_slot_requirements
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_lm_slot_assignments_updated_at BEFORE UPDATE ON learning_methods.lm_slot_assignments
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of schema definition
-- ============================================================================

-- ============================================================================
-- End of Migration: 060_capability_slots.sql
-- ============================================================================
