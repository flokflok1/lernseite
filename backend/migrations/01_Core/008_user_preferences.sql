-- ============================================================================
-- Migration: 008_user_preferences.sql
-- Version: 1.0.0
-- Description: Create user_preferences table for storing user-specific settings
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

BEGIN;

-- ============================================================================
-- CREATE TABLE: user_preferences - Base structure
-- Description: User-specific preferences and UI settings
-- ============================================================================

CREATE TABLE IF NOT EXISTS core.user_preferences (
    user_preferences_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Reference to user
    user_id UUID NOT NULL UNIQUE REFERENCES core.users(user_id) ON DELETE CASCADE,

    -- UI Settings
    window_sizes JSONB DEFAULT '{}'::JSONB,
    ui_settings JSONB DEFAULT '{}'::JSONB,
    general_settings JSONB DEFAULT '{}'::JSONB,

    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- Indexes
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_user_preferences_user ON core.user_preferences(user_id);

-- GIN index for JSONB queries if needed
CREATE INDEX IF NOT EXISTS idx_user_preferences_window_sizes ON core.user_preferences USING GIN (window_sizes);

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE core.user_preferences IS 'User-specific preferences and UI settings';
COMMENT ON COLUMN core.user_preferences.window_sizes IS 'Window size preferences per window type, e.g. {"admin-model-selector": {"width": 800, "height": 600}}';
COMMENT ON COLUMN core.user_preferences.ui_settings IS 'UI-related settings like taskbar position, sidebar state, etc.';
COMMENT ON COLUMN core.user_preferences.general_settings IS 'General preferences like notification settings, defaults, etc.';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================

DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON core.user_preferences;
CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON core.user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Verification
-- ============================================================================

DO $$
DECLARE
    table_exists BOOLEAN;
BEGIN
    -- Check if table exists
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = 'user_preferences'
    ) INTO table_exists;

    IF NOT table_exists THEN
        RAISE EXCEPTION 'Migration failed: user_preferences table not found';
    END IF;

    RAISE NOTICE 'Migration 008 completed successfully';
    RAISE NOTICE '  - user_preferences table created';
    RAISE NOTICE '  - JSONB columns: window_sizes, ui_settings, general_settings';
    RAISE NOTICE '  - Unique constraint on user_id';
END $$;

COMMIT;
