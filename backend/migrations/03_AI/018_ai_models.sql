-- ============================================================================
-- Migration: 018_ai_models.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_pipeline.ai_models (
    model_id SERIAL PRIMARY KEY,
    provider_id INTEGER REFERENCES ai_pipeline.ai_providers(provider_id) ON DELETE CASCADE,
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

CREATE INDEX IF NOT EXISTS idx_ai_models_provider ON ai_pipeline.ai_models(provider_id);
CREATE INDEX IF NOT EXISTS idx_ai_models_name ON ai_pipeline.ai_models(model_name);
CREATE INDEX IF NOT EXISTS idx_ai_models_type ON ai_pipeline.ai_models(model_type);
CREATE INDEX IF NOT EXISTS idx_ai_models_active ON ai_pipeline.ai_models(active) WHERE active = TRUE;

COMMENT ON TABLE ai_pipeline.ai_models IS 'AI model definitions with pricing and capabilities';
COMMENT ON COLUMN ai_pipeline.ai_models.capabilities IS 'Array of capabilities: code, analysis, creative, etc.';

-- ============================================================================
-- NOTE: Keine Seed-Daten - Models werden via API synchronisiert
-- ============================================================================

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
DROP TRIGGER IF EXISTS update_ai_models_updated_at ON ai_pipeline.ai_models;
CREATE TRIGGER update_ai_models_updated_at BEFORE UPDATE ON ai_pipeline.ai_models
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 018_ai_models.sql
-- ============================================================================
