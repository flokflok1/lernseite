-- ============================================================================
-- Migration: 050_ai_models.sql
-- Description: Extend AI Models registry for OpenAI model selection (Phase C3.0)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-11-26
-- ============================================================================

-- ============================================================================
-- ALTER: ai_models table - add new fields for model selection
-- ============================================================================

-- Add category field (maps from model_type but with extended values)
ALTER TABLE ai_models
ADD COLUMN IF NOT EXISTS category TEXT DEFAULT 'chat';

-- Add cost_level field
ALTER TABLE ai_models
ADD COLUMN IF NOT EXISTS cost_level TEXT DEFAULT 'medium';

-- Add speed field
ALTER TABLE ai_models
ADD COLUMN IF NOT EXISTS speed TEXT DEFAULT 'medium';

-- Add description field
ALTER TABLE ai_models
ADD COLUMN IF NOT EXISTS description TEXT;

-- Add is_default field
ALTER TABLE ai_models
ADD COLUMN IF NOT EXISTS is_default BOOLEAN DEFAULT FALSE;

-- Add max_output_tokens field (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'ai_models' AND column_name = 'max_output_tokens') THEN
        ALTER TABLE ai_models ADD COLUMN max_output_tokens INTEGER;
    END IF;
END $$;

-- Comments
COMMENT ON COLUMN ai_models.category IS 'Model category: reasoning, chat, realtime, audio, image, video, embedding, moderation';
COMMENT ON COLUMN ai_models.cost_level IS 'Cost level: free, low, medium, high, very_high';
COMMENT ON COLUMN ai_models.speed IS 'Response speed: very_fast, fast, medium, slow';
COMMENT ON COLUMN ai_models.is_default IS 'Whether this is the system-wide default model';
COMMENT ON COLUMN ai_models.description IS 'Human-readable model description';

-- ============================================================================
-- Create indexes for new fields
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_ai_models_category_new ON ai_models(category);
CREATE INDEX IF NOT EXISTS idx_ai_models_is_default_new ON ai_models(is_default) WHERE is_default = TRUE;
CREATE INDEX IF NOT EXISTS idx_ai_models_cost_level ON ai_models(cost_level);

-- ============================================================================
-- ALTER: courses table - add ai_model_override
-- ============================================================================
ALTER TABLE courses
ADD COLUMN IF NOT EXISTS ai_model_override TEXT NULL;

COMMENT ON COLUMN courses.ai_model_override IS 'Optional AI model override for this course';

-- ============================================================================
-- ALTER: chapters table - add ai_model_override
-- ============================================================================
ALTER TABLE chapters
ADD COLUMN IF NOT EXISTS ai_model_override TEXT NULL;

COMMENT ON COLUMN chapters.ai_model_override IS 'Optional AI model override for this chapter';

-- ============================================================================
-- ALTER: ai_jobs table - add model field
-- ============================================================================
ALTER TABLE ai_jobs
ADD COLUMN IF NOT EXISTS model TEXT NULL;

COMMENT ON COLUMN ai_jobs.model IS 'AI model used for this job';

-- ============================================================================
-- Ensure only one default model per category (trigger function)
-- ============================================================================
CREATE OR REPLACE FUNCTION ensure_single_default_ai_model()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_default = TRUE THEN
        UPDATE ai_models
        SET is_default = FALSE
        WHERE category = NEW.category
        AND model_id != NEW.model_id
        AND is_default = TRUE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS ensure_single_default_ai_model ON ai_models;
CREATE TRIGGER ensure_single_default_ai_model
    BEFORE INSERT OR UPDATE OF is_default ON ai_models
    FOR EACH ROW
    WHEN (NEW.is_default = TRUE)
    EXECUTE FUNCTION ensure_single_default_ai_model();

-- ============================================================================
-- Update existing models with new fields
-- ============================================================================
UPDATE ai_models SET
    category = COALESCE(
        CASE model_type
            WHEN 'completion' THEN 'chat'
            WHEN 'chat' THEN 'chat'
            WHEN 'embedding' THEN 'embedding'
            WHEN 'vision' THEN 'chat'
            WHEN 'audio' THEN 'audio'
            WHEN 'multimodal' THEN 'chat'
            ELSE 'chat'
        END,
        'chat'
    ),
    cost_level = CASE
        WHEN model_name LIKE '%gpt-4o%' THEN 'high'
        WHEN model_name LIKE '%gpt-4%' THEN 'high'
        WHEN model_name LIKE '%gpt-3.5%' THEN 'low'
        WHEN model_name LIKE '%o1%' THEN 'very_high'
        WHEN model_name LIKE '%claude-3-5-sonnet%' THEN 'high'
        WHEN model_name LIKE '%claude-3-5-haiku%' THEN 'low'
        ELSE 'medium'
    END,
    speed = CASE
        WHEN model_name LIKE '%mini%' OR model_name LIKE '%haiku%' THEN 'very_fast'
        WHEN model_name LIKE '%turbo%' THEN 'fast'
        WHEN model_name LIKE '%o1%' THEN 'slow'
        ELSE 'medium'
    END,
    description = CASE
        WHEN model_name = 'gpt-4o' THEN 'Most capable GPT-4 model with vision'
        WHEN model_name = 'gpt-4o-mini' THEN 'Fast and affordable small model'
        WHEN model_name LIKE '%claude-3-5-sonnet%' THEN 'High capability Claude model'
        WHEN model_name LIKE '%claude-3-5-haiku%' THEN 'Fast Claude model'
        ELSE display_name
    END
WHERE category IS NULL OR category = '';

-- Set default models (one per category)
UPDATE ai_models SET is_default = TRUE WHERE model_name = 'gpt-4o';

-- ============================================================================
-- Insert additional OpenAI models if not exist
-- ============================================================================

-- Reasoning Models
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'o1',
    'OpenAI o1',
    'chat',
    'reasoning',
    'Most capable reasoning model for complex tasks',
    'very_high',
    'slow',
    200000,
    100000,
    TRUE,
    FALSE,
    TRUE,
    TRUE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'o1');

INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'o1-preview',
    'OpenAI o1 Preview',
    'chat',
    'reasoning',
    'Preview of o1 reasoning capabilities',
    'very_high',
    'slow',
    128000,
    32768,
    FALSE,
    FALSE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'o1-preview');

INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'o1-mini',
    'OpenAI o1 Mini',
    'chat',
    'reasoning',
    'Fast and affordable reasoning model',
    'high',
    'medium',
    128000,
    65536,
    FALSE,
    FALSE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'o1-mini');

-- Chat Models
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'gpt-4-turbo',
    'GPT-4 Turbo',
    'chat',
    'chat',
    'GPT-4 Turbo with vision capabilities',
    'high',
    'fast',
    128000,
    4096,
    TRUE,
    TRUE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'gpt-4-turbo');

INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'gpt-3.5-turbo',
    'GPT-3.5 Turbo',
    'chat',
    'chat',
    'Fast and cost-effective model',
    'low',
    'very_fast',
    16385,
    4096,
    FALSE,
    TRUE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'gpt-3.5-turbo');

-- Realtime Models
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'gpt-4o-realtime-preview',
    'GPT-4o Realtime',
    'multimodal',
    'realtime',
    'Real-time audio/video processing',
    'very_high',
    'very_fast',
    128000,
    4096,
    TRUE,
    TRUE,
    TRUE,
    TRUE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'gpt-4o-realtime-preview');

-- Audio Models
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'whisper-1',
    'Whisper',
    'audio',
    'audio',
    'Speech-to-text transcription',
    'low',
    'fast',
    NULL,
    NULL,
    FALSE,
    FALSE,
    TRUE,
    TRUE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'whisper-1');

INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'tts-1',
    'TTS-1',
    'audio',
    'audio',
    'Text-to-speech standard quality',
    'low',
    'fast',
    NULL,
    NULL,
    FALSE,
    FALSE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'tts-1');

INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'tts-1-hd',
    'TTS-1 HD',
    'audio',
    'audio',
    'Text-to-speech high definition',
    'medium',
    'medium',
    NULL,
    NULL,
    FALSE,
    FALSE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'tts-1-hd');

-- Image Models
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'dall-e-3',
    'DALL-E 3',
    'vision',
    'image',
    'Advanced image generation',
    'high',
    'medium',
    NULL,
    NULL,
    FALSE,
    FALSE,
    TRUE,
    TRUE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'dall-e-3');

INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'dall-e-2',
    'DALL-E 2',
    'vision',
    'image',
    'Image generation and editing',
    'medium',
    'fast',
    NULL,
    NULL,
    FALSE,
    FALSE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'dall-e-2');

-- Embedding Models
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'text-embedding-3-large',
    'Text Embedding 3 Large',
    'embedding',
    'embedding',
    'High quality text embeddings',
    'low',
    'fast',
    8191,
    NULL,
    FALSE,
    FALSE,
    TRUE,
    TRUE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'text-embedding-3-large');

INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'text-embedding-3-small',
    'Text Embedding 3 Small',
    'embedding',
    'embedding',
    'Fast and affordable embeddings',
    'free',
    'very_fast',
    8191,
    NULL,
    FALSE,
    FALSE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'text-embedding-3-small');

-- Moderation Models
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'omni-moderation-latest',
    'Omni Moderation',
    'chat',
    'moderation',
    'Content moderation with vision',
    'free',
    'very_fast',
    NULL,
    NULL,
    TRUE,
    FALSE,
    TRUE,
    TRUE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'omni-moderation-latest');

-- ============================================================================
-- Record migration
-- ============================================================================
INSERT INTO migration_history (migration_name, description, executed_at)
VALUES ('050_ai_models', 'Extend AI Models for OpenAI model selection (Phase C3.0)', NOW())
ON CONFLICT DO NOTHING;

-- ============================================================================
-- End of Migration: 050_ai_models.sql
-- ============================================================================
