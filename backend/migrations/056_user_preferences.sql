/**
 * Migration 058: User Preferences Table
 *
 * Purpose:
 *   Create user_preferences table for storing user-specific settings
 *   such as UI preferences, window sizes, and other customizations.
 *
 * Changes:
 *   - Create user_preferences table with JSONB columns for flexibility
 *   - Support for window_sizes, ui_settings, and general preferences
 *
 * Compliance: PostgreSQL 14+
 * Impact: New table, no breaking changes
 * Rollback: DROP TABLE user_preferences;
 */

-- ============================================================================
-- TABLE: user_preferences
-- Description: User-specific preferences and UI settings
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_preferences (
    preference_id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- UI Settings (window sizes, layout preferences)
    window_sizes JSONB DEFAULT '{}'::JSONB,

    -- Desktop UI preferences (taskbar position, default views, etc.)
    ui_settings JSONB DEFAULT '{}'::JSONB,

    -- General preferences (notification settings, defaults, etc.)
    general_settings JSONB DEFAULT '{}'::JSONB,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Each user has only one preferences row
    CONSTRAINT uq_user_preferences_user UNIQUE (user_id)
);

-- ============================================================================
-- Indexes
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_user_preferences_user ON user_preferences(user_id);

-- GIN index for JSONB queries if needed
CREATE INDEX IF NOT EXISTS idx_user_preferences_window_sizes ON user_preferences USING GIN (window_sizes);

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE user_preferences IS 'User-specific preferences and UI settings';
COMMENT ON COLUMN user_preferences.window_sizes IS 'Window size preferences per window type, e.g. {"admin-model-selector": {"width": 800, "height": 600}}';
COMMENT ON COLUMN user_preferences.ui_settings IS 'UI-related settings like taskbar position, sidebar state, etc.';
COMMENT ON COLUMN user_preferences.general_settings IS 'General preferences like notification settings, defaults, etc.';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================

CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
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

    RAISE NOTICE 'Migration 058 completed successfully';
    RAISE NOTICE '  - user_preferences table created';
    RAISE NOTICE '  - JSONB columns: window_sizes, ui_settings, general_settings';
    RAISE NOTICE '  - Unique constraint on user_id';
END $$;
