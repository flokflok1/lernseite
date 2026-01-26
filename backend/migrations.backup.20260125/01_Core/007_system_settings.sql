-- ============================================================================
-- Migration: 007_system_settings.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
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
-- Seed System Settings
-- ============================================================================
INSERT INTO core.system_settings (key, value, value_type, category, description, editable) VALUES
    ('system.name', 'LernsystemX', 'string', 'general', 'System name', false),
    ('system.version', '1.0.0', 'string', 'general', 'Current system version', false),
    ('system.installed', 'true', 'boolean', 'setup', 'Installation completed', false),
    ('system.maintenance_mode', 'false', 'boolean', 'general', 'Maintenance mode enabled', true),
    ('security.password_min_length', '8', 'number', 'security', 'Minimum password length', true),
    ('security.max_login_attempts', '5', 'number', 'security', 'Maximum login attempts before lockout', true),
    ('security.lockout_duration_minutes', '30', 'number', 'security', 'Account lockout duration in minutes', true),
    ('security.session_timeout_hours', '24', 'number', 'security', 'Session timeout in hours', true),
    ('email.from_address', 'noreply@lernsystemx.com', 'string', 'email', 'Default from email address', true),
    ('email.from_name', 'LernsystemX', 'string', 'email', 'Default from name', true),
    ('ai.default_provider', 'anthropic', 'string', 'ai', 'Default AI provider', true),
    ('ai.max_tokens_per_request', '4000', 'number', 'ai', 'Maximum tokens per AI request', true),
    ('storage.max_upload_size_mb', '50', 'number', 'storage', 'Maximum file upload size in MB', true),
    ('courses.max_chapters_per_course', '50', 'number', 'courses', 'Maximum chapters per course', true),
    ('analytics.retention_days', '90', 'number', 'analytics', 'Analytics data retention in days', true)
ON CONFLICT (key) DO NOTHING;

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
DROP TRIGGER IF EXISTS update_system_settings_updated_at ON core.system_settings;
CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON core.system_settings
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_feature_flags_updated_at ON core.feature_flags;
CREATE TRIGGER update_feature_flags_updated_at BEFORE UPDATE ON core.feature_flags
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 007_system_settings.sql
-- ============================================================================
