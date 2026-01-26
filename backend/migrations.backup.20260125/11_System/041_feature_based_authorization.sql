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
    role_id INTEGER NOT NULL REFERENCES core.roles(role_id) ON DELETE CASCADE,
    feature_code VARCHAR(50) NOT NULL REFERENCES support_systems.system_features(feature_code) ON DELETE CASCADE,
    access_level VARCHAR(20) DEFAULT 'view',  -- view, edit, manage, execute
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (role_id, feature_code)
);

CREATE INDEX IF NOT EXISTS idx_role_features_role ON core.role_features(role_id);
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
    organization_id UUID NOT NULL REFERENCES organisations.organisations(organization_id) ON DELETE CASCADE,
    feature_code VARCHAR(50) NOT NULL REFERENCES support_systems.system_features(feature_code) ON DELETE CASCADE,
    tier VARCHAR(50),  -- free, premium, enterprise, custom
    is_active BOOLEAN DEFAULT TRUE,
    enabled_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,  -- NULL = never expires
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (organization_id, feature_code)
);

CREATE INDEX IF NOT EXISTS idx_org_subscriptions_org ON organisations.feature_subscriptions(organization_id);
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
    role_id INTEGER NOT NULL REFERENCES core.roles(role_id) ON DELETE CASCADE,
    feature_code VARCHAR(50) NOT NULL REFERENCES support_systems.system_features(feature_code) ON DELETE CASCADE,
    permission_key VARCHAR(100) NOT NULL,  -- e.g., 'ai_studio.read', 'ai_studio.execute', 'ai_studio.manage'
    allowed BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (role_id, feature_code, permission_key)
);

CREATE INDEX IF NOT EXISTS idx_feature_perms_role ON core.feature_permissions(role_id);
CREATE INDEX IF NOT EXISTS idx_feature_perms_feature ON core.feature_permissions(feature_code);
CREATE INDEX IF NOT EXISTS idx_feature_perms_allowed ON core.feature_permissions(allowed) WHERE allowed = TRUE;

COMMENT ON TABLE core.feature_permissions IS 'Granular permissions within features (e.g., who can execute AI operations vs just view results)';
COMMENT ON COLUMN core.feature_permissions.permission_key IS 'Specific permission within feature: {feature_code}.{action} (e.g., ai_studio.execute)';

-- ============================================================================
-- SEED DATA: Initial Feature Role Mapping
-- ============================================================================

-- Free Tier Features (all free users get these)
INSERT INTO core.role_features (role_id, feature_code, access_level, enabled) VALUES
    -- Learning execution (all free users)
    (1, 'code_sandbox', 'execute', TRUE),  -- role_id=1 is 'student'/free
    (1, 'terminal_access', 'execute', TRUE),

    -- Learning features (limited)
    (1, 'learning_journal', 'view', TRUE),

    -- Tutor features
    (1, 'comprehension_checker', 'execute', TRUE),

    -- Gamification features
    (1, 'adaptive_difficulty', 'execute', TRUE),
    (1, 'daily_recall', 'execute', TRUE)
ON CONFLICT (role_id, feature_code) DO NOTHING;

-- Premium Tier Features
INSERT INTO core.role_features (role_id, feature_code, access_level, enabled) VALUES
    -- Premium = role_id 2 (can use advanced features)
    (2, 'whiteboard_engine', 'execute', TRUE),
    (2, 'network_simulation', 'execute', TRUE),
    (2, 'speech_to_text', 'execute', TRUE),
    (2, 'timer_wrapper', 'execute', TRUE),
    (2, 'project_portfolio', 'execute', TRUE),
    (2, 'project_based_learning', 'execute', TRUE),
    (2, 'learning_path_generator', 'execute', TRUE),
    (2, 'npc_tutor', 'execute', TRUE),
    (2, 'mindmap_generator', 'execute', TRUE),

    -- Everything from free tier
    (2, 'code_sandbox', 'execute', TRUE),
    (2, 'terminal_access', 'execute', TRUE),
    (2, 'learning_journal', 'execute', TRUE),
    (2, 'comprehension_checker', 'execute', TRUE),
    (2, 'adaptive_difficulty', 'execute', TRUE),
    (2, 'daily_recall', 'execute', TRUE)
ON CONFLICT (role_id, feature_code) DO NOTHING;

-- Creator/Teacher Role Features (role_id = 3)
INSERT INTO core.role_features (role_id, feature_code, access_level, enabled) VALUES
    -- Creator = role_id 3 (can manage teaching features)
    (3, 'whiteboard_engine', 'manage', TRUE),  -- Can create interactive tasks
    (3, 'project_based_learning', 'manage', TRUE),
    (3, 'learning_path_generator', 'manage', TRUE),
    (3, 'npc_tutor', 'manage', TRUE),
    (3, 'socratic_dialog', 'manage', TRUE),
    (3, 'peer_instruction', 'manage', TRUE),
    (3, 'peer_review', 'manage', TRUE),
    (3, 'team_case', 'manage', TRUE),
    (3, 'project_portfolio', 'manage', TRUE),
    (3, 'xp_quest_system', 'manage', TRUE),
    (3, 'inverted_classroom', 'manage', TRUE),
    (3, 'mindmap_generator', 'manage', TRUE),

    -- Everything from free + premium tiers
    (3, 'code_sandbox', 'manage', TRUE),
    (3, 'terminal_access', 'execute', TRUE),
    (3, 'learning_journal', 'execute', TRUE),
    (3, 'comprehension_checker', 'execute', TRUE),
    (3, 'adaptive_difficulty', 'execute', TRUE),
    (3, 'daily_recall', 'execute', TRUE),
    (3, 'network_simulation', 'execute', TRUE),
    (3, 'speech_to_text', 'execute', TRUE),
    (3, 'timer_wrapper', 'execute', TRUE)
ON CONFLICT (role_id, feature_code) DO NOTHING;

-- Admin Role Features (all features, full control) - role_id = 7 (Admin)
INSERT INTO core.role_features (role_id, feature_code, access_level, enabled)
SELECT
    7,
    feature_code,
    'manage',
    TRUE
FROM support_systems.system_features
ON CONFLICT (role_id, feature_code) DO NOTHING;

-- Superadmin Role (all features) - role_id = 8
INSERT INTO core.role_features (role_id, feature_code, access_level, enabled)
SELECT
    8,
    feature_code,
    'manage',
    TRUE
FROM support_systems.system_features
ON CONFLICT (role_id, feature_code) DO NOTHING;

-- ============================================================================
-- SEED DATA: Initial Feature Permissions (granular control within features)
-- ============================================================================

-- Learning execution permissions
INSERT INTO core.feature_permissions (role_id, feature_code, permission_key, allowed) VALUES
    (1, 'code_sandbox', 'learning.execute', TRUE),
    (1, 'code_sandbox', 'learning.manage', FALSE),

    (2, 'code_sandbox', 'learning.execute', TRUE),
    (2, 'code_sandbox', 'learning.manage', FALSE),

    (3, 'code_sandbox', 'learning.execute', TRUE),
    (3, 'code_sandbox', 'learning.manage', TRUE)
ON CONFLICT (role_id, feature_code, permission_key) DO NOTHING;

-- Analytics permissions (learning_journal analytics access)
INSERT INTO core.feature_permissions (role_id, feature_code, permission_key, allowed) VALUES
    (1, 'learning_journal', 'analytics.view', TRUE),
    (1, 'learning_journal', 'analytics.export', FALSE),

    (2, 'learning_journal', 'analytics.view', TRUE),
    (2, 'learning_journal', 'analytics.export', TRUE),

    (3, 'learning_journal', 'analytics.view', TRUE),
    (3, 'learning_journal', 'analytics.export', TRUE),
    (3, 'learning_journal', 'analytics.manage', TRUE)
ON CONFLICT (role_id, feature_code, permission_key) DO NOTHING;

-- ============================================================================
-- IDEMPOTENCY VERIFICATION
-- ============================================================================
-- Verify tables were created
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'core' AND table_name IN ('role_features', 'feature_permissions')
UNION ALL
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'organisations' AND table_name = 'feature_subscriptions';
