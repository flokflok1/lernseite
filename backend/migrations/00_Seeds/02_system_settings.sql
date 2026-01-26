-- ============================================================================
-- Seed Migration: 02_system_settings.sql
-- Description: Seed data for system settings and feature flags
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-25
-- Phase: 4 (Seeds - executes AFTER all table creation)
-- Dependencies: 006_system_settings.sql (tables must exist first)
-- ============================================================================

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
-- Verification
-- ============================================================================
-- Expected: 15 system settings records
SELECT COUNT(*) as "system_settings_count" FROM core.system_settings;

-- Expected: 2 triggers created
SELECT COUNT(*) as "triggers_count" FROM information_schema.triggers
WHERE trigger_schema = 'core' AND trigger_name LIKE 'update_%_updated_at';

-- ============================================================================
-- End of Seed Migration: 02_system_settings.sql
-- ============================================================================
