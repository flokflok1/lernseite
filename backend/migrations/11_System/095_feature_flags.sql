-- ============================================================================
-- Migration: 095_feature_flags.sql
-- Description: Feature Flags System (Dark Launch) - Progressive Rollout
--              Strategy: Build 100%, Enable 0% (gradually)
--              Priority: User > Org > Segment > Percentage > Global
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-01-16
-- ============================================================================
-- Previous number: 076 (11_System) → Renumbered to 095 to resolve duplicates
-- Phase: Feature Flag System - Progressive Feature Rollout
--
-- Tables created:
-- - feature_flags (global flags)
-- - feature_flag_user_overrides (user-specific)
-- - feature_flag_org_overrides (organization-specific)
-- - feature_flag_segments (beta, premium, etc.)
-- - feature_flag_rollouts (percentage-based)
-- - feature_flag_groups (UI grouping)
-- - feature_flag_audit_log (changes tracking)
-- ============================================================================

BEGIN;

-- =====================================================
-- 1. GLOBAL FEATURE FLAGS
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_enabled BOOLEAN DEFAULT FALSE,
    category VARCHAR(50), -- 'social', 'compliance', 'drm', 'analytics'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(36), -- admin user_id

    CONSTRAINT chk_feature_flag_name CHECK (name ~* '^[a-z_]+$'), -- lowercase_underscore only
    CONSTRAINT chk_feature_flag_category CHECK (category IN (
        'social', 'discovery', 'messaging', 'advanced_social',
        'moderation', 'analytics', 'compliance', 'drm', 'gdpr', 'system'
    ))
);

CREATE INDEX idx_feature_flags_name ON feature_flags(name);
CREATE INDEX idx_feature_flags_enabled ON feature_flags(is_enabled);
CREATE INDEX idx_feature_flags_category ON feature_flags(category);

COMMENT ON TABLE feature_flags IS 'Global feature flags for progressive rollout (Dark Launch strategy)';
COMMENT ON COLUMN feature_flags.name IS 'Unique feature identifier (e.g., user_posts, feed_system)';
COMMENT ON COLUMN feature_flags.is_enabled IS 'Global enable/disable state (lowest priority)';

-- =====================================================
-- 2. USER-SPECIFIC OVERRIDES (Highest Priority)
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flag_user_overrides (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL REFERENCES feature_flags(name) ON DELETE CASCADE,
    user_id VARCHAR(36) NOT NULL,
    is_enabled BOOLEAN NOT NULL,
    reason TEXT, -- Why this user has override (e.g., 'Beta tester', 'VIP user')
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(36), -- admin user_id who created override

    CONSTRAINT uq_feature_user UNIQUE(feature_name, user_id)
);

CREATE INDEX idx_feature_user_override_user ON feature_flag_user_overrides(user_id);
CREATE INDEX idx_feature_user_override_feature ON feature_flag_user_overrides(feature_name);
CREATE INDEX idx_feature_user_override_enabled ON feature_flag_user_overrides(is_enabled);

COMMENT ON TABLE feature_flag_user_overrides IS 'User-specific feature flag overrides (highest priority)';
COMMENT ON COLUMN feature_flag_user_overrides.reason IS 'Reason for override (beta tester, VIP, bug fix, etc.)';

-- =====================================================
-- 3. ORGANIZATION-SPECIFIC OVERRIDES
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flag_org_overrides (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL REFERENCES feature_flags(name) ON DELETE CASCADE,
    organization_id VARCHAR(36) NOT NULL,
    is_enabled BOOLEAN NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(36),

    CONSTRAINT uq_feature_org UNIQUE(feature_name, organization_id)
);

CREATE INDEX idx_feature_org_override_org ON feature_flag_org_overrides(organization_id);
CREATE INDEX idx_feature_org_override_feature ON feature_flag_org_overrides(feature_name);
CREATE INDEX idx_feature_org_override_enabled ON feature_flag_org_overrides(is_enabled);

COMMENT ON TABLE feature_flag_org_overrides IS 'Organization-specific feature flag overrides (second priority)';
COMMENT ON COLUMN feature_flag_org_overrides.reason IS 'Reason for org override (enterprise tier, pilot program, etc.)';

-- =====================================================
-- 4. USER SEGMENTS (Beta, Premium, etc.)
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flag_segments (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL REFERENCES feature_flags(name) ON DELETE CASCADE,
    segment VARCHAR(50) NOT NULL, -- 'beta', 'premium', 'enterprise', 'early_access'
    is_enabled BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_feature_segment UNIQUE(feature_name, segment),
    CONSTRAINT chk_segment_name CHECK (segment IN (
        'beta', 'premium', 'enterprise', 'early_access',
        'free', 'creator', 'teacher', 'school', 'company'
    ))
);

CREATE INDEX idx_feature_segment_feature ON feature_flag_segments(feature_name);
CREATE INDEX idx_feature_segment_segment ON feature_flag_segments(segment);
CREATE INDEX idx_feature_segment_enabled ON feature_flag_segments(is_enabled);

COMMENT ON TABLE feature_flag_segments IS 'Feature flags for user segments (beta, premium, etc.)';
COMMENT ON COLUMN feature_flag_segments.segment IS 'User segment (beta, premium, enterprise, etc.)';

-- =====================================================
-- 5. PERCENTAGE ROLLOUT (5% → 25% → 100%)
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flag_rollouts (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL UNIQUE REFERENCES feature_flags(name) ON DELETE CASCADE,
    percentage INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_rollout_percentage CHECK (percentage >= 0 AND percentage <= 100)
);

CREATE INDEX idx_feature_rollout_feature ON feature_flag_rollouts(feature_name);
CREATE INDEX idx_feature_rollout_percentage ON feature_flag_rollouts(percentage);

COMMENT ON TABLE feature_flag_rollouts IS 'Percentage-based feature rollout (5% → 25% → 50% → 100%)';
COMMENT ON COLUMN feature_flag_rollouts.percentage IS 'Percentage of users who have access (0-100)';

-- =====================================================
-- 6. FEATURE FLAG GROUPS (Admin UI Organization)
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flag_groups (
    id SERIAL PRIMARY KEY,
    group_name VARCHAR(50) NOT NULL, -- 'social_core', 'discovery', 'compliance'
    feature_name VARCHAR(100) NOT NULL REFERENCES feature_flags(name) ON DELETE CASCADE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_group_feature UNIQUE(group_name, feature_name)
);

CREATE INDEX idx_feature_group_name ON feature_flag_groups(group_name);
CREATE INDEX idx_feature_group_feature ON feature_flag_groups(feature_name);
CREATE INDEX idx_feature_group_order ON feature_flag_groups(display_order);

COMMENT ON TABLE feature_flag_groups IS 'Group feature flags for Admin UI organization';
COMMENT ON COLUMN feature_flag_groups.display_order IS 'Display order in Admin UI';

-- =====================================================
-- 7. AUDIT LOG (Track all changes)
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flag_audit_log (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL, -- 'created', 'enabled', 'disabled', 'rollout_changed'
    old_value JSONB,
    new_value JSONB,
    user_id VARCHAR(36), -- Admin who made change
    organization_id VARCHAR(36), -- If org-specific change
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_audit_action CHECK (action IN (
        'created', 'enabled', 'disabled', 'rollout_changed',
        'user_override_added', 'user_override_removed',
        'org_override_added', 'org_override_removed',
        'segment_enabled', 'segment_disabled'
    ))
);

CREATE INDEX idx_feature_audit_feature ON feature_flag_audit_log(feature_name);
CREATE INDEX idx_feature_audit_action ON feature_flag_audit_log(action);
CREATE INDEX idx_feature_audit_user ON feature_flag_audit_log(user_id);
CREATE INDEX idx_feature_audit_created ON feature_flag_audit_log(created_at DESC);

COMMENT ON TABLE feature_flag_audit_log IS 'Audit log for all feature flag changes (compliance requirement)';
COMMENT ON COLUMN feature_flag_audit_log.action IS 'Type of change made to feature flag';

-- =====================================================
-- 8. UPDATED_AT TRIGGER FUNCTION
-- =====================================================

CREATE OR REPLACE FUNCTION update_feature_flag_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER trg_feature_flags_updated_at
    BEFORE UPDATE ON feature_flags
    FOR EACH ROW EXECUTE FUNCTION update_feature_flag_updated_at();

CREATE TRIGGER trg_feature_user_overrides_updated_at
    BEFORE UPDATE ON feature_flag_user_overrides
    FOR EACH ROW EXECUTE FUNCTION update_feature_flag_updated_at();

CREATE TRIGGER trg_feature_org_overrides_updated_at
    BEFORE UPDATE ON feature_flag_org_overrides
    FOR EACH ROW EXECUTE FUNCTION update_feature_flag_updated_at();

CREATE TRIGGER trg_feature_segments_updated_at
    BEFORE UPDATE ON feature_flag_segments
    FOR EACH ROW EXECUTE FUNCTION update_feature_flag_updated_at();

CREATE TRIGGER trg_feature_rollouts_updated_at
    BEFORE UPDATE ON feature_flag_rollouts
    FOR EACH ROW EXECUTE FUNCTION update_feature_flag_updated_at();

-- =====================================================
-- 9. SEED DATA - ALL FEATURE FLAGS (Dark Launch: 100% Built, 0% Enabled)
-- =====================================================

-- Social Core (7 Flags)
INSERT INTO feature_flags (name, description, is_enabled, category) VALUES
    ('user_posts', 'Users can create text/media posts on their profile', FALSE, 'social'),
    ('feed_system', 'Personalized algorithmic feed generation', FALSE, 'social'),
    ('follow_system', 'Follow/unfollow other users, followers list', FALSE, 'social'),
    ('likes_reactions', 'Like and react to posts, comments, content', FALSE, 'social'),
    ('comments', 'Comment system (partially enabled for course discussions)', TRUE, 'social'),
    ('shares', 'Share/repost content to own feed', FALSE, 'social'),
    ('bookmarks', 'Save posts/content for later', FALSE, 'social')
ON CONFLICT (name) DO NOTHING;

-- Discovery (4 Flags)
INSERT INTO feature_flags (name, description, is_enabled, category) VALUES
    ('trending_discovery', 'Trending content discovery page', FALSE, 'discovery'),
    ('hashtags', 'Hashtag tagging and search', FALSE, 'discovery'),
    ('mentions', '@mention users in posts and comments', FALSE, 'discovery'),
    ('explore_page', 'Explore feed with recommended content', FALSE, 'discovery')
ON CONFLICT (name) DO NOTHING;

-- Messaging (2 Flags)
INSERT INTO feature_flags (name, description, is_enabled, category) VALUES
    ('direct_messages', '1-on-1 direct messaging', FALSE, 'messaging'),
    ('group_chat', 'Group chat rooms (enabled for study groups)', TRUE, 'messaging')
ON CONFLICT (name) DO NOTHING;

-- Advanced Social (3 Flags)
INSERT INTO feature_flags (name, description, is_enabled, category) VALUES
    ('stories', 'Instagram-style ephemeral stories', FALSE, 'advanced_social'),
    ('live_streams', 'Live video streaming', FALSE, 'advanced_social'),
    ('polls', 'Poll posts and voting', FALSE, 'advanced_social')
ON CONFLICT (name) DO NOTHING;

-- Moderation (3 Flags)
INSERT INTO feature_flags (name, description, is_enabled, category) VALUES
    ('ai_moderation', 'AI-powered content pre-screening (DSA compliance)', TRUE, 'moderation'),
    ('human_moderation', 'Human review queue for reported content', FALSE, 'moderation'),
    ('community_moderation', 'Community-driven content reporting', FALSE, 'moderation')
ON CONFLICT (name) DO NOTHING;

-- Analytics (2 Flags)
INSERT INTO feature_flags (name, description, is_enabled, category) VALUES
    ('social_analytics', 'Post performance analytics for users', FALSE, 'analytics'),
    ('audience_insights', 'Follower demographics and insights', FALSE, 'analytics')
ON CONFLICT (name) DO NOTHING;

-- Compliance (3 Flags)
INSERT INTO feature_flags (name, description, is_enabled, category) VALUES
    ('dsa_transparency', 'DSA-mandated transparency features', FALSE, 'compliance'),
    ('netzdg_reporting', 'NetzDG-compliant illegal content reporting', FALSE, 'compliance'),
    ('child_safety_strict', 'Child safety features (COPPA, age verification)', TRUE, 'compliance')
ON CONFLICT (name) DO NOTHING;

-- DRM (3 Flags)
INSERT INTO feature_flags (name, description, is_enabled, category) VALUES
    ('drm_protection', 'DRM content protection (Denuvo-style)', FALSE, 'drm'),
    ('watermarking', 'Forensic watermarking for content', FALSE, 'drm'),
    ('license_management', 'License validation and management', FALSE, 'drm')
ON CONFLICT (name) DO NOTHING;

-- GDPR (3 Flags)
INSERT INTO feature_flags (name, description, is_enabled, category) VALUES
    ('gdpr_consent', 'GDPR consent management', TRUE, 'gdpr'),
    ('data_portability', 'GDPR Art. 20 data export', FALSE, 'gdpr'),
    ('right_to_erasure', 'GDPR Art. 17 right to deletion', FALSE, 'gdpr')
ON CONFLICT (name) DO NOTHING;

-- =====================================================
-- 10. SEED FEATURE GROUPS (Admin UI Organization)
-- =====================================================

INSERT INTO feature_flag_groups (group_name, feature_name, display_order) VALUES
    -- Social Core
    ('social_core', 'user_posts', 1),
    ('social_core', 'feed_system', 2),
    ('social_core', 'follow_system', 3),
    ('social_core', 'likes_reactions', 4),
    ('social_core', 'comments', 5),
    ('social_core', 'shares', 6),
    ('social_core', 'bookmarks', 7),
    -- Discovery
    ('discovery', 'trending_discovery', 1),
    ('discovery', 'hashtags', 2),
    ('discovery', 'mentions', 3),
    ('discovery', 'explore_page', 4),
    -- Messaging
    ('messaging', 'direct_messages', 1),
    ('messaging', 'group_chat', 2),
    -- Advanced Social
    ('advanced_social', 'stories', 1),
    ('advanced_social', 'live_streams', 2),
    ('advanced_social', 'polls', 3),
    -- Moderation
    ('moderation', 'ai_moderation', 1),
    ('moderation', 'human_moderation', 2),
    ('moderation', 'community_moderation', 3),
    -- Analytics
    ('analytics', 'social_analytics', 1),
    ('analytics', 'audience_insights', 2),
    -- Compliance
    ('compliance', 'dsa_transparency', 1),
    ('compliance', 'netzdg_reporting', 2),
    ('compliance', 'child_safety_strict', 3),
    ('compliance', 'gdpr_consent', 4),
    ('compliance', 'data_portability', 5),
    ('compliance', 'right_to_erasure', 6),
    -- DRM
    ('drm', 'drm_protection', 1),
    ('drm', 'watermarking', 2),
    ('drm', 'license_management', 3)
ON CONFLICT (group_name, feature_name) DO NOTHING;

-- =====================================================
-- ENHANCEMENTS: ENTERPRISE FEATURE CONFIGURATION
-- (Added in Phase 1 of Feature Configuration System)
-- =====================================================

-- =====================================================
-- 11. FEATURE ROLE MAPPINGS (Role-based fine-grained control)
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flag_role_mappings (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL REFERENCES feature_flags(name) ON DELETE CASCADE,
    role_code VARCHAR(50) NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    max_usage_per_day INTEGER,
    max_creation_per_month INTEGER,
    priority_level INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_feature_role UNIQUE(feature_name, role_code),
    CONSTRAINT chk_role_code CHECK (role_code IN (
        'admin', 'creator', 'teacher', 'student', 'parent',
        'moderator', 'support', 'company', 'school'
    ))
);

CREATE INDEX idx_feature_role_feature ON feature_flag_role_mappings(feature_name);
CREATE INDEX idx_feature_role_role ON feature_flag_role_mappings(role_code);
CREATE INDEX idx_feature_role_enabled ON feature_flag_role_mappings(is_enabled);
CREATE INDEX idx_feature_role_priority ON feature_flag_role_mappings(priority_level);

COMMENT ON TABLE feature_flag_role_mappings IS 'Role-based access control with per-role quotas';
COMMENT ON COLUMN feature_flag_role_mappings.max_usage_per_day IS 'Daily limit (NULL = unlimited)';
COMMENT ON COLUMN feature_flag_role_mappings.priority_level IS '0=normal, 10=premium, 20=enterprise';

-- =====================================================
-- 12. FEATURE TIER LIMITS (Subscription tier-based quotas)
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flag_tier_limits (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL REFERENCES feature_flags(name) ON DELETE CASCADE,
    tier_code VARCHAR(50) NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    max_concurrent_usage INTEGER,
    max_monthly_quota INTEGER,
    max_per_day INTEGER,
    max_storage_gb DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_feature_tier UNIQUE(feature_name, tier_code),
    CONSTRAINT chk_tier_code CHECK (tier_code IN ('free', 'premium', 'enterprise'))
);

CREATE INDEX idx_feature_tier_feature ON feature_flag_tier_limits(feature_name);
CREATE INDEX idx_feature_tier_tier ON feature_flag_tier_limits(tier_code);
CREATE INDEX idx_feature_tier_enabled ON feature_flag_tier_limits(is_enabled);

COMMENT ON TABLE feature_flag_tier_limits IS 'Tier-based feature limits (free, premium, enterprise)';

-- =====================================================
-- 13. FEATURE ROLLOUT PLANS (4-Phase progressive rollout)
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flag_rollout_plans (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL REFERENCES feature_flags(name) ON DELETE CASCADE,
    plan_name VARCHAR(255) NOT NULL,
    phase_1_percentage INTEGER DEFAULT 5,
    phase_1_duration_hours INTEGER DEFAULT 12,
    phase_1_start_at TIMESTAMP,
    phase_2_percentage INTEGER DEFAULT 25,
    phase_2_duration_hours INTEGER DEFAULT 24,
    phase_2_start_at TIMESTAMP,
    phase_3_percentage INTEGER DEFAULT 50,
    phase_3_duration_hours INTEGER DEFAULT 48,
    phase_3_start_at TIMESTAMP,
    phase_4_start_at TIMESTAMP,
    current_phase INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'planned',
    target_roles TEXT[],
    target_tiers TEXT[],
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(36),

    CONSTRAINT uq_feature_rollout UNIQUE(feature_name),
    CONSTRAINT chk_rollout_status CHECK (status IN ('planned', 'active', 'paused', 'completed', 'rolled_back')),
    CONSTRAINT chk_current_phase CHECK (current_phase >= 0 AND current_phase <= 5)
);

CREATE INDEX idx_rollout_feature ON feature_flag_rollout_plans(feature_name);
CREATE INDEX idx_rollout_status ON feature_flag_rollout_plans(status);
CREATE INDEX idx_rollout_active ON feature_flag_rollout_plans(status) WHERE status = 'active';

COMMENT ON TABLE feature_flag_rollout_plans IS '4-phase progressive rollout (canary → early → wider → full)';

-- =====================================================
-- 14. FEATURE A/B TESTS (Variant testing)
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flag_ab_tests (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL REFERENCES feature_flags(name) ON DELETE CASCADE,
    test_name VARCHAR(255) NOT NULL,
    variant_a_name VARCHAR(100) NOT NULL,
    variant_a_percentage INTEGER NOT NULL DEFAULT 50,
    variant_a_config JSONB,
    variant_b_name VARCHAR(100) NOT NULL,
    variant_b_percentage INTEGER NOT NULL DEFAULT 50,
    variant_b_config JSONB,
    target_roles TEXT[],
    target_tiers TEXT[],
    metrics_to_track TEXT[],
    started_at TIMESTAMP,
    planned_duration_days INTEGER DEFAULT 14,
    ended_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'planned',
    winner VARCHAR(1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(36),

    CONSTRAINT chk_ab_percentages CHECK (variant_a_percentage + variant_b_percentage = 100),
    CONSTRAINT chk_ab_status CHECK (status IN ('planned', 'active', 'paused', 'completed')),
    CONSTRAINT chk_ab_winner CHECK (winner IS NULL OR winner IN ('A', 'B'))
);

CREATE INDEX idx_ab_feature ON feature_flag_ab_tests(feature_name);
CREATE INDEX idx_ab_status ON feature_flag_ab_tests(status);
CREATE INDEX idx_ab_active ON feature_flag_ab_tests(status) WHERE status = 'active';

COMMENT ON TABLE feature_flag_ab_tests IS 'A/B test configuration for feature variants';

-- =====================================================
-- 15. FEATURE CONFIGURATION CACHE TRACKING
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flag_cache_status (
    feature_name VARCHAR(100) PRIMARY KEY REFERENCES feature_flags(name) ON DELETE CASCADE,
    last_config_change TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cache_invalidated_at TIMESTAMP,
    cache_ttl_seconds INTEGER DEFAULT 300,
    requires_redis_pubsub BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_cache_status_invalidated ON feature_flag_cache_status(cache_invalidated_at);
CREATE INDEX idx_cache_status_requires_pubsub ON feature_flag_cache_status(requires_redis_pubsub) WHERE requires_redis_pubsub = TRUE;

COMMENT ON TABLE feature_flag_cache_status IS 'Track cache invalidation for Redis Pub/Sub events';

-- =====================================================
-- 16. ENHANCED AUDIT LOG WITH IMPACT TRACKING
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flag_audit_log_enhanced (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    changed_field VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    change_details JSONB,
    user_id VARCHAR(36),
    user_email VARCHAR(255),
    organization_id VARCHAR(36),
    ip_address INET,
    user_agent TEXT,
    estimated_affected_users INTEGER,
    estimated_affected_organizations INTEGER,
    rollback_possible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_action CHECK (action IN (
        'feature_created', 'feature_enabled', 'feature_disabled',
        'role_permission_added', 'role_permission_removed', 'role_quota_updated',
        'tier_limit_added', 'tier_limit_removed', 'tier_limit_updated',
        'org_override_added', 'org_override_removed', 'org_override_updated',
        'rollout_started', 'rollout_paused', 'rollout_completed', 'rollout_rolled_back',
        'rollout_phase_advanced', 'rollout_percentage_adjusted',
        'ab_test_started', 'ab_test_ended', 'ab_test_winner_announced',
        'segment_enabled', 'segment_disabled', 'segment_updated',
        'user_override_added', 'user_override_removed'
    ))
);

CREATE INDEX idx_audit_enhanced_feature ON feature_flag_audit_log_enhanced(feature_name);
CREATE INDEX idx_audit_enhanced_action ON feature_flag_audit_log_enhanced(action);
CREATE INDEX idx_audit_enhanced_user ON feature_flag_audit_log_enhanced(user_id);
CREATE INDEX idx_audit_enhanced_created ON feature_flag_audit_log_enhanced(created_at DESC);
CREATE INDEX idx_audit_enhanced_org ON feature_flag_audit_log_enhanced(organization_id);

COMMENT ON TABLE feature_flag_audit_log_enhanced IS 'Enhanced audit log with impact tracking for compliance';

-- =====================================================
-- 17. FEATURE CONFIGURATION SNAPSHOTS (For rollback)
-- =====================================================

CREATE TABLE IF NOT EXISTS feature_flag_config_snapshots (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL REFERENCES feature_flags(name) ON DELETE CASCADE,
    snapshot_type VARCHAR(20) NOT NULL,
    feature_config JSONB NOT NULL,
    role_mappings JSONB,
    tier_limits JSONB,
    org_overrides JSONB,
    rollout_plan JSONB,
    ab_tests JSONB,
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,

    CONSTRAINT chk_snapshot_type CHECK (snapshot_type IN ('pre_change', 'post_change', 'rollback'))
);

CREATE INDEX idx_snapshot_feature ON feature_flag_config_snapshots(feature_name);
CREATE INDEX idx_snapshot_created ON feature_flag_config_snapshots(created_at DESC);
CREATE INDEX idx_snapshot_type ON feature_flag_config_snapshots(snapshot_type);

COMMENT ON TABLE feature_flag_config_snapshots IS 'Configuration snapshots for rollback capability';

-- =====================================================
-- 18. TRIGGERS FOR UPDATED_AT AND CACHE INVALIDATION
-- =====================================================

CREATE OR REPLACE FUNCTION update_feature_config_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_feature_role_mappings_updated_at
    BEFORE UPDATE ON feature_flag_role_mappings
    FOR EACH ROW EXECUTE FUNCTION update_feature_config_timestamp();

CREATE TRIGGER trg_feature_tier_limits_updated_at
    BEFORE UPDATE ON feature_flag_tier_limits
    FOR EACH ROW EXECUTE FUNCTION update_feature_config_timestamp();

CREATE TRIGGER trg_feature_rollout_plans_updated_at
    BEFORE UPDATE ON feature_flag_rollout_plans
    FOR EACH ROW EXECUTE FUNCTION update_feature_config_timestamp();

CREATE TRIGGER trg_feature_ab_tests_updated_at
    BEFORE UPDATE ON feature_flag_ab_tests
    FOR EACH ROW EXECUTE FUNCTION update_feature_config_timestamp();

-- Cache invalidation trigger
CREATE OR REPLACE FUNCTION invalidate_feature_cache()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO feature_flag_cache_status (feature_name, last_config_change, cache_invalidated_at)
    VALUES (NEW.feature_name, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    ON CONFLICT (feature_name) DO UPDATE SET
        last_config_change = CURRENT_TIMESTAMP,
        cache_invalidated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_invalidate_cache_on_role_mapping
    AFTER INSERT OR UPDATE OR DELETE ON feature_flag_role_mappings
    FOR EACH ROW EXECUTE FUNCTION invalidate_feature_cache();

CREATE TRIGGER trg_invalidate_cache_on_tier_limits
    AFTER INSERT OR UPDATE OR DELETE ON feature_flag_tier_limits
    FOR EACH ROW EXECUTE FUNCTION invalidate_feature_cache();

CREATE TRIGGER trg_invalidate_cache_on_rollout
    AFTER INSERT OR UPDATE OR DELETE ON feature_flag_rollout_plans
    FOR EACH ROW EXECUTE FUNCTION invalidate_feature_cache();

CREATE TRIGGER trg_invalidate_cache_on_ab_test
    AFTER INSERT OR UPDATE OR DELETE ON feature_flag_ab_tests
    FOR EACH ROW EXECUTE FUNCTION invalidate_feature_cache();

COMMIT;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Count feature flags by category
-- SELECT category, COUNT(*), SUM(CASE WHEN is_enabled THEN 1 ELSE 0 END) as enabled
-- FROM feature_flags
-- GROUP BY category
-- ORDER BY category;

-- Show all enabled flags
-- SELECT name, description, category
-- FROM feature_flags
-- WHERE is_enabled = TRUE
-- ORDER BY category, name;

-- =====================================================
-- END MIGRATION 076
-- =====================================================
