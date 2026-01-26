-- ============================================================================
-- Migration: 005_api_gateway.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

CREATE TABLE IF NOT EXISTS core.api_clients (
    client_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    organization_id UUID REFERENCES organisations.organisations(organization_id) ON DELETE CASCADE,
    user_id UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    client_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_api_client_type CHECK (client_type IN ('oauth', 'service', 'webhook', 'integration')),
    CONSTRAINT chk_api_client_status CHECK (status IN ('active', 'disabled', 'revoked'))
);

CREATE INDEX IF NOT EXISTS idx_api_clients_org ON core.api_clients(organization_id);
CREATE INDEX IF NOT EXISTS idx_api_clients_user ON core.api_clients(user_id);
CREATE INDEX IF NOT EXISTS idx_api_clients_status ON core.api_clients(status) WHERE status = 'active';

COMMENT ON TABLE core.api_clients IS 'API clients for third-party integrations and webhooks';

-- ============================================================================
-- TABLE: api_keys
-- Description: API keys for authentication
-- ============================================================================
CREATE TABLE IF NOT EXISTS core.api_keys (
    key_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES core.api_clients(client_id) ON DELETE CASCADE,
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

CREATE INDEX IF NOT EXISTS idx_api_keys_client ON core.api_keys(client_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_prefix ON core.api_keys(key_prefix);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON core.api_keys(revoked, expires_at);
CREATE INDEX IF NOT EXISTS idx_api_keys_expires ON core.api_keys(expires_at) WHERE revoked = FALSE;

COMMENT ON TABLE core.api_keys IS 'API keys with scopes and rate limiting';

-- ============================================================================
-- TABLE: api_routes
-- Description: API route definitions and versioning
-- ============================================================================
CREATE TABLE IF NOT EXISTS core.api_routes (
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

CREATE INDEX IF NOT EXISTS idx_api_routes_path ON core.api_routes(path, method);
CREATE INDEX IF NOT EXISTS idx_api_routes_version ON core.api_routes(version);
CREATE INDEX IF NOT EXISTS idx_api_routes_deprecated ON core.api_routes(deprecated) WHERE deprecated = TRUE;

COMMENT ON TABLE core.api_routes IS 'API route registry with versioning and deprecation tracking';

-- ============================================================================
-- TABLE: api_request_logs
-- Description: API request logging for analytics
-- ============================================================================
CREATE TABLE IF NOT EXISTS core.api_request_logs (
    log_id BIGSERIAL PRIMARY KEY,
    client_id UUID REFERENCES core.api_clients(client_id) ON DELETE SET NULL,
    user_id UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
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

CREATE INDEX IF NOT EXISTS idx_api_logs_client ON core.api_request_logs(client_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_logs_user ON core.api_request_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_logs_path ON core.api_request_logs(path, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_logs_status ON core.api_request_logs(status_code, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_logs_time ON core.api_request_logs(created_at DESC);

COMMENT ON TABLE core.api_request_logs IS 'API request logs for analytics and debugging';

-- ============================================================================
-- TABLE: api_webhooks
-- Description: Webhook subscriptions
-- ============================================================================
CREATE TABLE IF NOT EXISTS core.api_webhooks (
    webhook_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES core.api_clients(client_id) ON DELETE CASCADE,
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

CREATE INDEX IF NOT EXISTS idx_api_webhooks_client ON core.api_webhooks(client_id);
CREATE INDEX IF NOT EXISTS idx_api_webhooks_event ON core.api_webhooks(event_type) WHERE active = TRUE;
CREATE INDEX IF NOT EXISTS idx_api_webhooks_active ON core.api_webhooks(active);

COMMENT ON TABLE core.api_webhooks IS 'Webhook subscriptions for event notifications';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
DROP TRIGGER IF EXISTS update_api_clients_updated_at ON core.api_clients;
CREATE TRIGGER update_api_clients_updated_at BEFORE UPDATE ON core.api_clients
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_api_webhooks_updated_at ON core.api_webhooks;
CREATE TRIGGER update_api_webhooks_updated_at BEFORE UPDATE ON core.api_webhooks
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 005_api_gateway.sql
-- ============================================================================
