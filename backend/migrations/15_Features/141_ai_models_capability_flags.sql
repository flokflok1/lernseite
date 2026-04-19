-- ============================================================================
-- Migration: 141_ai_models_capability_flags.sql
-- Description: Neue JSONB-Spalte ai_models.capability_flags für strukturierte
--              Provider-Capabilities (z.B. requires_completion_tokens).
--              Ergänzt das bestehende capabilities-Feld (text[]) ohne es
--              zu modifizieren.
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-04-19
-- ============================================================================

ALTER TABLE ai_pipeline.ai_models
    ADD COLUMN IF NOT EXISTS capability_flags JSONB NOT NULL DEFAULT '{}'::jsonb;

COMMENT ON COLUMN ai_pipeline.ai_models.capability_flags IS
'Provider-spezifische Laufzeit-Capabilities, lazy gelernt: z.B.
{"requires_completion_tokens": true, "supports_temperature": false}.
Wird vom Provider beim ersten Request automatisch gesetzt.';

CREATE INDEX IF NOT EXISTS idx_ai_models_capability_flags
    ON ai_pipeline.ai_models USING GIN (capability_flags);

COMMIT;
