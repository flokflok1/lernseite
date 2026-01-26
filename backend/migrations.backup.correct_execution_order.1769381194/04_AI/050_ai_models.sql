-- ============================================================================
-- Migration: 045_ai_models.sql
-- Description: Extend AI Models registry (category, cost_level, speed, is_default)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-11-26
-- ============================================================================

-- ============================================================================
-- ALTER: ai_models table - add new fields for model selection
-- ============================================================================

-- Add category field (maps from model_type but with extended values)
ALTER TABLE ai_pipeline.ai_models
ADD COLUMN IF NOT EXISTS category TEXT DEFAULT 'chat';

-- Add cost_level field
ALTER TABLE ai_pipeline.ai_models
ADD COLUMN IF NOT EXISTS cost_level TEXT DEFAULT 'medium';

-- Add speed field
ALTER TABLE ai_pipeline.ai_models
ADD COLUMN IF NOT EXISTS speed TEXT DEFAULT 'medium';

-- Add description field
ALTER TABLE ai_pipeline.ai_models
ADD COLUMN IF NOT EXISTS description TEXT;

-- Add is_default field
ALTER TABLE ai_pipeline.ai_models
ADD COLUMN IF NOT EXISTS is_default BOOLEAN DEFAULT FALSE;

-- Add max_output_tokens field (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_models' AND column_name = 'max_output_tokens') THEN
        ALTER TABLE ai_pipeline.ai_models ADD COLUMN max_output_tokens INTEGER;
    END IF;
END $$;

-- Comments
COMMENT ON COLUMN ai_pipeline.ai_models.category IS 'Model category: reasoning, chat, realtime, audio, image, video, embedding, moderation';
COMMENT ON COLUMN ai_pipeline.ai_models.cost_level IS 'Cost level: free, low, medium, high, very_high';
COMMENT ON COLUMN ai_pipeline.ai_models.speed IS 'Response speed: very_fast, fast, medium, slow';
COMMENT ON COLUMN ai_pipeline.ai_models.is_default IS 'Whether this is the system-wide default model';
COMMENT ON COLUMN ai_pipeline.ai_models.description IS 'Human-readable model description';

-- ============================================================================
-- Create indexes for new fields
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_ai_models_category_new ON ai_pipeline.ai_models (category);
CREATE INDEX IF NOT EXISTS idx_ai_models_is_default_new ON ai_pipeline.ai_models (is_default) WHERE is_default = TRUE;
CREATE INDEX IF NOT EXISTS idx_ai_models_cost_level ON ai_pipeline.ai_models (cost_level);

-- ============================================================================
-- ALTER: courses table - add ai_model_override
-- ============================================================================
ALTER TABLE courses.courses
ADD COLUMN IF NOT EXISTS ai_model_override TEXT NULL;

COMMENT ON COLUMN courses.courses.ai_model_override IS 'Optional AI model override for this course';

-- ============================================================================
-- ALTER: chapters table - add ai_model_override
-- ============================================================================
ALTER TABLE courses.chapters
ADD COLUMN IF NOT EXISTS ai_model_override TEXT NULL;

COMMENT ON COLUMN courses.chapters.ai_model_override IS 'Optional AI model override for this chapter';

-- ============================================================================
-- ALTER: ai_jobs table - add model field
-- ============================================================================
ALTER TABLE ai_pipeline.ai_jobs
ADD COLUMN IF NOT EXISTS model TEXT NULL;

COMMENT ON COLUMN ai_pipeline.ai_jobs.model IS 'AI model used for this job';

-- ============================================================================
-- Ensure only one default model per category (trigger function)
-- ============================================================================
CREATE OR REPLACE FUNCTION ensure_single_default_ai_model()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_default = TRUE THEN
        UPDATE ai_pipeline.ai_models
        SET is_default = FALSE
        WHERE category = NEW.category
        AND model_id != NEW.model_id
        AND is_default = TRUE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS ensure_single_default_ai_model ON ai_pipeline.ai_models ;
CREATE TRIGGER ensure_single_default_ai_model
    BEFORE INSERT OR UPDATE OF is_default ON ai_pipeline.ai_models
    FOR EACH ROW
    WHEN (NEW.is_default = TRUE)
    EXECUTE FUNCTION ensure_single_default_ai_model();

-- ============================================================================
-- NOTE: Keine Seed-Daten - Models werden via API synchronisiert
-- Alle Modelle werden im Frontend über die KI-Studio-Oberfläche konfiguriert
-- ============================================================================

-- ============================================================================
-- End of Migration: 045_ai_models.sql
-- ============================================================================
