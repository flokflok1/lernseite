-- ============================================================================
-- Migration: 057_ai_models_sync_support.sql
-- Description: Add columns for AI model sync system (rename price columns)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-12-04
-- ============================================================================

-- ============================================================================
-- Rename price columns for consistency with API
-- ============================================================================

-- Add new columns if they don't exist (some might exist from 050_ai_models.sql)
ALTER TABLE ai_models
ADD COLUMN IF NOT EXISTS input_price_per_1k DECIMAL(10,6);

ALTER TABLE ai_models
ADD COLUMN IF NOT EXISTS output_price_per_1k DECIMAL(10,6);

-- Copy data from old columns if they exist
UPDATE ai_models
SET input_price_per_1k = COALESCE(input_price_per_1k, cost_per_1k_input),
    output_price_per_1k = COALESCE(output_price_per_1k, cost_per_1k_output)
WHERE input_price_per_1k IS NULL OR output_price_per_1k IS NULL;

-- Add model_type to constraint if not already (might have been changed by 050)
-- First check if the constraint exists and drop it
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_model_type') THEN
        ALTER TABLE ai_models DROP CONSTRAINT chk_model_type;
    END IF;
END $$;

-- Add updated constraint with more categories
ALTER TABLE ai_models
ADD CONSTRAINT chk_model_type_extended CHECK (
    model_type IN ('completion', 'chat', 'embedding', 'vision', 'audio', 'multimodal', 'reasoning', 'image', 'video')
);

-- ============================================================================
-- Add sync tracking columns
-- ============================================================================

ALTER TABLE ai_models
ADD COLUMN IF NOT EXISTS last_synced_at TIMESTAMPTZ;

ALTER TABLE ai_models
ADD COLUMN IF NOT EXISTS sync_source VARCHAR(50) DEFAULT 'manual';

COMMENT ON COLUMN ai_models.last_synced_at IS 'Timestamp of last sync from provider API';
COMMENT ON COLUMN ai_models.sync_source IS 'Source of model data: api, manual, adapter';

-- ============================================================================
-- Create index for faster sync queries
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_ai_models_provider_name ON ai_models(provider_id, model_name);
CREATE INDEX IF NOT EXISTS idx_ai_models_sync ON ai_models(last_synced_at);

-- ============================================================================
-- Record migration
-- ============================================================================

INSERT INTO migration_history (migration_name, description, executed_at)
VALUES ('057_ai_models_sync_support', 'Add columns for AI model sync system', NOW())
ON CONFLICT DO NOTHING;

-- ============================================================================
-- End of Migration: 057_ai_models_sync_support.sql
-- ============================================================================
