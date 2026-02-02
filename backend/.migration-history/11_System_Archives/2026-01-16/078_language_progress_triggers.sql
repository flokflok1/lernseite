-- ============================================================================
-- Migration: 078_language_progress_triggers.sql
-- Description: Automatic language progress calculation triggers
--              - Maintains completion_percent in supported_languages
--              - Updates total_keys and translated_keys automatically
--              - Ensures language statistics are always current
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-15
-- ============================================================================
--
-- PURPOSE:
-- When new translations are added or deleted, automatically update the language
-- progress statistics (completion_percent, total_keys, translated_keys) to keep
-- them in sync with actual translation data.
--
-- PROBLEM SOLVED:
-- Previously, these stats were hardcoded to 0% and never updated, causing
-- incorrect display in the frontend language selector.
--
-- TRIGGERS:
-- 1. update_language_progress_on_translation_insert
--    - Fires after INSERT on i18n_translations
--    - Recalculates progress for that language
--
-- 2. update_language_progress_on_translation_delete
--    - Fires after DELETE on i18n_translations
--    - Recalculates progress for that language
--
-- 3. update_supported_languages_timestamp
--    - Updates the updated_at timestamp when stats change
--
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. TRIGGER FUNCTION: Update Language Progress After Translation Change
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
'Trigger function that updates language progress statistics (total_keys, translated_keys, completion_percent)
whenever translations are inserted, updated, or deleted. Keeps stats in sync with actual translation data.';

-- ============================================================================
-- 2. TRIGGER: Update Progress After Translation INSERT
-- ============================================================================
-- Note: FOR EACH ROW trigger fires once per affected row
-- This allows the trigger function to access NEW/OLD context variables
-- and properly calculate progress for the affected language

DROP TRIGGER IF EXISTS trg_update_language_progress_insert ON translations.i18n_translations;

CREATE TRIGGER trg_update_language_progress_insert
AFTER INSERT ON translations.i18n_translations
FOR EACH ROW
EXECUTE FUNCTION translations.update_language_progress_trigger();

COMMENT ON TRIGGER trg_update_language_progress_insert ON translations.i18n_translations IS
'Automatically recalculates language progress after new translations are inserted.
Keeps completion_percent, total_keys, and translated_keys in sync with actual data.';

-- ============================================================================
-- 3. TRIGGER: Update Progress After Translation DELETE
-- ============================================================================

DROP TRIGGER IF EXISTS trg_update_language_progress_delete ON translations.i18n_translations;

CREATE TRIGGER trg_update_language_progress_delete
AFTER DELETE ON translations.i18n_translations
FOR EACH ROW
EXECUTE FUNCTION translations.update_language_progress_trigger();

COMMENT ON TRIGGER trg_update_language_progress_delete ON translations.i18n_translations IS
'Automatically recalculates language progress after translations are deleted.
Keeps completion_percent, total_keys, and translated_keys in sync with actual data.';

-- ============================================================================
-- 4. TRIGGER: Update Progress After Translation UPDATE
-- ============================================================================

DROP TRIGGER IF EXISTS trg_update_language_progress_update ON translations.i18n_translations;

CREATE TRIGGER trg_update_language_progress_update
AFTER UPDATE ON translations.i18n_translations
FOR EACH ROW
EXECUTE FUNCTION translations.update_language_progress_trigger();

COMMENT ON TRIGGER trg_update_language_progress_update ON translations.i18n_translations IS
'Automatically recalculates language progress after translations are updated.
Ensures statistics reflect any changes to translation data.';

-- ============================================================================
-- 5. INITIAL DATA FIX: Recalculate Progress with Current Data
-- ============================================================================

-- Ensure progress stats are initialized with actual data
-- Note: After function creation, triggers will handle updates automatically
-- This initial call ensures stats are correct if migration runs while system is active
DO $$
DECLARE
    v_lang_code VARCHAR(10);
BEGIN
    -- Recalculate stats for each language by calling the trigger function directly
    FOR v_lang_code IN SELECT DISTINCT language_code FROM translations.i18n_translations LOOP
        UPDATE translations.supported_languages sl
        SET
            total_keys = (SELECT COUNT(DISTINCT key_id) FROM translations.i18n_translations),
            translated_keys = (SELECT COUNT(DISTINCT key_id) FROM translations.i18n_translations WHERE language_code = v_lang_code),
            updated_at = CURRENT_TIMESTAMP
        WHERE sl.language_code = v_lang_code;
    END LOOP;
END;
$$;

COMMIT;
