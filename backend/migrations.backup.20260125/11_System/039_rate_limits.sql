-- ============================================================================
-- Migration: 039_rate_limits.sql
-- Version: 1.0.0
-- Description: Database migration
-- Author: LernsystemX Migration System
-- Date: 2026-01-02
-- ============================================================================

CREATE TABLE IF NOT EXISTS core.rate_limits (
    limit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    limit_key VARCHAR(100) UNIQUE NOT NULL,
    limit_type VARCHAR(50) NOT NULL,
    scope VARCHAR(50) NOT NULL,
    max_requests INTEGER NOT NULL,
    window_seconds INTEGER NOT NULL,
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organisations.organisations(organization_id) ON DELETE CASCADE,
    ip_address INET,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_rate_limit_type CHECK (limit_type IN ('api', 'ai', 'upload', 'download', 'login', 'email', 'custom')),
    CONSTRAINT chk_rate_limit_scope CHECK (scope IN ('global', 'user', 'organization', 'ip', 'endpoint'))
);

CREATE INDEX IF NOT EXISTS idx_rate_limits_key ON core.rate_limits(limit_key);
CREATE INDEX IF NOT EXISTS idx_rate_limits_type ON core.rate_limits(limit_type);
CREATE INDEX IF NOT EXISTS idx_rate_limits_scope ON core.rate_limits(scope);
CREATE INDEX IF NOT EXISTS idx_rate_limits_user ON core.rate_limits(user_id);
CREATE INDEX IF NOT EXISTS idx_rate_limits_org ON core.rate_limits(organization_id);
CREATE INDEX IF NOT EXISTS idx_rate_limits_ip ON core.rate_limits(ip_address);

COMMENT ON TABLE core.rate_limits IS 'Rate limit configurations for API, AI, uploads, etc.';

-- ============================================================================
-- TABLE: rate_limit_hits
-- Description: Rate limit hit tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS core.rate_limit_hits (
    hit_id BIGSERIAL PRIMARY KEY,
    limit_key VARCHAR(100) NOT NULL,
    user_id UUID REFERENCES core.users(user_id) ON DELETE SET NULL,
    organization_id UUID REFERENCES organisations.organisations(organization_id) ON DELETE SET NULL,
    ip_address INET,
    endpoint VARCHAR(500),
    hit_at TIMESTAMPTZ DEFAULT NOW(),
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_rate_limit_hits_key ON core.rate_limit_hits(limit_key, window_start, window_end);
CREATE INDEX IF NOT EXISTS idx_rate_limit_hits_user ON core.rate_limit_hits(user_id, hit_at DESC);
CREATE INDEX IF NOT EXISTS idx_rate_limit_hits_org ON core.rate_limit_hits(organization_id, hit_at DESC);
CREATE INDEX IF NOT EXISTS idx_rate_limit_hits_ip ON core.rate_limit_hits(ip_address, hit_at DESC);
CREATE INDEX IF NOT EXISTS idx_rate_limit_hits_window ON core.rate_limit_hits(window_start, window_end);

COMMENT ON TABLE core.rate_limit_hits IS 'Rate limit hit tracking for enforcement';

-- ============================================================================
-- TABLE: quota_usage
-- Description: Resource quota usage tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS billing_storage.quota_usage (
    usage_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES core.users(user_id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organisations.organisations(organization_id) ON DELETE CASCADE,
    resource_type VARCHAR(50) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    quota_limit INTEGER NOT NULL,
    current_usage INTEGER DEFAULT 0,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_quota_resource CHECK (resource_type IN ('api_calls', 'ai_tokens', 'storage_mb', 'users', 'courses', 'liverooms', 'recordings')),
    CONSTRAINT chk_quota_target CHECK (
        (user_id IS NOT NULL AND organization_id IS NULL) OR
        (user_id IS NULL AND organization_id IS NOT NULL)
    ),
    UNIQUE (user_id, resource_type, period_start),
    UNIQUE (organization_id, resource_type, period_start)
);

CREATE INDEX IF NOT EXISTS idx_quota_usage_user ON billing_storage.quota_usage(user_id, resource_type);
CREATE INDEX IF NOT EXISTS idx_quota_usage_org ON billing_storage.quota_usage(organization_id, resource_type);
CREATE INDEX IF NOT EXISTS idx_quota_usage_period ON billing_storage.quota_usage(period_start, period_end);

COMMENT ON TABLE billing_storage.quota_usage IS 'Resource quota usage tracking per user/organization';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
DROP TRIGGER IF EXISTS update_rate_limits_updated_at ON core.rate_limits;
CREATE TRIGGER update_rate_limits_updated_at BEFORE UPDATE ON core.rate_limits
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 039_rate_limits.sql
-- ============================================================================
