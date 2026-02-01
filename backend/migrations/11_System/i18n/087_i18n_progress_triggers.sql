-- ============================================================================
-- Migration: 087_i18n_progress_triggers.sql
-- Description: Language Progress Auto-Update System
--              - Trigger function to maintain completion statistics
--              - Fires on INSERT/UPDATE/DELETE of i18n_translations
--              - Auto-calculates total_keys, translated_keys, completion_percent
--
-- Version: 2.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================
--
-- Part 4 of 5-part i18n system (split from 038_i18n_complete.sql)
-- Other parts: 084 (core), 085 (languages), 086 (sync), 088 (namespaces)
--
-- TRIGGER ARCHITECTURE:
-- This system automatically maintains language progress statistics in the
-- supported_languages table. Whenever a translation is added, updated, or
-- deleted, the trigger recalculates:
-- - total_keys: Total distinct keys that have translations in any language
-- - translated_keys: Keys translated for this specific language
-- - completion_percent: (translated_keys / total_keys) * 100
--
-- This ensures the language progress dashboard always shows accurate data
-- without manual recalculation.
--
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. TRIGGER FUNCTION (Auto-update Language Progress)
-- ============================================================================
-- Purpose: Recalculate language statistics when translations change
-- Fires: AFTER INSERT/UPDATE/DELETE on i18n_translations
-- Updates: supported_languages.total_keys, translated_keys, completion_percent
-- ============================================================================

CREATE OR REPLACE FUNCTION translations.update_language_progress_trigger()
RETURNS TRIGGER AS $$
DECLARE
    v_total_keys INTEGER;
    v_translated_keys INTEGER;
    v_completion_percent DECIMAL(5,2);
    v_language_code VARCHAR(10);
BEGIN
    -- Get language code from the row that changed
    IF TG_OP = 'DELETE' THEN
        v_language_code := OLD.language_code;
    ELSE
        v_language_code := NEW.language_code;
    END IF;

    -- Count total keys (keys that have at least one translation in any language)
    SELECT COUNT(DISTINCT key_id)
    INTO v_total_keys
    FROM translations.i18n_translations;

    -- Count translated keys for this language
    SELECT COUNT(DISTINCT key_id)
    INTO v_translated_keys
    FROM translations.i18n_translations
    WHERE language_code = v_language_code;

    -- Calculate completion percentage
    IF v_total_keys > 0 THEN
        v_completion_percent := (v_translated_keys::DECIMAL / v_total_keys::DECIMAL) * 100;
    ELSE
        v_completion_percent := 0;
    END IF;

    -- Update supported_languages table
    UPDATE translations.supported_languages
    SET
        total_keys = v_total_keys,
        translated_keys = v_translated_keys,
        completion_percent = v_completion_percent,
        updated_at = CURRENT_TIMESTAMP
    WHERE language_code = v_language_code;

    -- Return the appropriate row for trigger
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION translations.update_language_progress_trigger() IS
'Trigger function that updates language progress statistics whenever translations are inserted, updated, or deleted';

-- ============================================================================
-- 2. CREATE TRIGGERS (Insert, Update, Delete)
-- ============================================================================
-- Purpose: Attach trigger function to all DML operations on i18n_translations
-- ============================================================================

-- Trigger: INSERT (new translation added)
DROP TRIGGER IF EXISTS trg_update_language_progress_insert ON translations.i18n_translations;
CREATE TRIGGER trg_update_language_progress_insert
    AFTER INSERT ON translations.i18n_translations
    FOR EACH ROW
    EXECUTE FUNCTION translations.update_language_progress_trigger();

-- Trigger: DELETE (translation removed)
DROP TRIGGER IF EXISTS trg_update_language_progress_delete ON translations.i18n_translations;
CREATE TRIGGER trg_update_language_progress_delete
    AFTER DELETE ON translations.i18n_translations
    FOR EACH ROW
    EXECUTE FUNCTION translations.update_language_progress_trigger();

-- Trigger: UPDATE (translation modified)
DROP TRIGGER IF EXISTS trg_update_language_progress_update ON translations.i18n_translations;
CREATE TRIGGER trg_update_language_progress_update
    AFTER UPDATE ON translations.i18n_translations
    FOR EACH ROW
    EXECUTE FUNCTION translations.update_language_progress_trigger();

-- ============================================================================
-- 3. INITIAL DATA FIX (Recalculate Existing Progress)
-- ============================================================================
-- Purpose: Recalculate progress for all languages that already have translations
-- Note: This ensures consistency if migrations are run on existing data
-- ============================================================================

DO $$
DECLARE
    v_lang_code VARCHAR(10);
    v_total_keys INTEGER;
    v_translated_keys INTEGER;
    v_completion_percent DECIMAL(5,2);
BEGIN
    -- Get total distinct keys across all languages
    SELECT COUNT(DISTINCT key_id)
    INTO v_total_keys
    FROM translations.i18n_translations;

    -- Loop through each language that has translations
    FOR v_lang_code IN SELECT DISTINCT language_code FROM translations.i18n_translations LOOP
        -- Count translated keys for this language
        SELECT COUNT(DISTINCT key_id)
        INTO v_translated_keys
        FROM translations.i18n_translations
        WHERE language_code = v_lang_code;

        -- Calculate completion percentage
        IF v_total_keys > 0 THEN
            v_completion_percent := (v_translated_keys::DECIMAL / v_total_keys::DECIMAL) * 100;
        ELSE
            v_completion_percent := 0;
        END IF;

        -- Update supported_languages table
        UPDATE translations.supported_languages
        SET
            total_keys = v_total_keys,
            translated_keys = v_translated_keys,
            completion_percent = v_completion_percent,
            updated_at = CURRENT_TIMESTAMP
        WHERE language_code = v_lang_code;
    END LOOP;
END;
$$;

COMMIT;

-- ============================================================================
-- END MIGRATION 087 (i18n Progress Triggers - Auto-update Statistics)
-- ============================================================================
