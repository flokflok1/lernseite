-- ============================================================================
-- Migration: 041_feature_based_authorization.sql
-- Version: 1.0.0
-- Description: Feature-Based Authorization - Role/Feature/Permission Mapping
-- Author: LernsystemX Migration System
-- Date: 2026-01-14
-- Dependencies: 001_core_users_roles.sql, 074_system_features.sql
-- ============================================================================

-- ============================================================================
-- TABLE: core.role_features
-- Description: Role-to-Feature mapping (which features each role can access)
-- ============================================================================
CREATE TABLE IF NOT EXISTS core.role_features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_id UUID NOT NULL REFERENCES core.groups(id) ON DELETE CASCADE,
    feature_code VARCHAR(50) NOT NULL REFERENCES support_systems.system_features(feature_code) ON DELETE CASCADE,
    access_level VARCHAR(20) DEFAULT 'view',  -- view, edit, manage, execute
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (group_id, feature_code)
);

CREATE INDEX IF NOT EXISTS idx_role_features_role ON core.role_features(group_id);
CREATE INDEX IF NOT EXISTS idx_role_features_feature ON core.role_features(feature_code);
CREATE INDEX IF NOT EXISTS idx_role_features_enabled ON core.role_features(enabled) WHERE enabled = TRUE;

COMMENT ON TABLE core.role_features IS 'Maps roles to available features with granular access levels';
COMMENT ON COLUMN core.role_features.access_level IS 'Granular access: view=read-only, edit=modify, manage=full control, execute=can trigger actions';

-- ============================================================================
-- TABLE: organisations.feature_subscriptions
-- Description: Organization-to-Feature subscriptions (SaaS tier management)
-- ============================================================================
CREATE TABLE IF NOT EXISTS organisations.feature_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organisation_id UUID NOT NULL REFERENCES organisations.organisations(organisation_id) ON DELETE CASCADE,
    feature_code VARCHAR(50) NOT NULL REFERENCES support_systems.system_features(feature_code) ON DELETE CASCADE,
    tier VARCHAR(50),  -- free, premium, enterprise, custom
    is_active BOOLEAN DEFAULT TRUE,
    enabled_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,  -- NULL = never expires
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (organisation_id, feature_code)
);

CREATE INDEX IF NOT EXISTS idx_org_subscriptions_org ON organisations.feature_subscriptions(organisation_id);
CREATE INDEX IF NOT EXISTS idx_org_subscriptions_feature ON organisations.feature_subscriptions(feature_code);
CREATE INDEX IF NOT EXISTS idx_org_subscriptions_active ON organisations.feature_subscriptions(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_org_subscriptions_tier ON organisations.feature_subscriptions(tier);

COMMENT ON TABLE organisations.feature_subscriptions IS 'Tracks which features organisations have subscribed to (SaaS model)';
COMMENT ON COLUMN organisations.feature_subscriptions.tier IS 'Subscription tier: free=limited, premium=standard, enterprise=unlimited';
COMMENT ON COLUMN organisations.feature_subscriptions.expires_at IS 'Subscription expiration date (NULL = permanent)';

-- ============================================================================
-- TABLE: core.feature_permissions
-- Description: Granular feature permissions (e.g., within ai_studio: read, execute, manage)
-- ============================================================================
CREATE TABLE IF NOT EXISTS core.feature_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_id UUID NOT NULL REFERENCES core.groups(id) ON DELETE CASCADE,
    feature_code VARCHAR(50) NOT NULL REFERENCES support_systems.system_features(feature_code) ON DELETE CASCADE,
    permission_key VARCHAR(100) NOT NULL,  -- e.g., 'ai_studio.read', 'ai_studio.execute', 'ai_studio.manage'
    allowed BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (group_id, feature_code, permission_key)
);

CREATE INDEX IF NOT EXISTS idx_feature_perms_role ON core.feature_permissions(group_id);
CREATE INDEX IF NOT EXISTS idx_feature_perms_feature ON core.feature_permissions(feature_code);
CREATE INDEX IF NOT EXISTS idx_feature_perms_allowed ON core.feature_permissions(allowed) WHERE allowed = TRUE;

COMMENT ON TABLE core.feature_permissions IS 'Granular permissions within features (e.g., who can execute AI operations vs just view results)';
COMMENT ON COLUMN core.feature_permissions.permission_key IS 'Specific permission within feature: {feature_code}.{action} (e.g., ai_studio.execute)';

-- Seed data disabled (requires UUID group_id lookup - to be implemented)
