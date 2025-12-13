-- ============================================================================
-- Migration: 018_ai_models.sql
-- Description: AI models configuration
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: ai_models
-- Description: AI model definitions with costs and capabilities
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_models (
    model_id SERIAL PRIMARY KEY,
    provider_id INTEGER REFERENCES ai_providers(provider_id) ON DELETE CASCADE,
    model_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    max_tokens INTEGER,
    context_window INTEGER,
    cost_per_1k_input DECIMAL(10,6),
    cost_per_1k_output DECIMAL(10,6),
    capabilities TEXT[],
    supports_streaming BOOLEAN DEFAULT FALSE,
    supports_functions BOOLEAN DEFAULT FALSE,
    supports_vision BOOLEAN DEFAULT FALSE,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_model_type CHECK (model_type IN ('completion', 'chat', 'embedding', 'vision', 'audio', 'multimodal')),
    UNIQUE (provider_id, model_name)
);

CREATE INDEX IF NOT EXISTS idx_ai_models_provider ON ai_models(provider_id);
CREATE INDEX IF NOT EXISTS idx_ai_models_name ON ai_models(model_name);
CREATE INDEX IF NOT EXISTS idx_ai_models_type ON ai_models(model_type);
CREATE INDEX IF NOT EXISTS idx_ai_models_active ON ai_models(active) WHERE active = TRUE;

COMMENT ON TABLE ai_models IS 'AI model definitions with pricing and capabilities';
COMMENT ON COLUMN ai_models.capabilities IS 'Array of capabilities: code, analysis, creative, etc.';

-- ============================================================================
-- Seed AI Models
-- ============================================================================
INSERT INTO ai_models (provider_id, model_name, display_name, model_type, max_tokens, context_window, cost_per_1k_input, cost_per_1k_output, capabilities, supports_streaming, supports_functions) VALUES
    ((SELECT provider_id FROM ai_providers WHERE name = 'openai'), 'gpt-4o', 'GPT-4o', 'chat', 4096, 128000, 0.005, 0.015, ARRAY['code', 'analysis', 'creative'], true, true),
    ((SELECT provider_id FROM ai_providers WHERE name = 'openai'), 'gpt-4o-mini', 'GPT-4o Mini', 'chat', 4096, 128000, 0.00015, 0.0006, ARRAY['code', 'analysis'], true, true),
    ((SELECT provider_id FROM ai_providers WHERE name = 'anthropic'), 'claude-3-5-sonnet-20241022', 'Claude 3.5 Sonnet', 'chat', 8192, 200000, 0.003, 0.015, ARRAY['code', 'analysis', 'creative'], true, true),
    ((SELECT provider_id FROM ai_providers WHERE name = 'anthropic'), 'claude-3-5-haiku-20241022', 'Claude 3.5 Haiku', 'chat', 8192, 200000, 0.001, 0.005, ARRAY['code', 'analysis'], true, true)
ON CONFLICT (provider_id, model_name) DO NOTHING;

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_ai_models_updated_at BEFORE UPDATE ON ai_models
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 018_ai_models.sql
-- ============================================================================
