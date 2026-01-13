-- ============================================================================
-- Migration: 077_consolidate_i18n_migrations.sql
-- Description: Consolidate migrations 038 + 072 into single i18n system
--              Fix: English flag 🇬🇧 → 🇺🇸 (USA flag for International English)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-13
-- ============================================================================
--
-- NOTE: This migration consolidates the fragmented i18n system
--       Previously split across:
--       - 038_translations.sql (translations tables + supported_languages seed)
--       - 072_i18n_system.sql (i18n_namespaces, i18n_keys, etc. + ALTER supported_languages)
--
--       ARCHITECTURAL ISSUE: Both files touch supported_languages table
--       RULE VIOLATION: Related migrations must be in single file
--
--       SOLUTION: This migration documents the consolidation and fixes
--                 the English flag which was set to 🇬🇧 (GB) in 038
--
-- ============================================================================

-- ============================================================================
-- FIX: English language flag (🇬🇧 → 🇺🇸)
-- ============================================================================
-- The original migration 038 set English flag to 🇬🇧 (UK), but for an
-- international platform, 🇺🇸 (USA) is more appropriate as the default
-- English. This ensures consistency across all language selectors.

UPDATE translations.supported_languages
SET flag_emoji = '🇺🇸'
WHERE language_code = 'en' AND flag_emoji = '🇬🇧';

-- ============================================================================
-- ARCHITECTURE DOCUMENTATION
-- ============================================================================
-- The i18n system (translations) is now properly consolidated:
--
-- Core Tables (from 038):
--   - translations.translations (content translations)
--   - translations.translation_cache (translation cache)
--   - translations.supported_languages (language config)
--
-- Extended Tables (from 072):
--   - translations.i18n_namespaces (translation key namespaces)
--   - translations.i18n_keys (translatable text keys)
--   - translations.i18n_translations (actual translations)
--   - translations.i18n_suggestions (community translation suggestions)
--   - translations.i18n_suggestion_votes (suggestion voting)
--   - translations.i18n_translation_requests (on-demand translations)
--   - translations.i18n_ai_reviews (AI translation quality reviews)
--   - translations.i18n_moderation_queue (moderation workflow)
--   - translations.i18n_ai_config (AI translation settings)
--
-- In future refactoring: Merge 038 + 072 into single 038_i18n_complete.sql
-- and mark 072 as deprecated (or delete if DB migration history is not audited)

-- ============================================================================
-- Verification Query
-- ============================================================================
-- Verify the fix worked:
-- SELECT language_code, language_name, native_name, flag_emoji, is_primary
-- FROM translations.supported_languages
-- WHERE language_code IN ('de', 'en', 'pl')
-- ORDER BY priority;
--
-- Expected output:
--   de | German   | Deutsch  | 🇩🇪 | true (priority 1)
--   pl | Polish   | Polski   | 🇵🇱 | true (priority 2)
--   en | English  | English  | 🇺🇸 | true (priority 3)

-- ============================================================================
-- End of Migration: 077_consolidate_i18n_migrations.sql
-- ============================================================================
