-- ============================================================================
-- Migration: 005_api_gateway.sql
-- Description: API Gateway tables (keys, clients, routing, versioning)
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: api_clients
-- Description: API clients for third-party integrations
-- ============================================================================
CREATE TABLE IF NOT EXISTS api_clients (
    client_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    organization_id UUID REFERENCES organizations(organization_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    client_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_api_client_type CHECK (client_type IN ('oauth', 'service', 'webhook', 'integration')),
    CONSTRAINT chk_api_client_status CHECK (status IN ('active', 'disabled', 'revoked'))
);

CREATE INDEX IF NOT EXISTS idx_api_clients_org ON api_clients(organization_id);
CREATE INDEX IF NOT EXISTS idx_api_clients_user ON api_clients(user_id);
CREATE INDEX IF NOT EXISTS idx_api_clients_status ON api_clients(status) WHERE status = 'active';

COMMENT ON TABLE api_clients IS 'API clients for third-party integrations and webhooks';

-- ============================================================================
-- TABLE: api_keys
-- Description: API keys for authentication
-- ============================================================================
CREATE TABLE IF NOT EXISTS api_keys (
    key_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES api_clients(client_id) ON DELETE CASCADE,
    key_hash VARCHAR(255) NOT NULL,
    key_prefix VARCHAR(20) NOT NULL,
    name VARCHAR(255),
    scopes TEXT[],
    rate_limit INTEGER DEFAULT 1000,
    rate_limit_window VARCHAR(20) DEFAULT 'hour',
    last_used_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_api_key_window CHECK (rate_limit_window IN ('minute', 'hour', 'day'))
);

CREATE INDEX IF NOT EXISTS idx_api_keys_client ON api_keys(client_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_prefix ON api_keys(key_prefix);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(revoked, expires_at);
CREATE INDEX IF NOT EXISTS idx_api_keys_expires ON api_keys(expires_at) WHERE revoked = FALSE;

COMMENT ON TABLE api_keys IS 'API keys with scopes and rate limiting';

-- ============================================================================
-- TABLE: api_routes
-- Description: API route definitions and versioning
-- ============================================================================
CREATE TABLE IF NOT EXISTS api_routes (
    route_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    path VARCHAR(500) NOT NULL,
    method VARCHAR(10) NOT NULL,
    version VARCHAR(20) NOT NULL,
    handler VARCHAR(255) NOT NULL,
    deprecated BOOLEAN DEFAULT FALSE,
    deprecated_at TIMESTAMPTZ,
    sunset_date DATE,
    replacement_route VARCHAR(500),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_api_method CHECK (method IN ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS')),
    UNIQUE (path, method, version)
);

CREATE INDEX IF NOT EXISTS idx_api_routes_path ON api_routes(path, method);
CREATE INDEX IF NOT EXISTS idx_api_routes_version ON api_routes(version);
CREATE INDEX IF NOT EXISTS idx_api_routes_deprecated ON api_routes(deprecated) WHERE deprecated = TRUE;

COMMENT ON TABLE api_routes IS 'API route registry with versioning and deprecation tracking';

-- ============================================================================
-- TABLE: api_request_logs
-- Description: API request logging for analytics
-- ============================================================================
CREATE TABLE IF NOT EXISTS api_request_logs (
    log_id BIGSERIAL PRIMARY KEY,
    client_id UUID REFERENCES api_clients(client_id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    method VARCHAR(10) NOT NULL,
    path VARCHAR(500) NOT NULL,
    query_params JSONB,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER,
    ip_address INET,
    user_agent TEXT,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_api_logs_client ON api_request_logs(client_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_logs_user ON api_request_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_logs_path ON api_request_logs(path, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_logs_status ON api_request_logs(status_code, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_logs_time ON api_request_logs(created_at DESC);

COMMENT ON TABLE api_request_logs IS 'API request logs for analytics and debugging';

-- ============================================================================
-- TABLE: api_webhooks
-- Description: Webhook subscriptions
-- ============================================================================
CREATE TABLE IF NOT EXISTS api_webhooks (
    webhook_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES api_clients(client_id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    target_url VARCHAR(500) NOT NULL,
    secret_key VARCHAR(255),
    headers JSONB,
    retry_count INTEGER DEFAULT 3,
    timeout_seconds INTEGER DEFAULT 30,
    active BOOLEAN DEFAULT TRUE,
    last_triggered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_api_webhooks_client ON api_webhooks(client_id);
CREATE INDEX IF NOT EXISTS idx_api_webhooks_event ON api_webhooks(event_type) WHERE active = TRUE;
CREATE INDEX IF NOT EXISTS idx_api_webhooks_active ON api_webhooks(active);

COMMENT ON TABLE api_webhooks IS 'Webhook subscriptions for event notifications';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_api_clients_updated_at BEFORE UPDATE ON api_clients
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_api_webhooks_updated_at BEFORE UPDATE ON api_webhooks
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 005_api_gateway.sql
-- ============================================================================
