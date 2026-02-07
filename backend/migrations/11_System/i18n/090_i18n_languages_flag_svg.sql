-- ============================================================================
-- Migration: 090_i18n_languages_flag_svg.sql
-- Description: Replace emoji flag column with flag_svg_code for SVG rendering.
--              Safe 3-phase approach: add nullable -> backfill -> set NOT NULL.
--              Drops old VARCHAR(10) flag column after migration.
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-02-07
-- ============================================================================

BEGIN;

-- ============================================================================
-- Phase 1: Add new column (NULLABLE, no default)
-- ============================================================================
ALTER TABLE translations.supported_languages
ADD COLUMN IF NOT EXISTS flag_svg_code TEXT;

-- ============================================================================
-- Phase 2: Backfill from existing flag column (lowercase emoji → code)
-- ============================================================================
UPDATE translations.supported_languages
SET flag_svg_code = LOWER(TRIM(language_code))
WHERE flag_svg_code IS NULL;

-- ============================================================================
-- Phase 3: Set NOT NULL + CHECK constraint
-- ============================================================================
ALTER TABLE translations.supported_languages
ALTER COLUMN flag_svg_code SET NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_flag_svg_code_format'
    ) THEN
        ALTER TABLE translations.supported_languages
        ADD CONSTRAINT chk_flag_svg_code_format
        CHECK (flag_svg_code ~ '^[a-z0-9-]{2,10}$');
    END IF;
END $$;

-- ============================================================================
-- Phase 4: Drop old flag column
-- ============================================================================
ALTER TABLE translations.supported_languages
DROP COLUMN IF EXISTS flag;

COMMIT;

-- ============================================================================
-- END MIGRATION 090 (i18n Languages Flag SVG Code)
-- ============================================================================
