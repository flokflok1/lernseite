/**
 * Migration 044: Add Theme Preference to Users
 *
 * Purpose:
 *   Add theme_preference column to users table for dark/light mode support
 *
 * Changes:
 *   - Add theme_preference column (VARCHAR(16), NOT NULL, DEFAULT 'dark')
 *   - Add CHECK constraint for valid values ('system', 'light', 'dark')
 *
 * Compliance: PostgreSQL 14+
 * Impact: Non-breaking change, existing users get 'dark' as default
 * Rollback: DROP COLUMN theme_preference
 */

-- ============================================================================
-- Add theme_preference column to users table
-- ============================================================================

ALTER TABLE users
ADD COLUMN theme_preference VARCHAR(16) NOT NULL DEFAULT 'dark';

-- ============================================================================
-- Add constraint to ensure only valid theme values
-- ============================================================================

ALTER TABLE users
ADD CONSTRAINT check_theme_preference
CHECK (theme_preference IN ('system', 'light', 'dark'));

-- ============================================================================
-- Verification
-- ============================================================================

-- Verify column exists and has correct default
DO $$
DECLARE
    column_exists BOOLEAN;
    default_value TEXT;
BEGIN
    -- Check if column exists
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'users'
        AND column_name = 'theme_preference'
    ) INTO column_exists;

    IF NOT column_exists THEN
        RAISE EXCEPTION 'Migration failed: theme_preference column not found';
    END IF;

    -- Check default value
    SELECT column_default
    FROM information_schema.columns
    WHERE table_name = 'users'
    AND column_name = 'theme_preference'
    INTO default_value;

    IF default_value IS NULL OR default_value NOT LIKE '%dark%' THEN
        RAISE WARNING 'Default value for theme_preference may not be set correctly: %', default_value;
    END IF;

    RAISE NOTICE 'Migration 044 completed successfully';
    RAISE NOTICE '  - theme_preference column added';
    RAISE NOTICE '  - Default theme: dark';
    RAISE NOTICE '  - Constraint: system, light, dark';
END $$;
