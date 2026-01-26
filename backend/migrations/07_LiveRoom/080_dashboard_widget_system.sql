-- ============================================================================
-- Migration: 075_dashboard_widget_system.sql
-- Version: 2.0.0 (Doku-konform überarbeitet)
-- Description: Complete Dashboard & Widget System (DB-driven, Doc-compliant)
-- Author: Claude Code / LernsystemX Migration System
-- Date: 2026-01-02
-- Dependencies: 001_core_users_roles.sql, 051_user_preferences.sql
-- ============================================================================

-- WICHTIG: Diese Migration folgt EXAKT der Spezifikation aus:
-- - LernsystemX-Doku/03_Features/03_Widget-System.md
-- - LernsystemX-Doku/03_Features/02_Dashboard-System.md

-- ============================================================================
-- 1. widgets - Widget-Definitionen (Registry)
-- ============================================================================

CREATE TABLE IF NOT EXISTS dashboards.widgets (
    widget_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    widget_type VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    component_path VARCHAR(255) NOT NULL,
    default_settings JSONB DEFAULT '{}',
    min_role_required VARCHAR(20) DEFAULT 'free',
    is_active BOOLEAN DEFAULT TRUE,
    version VARCHAR(10) DEFAULT '1.0.0',
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_widget_min_role CHECK (min_role_required IN (
        'free', 'premium', 'creator', 'teacher',
        'school_admin', 'company_admin', 'admin', 'superadmin'
    ))
);

CREATE INDEX IF NOT EXISTS idx_widgets_type ON dashboards.widgets(widget_type);
CREATE INDEX IF NOT EXISTS idx_widgets_active ON dashboards.widgets(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE dashboards.widgets IS 'Widget-Type Registry - definiert verfügbare Widget-Typen (Doku: 03_Widget-System.md)';
COMMENT ON COLUMN dashboards.widgets.widget_type IS 'Eindeutiger Widget-Typ Identifier (z.B. "progress", "ki_recommendations")';
COMMENT ON COLUMN dashboards.widgets.min_role_required IS 'Minimale Rolle für Zugriff auf dieses Widget';

-- ============================================================================
-- 2. dashboard_layouts - User Dashboard Layouts
-- ============================================================================

CREATE TABLE IF NOT EXISTS dashboards.dashboard_layouts (
    layout_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    layout_name VARCHAR(100) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    is_adhd_mode BOOLEAN DEFAULT FALSE,
    grid_columns INTEGER DEFAULT 12,
    grid_rows INTEGER DEFAULT 6,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT unique_user_layout_name UNIQUE (user_id, layout_name)
);

CREATE INDEX IF NOT EXISTS idx_layouts_user_default ON dashboards.dashboard_layouts(user_id, is_default);
CREATE INDEX IF NOT EXISTS idx_layouts_adhd ON dashboards.dashboard_layouts(is_adhd_mode) WHERE is_adhd_mode = TRUE;

COMMENT ON TABLE dashboards.dashboard_layouts IS 'User Dashboard Layouts - mehrere Layouts pro User (Standard, Fokus, Detail, etc.)';
COMMENT ON COLUMN dashboards.dashboard_layouts.is_adhd_mode IS 'ADHD/ADHS-Mode: Reduzierte, fokussierte Ansicht (1-3 Widgets)';
COMMENT ON COLUMN dashboards.dashboard_layouts.grid_columns IS 'Grid-Spalten für Drag & Drop Layout (Standard: 12)';

-- ============================================================================
-- 3. user_widgets - User Widget Instances
-- ============================================================================

CREATE TABLE IF NOT EXISTS dashboards.user_widgets (
    user_widget_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    widget_id UUID NOT NULL REFERENCES dashboards.widgets(widget_id) ON DELETE CASCADE,
    layout_id UUID REFERENCES dashboards.dashboard_layouts(layout_id) ON DELETE CASCADE,

    -- Grid Position (Drag & Drop)
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    width INTEGER DEFAULT 1,
    height INTEGER DEFAULT 1,

    -- Display Order (Fallback für einfache Layouts)
    display_order INTEGER DEFAULT 0,

    -- State
    is_collapsed BOOLEAN DEFAULT FALSE,
    is_visible BOOLEAN DEFAULT TRUE,

    -- Custom Settings
    custom_settings JSONB DEFAULT '{}',

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT unique_user_widget_layout UNIQUE (user_id, widget_id, layout_id)
);

CREATE INDEX IF NOT EXISTS idx_user_widgets_user_layout ON dashboards.user_widgets(user_id, layout_id);
CREATE INDEX IF NOT EXISTS idx_user_widgets_widget ON dashboards.user_widgets(widget_id);
CREATE INDEX IF NOT EXISTS idx_user_widgets_visible ON dashboards.user_widgets(is_visible) WHERE is_visible = TRUE;

COMMENT ON TABLE dashboards.user_widgets IS 'User Widget Instances - konkrete Widget-Instanzen mit Positionen';
COMMENT ON COLUMN dashboards.user_widgets.position_x IS 'X-Position im Grid (für Drag & Drop)';
COMMENT ON COLUMN dashboards.user_widgets.position_y IS 'Y-Position im Grid (für Drag & Drop)';
COMMENT ON COLUMN dashboards.user_widgets.custom_settings IS 'User-spezifische Widget-Einstellungen (überschreibt defaults)';

-- ============================================================================
-- 4. widget_data_cache - Widget Data Caching
-- ============================================================================

CREATE TABLE IF NOT EXISTS dashboards.widget_data_cache (
    cache_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    widget_id UUID NOT NULL REFERENCES dashboards.widgets(widget_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,

    -- Cached Data
    cached_data JSONB NOT NULL,

    -- TTL
    expires_at TIMESTAMPTZ NOT NULL,
    last_refreshed TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT unique_widget_user_cache UNIQUE (widget_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_cache_widget_user ON dashboards.widget_data_cache(widget_id, user_id);
CREATE INDEX IF NOT EXISTS idx_cache_expires ON dashboards.widget_data_cache(expires_at);

COMMENT ON TABLE dashboards.widget_data_cache IS 'Widget Data Cache - gecachte Widget-Daten mit TTL';
COMMENT ON COLUMN dashboards.widget_data_cache.expires_at IS 'Cache Expiry Time (TTL)';

-- ============================================================================
-- 5. ki_recommendations - KI Recommendations (Premium+)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_pipeline.ki_recommendations (
    recommendation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,

    -- Recommendation Data
    recommendation_type VARCHAR(50) NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id UUID NOT NULL,

    -- Scoring
    score DECIMAL(3,2) NOT NULL CHECK (score >= 0 AND score <= 1),
    confidence DECIMAL(3,2) DEFAULT 0.85 CHECK (confidence >= 0 AND confidence <= 1),

    -- Content
    reason TEXT NOT NULL,
    context JSONB DEFAULT '{}',

    -- Interaction Tracking
    is_shown BOOLEAN DEFAULT FALSE,
    is_dismissed BOOLEAN DEFAULT FALSE,
    is_accepted BOOLEAN DEFAULT FALSE,
    shown_at TIMESTAMPTZ,
    dismissed_at TIMESTAMPTZ,
    accepted_at TIMESTAMPTZ,

    -- TTL
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,

    CONSTRAINT chk_recommendation_type CHECK (recommendation_type IN (
        'course', 'lesson', 'learning_method', 'exam', 'category', 'pathway'
    )),
    CONSTRAINT chk_target_type CHECK (target_type IN (
        'course', 'lesson', 'exam', 'category', 'learning_method'
    ))
);

CREATE INDEX IF NOT EXISTS idx_recommendations_user ON ai_pipeline.ki_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_type ON ai_pipeline.ki_recommendations(recommendation_type);
CREATE INDEX IF NOT EXISTS idx_recommendations_active ON ai_pipeline.ki_recommendations(user_id, is_shown, is_dismissed, expires_at)
    WHERE is_dismissed = FALSE;
CREATE INDEX IF NOT EXISTS idx_recommendations_expires ON ai_pipeline.ki_recommendations(expires_at);

COMMENT ON TABLE ai_pipeline.ki_recommendations IS 'KI-gestützte Lern-Empfehlungen für Premium+ Users';
COMMENT ON COLUMN ai_pipeline.ki_recommendations.score IS 'Recommendation Score (0.0 - 1.0)';
COMMENT ON COLUMN ai_pipeline.ki_recommendations.confidence IS 'KI Confidence Level (0.0 - 1.0)';
COMMENT ON COLUMN ai_pipeline.ki_recommendations.reason IS 'Human-readable Begründung für Empfehlung';

-- ============================================================================
-- 6. widget_access_log - Widget Access Logging (Analytics)
-- ============================================================================

CREATE TABLE IF NOT EXISTS dashboards.widget_access_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES core.users(user_id) ON DELETE CASCADE,
    widget_id UUID NOT NULL REFERENCES dashboards.widgets(widget_id) ON DELETE CASCADE,

    -- Action
    action VARCHAR(50) NOT NULL,

    -- Performance
    response_time_ms INTEGER,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_widget_action CHECK (action IN (
        'view', 'refresh', 'collapse', 'expand', 'remove', 'add', 'resize', 'move'
    ))
);

CREATE INDEX IF NOT EXISTS idx_widget_log_user ON dashboards.widget_access_log(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_widget_log_widget ON dashboards.widget_access_log(widget_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_widget_log_created ON dashboards.widget_access_log(created_at DESC);

COMMENT ON TABLE dashboards.widget_access_log IS 'Widget Access Logs - Analytics für Widget-Nutzung';
COMMENT ON COLUMN dashboards.widget_access_log.response_time_ms IS 'Widget Load Time in Millisekunden';

-- ============================================================================
-- 7. Helper Functions
-- ============================================================================

-- Function: get_widgets_for_role
CREATE OR REPLACE FUNCTION get_widgets_for_role(p_role VARCHAR)
RETURNS TABLE (
    widget_id UUID,
    widget_type VARCHAR,
    name VARCHAR,
    description TEXT,
    component_path VARCHAR,
    default_settings JSONB,
    min_role_required VARCHAR,
    is_active BOOLEAN,
    version VARCHAR,
    created_at TIMESTAMPTZ
) AS $$
DECLARE
    role_hierarchy_level INTEGER;
BEGIN
    -- Map role to hierarchy level
    role_hierarchy_level := CASE p_role
        WHEN 'free' THEN 1
        WHEN 'premium' THEN 2
        WHEN 'creator' THEN 3
        WHEN 'teacher' THEN 4
        WHEN 'school_admin' THEN 5
        WHEN 'company_admin' THEN 6
        WHEN 'admin' THEN 7
        WHEN 'superadmin' THEN 8
        ELSE 0
    END;

    -- Return widgets accessible for role
    RETURN QUERY
    SELECT
        w.widget_id, w.widget_type, w.name, w.description,
        w.component_path, w.default_settings, w.min_role_required,
        w.is_active, w.version, w.created_at
    FROM dashboards.widgets w
    WHERE w.is_active = TRUE
    AND (
        CASE w.min_role_required
            WHEN 'free' THEN 1
            WHEN 'premium' THEN 2
            WHEN 'creator' THEN 3
            WHEN 'teacher' THEN 4
            WHEN 'school_admin' THEN 5
            WHEN 'company_admin' THEN 6
            WHEN 'admin' THEN 7
            WHEN 'superadmin' THEN 8
            ELSE 0
        END
    ) <= role_hierarchy_level
    ORDER BY w.name;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_widgets_for_role IS 'Gibt alle Widgets zurück die für eine Rolle zugänglich sind';

-- Function: cleanup_expired_cache
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM dashboards.widget_data_cache
    WHERE expires_at < NOW();

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_expired_cache IS 'Löscht abgelaufene Cache-Einträge';

-- Function: cleanup_expired_recommendations
CREATE OR REPLACE FUNCTION cleanup_expired_recommendations()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM ai_pipeline.ki_recommendations
    WHERE expires_at < NOW();

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_expired_recommendations IS 'Löscht abgelaufene KI-Empfehlungen';

-- ============================================================================
-- 8. Seed Data Relocation Notice
-- ============================================================================
-- The following seed data statements have been moved to dedicated seed files:
-- - 15 Widget Definitions (dashboard widgets) → 00_Seeds/16_dashboard_widgets.sql
--
-- This migration file now contains ONLY structural CREATE statements.

-- ============================================================================
-- 9. Seed Data - Default Layouts für Rollen
-- ============================================================================

-- Create helper function for default layout creation
CREATE OR REPLACE FUNCTION create_default_layout_for_user(
    p_user_id UUID,
    p_role VARCHAR
) RETURNS UUID AS $$
DECLARE
    v_layout_id UUID;
    v_widget_id UUID;
    v_position_y INTEGER := 0;
BEGIN
    -- Create default layout
    INSERT INTO dashboards.dashboard_layouts (user_id, layout_name, is_default, grid_columns, grid_rows)
    VALUES (p_user_id, 'Standard', TRUE, 12, 6)
    RETURNING layout_id INTO v_layout_id;

    -- Add widgets based on role
    IF p_role = 'free' THEN
        -- Free User: 5 basic widgets
        FOR v_widget_id IN
            SELECT widget_id FROM dashboards.widgets
            WHERE widget_type IN ('progress', 'courses', 'score', 'library', 'messages')
            ORDER BY widget_type
        LOOP
            INSERT INTO dashboards.user_widgets (user_id, widget_id, layout_id, position_x, position_y, width, height)
            VALUES (p_user_id, v_widget_id, v_layout_id, 0, v_position_y, 12, 1);
            v_position_y := v_position_y + 1;
        END LOOP;

    ELSIF p_role IN ('premium', 'creator') THEN
        -- Premium User: 8 widgets with KI
        FOR v_widget_id IN
            SELECT widget_id FROM dashboards.widgets
            WHERE widget_type IN ('progress', 'courses', 'ki_recommendations', 'token_status', 'score', 'tasks', 'liveroom', 'groups')
            ORDER BY widget_type
        LOOP
            INSERT INTO dashboards.user_widgets (user_id, widget_id, layout_id, position_x, position_y, width, height)
            VALUES (p_user_id, v_widget_id, v_layout_id,
                    CASE WHEN v_position_y % 2 = 0 THEN 0 ELSE 6 END,
                    v_position_y / 2, 6, 1);
            v_position_y := v_position_y + 1;
        END LOOP;

    ELSIF p_role IN ('teacher', 'school_admin') THEN
        -- Teacher: 9 widgets with calendar
        FOR v_widget_id IN
            SELECT widget_id FROM dashboards.widgets
            WHERE widget_type IN ('progress', 'courses', 'calendar', 'tasks', 'score', 'groups', 'messages', 'theory_access', 'library')
            ORDER BY widget_type
        LOOP
            INSERT INTO dashboards.user_widgets (user_id, widget_id, layout_id, position_x, position_y, width, height)
            VALUES (p_user_id, v_widget_id, v_layout_id,
                    CASE WHEN v_position_y % 2 = 0 THEN 0 ELSE 6 END,
                    v_position_y / 2, 6, 1);
            v_position_y := v_position_y + 1;
        END LOOP;
    END IF;

    RETURN v_layout_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION create_default_layout_for_user IS 'Erstellt Default-Layout für neuen User basierend auf Rolle';

-- ============================================================================
-- Migration Complete
-- ============================================================================

-- Verify tables
DO $$
BEGIN
    ASSERT (SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'widgets') = 1,
        'Table widgets not created';
    ASSERT (SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'dashboard_layouts') = 1,
        'Table dashboard_layouts not created';
    ASSERT (SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'user_widgets') = 1,
        'Table user_widgets not created';
    ASSERT (SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'widget_data_cache') = 1,
        'Table widget_data_cache not created';
    ASSERT (SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'ki_recommendations') = 1,
        'Table ki_recommendations not created';
    ASSERT (SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'widget_access_log') = 1,
        'Table widget_access_log not created';

    RAISE NOTICE '✓ Migration 075 completed successfully - 6 tables created with structural schema';
    RAISE NOTICE '  Seed data (15 widgets): loaded from 00_Seeds/16_dashboard_widgets.sql';
END $$;
