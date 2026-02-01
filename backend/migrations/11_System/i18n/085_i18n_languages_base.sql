-- ============================================================================
-- Migration: 085_i18n_languages_base.sql
-- Description: Base language configuration (3 core languages only)
--              - DE (Deutsch) - Primary language, Priority 1
--              - PL (Polski) - Secondary language, Priority 2
--              - EN (English) - Tertiary language, Priority 3
--
--              Additional languages can be added dynamically via Admin Panel.
--
-- Version: 2.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================
--
-- Part 2 of 5-part i18n system (split from 038_i18n_complete.sql)
-- Other parts: 084 (core), 086 (sync), 087 (triggers), 088 (namespaces)
--
-- FLEXIBLE DESIGN:
-- This migration ONLY seeds the 3 core languages (DE, PL, EN).
-- Additional languages can be added dynamically via Admin Panel.
-- The system supports all ISO 639-1 language codes without requiring migrations.
--
-- ============================================================================

BEGIN;

-- ============================================================================
-- SEED: 3 Core Languages (DE, PL, EN)
-- ============================================================================

INSERT INTO translations.supported_languages
(language_code, language_name, native_name, flag, is_active, is_rtl, priority, total_keys, translated_keys, completion_percent)
VALUES
    -- Priority 1: German (Primary)
    ('de', 'German', 'Deutsch', '🇩🇪', true, false, 1, 0, 0, 0.00),

    -- Priority 2: Polish (Secondary)
    ('pl', 'Polish', 'Polski', '🇵🇱', true, false, 2, 0, 0, 0.00),

    -- Priority 3: English (Tertiary)
    ('en', 'English', 'English', 'EN', true, false, 3, 0, 0, 0.00)

ON CONFLICT (language_code) DO UPDATE SET
    language_name = EXCLUDED.language_name,
    native_name = EXCLUDED.native_name,
    flag = EXCLUDED.flag,
    is_active = EXCLUDED.is_active,
    is_rtl = EXCLUDED.is_rtl,
    priority = EXCLUDED.priority,
    updated_at = NOW();

-- ============================================================================
-- ADDING ADDITIONAL LANGUAGES
-- ============================================================================
--
-- Additional languages can be added dynamically via Admin Panel:
--
--   Admin UI: /admin/system/languages
--   API: POST /api/admin/system/languages
--
-- The system supports all ISO 639-1 language codes.
-- Additional languages can be added at any time without database migrations.
--
-- ============================================================================

COMMIT;

-- ============================================================================
-- END MIGRATION 085 (i18n Languages Base - 3 Core Languages)
-- ============================================================================
