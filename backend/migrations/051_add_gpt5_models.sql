-- ============================================================================
-- Migration: 051_add_gpt5_models.sql
-- Description: Add GPT-5 series and latest OpenAI models (Phase C3.1)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-11-26
-- ============================================================================

-- ============================================================================
-- Insert GPT-5 Series Models
-- ============================================================================

-- GPT-5.1
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'gpt-5.1',
    'GPT-5.1',
    'chat',
    'chat',
    'Latest flagship GPT-5.1 model',
    'very_high',
    'fast',
    256000,
    64000,
    TRUE,
    TRUE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'gpt-5.1');

-- GPT-5
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'gpt-5',
    'GPT-5',
    'chat',
    'chat',
    'GPT-5 flagship model',
    'very_high',
    'fast',
    256000,
    64000,
    TRUE,
    TRUE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'gpt-5');

-- GPT-5-mini
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'gpt-5-mini',
    'GPT-5 Mini',
    'chat',
    'chat',
    'Smaller, faster GPT-5 variant',
    'medium',
    'very_fast',
    128000,
    32768,
    TRUE,
    TRUE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'gpt-5-mini');

-- GPT-5-nano
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'gpt-5-nano',
    'GPT-5 Nano',
    'chat',
    'chat',
    'Ultra-fast GPT-5 for simple tasks',
    'low',
    'very_fast',
    64000,
    16384,
    FALSE,
    TRUE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'gpt-5-nano');

-- GPT-5-pro
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'gpt-5-pro',
    'GPT-5 Pro',
    'chat',
    'chat',
    'Professional GPT-5 with extended context',
    'very_high',
    'medium',
    512000,
    128000,
    TRUE,
    TRUE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'gpt-5-pro');

-- ============================================================================
-- Insert GPT-5 Codex Series
-- ============================================================================

-- GPT-5.1 Codex
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'gpt-5.1-codex',
    'GPT-5.1 Codex',
    'chat',
    'coding',
    'Specialized code generation model',
    'very_high',
    'fast',
    256000,
    64000,
    FALSE,
    TRUE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'gpt-5.1-codex');

-- GPT-5 Codex
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'gpt-5-codex',
    'GPT-5 Codex',
    'chat',
    'coding',
    'GPT-5 optimized for code',
    'very_high',
    'fast',
    256000,
    64000,
    FALSE,
    TRUE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'gpt-5-codex');

-- GPT-5.1 Codex Mini
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'gpt-5.1-codex-mini',
    'GPT-5.1 Codex Mini',
    'chat',
    'coding',
    'Fast code generation model',
    'medium',
    'very_fast',
    128000,
    32768,
    FALSE,
    TRUE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'gpt-5.1-codex-mini');

-- ============================================================================
-- Insert O-Series Deep Research Models
-- ============================================================================

-- o3-deep-research
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'o3-deep-research',
    'o3 Deep Research',
    'chat',
    'reasoning',
    'Deep research and analysis model',
    'very_high',
    'slow',
    200000,
    100000,
    TRUE,
    FALSE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'o3-deep-research');

-- o4-mini-deep-research
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'o4-mini-deep-research',
    'o4 Mini Deep Research',
    'chat',
    'reasoning',
    'Fast deep research model',
    'high',
    'medium',
    200000,
    100000,
    TRUE,
    FALSE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'o4-mini-deep-research');

-- o4-mini
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'o4-mini',
    'o4 Mini',
    'chat',
    'reasoning',
    'Fast reasoning model',
    'medium',
    'fast',
    200000,
    100000,
    TRUE,
    FALSE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'o4-mini');

-- o3
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'o3',
    'o3',
    'chat',
    'reasoning',
    'Advanced reasoning model',
    'very_high',
    'slow',
    200000,
    100000,
    TRUE,
    FALSE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'o3');

-- o3-pro
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'o3-pro',
    'o3 Pro',
    'chat',
    'reasoning',
    'Professional reasoning model',
    'very_high',
    'slow',
    200000,
    100000,
    TRUE,
    FALSE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'o3-pro');

-- o3-mini
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'o3-mini',
    'o3 Mini',
    'chat',
    'reasoning',
    'Compact reasoning model',
    'medium',
    'fast',
    200000,
    65536,
    FALSE,
    FALSE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'o3-mini');

-- ============================================================================
-- Insert Search Preview Models
-- ============================================================================

-- gpt-4o-search-preview
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'gpt-4o-search-preview',
    'GPT-4o Search',
    'chat',
    'search',
    'GPT-4o with web search capabilities',
    'high',
    'medium',
    128000,
    16384,
    TRUE,
    TRUE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'gpt-4o-search-preview');

-- gpt-4o-mini-search-preview
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'gpt-4o-mini-search-preview',
    'GPT-4o Mini Search',
    'chat',
    'search',
    'GPT-4o Mini with web search',
    'medium',
    'fast',
    128000,
    16384,
    TRUE,
    TRUE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'gpt-4o-mini-search-preview');

-- ============================================================================
-- Insert Computer Use Model
-- ============================================================================

-- computer-use-preview
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'computer-use-preview',
    'Computer Use',
    'chat',
    'agent',
    'Agentic computer automation model',
    'high',
    'medium',
    128000,
    16384,
    TRUE,
    TRUE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'computer-use-preview');

-- ============================================================================
-- Insert Video Models (Sora)
-- ============================================================================

-- sora-2
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'sora-2',
    'Sora 2',
    'vision',
    'video',
    'AI video generation model',
    'very_high',
    'slow',
    NULL,
    NULL,
    FALSE,
    FALSE,
    TRUE,
    TRUE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'sora-2');

-- sora-2-pro
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'sora-2-pro',
    'Sora 2 Pro',
    'vision',
    'video',
    'Professional AI video generation',
    'very_high',
    'slow',
    NULL,
    NULL,
    FALSE,
    FALSE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'sora-2-pro');

-- ============================================================================
-- Insert Audio Models
-- ============================================================================

-- gpt-audio
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'gpt-audio',
    'GPT Audio',
    'audio',
    'audio',
    'Audio processing and generation',
    'high',
    'medium',
    128000,
    16384,
    FALSE,
    FALSE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'gpt-audio');

-- gpt-audio-mini
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'gpt-audio-mini',
    'GPT Audio Mini',
    'audio',
    'audio',
    'Fast audio processing',
    'medium',
    'fast',
    128000,
    16384,
    FALSE,
    FALSE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'gpt-audio-mini');

-- gpt-realtime
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'gpt-realtime',
    'GPT Realtime',
    'multimodal',
    'realtime',
    'Real-time conversational AI',
    'very_high',
    'very_fast',
    128000,
    4096,
    TRUE,
    TRUE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'gpt-realtime');

-- gpt-realtime-mini
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'gpt-realtime-mini',
    'GPT Realtime Mini',
    'multimodal',
    'realtime',
    'Fast real-time AI',
    'medium',
    'very_fast',
    128000,
    4096,
    TRUE,
    TRUE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'gpt-realtime-mini');

-- gpt-4o-transcribe-diarize
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'gpt-4o-transcribe-diarize',
    'GPT-4o Transcribe Diarize',
    'audio',
    'audio',
    'Transcription with speaker identification',
    'high',
    'medium',
    128000,
    16384,
    FALSE,
    FALSE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'gpt-4o-transcribe-diarize');

-- ============================================================================
-- Insert Open-Source Models (GPT-OSS)
-- ============================================================================

-- gpt-oss-120b
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'gpt-oss-120b',
    'GPT OSS 120B',
    'chat',
    'open-source',
    'Open-weight 120B parameter model',
    'high',
    'slow',
    128000,
    32768,
    FALSE,
    TRUE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'gpt-oss-120b');

-- gpt-oss-20b
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, category, description, cost_level, speed, context_window, max_output_tokens, supports_vision, supports_functions, active, is_default)
SELECT
    (SELECT provider_id FROM ai_providers WHERE name = 'openai' LIMIT 1),
    'gpt-oss-20b',
    'GPT OSS 20B',
    'chat',
    'open-source',
    'Open-weight 20B parameter model',
    'low',
    'fast',
    128000,
    32768,
    FALSE,
    TRUE,
    TRUE,
    FALSE
WHERE NOT EXISTS (SELECT 1 FROM ai_models WHERE model_name = 'gpt-oss-20b');

-- ============================================================================
-- Add new categories
-- ============================================================================

-- Add coding, search, agent, video, open-source categories
UPDATE ai_models SET category = 'coding' WHERE model_name LIKE '%codex%' AND category = 'chat';
UPDATE ai_models SET category = 'search' WHERE model_name LIKE '%search%' AND category = 'chat';
UPDATE ai_models SET category = 'agent' WHERE model_name = 'computer-use-preview' AND category = 'chat';
UPDATE ai_models SET category = 'video' WHERE model_name LIKE 'sora%' AND category IS NULL;
UPDATE ai_models SET category = 'open-source' WHERE model_name LIKE 'gpt-oss%' AND category = 'chat';

-- ============================================================================
-- Record migration
-- ============================================================================
INSERT INTO migration_history (migration_name, description, executed_at)
VALUES ('051_add_gpt5_models', 'Add GPT-5 series and latest OpenAI models (Phase C3.1)', NOW())
ON CONFLICT DO NOTHING;

-- ============================================================================
-- End of Migration: 051_add_gpt5_models.sql
-- ============================================================================
