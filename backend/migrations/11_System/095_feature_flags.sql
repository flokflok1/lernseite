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
