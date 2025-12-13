-- ============================================================================
-- Migration: 017_ai_providers.sql
-- Description: AI providers configuration
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: ai_providers
-- Description: AI service providers (OpenAI, Anthropic, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_providers (
    provider_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    provider_type VARCHAR(50) NOT NULL,
    base_url VARCHAR(500),
    api_version VARCHAR(20),
    encrypted_api_key TEXT,
    encryption_salt VARCHAR(255),
    active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    rate_limit_per_minute INTEGER,
    config JSONB,
    last_validated TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_provider_type CHECK (provider_type IN ('openai', 'anthropic', 'google', 'cohere', 'huggingface', 'ollama', 'custom'))
);

CREATE INDEX IF NOT EXISTS idx_ai_providers_name ON ai_providers(name);
CREATE INDEX IF NOT EXISTS idx_ai_providers_active ON ai_providers(active, priority DESC);
CREATE INDEX IF NOT EXISTS idx_ai_providers_type ON ai_providers(provider_type);

COMMENT ON TABLE ai_providers IS 'AI service providers with encrypted API keys';
COMMENT ON COLUMN ai_providers.priority IS 'Higher priority providers are used first (0 = lowest)';

-- ============================================================================
-- TABLE: ai_provider_health
-- Description: Provider health monitoring
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_provider_health (
    health_id BIGSERIAL PRIMARY KEY,
    provider_id INTEGER REFERENCES ai_providers(provider_id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL,
    response_time_ms INTEGER,
    error_message TEXT,
    checked_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_provider_health CHECK (status IN ('healthy', 'degraded', 'down', 'unknown'))
);

CREATE INDEX IF NOT EXISTS idx_ai_provider_health_provider ON ai_provider_health(provider_id, checked_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_provider_health_status ON ai_provider_health(status, checked_at DESC);

COMMENT ON TABLE ai_provider_health IS 'AI provider health check history';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_ai_providers_updated_at BEFORE UPDATE ON ai_providers
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Seed AI Providers
-- ============================================================================
INSERT INTO ai_providers (name, display_name, provider_type, active, priority) VALUES
    ('openai', 'OpenAI', 'openai', false, 100),
    ('anthropic', 'Anthropic Claude', 'anthropic', false, 90),
    ('google', 'Google Gemini', 'google', false, 80)
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- End of Migration: 017_ai_providers.sql
-- ============================================================================
