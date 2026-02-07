-- ============================================================================
-- Migration: 089_i18n_languages_primary.sql
-- Description: Add is_primary column to supported_languages.
--              Enables admin to designate exactly ONE default language.
--              Includes partial unique index to enforce single primary.
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-02-06
-- ============================================================================

BEGIN;

-- Add is_primary column (default false)
ALTER TABLE translations.supported_languages
ADD COLUMN IF NOT EXISTS is_primary BOOLEAN NOT NULL DEFAULT FALSE;

-- Set German as the primary language (was implicit via priority=1 before)
UPDATE translations.supported_languages
SET is_primary = TRUE
WHERE language_code = 'de';

-- Ensure only one primary language at a time (partial unique index)
CREATE UNIQUE INDEX IF NOT EXISTS idx_supported_languages_primary
ON translations.supported_languages (is_primary) WHERE is_primary = TRUE;

COMMIT;

-- ============================================================================
-- END MIGRATION 089 (i18n Languages Primary Column)
-- ============================================================================
