-- Migration 092: Fix i18n bundle key format
-- ============================================
-- Problem: get_i18n_bundle() returned namespace_code || '.' || key_path
--          (e.g., 'panel.panel.system_panel') but the frontend $t() calls
--          use key_path directly (e.g., 'panel.system_panel').
--          This caused DB translations to never override JSON fallback values.
--
-- Fix: Return just key_path as the bundle key.

CREATE OR REPLACE FUNCTION get_i18n_bundle(
    p_language_code VARCHAR,
    p_namespace VARCHAR DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    result JSONB;
BEGIN
    -- Return key_path as bundle key (NOT namespace_code.key_path)
    -- key_path already contains the full qualified path matching $t() usage
    SELECT COALESCE(jsonb_object_agg(
        k.key_path,
        t.translated_value
    ), '{}'::jsonb)
    INTO result
    FROM translations.i18n_keys k
    JOIN translations.i18n_translations t ON k.key_id = t.key_id
    WHERE t.language_code = p_language_code
    AND t.is_active = TRUE
    AND k.is_active = TRUE
    AND (p_namespace IS NULL OR k.namespace_code = p_namespace);

    RETURN result;
END;
$$;
