-- ============================================================================
-- Migration: 004_organisation_settings.sql
-- Description: Organization settings, branding, and feature flags
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2025-01-17
-- ============================================================================

-- ============================================================================
-- TABLE: organization_settings
-- Description: Organization-specific configuration and preferences
-- ============================================================================
CREATE TABLE IF NOT EXISTS organisations.organization_settings (
    setting_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organisations.organisations(organization_id) ON DELETE CASCADE,
    key VARCHAR(100) NOT NULL,
    value TEXT,
    value_type VARCHAR(20) DEFAULT 'string',
    encrypted BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_org_setting_type CHECK (value_type IN ('string', 'number', 'boolean', 'json')),
    UNIQUE (organization_id, key)
);

CREATE INDEX IF NOT EXISTS idx_org_settings_org ON organisations.organization_settings (organization_id);
CREATE INDEX IF NOT EXISTS idx_org_settings_key ON organisations.organization_settings (key);

COMMENT ON TABLE organisations.organization_settings IS 'Organization-specific settings and preferences';

-- ============================================================================
-- TABLE: organization_branding
-- Description: Branding and white-label configuration
-- ============================================================================
CREATE TABLE IF NOT EXISTS organisations.organization_branding (
    branding_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organisations.organisations(organization_id) ON DELETE CASCADE UNIQUE,
    primary_color VARCHAR(7) DEFAULT '#1a73e8',
    secondary_color VARCHAR(7) DEFAULT '#34a853',
    accent_color VARCHAR(7),
    logo_url VARCHAR(500),
    logo_small_url VARCHAR(500),
    favicon_url VARCHAR(500),
    custom_css TEXT,
    custom_domain VARCHAR(255),
    email_from_name VARCHAR(100),
    email_from_address VARCHAR(255),
    email_footer_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_org_branding_org ON organisations.organization_branding (organization_id);
CREATE INDEX IF NOT EXISTS idx_org_branding_domain ON organisations.organization_branding (custom_domain);

COMMENT ON TABLE organisations.organization_branding IS 'White-label branding configuration for organizations';

-- ============================================================================
-- TABLE: organization_features
-- Description: Feature flags for organizations
-- ============================================================================
CREATE TABLE IF NOT EXISTS organisations.organization_features (
    feature_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organisations.organisations(organization_id) ON DELETE CASCADE,
    feature_key VARCHAR(100) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    config JSONB,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (organization_id, feature_key)
);

CREATE INDEX IF NOT EXISTS idx_org_features_org ON organisations.organization_features (organization_id);
CREATE INDEX IF NOT EXISTS idx_org_features_key ON organisations.organization_features (feature_key);
CREATE INDEX IF NOT EXISTS idx_org_features_enabled ON organisations.organization_features (enabled) WHERE enabled = TRUE;

COMMENT ON TABLE organisations.organization_features IS 'Feature toggles for organizations (e.g., ai_enabled, liverooms, analytics)';

-- ============================================================================
-- TABLE: organization_quotas
-- Description: Resource quotas and limits for organizations
-- ============================================================================
CREATE TABLE IF NOT EXISTS organisations.organization_quotas (
    quota_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organisations.organisations(organization_id) ON DELETE CASCADE,
    resource_type VARCHAR(50) NOT NULL,
    quota_limit INTEGER NOT NULL,
    current_usage INTEGER DEFAULT 0,
    reset_period VARCHAR(20),
    last_reset_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_org_quota_resource CHECK (resource_type IN ('users', 'courses', 'storage_mb', 'ai_requests', 'liverooms', 'recordings')),
    CONSTRAINT chk_org_quota_reset CHECK (reset_period IN ('daily', 'weekly', 'monthly', 'yearly', 'never')),
    UNIQUE (organization_id, resource_type)
);

CREATE INDEX IF NOT EXISTS idx_org_quotas_org ON organisations.organization_quotas (organization_id);
CREATE INDEX IF NOT EXISTS idx_org_quotas_resource ON organisations.organization_quotas (resource_type);

COMMENT ON TABLE organisations.organization_quotas IS 'Resource quotas and usage tracking for organizations';

-- ============================================================================
-- Trigger: Update updated_at timestamp
-- ============================================================================
CREATE TRIGGER update_org_settings_updated_at BEFORE UPDATE ON organisations.organization_settings
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_org_branding_updated_at BEFORE UPDATE ON organisations.organization_branding
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_org_features_updated_at BEFORE UPDATE ON organisations.organization_features
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_org_quotas_updated_at BEFORE UPDATE ON organisations.organization_quotas
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Migration: 004_organisation_settings.sql
-- ============================================================================
