-- ============================================================================
-- Migration: 020_ai_usage_logs.sql
-- Description: AI usage logging and cost tracking
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: ki_requests (legacy name from docs)
-- Description: AI request tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS ki_requests (
    ki_request_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    organization_id UUID REFERENCES organizations(organization_id) ON DELETE SET NULL,
    request_type VARCHAR(100) NOT NULL,
    model_id INTEGER REFERENCES ai_models(model_id) ON DELETE SET NULL,
    model_used VARCHAR(100),
    prompt_id UUID REFERENCES ai_prompts(prompt_id) ON DELETE SET NULL,
    input_reference TEXT,
    output_reference TEXT,
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    tokens_total INTEGER GENERATED ALWAYS AS (tokens_input + tokens_output) STORED,
    cost_usd DECIMAL(10,6),
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    CONSTRAINT chk_ki_status CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled'))
);

CREATE INDEX IF NOT EXISTS idx_ki_requests_user ON ki_requests(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ki_requests_org ON ki_requests(organization_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ki_requests_type ON ki_requests(request_type);
CREATE INDEX IF NOT EXISTS idx_ki_requests_status ON ki_requests(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ki_requests_model ON ki_requests(model_id);
CREATE INDEX IF NOT EXISTS idx_ki_requests_created ON ki_requests(created_at DESC);

COMMENT ON TABLE ki_requests IS 'AI request tracking for usage analytics and billing';

-- ============================================================================
-- TABLE: ki_raw_inputs
-- Description: Raw uploaded files for AI processing
-- ============================================================================
CREATE TABLE IF NOT EXISTS ki_raw_inputs (
    input_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    uploaded_by_user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    file_path VARCHAR(500) NOT NULL,
    original_filename VARCHAR(255),
    file_type VARCHAR(50),
    file_size_bytes BIGINT,
    parsed_json JSONB,
    processing_status VARCHAR(20) DEFAULT 'uploaded',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_input_status CHECK (processing_status IN ('uploaded', 'processing', 'completed', 'failed'))
);

CREATE INDEX IF NOT EXISTS idx_ki_inputs_user ON ki_raw_inputs(uploaded_by_user_id);
CREATE INDEX IF NOT EXISTS idx_ki_inputs_status ON ki_raw_inputs(processing_status);
CREATE INDEX IF NOT EXISTS idx_ki_inputs_created ON ki_raw_inputs(created_at DESC);

COMMENT ON TABLE ki_raw_inputs IS 'Raw file uploads for AI processing (PDF, DOCX, PPTX)';

-- ============================================================================
-- TABLE: ai_usage_aggregates
-- Description: Aggregated AI usage stats for fast queries
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_usage_aggregates (
    aggregate_id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(organization_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    request_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    total_cost_usd DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, date),
    UNIQUE (organization_id, date)
);

CREATE INDEX IF NOT EXISTS idx_ai_usage_agg_user ON ai_usage_aggregates(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_ai_usage_agg_org ON ai_usage_aggregates(organization_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_ai_usage_agg_date ON ai_usage_aggregates(date DESC);

COMMENT ON TABLE ai_usage_aggregates IS 'Daily aggregated AI usage for billing and analytics';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_ai_usage_agg_updated_at BEFORE UPDATE ON ai_usage_aggregates
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 020_ai_usage_logs.sql
-- ============================================================================
