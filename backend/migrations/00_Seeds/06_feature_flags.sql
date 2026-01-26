-- ============================================================================
-- Seed Data: Feature Flags & Feature Groups
-- Description: Progressive rollout feature flags (dark launch: all built, none enabled except essential)
-- Source: 090_feature_flags_core.sql
-- Author: LernsystemX Migration System
-- Date: 2026-01-26
-- Phase: 4 (Seed Data)
-- ============================================================================

-- All feature flags built, most disabled for progressive rollout (dark launch)

-- Social Core Features (7 flags)
INSERT INTO feature_flags (name, description, is_enabled, category) VALUES
    ('user_posts', 'Users can create text/media posts on their profile', FALSE, 'social'),
    ('feed_system', 'Personalized algorithmic feed generation', FALSE, 'social'),
    ('follow_system', 'Follow/unfollow other users, followers list', FALSE, 'social'),
    ('likes_reactions', 'Like and react to posts, comments, content', FALSE, 'social'),
    ('comments', 'Comment system (partially enabled for course discussions)', TRUE, 'social'),
    ('shares', 'Share/repost content to own feed', FALSE, 'social'),
    ('bookmarks', 'Save posts/content for later', FALSE, 'social')
ON CONFLICT (name) DO NOTHING;

-- Discovery (4 flags)
INSERT INTO feature_flags (name, description, is_enabled, category) VALUES
    ('trending_discovery', 'Trending content discovery page', FALSE, 'discovery'),
    ('hashtags', 'Hashtag tagging and search', FALSE, 'discovery'),
    ('mentions', '@mention users in posts and comments', FALSE, 'discovery'),
    ('explore_page', 'Explore feed with recommended content', FALSE, 'discovery')
ON CONFLICT (name) DO NOTHING;

-- Messaging (2 flags)
INSERT INTO feature_flags (name, description, is_enabled, category) VALUES
    ('direct_messages', '1-on-1 direct messaging', FALSE, 'messaging'),
    ('group_chat', 'Group chat rooms (enabled for study groups)', TRUE, 'messaging')
ON CONFLICT (name) DO NOTHING;

-- Advanced Social (3 flags)
INSERT INTO feature_flags (name, description, is_enabled, category) VALUES
    ('stories', 'Instagram-style ephemeral stories', FALSE, 'advanced_social'),
    ('live_streams', 'Live video streaming', FALSE, 'advanced_social'),
    ('polls', 'Poll posts and voting', FALSE, 'advanced_social')
ON CONFLICT (name) DO NOTHING;

-- Moderation (3 flags)
INSERT INTO feature_flags (name, description, is_enabled, category) VALUES
    ('ai_moderation', 'AI-powered content pre-screening (DSA compliance)', TRUE, 'moderation'),
    ('human_moderation', 'Human review queue for reported content', FALSE, 'moderation'),
    ('community_moderation', 'Community-driven content reporting', FALSE, 'moderation')
ON CONFLICT (name) DO NOTHING;

-- Analytics (2 flags)
INSERT INTO feature_flags (name, description, is_enabled, category) VALUES
    ('social_analytics', 'Post performance analytics for users', FALSE, 'analytics'),
    ('audience_insights', 'Follower demographics and insights', FALSE, 'analytics')
ON CONFLICT (name) DO NOTHING;

-- Compliance (3 flags)
INSERT INTO feature_flags (name, description, is_enabled, category) VALUES
    ('dsa_transparency', 'DSA-mandated transparency features', FALSE, 'compliance'),
    ('netzdg_reporting', 'NetzDG-compliant illegal content reporting', FALSE, 'compliance'),
    ('child_safety_strict', 'Child safety features (COPPA, age verification)', TRUE, 'compliance')
ON CONFLICT (name) DO NOTHING;

-- DRM (3 flags)
INSERT INTO feature_flags (name, description, is_enabled, category) VALUES
    ('drm_protection', 'DRM content protection (Denuvo-style)', FALSE, 'drm'),
    ('watermarking', 'Forensic watermarking for content', FALSE, 'drm'),
    ('license_management', 'License validation and management', FALSE, 'drm')
ON CONFLICT (name) DO NOTHING;

-- GDPR (3 flags)
INSERT INTO feature_flags (name, description, is_enabled, category) VALUES
    ('gdpr_consent', 'GDPR consent management', TRUE, 'gdpr'),
    ('data_portability', 'GDPR Art. 20 data export', FALSE, 'gdpr'),
    ('right_to_erasure', 'GDPR Art. 17 right to deletion', FALSE, 'gdpr')
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- Feature Groups (Admin UI Organization)
-- ============================================================================

INSERT INTO feature_flag_groups (group_name, feature_name, display_order) VALUES
    ('social_core', 'user_posts', 1),
    ('social_core', 'feed_system', 2),
    ('social_core', 'follow_system', 3),
    ('social_core', 'likes_reactions', 4),
    ('social_core', 'comments', 5),
    ('social_core', 'shares', 6),
    ('social_core', 'bookmarks', 7),
    ('discovery', 'trending_discovery', 1),
    ('discovery', 'hashtags', 2),
    ('discovery', 'mentions', 3),
    ('discovery', 'explore_page', 4),
    ('messaging', 'direct_messages', 1),
    ('messaging', 'group_chat', 2),
    ('advanced_social', 'stories', 1),
    ('advanced_social', 'live_streams', 2),
    ('advanced_social', 'polls', 3),
    ('moderation', 'ai_moderation', 1),
    ('moderation', 'human_moderation', 2),
    ('moderation', 'community_moderation', 3),
    ('analytics', 'social_analytics', 1),
    ('analytics', 'audience_insights', 2),
    ('compliance', 'dsa_transparency', 1),
    ('compliance', 'netzdg_reporting', 2),
    ('compliance', 'child_safety_strict', 3),
    ('drm', 'drm_protection', 1),
    ('drm', 'watermarking', 2),
    ('drm', 'license_management', 3),
    ('gdpr', 'gdpr_consent', 1),
    ('gdpr', 'data_portability', 2),
    ('gdpr', 'right_to_erasure', 3)
ON CONFLICT (group_name, feature_name, display_order) DO NOTHING;
