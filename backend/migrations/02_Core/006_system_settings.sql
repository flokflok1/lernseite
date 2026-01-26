-- ============================================================================
-- Migration: 006_system_settings.sql
-- Version: 1.0.0
-- Description: Core system settings tables (CREATE only)
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- Phase: 1 (Core Foundation)
-- ============================================================================

-- Drop old version of system_settings from Migration 001 (different schema)
DROP TABLE IF EXISTS core.system_settings CASCADE;

CREATE TABLE IF NOT EXISTS core.system_settings (
    setting_id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT,
    value_type VARCHAR(20) DEFAULT 'string',
    encrypted BOOLEAN DEFAULT FALSE,
    category VARCHAR(50),
    description TEXT,
    editable BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_system_setting_type CHECK (value_type IN ('string', 'number', 'boolean', 'json', 'array'))
);

CREATE INDEX IF NOT EXISTS idx_system_settings_key ON core.system_settings(key);
CREATE INDEX IF NOT EXISTS idx_system_settings_category ON core.system_settings(category);

COMMENT ON TABLE core.system_settings IS 'Global system configuration and preferences';

-- ============================================================================
-- TABLE: feature_flags
-- Description: System-wide feature toggles
-- ============================================================================
CREATE TABLE IF NOT EXISTS core.feature_flags (
    flag_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) UNIQUE NOT NULL,
    enabled BOOLEAN DEFAULT FALSE,
    rollout_percentage INTEGER DEFAULT 0,
    target_roles TEXT[],
    target_organizations UUID[],
    start_date DATE,
    end_date DATE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_feature_rollout CHECK (rollout_percentage BETWEEN 0 AND 100)
);

CREATE INDEX IF NOT EXISTS idx_feature_flags_key ON core.feature_flags(key);
CREATE INDEX IF NOT EXISTS idx_feature_flags_enabled ON core.feature_flags(enabled) WHERE enabled = TRUE;
CREATE INDEX IF NOT EXISTS idx_feature_flags_dates ON core.feature_flags(start_date, end_date);

COMMENT ON TABLE core.feature_flags IS 'System-wide feature toggles and gradual rollouts';

-- ============================================================================
-- TABLE: maintenance_windows
-- Description: Scheduled maintenance periods
-- ============================================================================
CREATE TABLE IF NOT EXISTS core.maintenance_windows (
    window_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    affected_services TEXT[],
    status VARCHAR(20) DEFAULT 'scheduled',
    notification_sent BOOLEAN DEFAULT FALSE,
    created_by UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_maintenance_status CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled'))
);

CREATE INDEX IF NOT EXISTS idx_maintenance_time ON core.maintenance_windows(start_time, end_time);
CREATE INDEX IF NOT EXISTS idx_maintenance_status ON core.maintenance_windows(status);

COMMENT ON TABLE core.maintenance_windows IS 'Scheduled maintenance windows and notifications';

-- ============================================================================
-- End of Migration: 006_system_settings.sql
-- ============================================================================
