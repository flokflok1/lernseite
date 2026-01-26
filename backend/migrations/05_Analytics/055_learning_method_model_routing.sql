-- ============================================================================
-- Migration: 052_learning_method_model_routing.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

-- CREATE: learning_method_model_assignments table
-- Mapping 19 Content-Lernmethoden to AI Models
-- Supports hierarchical overrides: System -> Course -> Chapter -> LM
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_methods.learning_method_model_assignments (
    assignment_id SERIAL PRIMARY KEY,

    -- Learning Method ID (0-25 Content-LMs, 0-31 für Abwärtskompatibilität)
    learning_method_id INTEGER NOT NULL,

    -- AI Model reference
    model_id INTEGER NOT NULL REFERENCES ai_pipeline.ai_models(model_id) ON DELETE CASCADE,

    -- Scope: 'system' (global), 'course', or 'chapter'
    scope VARCHAR(20) NOT NULL DEFAULT 'system',

    -- Optional scope reference (course_id or chapter_id depending on scope)
    scope_reference_id UUID NULL,

    -- Priority (lower = higher priority, used when multiple assignments exist)
    priority INTEGER NOT NULL DEFAULT 100,

    -- Is this assignment active?
    active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NULL REFERENCES core.users(user_id),

    -- Constraints
    CONSTRAINT chk_learning_method_id CHECK (learning_method_id >= 0 AND learning_method_id <= 32),
    CONSTRAINT chk_scope CHECK (scope IN ('system', 'course', 'chapter')),
    CONSTRAINT chk_scope_reference CHECK (
        (scope = 'system' AND scope_reference_id IS NULL) OR
        (scope IN ('course', 'chapter') AND scope_reference_id IS NOT NULL)
    )
);

-- Create unique constraint for system-level assignments (one per LM)
CREATE UNIQUE INDEX IF NOT EXISTS idx_lm_model_system_unique
ON learning_methods.learning_method_model_assignments(learning_method_id)
WHERE scope = 'system' AND active = TRUE;

-- Create unique constraint for course-level assignments (one per LM per course)
CREATE UNIQUE INDEX IF NOT EXISTS idx_lm_model_course_unique
ON learning_methods.learning_method_model_assignments(learning_method_id, scope_reference_id)
WHERE scope = 'course' AND active = TRUE;

-- Create unique constraint for chapter-level assignments (one per LM per chapter)
CREATE UNIQUE INDEX IF NOT EXISTS idx_lm_model_chapter_unique
ON learning_methods.learning_method_model_assignments(learning_method_id, scope_reference_id)
WHERE scope = 'chapter' AND active = TRUE;

-- General indexes for performance
CREATE INDEX IF NOT EXISTS idx_lm_model_assignments_lm_id ON learning_methods.learning_method_model_assignments(learning_method_id);
CREATE INDEX IF NOT EXISTS idx_lm_model_assignments_model_id ON learning_methods.learning_method_model_assignments(model_id);
CREATE INDEX IF NOT EXISTS idx_lm_model_assignments_scope ON learning_methods.learning_method_model_assignments(scope);
CREATE INDEX IF NOT EXISTS idx_lm_model_assignments_active ON learning_methods.learning_method_model_assignments(active) WHERE active = TRUE;

-- Comments
COMMENT ON TABLE learning_methods.learning_method_model_assignments IS 'Maps 19 Content-Lernmethoden to AI Models with hierarchical scope support';
COMMENT ON COLUMN learning_methods.learning_method_model_assignments.learning_method_id IS 'Content-LM ID (0-25), 0-31 für Abwärtskompatibilität';
COMMENT ON COLUMN learning_methods.learning_method_model_assignments.model_id IS 'Reference to ai_models table';
COMMENT ON COLUMN learning_methods.learning_method_model_assignments.scope IS 'Assignment scope: system (global), course, or chapter';
COMMENT ON COLUMN learning_methods.learning_method_model_assignments.scope_reference_id IS 'Course ID or Chapter ID depending on scope';
COMMENT ON COLUMN learning_methods.learning_method_model_assignments.priority IS 'Priority for resolution (lower = higher priority)';

-- ============================================================================
-- CREATE: learning_method_model_requirements table
-- Tracks which LMs require a model assignment (no fallback allowed)
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_methods.learning_method_model_requirements (
    requirement_id SERIAL PRIMARY KEY,

    -- Learning Method ID
    learning_method_id INTEGER NOT NULL UNIQUE,

    -- Is model assignment required? (TRUE = no fallback, must be configured)
    required BOOLEAN NOT NULL DEFAULT TRUE,

    -- Recommended model categories for this LM
    recommended_categories TEXT[] DEFAULT ARRAY['chat'],

    -- Minimum model capabilities required
    requires_vision BOOLEAN DEFAULT FALSE,
    requires_functions BOOLEAN DEFAULT FALSE,
    min_context_window INTEGER DEFAULT NULL,

    -- Description for admin UI
    description TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_lm_req_id CHECK (learning_method_id >= 0 AND learning_method_id <= 32)
);

COMMENT ON TABLE learning_methods.learning_method_model_requirements IS 'Defines model requirements for each Learning Method';
COMMENT ON COLUMN learning_methods.learning_method_model_requirements.required IS 'If TRUE, generation will fail without explicit model assignment';
COMMENT ON COLUMN learning_methods.learning_method_model_requirements.recommended_categories IS 'Model categories suitable for this LM (chat, reasoning, etc.)';

-- ============================================================================
-- Seed Data Relocation Notice
-- ============================================================================
-- The following seed data statements have been moved to dedicated seed files:
-- - Learning Method Model Requirements (33 records LM0-LM32) → 00_Seeds/17_learning_method_requirements.sql
--
-- This migration file now contains ONLY structural CREATE statements.

-- ============================================================================
-- CREATE: Function to resolve model for a learning method
-- Returns the best matching model based on hierarchy
-- ============================================================================

CREATE OR REPLACE FUNCTION resolve_lm_model(
    p_learning_method_id INTEGER,
    p_chapter_id UUID DEFAULT NULL,
    p_course_id UUID DEFAULT NULL
) RETURNS TABLE (
    model_id INTEGER,
    model_name TEXT,
    provider_name TEXT,
    scope TEXT,
    is_configured BOOLEAN
) AS $$
DECLARE
    v_model_id INTEGER;
    v_model_name TEXT;
    v_provider_name TEXT;
    v_scope TEXT;
    v_is_required BOOLEAN;
BEGIN
    -- Check if model is required
    SELECT required INTO v_is_required
    FROM learning_methods.learning_method_model_requirements
    WHERE learning_method_id = p_learning_method_id;

    -- Default to required if not in requirements table
    v_is_required := COALESCE(v_is_required, TRUE);

    -- Try chapter-level first (most specific)
    IF p_chapter_id IS NOT NULL THEN
        SELECT a.model_id, m.model_name, p.name, 'chapter'
        INTO v_model_id, v_model_name, v_provider_name, v_scope
        FROM learning_methods.learning_method_model_assignments a
        JOIN ai_pipeline.ai_models m ON a.model_id = m.model_id
        LEFT JOIN ai_pipeline.ai_providers p ON m.provider_id = p.provider_id
        WHERE a.learning_method_id = p_learning_method_id
        AND a.scope = 'chapter'
        AND a.scope_reference_id = p_chapter_id
        AND a.active = TRUE
        ORDER BY a.priority ASC
        LIMIT 1;

        IF v_model_id IS NOT NULL THEN
            RETURN QUERY SELECT v_model_id, v_model_name, v_provider_name, v_scope, TRUE;
            RETURN;
        END IF;
    END IF;

    -- Try course-level
    IF p_course_id IS NOT NULL THEN
        SELECT a.model_id, m.model_name, p.name, 'course'
        INTO v_model_id, v_model_name, v_provider_name, v_scope
        FROM learning_methods.learning_method_model_assignments a
        JOIN ai_pipeline.ai_models m ON a.model_id = m.model_id
        LEFT JOIN ai_pipeline.ai_providers p ON m.provider_id = p.provider_id
        WHERE a.learning_method_id = p_learning_method_id
        AND a.scope = 'course'
        AND a.scope_reference_id = p_course_id
        AND a.active = TRUE
        ORDER BY a.priority ASC
        LIMIT 1;

        IF v_model_id IS NOT NULL THEN
            RETURN QUERY SELECT v_model_id, v_model_name, v_provider_name, v_scope, TRUE;
            RETURN;
        END IF;
    END IF;

    -- Try system-level (global default)
    SELECT a.model_id, m.model_name, p.name, 'system'
    INTO v_model_id, v_model_name, v_provider_name, v_scope
    FROM learning_methods.learning_method_model_assignments a
    JOIN ai_pipeline.ai_models m ON a.model_id = m.model_id
    LEFT JOIN ai_pipeline.ai_providers p ON m.provider_id = p.provider_id
    WHERE a.learning_method_id = p_learning_method_id
    AND a.scope = 'system'
    AND a.active = TRUE
    ORDER BY a.priority ASC
    LIMIT 1;

    IF v_model_id IS NOT NULL THEN
        RETURN QUERY SELECT v_model_id, v_model_name, v_provider_name, v_scope, TRUE;
        RETURN;
    END IF;

    -- No model configured - return NULL with is_configured = FALSE
    RETURN QUERY SELECT NULL::INTEGER, NULL::TEXT, NULL::TEXT, 'none'::TEXT, FALSE;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION resolve_lm_model IS 'Resolves the AI model to use for a learning method based on hierarchical configuration';

-- ============================================================================
-- CREATE: View for admin overview of all LM assignments
-- ============================================================================

CREATE OR REPLACE VIEW v_learning_method_model_overview AS
SELECT
    lm.learning_method_id,
    lmr.required AS model_required,
    lmr.recommended_categories,
    lmr.description AS lm_description,
    a.assignment_id,
    a.scope,
    a.scope_reference_id,
    a.priority,
    a.active AS assignment_active,
    m.model_id,
    m.model_name,
    m.display_name AS model_display_name,
    m.category AS model_category,
    p.name AS provider_name,
    p.display_name AS provider_display_name
FROM
    (SELECT generate_series(0, 32) AS learning_method_id) lm
LEFT JOIN learning_methods.learning_method_model_requirements lmr ON lm.learning_method_id = lmr.learning_method_id
LEFT JOIN learning_methods.learning_method_model_assignments a ON lm.learning_method_id = a.learning_method_id AND a.scope = 'system' AND a.active = TRUE
LEFT JOIN ai_pipeline.ai_models m ON a.model_id = m.model_id
LEFT JOIN ai_pipeline.ai_providers p ON m.provider_id = p.provider_id
ORDER BY lm.learning_method_id;

COMMENT ON VIEW v_learning_method_model_overview IS 'Admin overview of Learning Method model assignments';

-- ============================================================================
-- End of schema definition
-- ============================================================================

-- ============================================================================
-- End of Migration: 059_learning_method_model_routing.sql
-- ============================================================================
